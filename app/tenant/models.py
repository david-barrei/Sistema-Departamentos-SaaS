from django.db import models

# Create your models here.
from django_tenants.models import TenantMixin,DomainMixin

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)


class Domain(DomainMixin):
    pass







