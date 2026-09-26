
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from getpass import getpass


class Command(BaseCommand):
    help = "Create the initial Anova Technologies administrator."

    def handle(self, *args, **options):
        User = get_user_model()

        # Check whether an admin already exists
        if User.objects.filter(role="admin").exists():
            self.stdout.write(
                self.style.WARNING(
                    "An administrator account already exists."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                "\nCreate the initial Anova Technologies administrator\n"
            )
        )

        # Username
        while True:
            username = input("Username: ").strip()

            if not username:
                self.stdout.write(
                    self.style.ERROR(
                        "Username cannot be empty."
                    )
                )
                continue

            if User.objects.filter(
                username__iexact=username
            ).exists():
                self.stdout.write(
                    self.style.ERROR(
                        "That username already exists."
                    )
                )
                continue

            break

        # Email
        while True:
            email = input("Email: ").strip().lower()

            if not email:
                self.stdout.write(
                    self.style.ERROR(
                        "Email cannot be empty."
                    )
                )
                continue

            if User.objects.filter(
                email__iexact=email
            ).exists():
                self.stdout.write(
                    self.style.ERROR(
                        "That email already exists."
                    )
                )
                continue

            break

        # Names
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()

        # Phone
        phone = input("Phone: ").strip()

        # Password
        while True:
            password = getpass("Password: ")
            password2 = getpass("Password confirmation: ")

            if password != password2:
                self.stdout.write(
                    self.style.ERROR(
                        "Passwords do not match."
                    )
                )
                continue

            if len(password) < 8:
                self.stdout.write(
                    self.style.ERROR(
                        "Password must be at least 8 characters."
                    )
                )
                continue

            break

        # Create administrator
        admin = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=password,
            role="admin",
            is_active=True,
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Administrator '{admin.username}' created successfully."
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "The administrator can now log into the Anova admin panel."
            )
        )

