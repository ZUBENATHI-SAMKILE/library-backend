from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = "Create the admin account"

    def handle(self, *args, **kwargs):
        email = input("Admin email: ")
        name = input("Admin name: ")
        password = input("Admin password: ")

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING("User already exists."))
            return

        user = User.objects.create_user(
            email=email,
            name=name,
            password=password,
            role="admin",
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Admin '{name}' created!"))