from django.urls import path
from .views import ReservationListView, ReservationCancelView

urlpatterns = [
    path("", ReservationListView.as_view()),
    path("<int:pk>/cancel/", ReservationCancelView.as_view()),
]