from django.contrib import admin

# Register your models here.
from .models import Building, Unit

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("name","address")
    search_fields = ("name","address")
    

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("building","code","floor","status")
    list_filter = ("building",)
    search_fields = ("code","building__name")

    fieldsets = (
        ("Básico", {
            "fields": ("building", "code", "floor", "status")
        }),
        ("Detalles (opcional)", {
            "classes": ("collapse",),
            "fields": ("bedrooms", "bathrooms", "area_m2")
        }),
    )