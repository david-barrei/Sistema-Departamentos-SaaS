
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from  django.views.generic import ListView,DetailView,DeleteView,UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Prefetch
from .services import sync_unit_status

from .forms import LeaseForm,TenantProfileForm
from .models import Lease,TenantProfile
from properties.models import Unit

# Create your views here.

@login_required(login_url="user:login")
def LeaseView(request, unit_id):
    unit = get_object_or_404(Unit, pk=unit_id )
    if unit.leases.filter(status=Lease.Status.ACTIVE).exists():
        messages.error(request,"Esta unidad ya tiene un contrato activo")
        return redirect("properties:unit_list", building_id=unit.building_id)
    
    if request.method == "POST":
        form =LeaseForm(request.POST, request.FILES, unit=unit)
        print(f"Archivos recibidos: {request.FILES}")   
        if form.is_valid():
            lease = form.save(commit=False)
            lease.unit = unit
            lease.created_by = request.user 
            lease.save()
            messages.success(request,"creado exitosamente")
            return redirect("lease:lease_detail", lease_id=lease.id)
    else:
        form = LeaseForm()
        
    return render(request, "lease_create.html", {"form": form,"unit":unit})


def LeaseList(request):
    leases = Lease.objects.select_related("tenant","unit").order_by("status")
    return render(request,"lease_list.html", {"leases":leases})

def LeaseDeatil(request, lease_id):
    lease = get_object_or_404(Lease, pk=lease_id)
    # Usamos el método que creamos en el modelo:
    total_deuda = lease.get_total_overdue()

    invoices = lease.invoices.all().order_by("period")
    
    # Podemos identificar cuáles son "Deuda Real" vs "Futuras"
    today = timezone.localdate() 

    return render(request, "lease_detail.html", {
        "lease": lease,
        "invoices":invoices,
        "total_deuda": total_deuda, # <-- Este es el dato clave
        "today": today,
        "deposit": getattr(lease, "deposit", None)
    })



    
class LeaseDetailView(DetailView):
    model = Lease
    template_name = "lease/detalle.html"


class LeaseUpdateView(UpdateView):
    model = Lease
    form_class = LeaseForm
    template_name = "lease_create.html" # Reutilizamos el form de creación
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editing'] = True
        context['unit'] = self.object.unit # Pasamos la unidad para mostrarla en el título
        return context

    def get_success_url(self):
        return reverse_lazy('lease:lease_detail', kwargs={'lease_id': self.object.id})
    


class LeaseDelete(DeleteView):
    model = Lease



@login_required(login_url="users:login")
def lease_end(request, lease_id):
    """
    Finaliza un contrato activo.

    Qué hace:
    - busca el contrato
    - verifica si ya está finalizado
    - cambia su estado a ended
    - si no tiene fecha fin, le coloca la fecha actual
    - sincroniza el estado de la unidad (debería volver a available)
    """
    lease = get_object_or_404(Lease, pk=lease_id)

    # Si ya está finalizado, no hacemos nada
    if lease.status == Lease.Status.ENDED:
        messages.warning(request, "Este contrato ya está finalizado.")
        return redirect("lease:lease_detail", lease_id=lease.id)
    # Cambiar estado del contrato
    lease.status = Lease.Status.ENDED
    # Si no tenía fecha de fin, usamos hoy
    if not lease.end_date:
        lease.end_date = timezone.localdate()
    lease.save()
    # Recalcular el estado de la unidad
    sync_unit_status(lease.unit)
    messages.success(request, "Contrato finalizado correctamente.")
    return redirect("lease:lease_detail", lease_id=lease.id)





def TenantProfileView(request):
    if request.method== "POST":
        form = TenantProfileForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Creado Inquilino")
            return redirect ("/")
    else:
        form = TenantProfileForm()
    return render(request,"tenant.html",{"form":form})


def TenantListView(request):
    tenant = TenantProfile.objects.prefetch_related(
        Prefetch(
            "leases",
            queryset=Lease.objects.filter(status=Lease.Status.ACTIVE),
            to_attr="active_leases" # guardar el resultado en active_leases y no en el relate_name
        )
    )
    return render(request, "tenant_list.html", {"tenant":tenant})

    
class TenantDetailView(DetailView):
    model = TenantProfile
    template_name = "tenant_detail.html"
    context_object_name = "tenant"

class TenantUpdateView(UpdateView):
    model = TenantProfile
    form_class = TenantProfileForm
    template_name = "tenant.html"

    def get_succes_url(self):
        return reverse_lazy('lease:tenant_detail', kwargs ={'pk': self.object.pk})

class TenantDeleteView(DeleteView):
   
    model = TenantProfile
    template_name = "tenant_confirm_delete.html"
    success_url = reverse_lazy('lease:tenant_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # LÓGICA DE PROTECCIÓN:
        # Si el inquilino tiene contratos, no permitimos borrar, mejor informamos.
        if self.object.leases.exists():
            messages.error(request, "No se puede eliminar este inquilino, tiene contratos asociados. Intente finalizar sus contratos")
            return redirect('lease:tenant_detail', pk=self.object.pk)
        return super().post(request, *args, **kwargs)