from django.db import models

# Create your models here.


class Building(models.Model):

    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
 
    def __str__(self):
        return self.name
    

class Unit(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Disponible"
        RENTED = "rented", "Rentado"
        MAINTENACE = "maintenance","Mantenimiento"

    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="units")
    code = models.CharField(max_length=20)
    floor = models.IntegerField(null=True, blank=True)
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)
    area_m2 = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)

    class Meta:
        constraints =[
            models.UniqueConstraint(fields=["building","code"], name="uniq_unit_code_per_building")

        ]

    def __str__(self):
        return f"{self.building.name} - {self.code}"
        
