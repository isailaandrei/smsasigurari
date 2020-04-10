from django.shortcuts import render,  redirect
from django.template import RequestContext
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View

from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect

from .models import Expirari, Messages, sendSMS, get_romanian_date
from .utils.fileUpload import uploadCSV
from .forms import ExpirariForm, MessagesForm

import logging
import json


# Get an instance of a logger
logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class HomeView(View):

    def get(self, request):

        expirari = Expirari.objects.filter(mesaje_trimise=0)

        for e in expirari:
            e.valabilitate_sfarsit = get_romanian_date(e.valabilitate_sfarsit)

        context = {
            'expirari': expirari,
            'mesaje': Messages.objects.all(),
        } 

        return render(request, 'sms/home.html', context)

@method_decorator(login_required, name='dispatch')
class SendView(View):

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
            sendSMS(request, expirari, message)
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({'success':'false'})

        return JsonResponse({'success':'true'})    
     

@method_decorator(login_required, name='dispatch')
class AboutView(View):

    def get(self, request):
       return render(request, 'sms/about.html', {})

@method_decorator(login_required, name='dispatch')
class LoadView(View):

    def get(self, request):
        return render(request, "sms/loadData.html")
    
    def post(self, request):
        return uploadCSV(request)     

@method_decorator(login_required, name='dispatch')
class MesajeView(View):

    def get(self, request):
        form = MessagesForm()
        return render(request, "sms/mesaje.html", {'form': form})
    
    def post(self, request):
        form = MessagesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Mesajul a fost adaugat!')
            return redirect('sms-mesaje')

        

