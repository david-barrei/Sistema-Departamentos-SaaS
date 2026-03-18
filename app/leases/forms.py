from django import forms
from .models import TenantProfile, Lease

class TenantProfileForm(forms.ModelForm):
    class Meta:
        model = TenantProfile
        fields = ["full_name","dni","phone","email","emergency_contact"]

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control select2","placeholder": "Jhonthan Merchan"}),
            "dni": forms.TextInput(attrs={"class": "form-control", "placeholder": "10 digitos"}),
            "phone": forms.TextInput(attrs={"class": "form-control",}),
            "email": forms.TextInput(attrs={"class": "form-control", }),
            "emergency_contact": forms.TextInput(attrs={"class": "form-control"}),
        }


class LeaseForm(forms.ModelForm):
    class Meta:
        model = Lease
        fields = ["tenant","start_date","end_date","monthly_rent","pay_day","contract_pdf"]
        widgets = {
            "tenant": forms.Select(attrs={"class": "form-control select2 ","style": "width: 100%;"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "monthly_rent": forms.NumberInput(attrs={"class": "form-control", "placeholder": "0.00"}),
            "pay_day": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Ej: 5"}),
            "contract_pdf": forms.ClearableFileInput(attrs={"class": "custom-file-input"})
        }

    def __init__(self, *args, **kwargs):
        self.unit = kwargs.pop("unit", None)
        super().__init__(*args, **kwargs)

    def clean_pay_day(self):
        pay_day = self.cleaned_data["pay_day"]
        if not 1 <= pay_day <= 28:
            raise forms.ValidationError("El día de pago debe estar entre 1 y 28.")
        return pay_day

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if end_date and start_date and end_date <= start_date:
            raise forms.ValidationError("La fecha fin debe ser mayor que la fecha inicio.")

        if self.unit:
            exists_active = Lease.objects.filter(
                unit=self.unit,
                status=Lease.Status.ACTIVE
            ).exists()

            if exists_active:
                raise forms.ValidationError("Esta unidad ya tiene un contrato activo.")

        return cleaned_data
        