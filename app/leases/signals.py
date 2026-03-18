

from django.db.models.signals import post_save
from django.dispatch import receiver

from billing.services import generate_invoices_for_lease
from .models import Lease
from .services import sync_unit_status


@receiver(post_save, sender=Lease)
def on_lease_saved(sender, instance: Lease, created: bool, **kwargs):
    """
    - Al crear un Lease nuevo: genera cuotas (ej: 12 meses).
    - Siempre sincroniza el estado del Unit.
    """
    if created:
        generate_invoices_for_lease(instance, months_ahead=12)

    sync_unit_status(instance.unit)

