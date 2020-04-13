from django.db import models
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

import nexmo
import csv
import logging


# Get an instance of a logger
logger = logging.getLogger(__name__)

class Expirari(models.Model):
    nume = models.CharField(blank = True, max_length=100)
    numar_telefon = models.CharField(max_length=20)
    numar_masina = models.CharField(blank = True, max_length=100)
    tip_asigurare = models.CharField(max_length=100)
    sucursala = models.CharField(blank=False, max_length=100)
    mesaje_trimise = models.IntegerField(blank=True, default=0)
    valabilitate_sfarsit = models.DateField()

    def __str__(self):
        return self.name

class Messages(models.Model):
    name = models.TextField()
    message = models.TextField()

    def __str__(self):
        return self.name



def sendSMS(request, expirari, messageObject):

    client = nexmo.Client(key=settings.NEXMO_API_KEY, secret=settings.NEXMO_SECRET)
    successful = 0
    for expirare in expirari:
        message = get_formatted_message(expirare, messageObject.message) 

        response = client.send_message({
            'from': 'Asigurari',
            'to': expirare.numar_telefon,
            'text': message
        })

        if response['messages'][0]['status'] == '0':
            expirare.delete()
            successful += 1
        else:
            logger.error('Mesajul nu a putut fi trimis: {}'.format(response['messages'][0]['error-text']))
            messages.warning(request, 'Mesajul nu a putut fi trimis lui {} pe numarul de telefon {}.'.format(expirare.nume, expirare.numar_telefon))
    return successful


def get_romanian_date(date):

    months_translate = {
        'Jan': 'Ianuarie',
        'Feb': 'Februarie',
        'Mar': 'Martie',
        'Apr': 'Aprilie',
        'May': 'Mai',
        'Jun': 'Iunie',
        'Jul': 'Iulie',
        'Aug': 'August',
        'Sep': 'Septembrie',
        'Oct': 'Octombrie',
        'Nov': 'Noiembrie',
        'Dec': 'Decembrie',
    }

    valabilitate_sfarsit = date.strftime('%d-%b-%Y')
    for eng, rom in months_translate.items():
        valabilitate_sfarsit = valabilitate_sfarsit.replace(eng, rom)

    return valabilitate_sfarsit
        
def get_formatted_message(expirare, message):
    fields = ['nume','numar_telefon','numar_masina','tip_asigurare','valabilitate_sfarsit','mesaje_trimise', 'sucursala']
    for field in fields:
        if field == 'valabilitate_sfarsit':
            message = message.replace('{' + field + '}', get_romanian_date(getattr(expirare, field)))
            continue
        message = message.replace('{' + field + '}', str(getattr(expirare, field)))
    return message