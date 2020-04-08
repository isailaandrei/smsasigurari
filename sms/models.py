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
    name = models.CharField(blank = True, max_length=100)
    numar_telefon = models.CharField(max_length=20)
    numar_masina = models.CharField(max_length=10)
    tip_asigurare = models.CharField(max_length=20)
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

def sendSMS(expirari, messageObject):

    client = nexmo.Client(key=settings.NEXMO_API_KEY, secret=settings.NEXMO_SECRET)
    message = messageObject.message
    
    for expirare in expirari:
        numar_telefon = expirare.numar_telefon.replace(' ', '')
        valabilitate_sfarsit = get_romanian_date(expirare.valabilitate_sfarsit)
        logger.error(valabilitate_sfarsit)
        response = client.send_message({
            'from': 'Asigurari',
            'to': numar_telefon,
            'text': message.format(expirare.numar_masina, valabilitate_sfarsit)
        })

        if response['messages'][0]['status'] == '0':
            expirare.mesaje_trimise += 1
            expirare.save()
        else:
            messages.error('Mesajul nu a putut fi trimis pentru numarul lui {} +\
                   pe numarul de telefon {}.'.format(expirare.name, expirare.numar_telefon))

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

    valabilitate_sfarsit = date.strftime('%d %b %Y')
    for eng, rom in months_translate.items():
        valabilitate_sfarsit = valabilitate_sfarsit.replace(eng, rom)

    return valabilitate_sfarsit
        