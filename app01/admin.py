from django.contrib import admin

# Register your models here.
from app01.models import User,Password
admin.site.register(User)
admin.site.register(Password)