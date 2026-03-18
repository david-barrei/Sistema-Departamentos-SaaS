from django import forms
from .models import Building,Unit

class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ["name","address","notes"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: Torre Norte"
            }),

            "address": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Dirección del edificio"
            }),

            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Notas adicionales"
            }),
        }


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ["code","floor","bedrooms","bathrooms","area_m2"]

        widgets = {
                "code": forms.TextInput(attrs={
                    "class": "form-control",
                    "placeholder": "Ej: 101"
                }),

                "floor": forms.TextInput(attrs={
                    "class": "form-control",
                    "placeholder": "Piso 1"
                }),

                "bedrooms": forms.NumberInput(attrs={
                    "class": "form-control",
                    
                }),

                "bathrooms": forms.NumberInput(attrs={
                    "class": "form-control",
                    
                }),

                "area_m2": forms.NumberInput(attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Ej: 30m"
                }),
            }
