
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum

from .models import Payment, RentInvoice


@receiver([post_save, post_delete], sender=Payment)
def on_payment_changed(sender, instance: Payment, **kwargs):
    invoice = instance.invoice

    total = invoice.payments.aggregate(s=Sum("amount"))["s"] or 0
    invoice.paid_total = total

    # recalcula status
    invoice.status = invoice.refresh_status()

    invoice.save(update_fields=["paid_total", "status"])