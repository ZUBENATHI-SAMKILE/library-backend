from django.db import models
from books.models import Book
from members.models import Member


class Borrowing(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("returned", "Returned"),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="borrowings")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    borrow_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    class Meta:
        ordering = ["-borrow_date"]

    def __str__(self):
        return f"{self.member.name} — {self.book.title}"