from django import forms
from django.conf import settings
from .models import Expirari, Messages

class ExpirariForm(forms.ModelForm):
    valabilitate_sfarsit = forms.DateField(label='valabilitate_sfarsit', input_formats=settings.DATE_INPUT_FORMATS, required=True)
  
    class Meta:
        model = Expirari
        fields = ['nume','numar_telefon','numar_masina','tip_asigurare','valabilitate_sfarsit','mesaje_trimise', 'sucursala']


class MessagesForm(forms.ModelForm):

    mesajExemplu = '''Exemplu: Buna ziua domnule {nume}. Asigurarea pentru masina cu numarul {numar_masina} expira la data {valabilitate_sfarsit}.'
                    \n\nImportant: Asigurati-va ca tagurile sunt scrie corect si faceti un test inainte sa trimiteti mesajul clientilor.'''
    name = forms.CharField(label = 'Nume', widget=forms.TextInput(attrs={'placeholder': 'Exemplu: RCA - Standard'}))
    message = forms.CharField(label = 'Mesaj', widget=forms.Textarea(attrs={'placeholder': mesajExemplu}))

    class Meta:
        model = Messages
        fields = ['name', 'message']