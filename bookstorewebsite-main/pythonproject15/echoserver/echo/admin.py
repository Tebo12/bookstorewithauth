from django.contrib import admin
from django.contrib.auth.models import Group, User

# Создадим группы при запуске приложения
def setup_groups():
    user_group, created = Group.objects.get_or_create(name='User')
    admin_group, created = Group.objects.get_or_create(name='Admin')

setup_groups()


