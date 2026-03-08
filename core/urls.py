from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("django-admin/", admin.site.urls),

    # Staff endpoints — protected by Django JWT
    path("api/auth/", include("users.urls")),
    path("api/books/", include("books.urls")),
    path("api/members/", include("members.urls")),
    path("api/borrowings/", include("borrowings.urls")),
    path("api/fines/", include("fines.urls")),
    path("api/reservations/", include("reservations.urls")),
    path("api/admin/", include("admin_panel.urls")),
    path("api/dashboard/", include("core.dashboard_urls")),

    # Member portal endpoints — protected by custom JWT only
    path("api/member/", include("core.member_urls")),
]