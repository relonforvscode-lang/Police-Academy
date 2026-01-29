import os
import django
from django.conf import settings
from django.contrib.auth.hashers import make_password

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from main.models import User, Assignment, Evaluation, Message, Notification

def setup_database():
    print("Cleaning up existing data...")
    Notification.objects.all().delete()
    Message.objects.all().delete()
    Evaluation.objects.all().delete()
    Assignment.objects.all().delete()
    User.objects.all().delete()

    print("Creating initial users...")
    # Admin
    admin = User.objects.create(
        username='admin',
        password=make_password('admin123'),
        full_name='System Administrator',
        role='admin'
    )

    # Trainers
    t1 = User.objects.create(
        username='trainer1',
        password=make_password('pass123'),
        full_name='Trainer John',
        role='trainer'
    )
    t2 = User.objects.create(
        username='trainer2',
        password=make_password('pass123'),
        full_name='Trainer Sarah',
        role='trainer'
    )

    # Cadets
    c1 = User.objects.create(
        username='cadet1',
        password=make_password('pass123'),
        full_name='Cadet Alex',
        role='cadet'
    )
    c2 = User.objects.create(
        username='cadet2',
        password=make_password('pass123'),
        full_name='Cadet Ryan',
        role='cadet'
    )
    c3 = User.objects.create(
        username='cadet3',
        password=make_password('pass123'),
        full_name='Cadet Sam',
        role='cadet'
    )

    print("Creating assignments...")
    Assignment.objects.create(trainer=t1, cadet=c1)
    Assignment.objects.create(trainer=t1, cadet=c2)
    Assignment.objects.create(trainer=t2, cadet=c3)

    print("Database setup completed successfully with hashed passwords!")

if __name__ == "__main__":
    setup_database()
