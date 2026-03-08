from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.utils import timezone
import jwt
from django.conf import settings

from .models import Fine
from .serializers import FineSerializer
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


class FineListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        paid_filter = request.query_params.get("paid", None)
        qs = Fine.objects.select_related("member", "book").all()
        if paid_filter == "true":
            qs = qs.filter(paid=True)
        elif paid_filter == "false":
            qs = qs.filter(paid=False)
        return Response(FineSerializer(qs, many=True).data)


class FinePayView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            fine = Fine.objects.get(pk=pk)
        except Fine.DoesNotExist:
            return Response({"error": "Fine not found"}, status=404)
        if fine.paid:
            return Response({"error": "Already paid"}, status=400)
        fine.paid = True
        fine.paid_date = timezone.now().date()
        fine.save()
        return Response(FineSerializer(fine).data)


class MemberFinesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        member = get_member_from_token(request)
        if not member:
            return Response({"error": "Unauthorized"}, status=401)
        qs = Fine.objects.select_related("book").filter(member=member)
        return Response(FineSerializer(qs, many=True).data)