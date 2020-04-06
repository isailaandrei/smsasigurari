from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required


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


@login_required
def home(request):
    context = {
        'expirari': Expirari.objects.filter(mesaje_trimise=0),
        'trimise': Expirari.objects.exclude(mesaje_trimise=0),
        'mesaje': Messages.objects.all(),
    } 

    return render(request, 'home.html', context)

@login_required
def send(request):


    expirariIds = request.POST.get('expirari-ids', None)
    messageId = request.POST.get('msg-id', '')
    delete_rows = request.POST.get('Delete', False)

    if expirariIds:
        expirariIds = json.loads(expirariIds)

    if delete_rows:
        Expirari.objects.filter(pk__in=expirariIds).delete()
        return JsonResponse({'success':'true'})
  
    try:
        expirari = Expirari.objects.filter(pk__in=expirariIds)
        message = Messages.objects.filter(pk=messageId)[0]
        sendSMS(expirari, message)
    except Exception as e:
        logger.error(str(e))
        return JsonResponse({'success':'false'})

    return JsonResponse({'success':'true'})    


def sendSMS(expirari, messageObject):

    client = nexmo.Client(key='cf5281a4', secret='4cCLU6v3J4lIIOaZ')
    sent = {}
    message = messageObject.message
    
    logger.error(message)
    for expirare in expirari:
        response = client.send_message({
            'from': 'Asigurari',
            'to': expirare.numar_telefon,
            'text': message.format(expirare.numar_masina, str(expirare.valabilitate_sfarsit))
        })

        if response['messages'][0]['status'] == '0':
            sent[expirare] = True
            # expirare.mesaje_trimise += 1
            # expirare.save()
        else:
            sent[expirare] = False
            logger.error(response[['messages'][0]])

            

@login_required
def about(request):
    return render(request, 'about.html', {})

@login_required
def load(request):
    data = {}
    if "GET" == request.method:
        return render(request, "loadData.html", data)
   
    # if not GET, then proceed
    try:
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith('.csv'):
            messages.error(request,'Fisierul trebuie sa fie in format CSV (comma separated)')
            return HttpResponseRedirect(reverse("sms-incarca"))

        file_data = csv_file.read().decode("utf-8")     

        lines = file_data.split("\n")


        # Get the position of each header
        headers = lines[0].split(',')
        pos = {}
        for i, h in enumerate(headers):
                if h == 'Asigurat':
                    pos['name'] = i
                elif h == 'Telefon Asigurat':
                    pos['numar_telefon'] = i
                elif h == 'Nr.Inmatriculare':
                    pos['numar_masina'] = i
                elif h == 'Tip polita':
                    pos['tip_asigurare'] = i
                elif h == 'Valabilitate Sfarsit':
                    pos['valabilitate_sfarsit'] = i

        # Insert the fields into the database
        for i in range(1, len(lines)):
            
            line = lines[i]

            # Remove any commas inside fields
            while '"' in line:
                fc = line.find('"')
                line = line.replace('"', '', 1)

                sc = line.find('"')
                line = line.replace('"', '', 1)
                
                field = aux =  line[fc:sc]
                field = field.replace(',', ' ')


                line = line.replace(aux, field)



            fields = line.split(",")
            fields.append('X')

            data_dict = {}
            data_dict['name'] = fields[pos.get('name', -1)]
            data_dict['numar_masina'] = fields[pos.get('numar_masina', -1)]
            data_dict['tip_asigurare'] = fields[pos.get('tip_asigurare', -1)]
            data_dict['valabilitate_sfarsit'] = fields[pos.get('valabilitate_sfarsit', -1)]
            data_dict['sucursala'] = 'Alba'

            numar_telefon = fields[pos.get('numar_telefon', -1)]
            if numar_telefon.startswith('7'):
                numar_telefon = '0' + numar_telefon

            data_dict['numar_telefon'] = numar_telefon

            logger.error(data_dict['valabilitate_sfarsit'])
            try:
                form = ExpirariForm(data_dict)
                if form.is_valid():
                    form.save()                 
                else:
                    logger.error(form.errors.as_json())                                              
            except Exception as e:
                logger.error(str(e))
                messages.error(request, 'Randul urmator nu a putut fi incarcat: {}. Eroarea: '.format(fields, str(e)))                    
                pass

        messages.success(request, 'Fisierul a fost incarcat cu succes')


    except Exception as e:
        logger.error("Unable to upload file. {} ".format(str(e)))
        messages.error(request, 'Nu s-a putut incarca. Eroarea: {}'.format(str(e)))
        pass


    return HttpResponseRedirect(reverse("sms-incarca"))



