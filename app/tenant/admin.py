from django.contrib import admin

# Register your models here.

from .models import Client, Domain

admin.site.register(Client)
admin.site.register(Domain)