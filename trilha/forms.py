from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Material


class CadastroForm(UserCreationForm):
    """Conta com e-mail e senha. O e-mail, normalizado em minúsculas, vira o username,
    e assim o login padrão do Django funciona sem backend de autenticação próprio."""

    email = forms.EmailField(label="E-mail")

    class Meta:
        model = get_user_model()
        fields = ("email",)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(username=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail.")
        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.username = self.cleaned_data["email"]
        usuario.email = self.cleaned_data["email"]
        if commit:
            usuario.save()
        return usuario


class EntrarForm(AuthenticationForm):
    username = forms.EmailField(label="E-mail")

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ["titulo", "autor", "progresso"]
        widgets = {
            "progresso": forms.NumberInput(attrs={"min": 0, "max": 100, "step": 5}),
        }
