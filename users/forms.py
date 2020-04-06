from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
 
 
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta():
        model = User
        fields = ['username', 'email', 'password1', 'password2']