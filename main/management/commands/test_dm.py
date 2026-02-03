from django.core.management.base import BaseCommand
from django.conf import settings
from main import discord_utils

class Command(BaseCommand):
    help = 'Test sending a Discord DM using configured DISCORD_BOT_TOKEN. Usage: python manage.py test_dm <discord_user_id> [message]'

    def add_arguments(self, parser):
        parser.add_argument('discord_user_id', type=str)
        parser.add_argument('message', nargs='?', type=str, default='This is a test DM from the application.')

    def handle(self, *args, **options):
        uid = options['discord_user_id']
        msg = options['message']
        self.stdout.write(f'Testing send_dm to: {uid}')
        ok = discord_utils.send_dm(uid, msg)
        if ok:
            self.stdout.write(self.style.SUCCESS('send_dm returned True — message likely sent'))
        else:
            self.stdout.write(self.style.ERROR('send_dm returned False — check logs, BOT token, bot permissions, and target user settings'))