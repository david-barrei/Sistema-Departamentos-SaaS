from django.db import models, connection
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, F
# Create your models here.


class TenantProfile(models.Model):
    full_name = models.CharField(max_length=100)
    dni = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True,null=True, unique=True)
    emergency_contact = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.full_name
    

def contract_upload_path(instance, filename):
    schema_name = connection.schema_name
    # Usamos el código de la unidad y el ID del contrato para la carpeta
    unit_code = instance.unit.code
    tenant_id = instance.tenant.id
    return f"{schema_name}/contracts/unit_{unit_code}/tenant_{tenant_id}/{filename}"

class Lease(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active","Activo"
        ENDED = "ended","Finalizado"
        MAINTENACE = "maintenance", "Mantenimiento" 

    unit = models.ForeignKey("properties.Unit", on_delete=models.PROTECT, related_name="leases")
    tenant = models.ForeignKey(TenantProfile, on_delete=models.PROTECT, related_name="leases")
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    pay_day = models.PositiveSmallIntegerField(default=3)
    late_fee_per_day = models.DecimalField(default=0,max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="leases_created")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    contract_pdf = models.FileField(upload_to=contract_upload_path,null=True, blank=True,verbose_name="Contrato Escaneado")

    class Meta:
        indexes = [
            models.Index(fields=["status", "start_date" ]),

        ]

    def __str__(self):
        return f"Lease {self.unit} - { self.tenant}"
    
    def get_total_overdue(self):
        """
        PARA QUÉ SIRVE: Calcula cuánto debe el inquilino REALMENTE hoy.
        Filtra facturas que:
        1. Estén ligadas a este contrato.
        2. Su fecha de vencimiento sea hoy o en el pasado (__lte = Less Than or Equal).
        3. No estén marcadas como PAID.
        """
        today = timezone.localdate()
        
        # Usamos agregación de Django para que la base de datos haga la suma
        res = self.invoices.filter(
            due_date__lte=today
        ).exclude(
            status='paid'
        ).aggregate(
            total_debt=Sum(F('amount') - F('paid_total'))
        )
        
        return res['total_debt'] or 0
    
    @property
    def is_active(self) -> bool:
        if self.status != self.Status.ACTIVE:
            return False
        if self.end_date and self.end_date < timezone.localdate():
            return False
        return True
    

    @property
    def is_expired(self):
        """
        Devuelve True si el contrato ya pasó su fecha fin.
        """
        return self.end_date is not None and self.end_date < timezone.localdate()

    @property
    def is_expiring_soon(self):
        """
        Devuelve True si el contrato vence en los próximos 30 días.
        """
        if not self.end_date:
            return False

        today = timezone.localdate()
        return today <= self.end_date <= (today + timezone.timedelta(days=30))

    @property
    def display_status(self):
        """
        Estado visible para mostrar en templates.
        """
        if self.status == self.Status.ENDED:
            return "Finalizado"

        if self.is_expired:
            return "Vencido"

        if self.is_expiring_soon:
            return "Por vencer"

        return "Activo"
    


