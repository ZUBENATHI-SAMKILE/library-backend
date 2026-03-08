from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from books.models import Book
from members.models import Member
from borrowings.models import Borrowing
from fines.models import Fine


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()

        total_books = Book.objects.count()
        available_books = Book.objects.filter(available_copies__gt=0).count()
        total_members = Member.objects.count()
        active_members = Member.objects.filter(status="active").count()
        active_borrowings = Borrowing.objects.filter(status="active").count()
        overdue_borrowings = Borrowing.objects.filter(status="active", due_date__lt=today).count()
        unpaid_fines = Fine.objects.filter(paid=False).count()
        total_fines_collected = sum(
            f.amount for f in Fine.objects.filter(paid=True)
        )

        recent_borrowings = Borrowing.objects.select_related(
            "member", "book"
        ).order_by("-borrow_date")[:5]

        recent_data = [
            {
                "id": b.id,
                "member": b.member.name,
                "book": b.book.title,
                "borrow_date": str(b.borrow_date),
                "due_date": str(b.due_date),
                "status": "overdue" if b.status == "active" and b.due_date < today else b.status,
            }
            for b in recent_borrowings
        ]

        return Response({
            "total_books": total_books,
            "available_books": available_books,
            "total_members": total_members,
            "active_members": active_members,
            "active_borrowings": active_borrowings,
            "overdue_borrowings": overdue_borrowings,
            "unpaid_fines": unpaid_fines,
            "total_fines_collected": float(total_fines_collected),
            "recent_borrowings": recent_data,
        })