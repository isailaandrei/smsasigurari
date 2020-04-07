from django.db import models
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

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
    valabilitate_sfarsit = models.DateField()
    mesaje_trimise = models.IntegerField(blank=True, default=0)

    def __str__(self):
        return self.name

class Messages(models.Model):
    name = models.TextField()
    message = models.TextField()

    def __str__(self):
        return self.name

def sendSMS(expirari, messageObject):

    client = nexmo.Client(key='cf5281a4', secret='4cCLU6v3J4lIIOaZ')
    message = messageObject.message
    
    for expirare in expirari:
        response = client.send_message({
            'from': 'Asigurari',
            'to': expirare.numar_telefon,
            'text': message.format(expirare.numar_masina, str(expirare.valabilitate_sfarsit))
        })

        # if response['messages'][0]['status'] == '0':
            # expirare.mesaje_trimise += 1
            # expirare.save()