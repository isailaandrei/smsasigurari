from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.views import View

from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect

from .models import Expirari, Messages
from .forms import ExpirariForm

import logging
import json


import csv

import nexmo

# Get an instance of a logger
logger = logging.getLogger(__name__)


class HomeView(View):

    @login_required
    def get(self, request):
        context = {
            'expirari': Expirari.objects.filter(mesaje_trimise=0),
            'trimise': Expirari.objects.exclude(mesaje_trimise=0),
            'mesaje': Messages.objects.all(),
        } 

        return render(request, 'home.html', context)

class SendView(View):

    @login_required
    def post(self, request):
        expirariIds = request.POST.get('expirari-ids', None)
        messageId = request.POST.get('msg-id', '')
        delete_rows = request.POST.get('Delete', False)

        expirariIds = json.loads(expirariIds)

        if delete_rows:
            Expirari.objects.filter(pk__in=expirariIds).delete()
            return JsonResponse({'success':'true'})
      
        try:
            expirari = Expirari.objects.filter(pk__in=expirariIds)
            message = Messages.objects.filter(pk=messageId)[0]
            models.sendSMS(expirari, message)
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({'success':'false'})

        return JsonResponse({'success':'true'})    
     

class AboutView(View):

    @login_required
    def get(self, request):
       return render(request, 'about.html', {})

class LoadView(View):

    @login_required
    def get(self, request):
        return render(request, "loadData.html", data)

    @login_required    
    def post(self, request):
        return models.uploadCSV(request)     


