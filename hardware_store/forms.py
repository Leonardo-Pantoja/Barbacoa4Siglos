from django import forms 
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Product, ProductCategory


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"


class CategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = "__all__"


class RegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput())

class CheckoutForm(forms.Form):
    first_name = forms.CharField(label='Nombre(s)', max_length=100, required=True)
    last_name = forms.CharField(label='Apellido(s)', max_length=200, required=True)
    address = forms.CharField(label='Dirección', max_length=300, required=True)
    housenumber = forms.CharField(label='Número de casa', max_length=4, required=True)
    phone = forms.CharField(label='Número de teléfono', max_length=15, required=True)
    pickup_time = forms.TimeField(label='Hora de recogida', required=True)
