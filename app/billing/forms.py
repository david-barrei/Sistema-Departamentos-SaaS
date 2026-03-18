from django import forms
from .models import Payment,Deposit


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount","receipt","notes"]



class DepositForm(forms.ModelForm):
    class Meta:
        model = Deposit
        fields = ["amount","received_at","returned_amount","returned_at","notes"]

        widgets= {
            
            "amount": forms.TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "received_at": forms.DateInput(attrs={"class": "form-control","type": "date"}),
            "returned_amount": forms.TextInput(attrs={"class": "form-control" }),
            "returned_at": forms.DateInput(attrs={"class": "form-control","type": "date"}),
            "notes": forms.TextInput(attrs={"class": "form-control"}),
        }