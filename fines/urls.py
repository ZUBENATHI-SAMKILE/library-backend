from django.urls import path
from .views import FineListView, FinePayView, MemberFinesView

urlpatterns = [
    path("my/", MemberFinesView.as_view()),
    path("", FineListView.as_view()),
    path("<int:pk>/pay/", FinePayView.as_view()),
]