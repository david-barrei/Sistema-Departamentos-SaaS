from django.contrib import admin

# Register your models here.

from .models import RentInvoice, Deposit, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

@admin.register(RentInvoice)
class RentInvoiceAdmin(admin.ModelAdmin):
    list_display = ("lease","period","due_date","amount","status","paid_total","remaining")
    list_filter = ("status","due_date")
    search_fields = ("lease__unit__code",)
    inlines = [PaymentInline]


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ("lease","amount")
    search_fields = ("lease__unit__code", "lease__tenant__full_name")

