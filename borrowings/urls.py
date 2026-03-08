from django.urls import path
from .views import BorrowingListView, BorrowingReturnView

urlpatterns = [
    path("", BorrowingListView.as_view()),
    path("<int:pk>/return/", BorrowingReturnView.as_view()),
]