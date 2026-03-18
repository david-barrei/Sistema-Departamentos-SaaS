from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column



from .models import CustomUser

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ["username","email","first_name","last_name","password"]

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout= Layout(
            Row(
                Column("username", css_class="form-group col-md-6 mb-0"),
                Column("email", css_class="form-group col-md-6 mb-0"),
                css_class = "form-row"
            ),
            Row(
                Column("first_name", css_class="form-group col-md-6 mb-0"),
                Column("last_name", css_class="form-group col-md-6 mb-0"),
                css_class = "form-row"
            ),
            Row(
                Column("password", css_class="form-group col-md-6 mb-0"),
                css_class = "form-row"
            ),

        )


#d