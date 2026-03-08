from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import jwt

from .models import Borrowing
from .serializers import BorrowingSerializer, BorrowingCreateSerializer
from fines.models import Fine
from members.models import Member


def get_member_from_token(request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("role") != "member":
            return None
        return Member.objects.get(id=payload["member_id"])
    except Exception:
        return None


class BorrowingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter_status = request.query_params.get("status", "")
        qs = Borrowing.objects.select_related("member", "book").all()
        if filter_status and filter_status != "overdue":
            qs = qs.filter(status=filter_status)

        today = timezone.now().date()
        data = []
        for b in qs:
            item = BorrowingSerializer(b).data
            if b.status == "active" and b.due_date < today:
                item["status"] = "overdue"
                if filter_status == "overdue":
                    data.append(item)
                    continue
            if filter_status not in ["overdue"]:
                data.append(item)
        return Response(data)

    def post(self, request):
        serializer = BorrowingCreateSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.validated_data["book"]
            if book.available_copies < 1:
                return Response(
                    {"error": "No copies available"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            borrowing = serializer.save()
            book.available_copies -= 1
            book.save()
            return Response(
                BorrowingSerializer(borrowing).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BorrowingReturnView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            borrowing = Borrowing.objects.select_related("book", "member").get(pk=pk)
        except Borrowing.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        if borrowing.status == "returned":
            return Response({"error": "Already returned"}, status=400)

        today = timezone.now().date()
        borrowing.return_date = today
        borrowing.status = "returned"
        borrowing.save()

        book = borrowing.book
        book.available_copies += 1
        book.save()

        if today > borrowing.due_date:
            days_overdue = (today - borrowing.due_date).days
            fine_rate = getattr(settings, "FINE_RATE_PER_DAY", 0.50)
            Fine.objects.create(
                borrowing=borrowing,
                member=borrowing.member,
                book=borrowing.book,
                amount=days_overdue * fine_rate,
                days_overdue=days_overdue,
            )

        return Response(BorrowingSerializer(borrowing).data)


class BorrowingRenewView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, pk):
        member = get_member_from_token(request)
        if not member:
            return Response({"error": "Unauthorized"}, status=401)
        try:
            borrowing = Borrowing.objects.get(pk=pk, member=member, status="active")
        except Borrowing.DoesNotExist:
            return Response({"error": "Borrowing not found"}, status=404)

        today = timezone.now().date()
        if today > borrowing.due_date:
            return Response(
                {"error": "Cannot renew overdue books. Please return and pay fine first."},
                status=400
            )

        borrowing.due_date = borrowing.due_date + timedelta(days=14)
        borrowing.save()
        return Response(BorrowingSerializer(borrowing).data)


class MemberBorrowingsView(APIView):
    permission_classes = [AllowAny]  # ← uses custom JWT not Django JWT

    def get(self, request):
        member = get_member_from_token(request)
        if not member:
            return Response({"error": "Unauthorized"}, status=401)

        today = timezone.now().date()
        qs = Borrowing.objects.select_related("book").filter(member=member)
        data = []
        for b in qs:
            item = BorrowingSerializer(b).data
            if b.status == "active" and b.due_date < today:
                item["status"] = "overdue"
            elif b.status == "active" and (b.due_date - today).days <= 3:
                item["due_soon"] = True
            data.append(item)
        return Response(data)