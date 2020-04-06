from django.db import models
from django.conf import settings


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