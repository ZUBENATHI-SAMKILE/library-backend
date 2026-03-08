from django.urls import path
from members.views import MemberRegisterView, MemberLoginView, MemberProfileView
from borrowings.views import MemberBorrowingsView, BorrowingRenewView
from fines.views import MemberFinesView
from reservations.views import MemberReservationsView
from books.views import MemberBookListView

urlpatterns = [
    # Auth
    path("auth/register/", MemberRegisterView.as_view()),
    path("auth/login/", MemberLoginView.as_view()),
    path("auth/profile/", MemberProfileView.as_view()),

    # Borrowings
    path("borrowings/", MemberBorrowingsView.as_view()),
    path("borrowings/<int:pk>/renew/", BorrowingRenewView.as_view()),

    # Fines
    path("fines/", MemberFinesView.as_view()),

    # Reservations
    path("reservations/", MemberReservationsView.as_view()),
    path("reservations/<int:pk>/", MemberReservationsView.as_view()),

    # Books
    path("books/", MemberBookListView.as_view()),
]