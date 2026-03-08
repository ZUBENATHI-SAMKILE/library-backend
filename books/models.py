from django.db import models


class Book(models.Model):
    GENRE_CHOICES = [
        ("Fiction", "Fiction"), ("Non-Fiction", "Non-Fiction"),
        ("Science", "Science"), ("History", "History"),
        ("Biography", "Biography"), ("Dystopian", "Dystopian"),
        ("Mystery", "Mystery"), ("Romance", "Romance"),
        ("Technology", "Technology"), ("Philosophy", "Philosophy"),
    ]

    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200, blank=True, default="")
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    isbn = models.CharField(max_length=20, blank=True, unique=True, null=True)
    year = models.IntegerField(null=True, blank=True)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    cover_image = models.CharField(max_length=200, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} by {self.author}"