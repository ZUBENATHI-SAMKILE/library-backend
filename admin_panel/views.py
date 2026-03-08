from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Count

from users.models import User
from users.serializers import UserSerializer
from borrowings.models import Borrowing


def is_admin(user):
    return user.role == "admin"


class StaffListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_admin(request.user):
            return Response({"error": "Admin access required"}, status=403)
        staff = User.objects.all().order_by("name")
        return Response(UserSerializer(staff, many=True).data)


class StaffDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if not is_admin(request.user):
            return Response({"error": "Admin access required"}, status=403)
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        allowed = {k: v for k, v in request.data.items() if k in ["role", "is_active"]}
        for field, value in allowed.items():
            setattr(user, field, value)
        user.save()
        return Response(UserSerializer(user).data)


class ActivityLogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_admin(request.user):
            return Response({"error": "Admin access required"}, status=403)
        borrowings = Borrowing.objects.select_related(
            "member", "book"
        ).order_by("-borrow_date")[:20]
        logs = []
        for b in borrowings:
            if b.return_date:
                logs.append({
                    "id": b.id,
                    "action": "Book Returned",
                    "details": f"'{b.book.title}' returned by {b.member.name}",
                    "user": "Staff",
                    "timestamp": str(b.return_date),
                })
            else:
                logs.append({
                    "id": b.id,
                    "action": "Book Issued",
                    "details": f"'{b.book.title}' issued to {b.member.name}",
                    "user": "Staff",
                    "timestamp": str(b.borrow_date),
                })
        return Response(logs)


class AdminReportsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_admin(request.user):
            return Response({"error": "Admin access required"}, status=403)
        most_borrowed = (
            Borrowing.objects
            .values("book__title", "book__author")
            .annotate(borrow_count=Count("id"))
            .order_by("-borrow_count")[:10]
        )
        return Response({
            "most_borrowed": [
                {
                    "title": item["book__title"],
                    "author": item["book__author"],
                    "borrow_count": item["borrow_count"],
                }
                for item in most_borrowed
            ]
        })


class PromoteMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not is_admin(request.user):
            return Response({"error": "Admin access required"}, status=403)

        member_id = request.data.get("member_id")
        if not member_id:
            return Response({"error": "member_id required"}, status=400)

        from members.models import Member
        try:
            member = Member.objects.get(pk=member_id)
        except Member.DoesNotExist:
            return Response({"error": "Member not found"}, status=404)

        if User.objects.filter(email=member.email).exists():
            return Response({"error": "Staff account already exists for this email"}, status=400)

        staff = User.objects.create_user(
            email=member.email,
            name=member.name,
            password="changeme123",  # temporary password
            role="librarian",
        )
        staff.save()

        return Response({
            "message": f"{member.name} promoted to Librarian successfully!",
            "temp_password": "changeme123",
            "note": "Please tell them to change their password after first login.",
        })