from django.urls import path
from core.dashboard_views import DashboardStatsView

urlpatterns = [
    path("stats/", DashboardStatsView.as_view()),
]