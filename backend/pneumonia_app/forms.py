from django import forms
import re
from django.core.exceptions import ValidationError

def validate_phone(value):
    if not re.match(r'^\d{10}$', value):
        raise ValidationError("Enter a valid 10-digit phone number.")

class SignupForm(forms.Form):
    name = forms.CharField(label='Full Name', max_length=100)
    username = forms.CharField(label='Username', max_length=100)
    email = forms.EmailField(label='Email')
    phone = forms.CharField(label='Phone Number', validators=[validate_phone])
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    
    
class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
