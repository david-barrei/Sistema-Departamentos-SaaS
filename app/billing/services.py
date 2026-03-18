
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from django.db import transaction
from django.utils import timezone
from leases.models import Lease
from django.db.models import F
from leases.services import sync_unit_status
from .models import RentInvoice

def month_start(d: date ) -> date:
    """devuelve el dia 1 del mes"""
    return d.replace(day=1)

def add_months(d: date, months: int) -> date:
    """Suma meses manteniendo el dia 1 """
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    return date(y, m, 1)



def due_date_for_period(period_start: date, pay_day: int) -> date:
    """
    Calcula due_date para el mes de 'period_start' usando pay_day.
    Recomendación: pay_day 1..28 (para evitar problemas Febrero).
    """
    pay_day = max(1, min(pay_day, 28))
    return period_start.replace(day=pay_day)


@transaction.atomic
def generate_invoices_for_lease(
    lease,
    months_ahead: int = 12,
    start_from: date | None = None,
) -> int:
    """
    Crea cuotas mensuales (RentInvoice) para un lease desde el mes actual o start_from.
    - No duplica si ya existen (por UniqueConstraint lease+period).
    - Devuelve cuántas creó.
    """
    if months_ahead < 1:
        return 0

    today = timezone.localdate()
    first_period = month_start(start_from or today)

    created_count = 0

    for i in range(months_ahead):
        period = add_months(first_period, i)
        due_date = due_date_for_period(period, lease.pay_day)

        # Puedes ajustar amount si luego quieres servicios extra
        amount = lease.monthly_rent

        obj, created = RentInvoice.objects.get_or_create(
            lease=lease,
            period=period,
            defaults={
                "due_date": due_date,
                "amount": amount,
                "status": RentInvoice.Status.PENDING,
                "paid_total": 0,
            },
        )
        if created:
            obj.refresh_status()
            obj.save()
            created_count += 1

    return created_count

# RELOJERO DEL SISTEMA  Recorre los contratos y las facturas para poner al día los estados según la fecha actual.
def sync_system_status():

    today = timezone.localdate()

    expired_leases = Lease.objects.filter(
        status=Lease.Status.ACTIVE,
        end_date__isnull=False,
        end_date__lt=today
    )

    for lease in expired_leases:
        lease.status = Lease.Status.ENDED
        lease.save(update_fields=["status"])

        sync_unit_status(lease.unit)

    overdue_invoices = RentInvoice.objects.filter(
        due_date__lt=today,
        paid_total__lt=F("amount")
    )

    for invoice in overdue_invoices:
        invoice.refresh_status()
        invoice.save(update_fields=["status"])
