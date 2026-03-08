from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"

    def validate(self, data):
        total = data.get(
            "total_copies",
            self.instance.total_copies if self.instance else 1
        )
        available = data.get("available_copies", total)
        if available > total:
            raise serializers.ValidationError(
                "Available copies cannot exceed total copies."
            )
        return data