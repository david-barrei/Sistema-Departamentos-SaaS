from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone 
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from leases.models import Lease
from .models import RentInvoice, Payment
from .forms import PaymentForm,DepositForm



def Invoce_list(request):
    today = timezone.localdate()
    current_month = today.replace(day=1)
    
    invoices = (RentInvoice.objects.select_related(   #Trae solo las facturas que requieren atención: atrasadas parciales pendientes del mes actual
        "lease", "lease__unit", "lease__tenant"
    ).filter(
        Q(status=RentInvoice.Status.LATE) |
        Q(period=current_month)
    ).order_by("due_date","period")
    )

    return render(request, "charge.html",{"invoices":invoices,
                                       "today":today,
                                       "current_month":current_month})


@require_POST
def quick_payment(request, invoice_id):
    try:
        # Usamos atomic para que si algo falla, no se guarde nada a medias
        with transaction.atomic():
            invoice = RentInvoice.objects.get(id=invoice_id)
            # Convertimos amount a float/decimal para poder comparar
            raw_amount = request.POST.get('amount', '0')
            amount = float(raw_amount)

            # 1. Creamos el registro del pago
            # Ajusta los campos según tu modelo de Payment
            Payment.objects.create(
                invoice=invoice,
                amount=amount,
                paid_on=timezone.now(),
                reference="Cobro Rápido Dashboard", # Para saber de dónde vino
                created_by=request.user
            )
            invoice.paid_total = float(invoice.paid_total or 0) + amount


            if amount >= float(invoice.amount):
                invoice.status = RentInvoice.Status.PAID # O tu estado de pagada
                invoice.paid_date = timezone.now()
            invoice.save()

        # 2. El modelo Invoice debería actualizar su saldo automáticamente 
        # (o puedes hacerlo aquí manualmente)
        
        return JsonResponse({'status': 'success', 'message': 'Pago registrado'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def Payment_create(request,invoice_id):
    invoice = get_object_or_404(RentInvoice, pk=invoice_id)
    today = timezone.localdate()

    if invoice.due_date > today:
        messages.error(request,"No se puede registrar de un mes futuro")
        return redirect("billing:invoice_list")

    if request.method == "POST":
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.created_by = request.user
            payment.save()
            messages.success(request,"Pago resgistrado exitosamente")
            return redirect("billing:invoice_list")
    else:
        form = PaymentForm()
    return render(request,"payment.html",{"form": form, "invoice": invoice})


@login_required(login_url="users:login")
def DepositCreateView(request, lease_id):
    # Obtener el contrato
    lease = get_object_or_404(Lease, pk=lease_id)

    # Verificar si ya existe garantía
    if hasattr(lease, "deposit"):
        messages.warning(request, "Este contrato ya tiene una garantía registrada.")
        return redirect("lease:lease_detail", lease_id=lease.id)

    if request.method == "POST":
        form = DepositForm(request.POST)
        if form.is_valid():
            deposit = form.save(commit=False)

            # Asociar contrato
            deposit.lease = lease
            # Guardar usuario que registra
            deposit.created_by = request.user

            deposit.save()
            messages.success(request, "Garantía registrada correctamente")
            return redirect("lease:lease_detail", lease_id=lease.id)
    else:
        form = DepositForm()

    return render(request, "deposit_create.html", {
        "form": form,
        "lease": lease
    })






