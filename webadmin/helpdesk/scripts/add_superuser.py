from django.contrib.auth.models import User
import datetime

def add_superuser():
    user = User()
    user.username='admin'
    user.last_name='admin'
    password="admin"
    user.set_password(password) 
    user.email = 'admin@test.loc'
    user.is_staff = True
    user.is_active = True
    user.is_superuser = True
    user.save()

add_superuser()