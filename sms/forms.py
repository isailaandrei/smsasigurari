from django import forms
from django.conf import settings
from .models import Expirari

class ExpirariForm(forms.ModelForm):
    valabilitate_sfarsit = forms.DateField(label='valabilitate_sfarsit', input_formats=settings.DATE_INPUT_FORMATS, required=True)
  
    class Meta:
        model = Expirari
        fields = ['name','numar_telefon','numar_masina','tip_asigurare','valabilitate_sfarsit','mesaje_trimise', 'sucursala']