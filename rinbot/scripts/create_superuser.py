#!/usr/bin/env python
import os
import django
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import django_config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from django.db.utils import IntegrityError


def create_superuser():
    superuser_config = django_config.get('superuser', {})
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', superuser_config.get('username'))
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', superuser_config.get('email'))
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', superuser_config.get('password'))
    
    # TODO: Use rinbot logger
    try:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created successfully.")
    
    except IntegrityError:
        print(f"Superuser '{username}' already exists.")


if __name__ == '__main__':
    create_superuser()
