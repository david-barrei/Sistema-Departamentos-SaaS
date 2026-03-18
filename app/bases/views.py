from django.shortcuts import render
from django.views.generic import *
from django.db.models import Sum, Q, F, Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone # -----------////
from datetime import timedelta 
from billing.models import RentInvoice,Payment
from leases.models import Lease,TenantProfile
from properties.models import Building,Unit
from billing.services import sync_system_status
# Create your views here.


class Home(LoginRequiredMixin,TemplateView): # Desabilitado 
    template_name = "bases/home.html"



def dashboardKPIs(request):

    """
    Dashboard principal del sistema.

    Aquí reunimos:
    - KPIs generales
    - cobros operativos
    - actividad reciente
    """

    #Actualiza estados de contratos e invoices antes de calcular
    sync_system_status()


    today =timezone.localdate()
    limit_date = today + timedelta(days=30)  # vencen en un rango desde hoy hasta 30 días después
    current_month = today.replace(day=1)

    # =========================
    # KPIs GENERALES
    # =========================
    #---------- Optimizamos consultas
    """
    total_buildings = Building.objects.count()
    total_units = Unit.objects.count()
    units_rented = Unit.objects.filter(status="rented").count()
    units_available = Unit.objects.filter(status="available").count()
    """
    # En lugar de 4 .count(), hacemos 1 solo aggregate. 
    unit_stats = Unit.objects.aggregate(
        total=Count('id'),
        rented=Count('id', filter=Q(status=Unit.Status.RENTED)),
        available=Count('id', filter=Q(status=Unit.Status.AVAILABLE)),
    )
    total_units = unit_stats['total']
    units_rented = unit_stats['rented']
    units_available = unit_stats['available']

    occupancy = round((units_rented / total_units * 100)) if total_units > 0 else 0

    # =========================
    # 4. FINANZAS Y COBROS
    # =========================

    #sumamos solo la DEUDA EXIGIBLE (vencida hoy o antes).
    real_debt = RentInvoice.objects.filter(
            due_date__lte=today,
            paid_total__lt=F("amount")
        ).aggregate(
            debt=Sum(F('amount') - F('paid_total'))
        )['debt'] or 0


   
    # Ingresos del mes (por pagos)
    month_income = (Payment.objects.filter(
        paid_on__year=today.year,
        paid_on__month=today.month
    ).aggregate(total=Sum("amount"))["total"] or 0
    )


    # Cobros urgentes (Top 5 para la tabla inferior)
    action_invoices = RentInvoice.objects.select_related(
        "lease__unit", "lease__tenant"
    ).filter(
        paid_total__lt=F("amount"),
        due_date__lte=today # Solo lo que ya hay que cobrar
    ).annotate(
        saldo_pendiente=F('amount') - F('paid_total')
    ).order_by("due_date")[:7]


    # Conteo de facturas con atraso (para alertas numéricas)
    overdue_count = RentInvoice.objects.filter(
        due_date__lt=today, 
        paid_total__lt=F("amount")
    ).count()


    # =========================
    # 5. CONTRATOS
    # =========================

    ## Conteo de contratos que vencen en los próximos 30 días
    leases_expiring_count = Lease.objects.filter(
        status=Lease.Status.ACTIVE,
        end_date__range=[today, limit_date]
    ).count()

    # Contratos vencidos (Finalizados)
    leases_expired_count = Lease.objects.filter(
        status=Lease.Status.ENDED
    ).count()


    # =========================
    # ACTIVIDAD RECIENTE
    # =========================


    # Armamos actividad reciente para el template

    recent_activity = []

    # Inquilinos recientes
    for t in TenantProfile.objects.order_by("-id")[:2]:
        recent_activity.append({"title": "Nuevo Inquilino", "description": t.full_name})

    # Pagos recientes
    for p in Payment.objects.select_related("invoice__lease__unit").order_by("-id")[:3]:
        recent_activity.append({
            "title": "Pago registrado", 
            "description": f"U-{p.invoice.lease.unit.code} - ${p.amount}"
        })

    # =========================
    # ALERTAS
    # =========================

    alerts = []

    # Facturas atrasadas
    late_invoices = RentInvoice.objects.select_related("lease__unit").filter(
        status=RentInvoice.Status.LATE
    )[:3]

    for invoice in late_invoices:
        alerts.append({
            "title": "Factura atrasada",
            "description": f"Unidad {invoice.lease.unit.code} - vence { invoice.due_date}",  
            "level": "danger" # Agregamos un nivel para el color en el HTML
        })
    
    # Alerta: Contratos por vencer
    expiring_leases = Lease.objects.select_related("unit").filter(
        status=Lease.Status.ACTIVE,
        end_date__range=[today, limit_date]
    ).order_by("end_date")[:3]

    for lease in expiring_leases:
        alerts.append({
            "title": "Contrato por vencer",
            "description": f"Unidad -{lease.unit.code} - vence {lease.end_date}",
            "level": "warning"
        })

    ## Alerta: Contratos finalizados que aún deben dinero
    expired_with_debt = (
        Lease.objects
        .select_related("unit", "tenant")
        .filter(
            status=Lease.Status.ENDED,
            invoices__paid_total__lt=F("invoices__amount")
        )
        .distinct()[:3]
    )

    for lease in expired_with_debt:
        alerts.append({
            "title": "Contrato finalizado con deuda",
            "description": f"Unidad {lease.unit.code} - {lease.tenant.full_name}",
            "level": "dark"
        })

    # =========================
    # CONTEXTO FINAL
    # =========================


    context = {
        "today":today,
        "total_buildings":Building.objects.count(),
        "total_units":total_units,
        "units_rented":units_rented,
        "units_available":units_available,
        "occupancy":occupancy,
        
        
        "month_income": month_income,
        "real_debt": real_debt,
        "action_invoices": action_invoices,

        "leases_expiring_count":leases_expiring_count,
        "leases_expired_count": leases_expired_count,
        
        "recent_activity":recent_activity[:5],
        "alerts": alerts[:5],
        "overdue_invoices":overdue_count,

    }
    return render(request, "bases/home.html", context)

