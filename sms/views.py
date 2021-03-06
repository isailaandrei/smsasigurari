from django.shortcuts import render,  redirect
from django.urls import reverse
from django.template import RequestContext
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.messages import get_messages

from django.http import FileResponse
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse

from .models import Expirari, Messages, sendSMS, get_romanian_date
from .utils.fileUpload import uploadCSV
from .forms import ExpirariForm, MessagesForm
from django.conf import settings

import logging
import json
import os


# Get an instance of a logger
logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class HomeView(View):

    def get(self, request):

        expirari = Expirari.objects.filter(user=request.user.username)

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
            trimise = sendSMS(request, expirari, message)
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({'success':'false'})

        if trimise > 0:
            messages.success(request, '{} din {} mesaje au fost trimise'.format(trimise, len(expirari)))
        
        return JsonResponse({'success':'true'})    
     

@method_decorator(login_required, name='dispatch')
class AboutView(View):

    def get(self, request):
       return render(request, 'sms/about.html')



@method_decorator(login_required, name='dispatch')
class LoadView(View):

    def get(self, request):
        downloadButton = request.GET.get('download', False)
        return render(request, "sms/loadData.html", {'downloadButton': downloadButton})
    
    def post(self, request):

        # Descarca fisierul daca argumentul 'descarca' e True
        descarca = request.POST.get('descarca', False)
        if descarca:
            fileName = request.session['csvFileName']
            response = FileResponse(open(fileName, 'rb'), content_type='text/csv')
            response['Content-Disposition'] = "inline; filename={}".format(fileName)
            if os.path.exists(fileName):
                os.remove(fileName)
            return response

        # Altfel creeaza fisierul
        csv_file = request.FILES["file"]
        if not csv_file.name.endswith('.csv'):
            messages.warning(request,'Fisierul trebuie sa fie in format CSV (comma separated)')
            return redirect('sms-incarca')
        
        # Initialize errors file
        eFileName = 'erori_{}.csv'.format(csv_file.name.split('.')[0])
        if os.path.exists(eFileName):
            os.remove(eFileName)

        noOfErrors = uploadCSV(request, csv_file, eFileName)

        request.session['csvFileName'] = eFileName

        response = redirect('sms-incarca')
        if noOfErrors > 0:
            response['Location'] += '?download=True'

        return response


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

def modify(request):
    
    try:
        eId = request.POST.get('id', 0)
        nume = request.POST.get('nume', 'Eroare')
        tip_asigurare = request.POST.get('tip_asigurare', 'Eroare')
        numar_masina = request.POST.get('numar_masina', 'Eroare')
        numar_telefon = request.POST.get('numar_telefon', 'Eroare')
        comanda_id = request.POST.get('comanda_id', 'Eroare')


        e = Expirari.objects.filter(pk=eId).first()

        e.nume = nume
        e.tip_asigurare = tip_asigurare
        e.numar_masina = numar_masina
        e.numar_telefon = numar_telefon
        e.comanda_id = comanda_id


        e.save()
    except:
        return JsonResponse({'success':'false'})
    return JsonResponse({'success':'true'})


def cert(request):
    return FileResponse(open('AA920CCDB7BC14100F7AC49C5451E46D.txt', 'rb'), content_type='text/csv')    

