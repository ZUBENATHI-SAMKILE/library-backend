from django.urls import path
from .views import BookListView, BookDetailView
from django.http import JsonResponse
from django.utils import timezone

def health(request):
    return JsonResponse({
        "status": "ok",
        "timestamp": timezone.now().isoformat(),
    })
urlpatterns = [
    path("health/", health),
    path("", BookListView.as_view()),
    path("<int:pk>/", BookDetailView.as_view()),
]