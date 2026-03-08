from rest_framework import serializers
from .models import Fine


class FineSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.name", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = Fine
        fields = [
            "id", "member", "member_name", "book", "book_title",
            "amount", "days_overdue", "paid", "paid_date", "created_at"
        ]