from django.urls import path
from .views import (
    StaffListView,
    StaffDetailView,
    ActivityLogsView,
    AdminReportsView,
    PromoteMemberView,
)

urlpatterns = [
    path("staff/", StaffListView.as_view()),
    path("staff/<int:pk>/", StaffDetailView.as_view()),
    path("logs/", ActivityLogsView.as_view()),
    path("reports/", AdminReportsView.as_view()),
    path("promote/", PromoteMemberView.as_view()),
]