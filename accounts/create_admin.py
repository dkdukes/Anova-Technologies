from django.core.management.base import BaseCommand
from customers.models import CustomUser


class Command(BaseCommand):
    help = "Create the Anova Technologies admin user"

    def handle(self, *args, **options):
        username = "admin"
        email = "admin@anovatechnologies.com"
        password = "YourStrongPassword123!"

        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if not created:
            user.email = email
            user.role = "admin"
            user.is_staff = True
            user.is_superuser = True

        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Admin user '{username}' is ready."
            )
        )