from django.contrib import admin

# Register your models here.
from .models import Lease, TenantProfile

@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ("unit","tenant","start_date","end_date",)
    list_filter = ("status", "start_date")
    search_fields = ("unit__code", "tenant__full_name")

@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name","dni","phone","email")
    search_fields = ("full_name","dni","email")