from django import forms
from .models import Order, Customer
from django.contrib.auth.models import User


class CheckOutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("ordered_by", "shipping_address", "email", "phone_number")


class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField(widget=forms.EmailInput())

    class Meta:
        model = Customer
        fields = ("username", "full_name", "address", "password", "email")

    def clean_username(self):
        uname = self.cleaned_data.get("username")
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError("Customer With this Username already Exists.")

        return uname


class CustomerLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())