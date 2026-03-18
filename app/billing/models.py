from django.db import models, connection
from django.conf import settings
from django.utils import timezone

# Create your models here.

class RentInvoice(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending","Pendiente"
        PARTIAL = "partial","Parcial"
        PAID = "paid","Pagado"
        LATE = "late","Atrasado"

    lease = models.ForeignKey("leases.Lease", on_delete=models.CASCADE, related_name="invoices") 
    period = models.DateField(help_text=" Usa el dia 1 del mes ej: 2026-02-01")
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    paid_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["lease","period"], name="unique_invoice_per_lease_and_period")
        ]

        indexes = [
            models.Index(fields=["status","due_date"]),
            models.Index(fields=["period"]),
        ]

    def __str__(self):
        return f"Invoice {self.lease.unit} {self.period}"
    
    @property
    def remaining(self):
        return max(self.amount - self.paid_total,0)
    
    def refresh_status(self):
        """
        Lógica mejorada: Una factura no es 'Atrasada' si aún no llega su fecha de vencimiento.
        """
        today = timezone.localdate()
        
        # 1. Si ya pagó todo, el estado siempre es PAID
        if self.paid_total >= self.amount:
            self.status = self.Status.PAID
        
        # 2. Si ha pagado algo pero no todo
        elif self.paid_total > 0:
            # Si ya pasó la fecha, es un pago parcial atrasado
            self.status = self.Status.LATE if self.due_date < today else self.Status.PARTIAL
            
        # 3. Si no ha pagado nada
        else:
            # Solo es LATE si la fecha de vencimiento ya pasó
            # Si la fecha es futura, se mantiene como PENDING
            self.status = self.Status.LATE if self.due_date < today else self.Status.PENDING
        
        return self.status
    
    @property
    def is_due(self):
        """
         Este helper nos dice si la factura ya 'venció' o vence hoy.
        Es vital para separar la deuda real de la futura.
        """
        return self.due_date <= timezone.localdate()

    @property
    def display_status(self):
   
    # el lado derecho de tus TextChoices (ej: "Atrasado" en vez de "late")
        return self.get_status_display()



class Deposit(models.Model):
    class Status(models.TextChoices):
        HELD = 'HELD', 'Custodia'
        PARTIALLY_RETURNED = "PARTIALLY_RETURNED", "Devuelto Parcialmente"
        RETURNED = 'RETURNED', 'Devuelto'

    lease = models.OneToOneField("leases.Lease", on_delete=models.CASCADE, related_name="deposit")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    received_at = models.DateTimeField(null=True, blank=True) # MODIFICAR A DATEFIELD
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.HELD)
    returned_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    returned_at = models.DateTimeField(null=True, blank=True)# MODIFICAR A DATEFIELD
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_deposits')


    def __str__(self):
        return f"Deposito {self.lease} - {self.amount}"
    

    

def receipt_upload_path(instance, filename):
    schema_name = connection.schema_name
    today = timezone.localdate()
    return f"{schema_name}/receipts/{today.year}/{today.month:02d}/invoice_{instance.invoice_id}/{filename}"


class Payment(models.Model):
    invoice = models.ForeignKey(RentInvoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_on = models.DateField(default=timezone.localdate)
    receipt = models.FileField(upload_to=receipt_upload_path, null=True, blank=True)

    reference = models.CharField(max_length=60, blank=True)  # ej: transferencia #123
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments_created")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["paid_on"]),
        ]

    def __str__(self):
        return f"Payment {self.invoice_id} - {self.amount}"