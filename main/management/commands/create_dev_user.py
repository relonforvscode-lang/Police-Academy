from django.core.management.base import BaseCommand
import os

from main.models import User


class Command(BaseCommand):
    help = 'Create a developer user for initial access (username from DEV_USERNAME, password from DEV_PASSWORD)'

    def handle(self, *args, **options):
        username = os.getenv('DEV_USERNAME', 'dev')
        password = os.getenv('DEV_PASSWORD', 'Mohd1213')
        full_name = os.getenv('DEV_FULL_NAME', 'Developer Account')

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists — skipping creation'))
            return

        user = User(username=username, full_name=full_name, rank='dev')
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS(f'Created user "{username}" with rank dev'))
