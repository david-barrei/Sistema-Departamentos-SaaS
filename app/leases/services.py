
from django.db import transaction
from django.utils import timezone

from properties.models import Unit
from .models import Lease



@transaction.atomic
def sync_unit_status(unit: Unit) -> None:
    """
    Marca Unit como RENTED si tiene al menos 1 Lease activo,
    caso contrario AVAILABLE (si no está en MAINTENANCE).
    """
    has_active = unit.leases.filter(status=Lease.Status.ACTIVE).exists()

    if unit.status == Unit.Status.MAINTENACE:
        # Si está en mantenimiento, no lo toques (regla de negocio simple)
        return

    unit.status = Unit.Status.RENTED if has_active else Unit.Status.AVAILABLE
    unit.save(update_fields=["status"])

