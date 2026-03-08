from django.db import models
from members.models import Member
from books.models import Book


class Fine(models.Model):
    borrowing = models.OneToOneField(
        "borrowings.Borrowing",
        on_delete=models.CASCADE,
        related_name="fine"
    )
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="fines")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="fines")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    days_overdue = models.IntegerField(default=0)
    paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Fine: {self.member.name} — ${self.amount}"