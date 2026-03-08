from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
import jwt
from django.conf import settings

from .models import Reservation
from .serializers import ReservationSerializer
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


class ReservationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter_status = request.query_params.get("status", "")
        qs = Reservation.objects.select_related("member", "book").all()
        if filter_status:
            qs = qs.filter(status=filter_status)
        return Response(ReservationSerializer(qs, many=True).data)

    def post(self, request):
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            reservation = serializer.save()
            return Response(
                ReservationSerializer(reservation).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReservationCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            reservation = Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
        if reservation.status != "pending":
            return Response(
                {"error": "Only pending reservations can be cancelled"},
                status=400
            )
        reservation.status = "cancelled"
        reservation.save()
        return Response(ReservationSerializer(reservation).data)


class MemberReservationsView(APIView):
    permission_classes = [AllowAny]  # ← uses custom JWT not Django JWT

    def get(self, request):
        member = get_member_from_token(request)
        if not member:
            return Response({"error": "Unauthorized"}, status=401)
        qs = Reservation.objects.select_related("book").filter(member=member)
        return Response(ReservationSerializer(qs, many=True).data)

    def post(self, request):
        member = get_member_from_token(request)
        if not member:
            return Response({"error": "Unauthorized"}, status=401)
        data = {**request.data, "member": member.id}
        serializer = ReservationSerializer(data=data)
        if serializer.is_valid():
            reservation = serializer.save()
            return Response(ReservationSerializer(reservation).data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        member = get_member_from_token(request)
        if not member:
            return Response({"error": "Unauthorized"}, status=401)
        try:
            reservation = Reservation.objects.get(pk=pk, member=member)
        except Reservation.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
        reservation.status = "cancelled"
        reservation.save()
        return Response(ReservationSerializer(reservation).data)