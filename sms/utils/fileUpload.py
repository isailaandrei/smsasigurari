from django.db import models
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from sms.forms import ExpirariForm

import nexmo
import csv
import logging


# Get an instance of a logger
logger = logging.getLogger(__name__)


def uploadCSV(request):

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
        logger.error(headers)

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

            logger.error('here')
            # Remove any commas inside fields
            while '"' in line:
                fc = line.find('"')
                line = line.replace('"', '', 1)

                sc = line.find('"')
                line = line.replace('"', '', 1)
                
                field = aux =  line[fc:sc]
                field = field.replace(',', ' ')


                line = line.replace(aux, field)

            logger.error('here2')

            fields = line.split(",")
            fields.append('X')
            logger.error(fields)

            data_dict = {}
            data_dict['name'] = fields[pos.get('name', -1)]
            data_dict['numar_masina'] = fields[pos.get('numar_masina', -1)]
            data_dict['tip_asigurare'] = fields[pos.get('tip_asigurare', -1)]
            data_dict['numar_telefon'] = fields[pos.get('numar_telefon', -1)]
            data_dict['valabilitate_sfarsit'] = fields[pos.get('valabilitate_sfarsit', -1)]
            data_dict['sucursala'] = 'Alba'

            logger.error('here3')

            # Doar polite RCA deocamdata
            if data_dict['tip_asigurare'] != 'RCA':
                continue

            if data_dict['numar_telefon'].startswith('7'):
                data_dict['numar_telefon'] = '+40 ' + data_dict['numar_telefon']

            logger.error('here4')

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

