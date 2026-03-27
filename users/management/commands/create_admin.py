from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = "Create the admin account"

    def add_arguments(self, parser):
        parser.add_argument("--email", default="Noneka@library.com")
        parser.add_argument("--name", default="Noneka")
        parser.add_argument("--password", default="Noneka01")

    def handle(self, *args, **kwargs):
        email = kwargs["email"]
        name = kwargs["name"]
        password = kwargs["password"]

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING("User already exists."))
            return

        User.objects.create_superuser(
            email=email,
            name=name,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f"Admin '{name}' created!"))