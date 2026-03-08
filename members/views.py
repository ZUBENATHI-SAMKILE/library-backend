from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta, datetime
import jwt
from django.conf import settings

from .models import Member
from .serializers import MemberSerializer


def generate_member_token(member):
    payload = {
        "member_id": member.id,
        "email": member.email,
        "role": "member",
        "exp": datetime.utcnow() + timedelta(days=1),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


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


# ── Member Auth ───────────────────────────────────────────────────────────────

class MemberRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        if not data.get("name"):
            return Response({"error": "Name is required"}, status=400)
        if not data.get("email"):
            return Response({"error": "Email is required"}, status=400)
        if not data.get("password"):
            return Response({"error": "Password is required"}, status=400)
        if len(data.get("password", "")) < 6:
            return Response({"error": "Password must be at least 6 characters"}, status=400)
        if Member.objects.filter(email=data.get("email")).exists():
            return Response({"error": "Email already registered"}, status=400)

        expiry = (timezone.now() + timedelta(days=365)).date()

        member = Member(
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            address=data.get("address", ""),
            membership_expiry=expiry,
            status="active",
        )
        member.set_password(data.get("password"))
        member.save()

        token = generate_member_token(member)
        return Response({
            "member": MemberSerializer(member).data,
            "token": token,
            "role": "member",
        }, status=201)


class MemberLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=400)

        try:
            member = Member.objects.get(email=email)
        except Member.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=401)

        if not member.check_password(password):
            return Response({"error": "Invalid credentials"}, status=401)

        if member.status == "suspended":
            return Response({"error": "Your account has been suspended"}, status=403)

        token = generate_member_token(member)
        return Response({
            "member": MemberSerializer(member).data,
            "token": token,
            "role": "member",
        })


class MemberProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        member = get_member_from_token(request)
        if not member:
            return Response({"error": "Unauthorized"}, status=401)
        return Response({**MemberSerializer(member).data, "role": "member"})

    def patch(self, request):
        member = get_member_from_token(request)
        if not member:
            return Response({"error": "Unauthorized"}, status=401)

        allowed = ["name", "phone", "address"]
        for field in allowed:
            if field in request.data:
                setattr(member, field, request.data[field])

        if request.data.get("password"):
            member.set_password(request.data["password"])

        member.save()
        return Response(MemberSerializer(member).data)


# ── Staff Member Management ───────────────────────────────────────────────────

class MemberListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.query_params.get("search", "")
        qs = Member.objects.all()
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        return Response(MemberSerializer(qs, many=True).data)

    def post(self, request):
        data = request.data.copy()
        # If staff adds a member manually, set default password and expiry
        if "membership_expiry" not in data:
            data["membership_expiry"] = (
                timezone.now() + timedelta(days=365)
            ).date().isoformat()

        serializer = MemberSerializer(data=data)
        if serializer.is_valid():
            member = serializer.save()
            # Set a default password if provided
            if request.data.get("password"):
                member.set_password(request.data["password"])
            else:
                member.set_password("changeme123")
            member.save()
            return Response(MemberSerializer(member).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MemberDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Member.objects.get(pk=pk)
        except Member.DoesNotExist:
            return None

    def get(self, request, pk):
        member = self.get_object(pk)
        if not member:
            return Response({"error": "Member not found"}, status=404)
        return Response(MemberSerializer(member).data)

    def patch(self, request, pk):
        member = self.get_object(pk)
        if not member:
            return Response({"error": "Member not found"}, status=404)
        serializer = MemberSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        member = self.get_object(pk)
        if not member:
            return Response({"error": "Member not found"}, status=404)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)