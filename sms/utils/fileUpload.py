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

    atLeastOneIssue = False
    try:
        csv_file = request.FILES["file"]
        if not csv_file.name.endswith('.csv'):
            messages.warning(request,'Fisierul trebuie sa fie in format CSV (comma separated)')
            return HttpResponseRedirect(reverse("sms-incarca"))

        file_data = csv_file.read().decode("utf-8")     

        lines = file_data.split("\n")


        # Get the position of each header
        headers = lines[0].split(',')
        columns = len(headers)
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
            line = remove_commas_inside_fields(line)


            fields = line.split(",")
            if len(fields) != columns:
                messages.warning(request, 'Randul urmator nu a putut fi incarcat: {}. Numarul de celule nu corespunde'.format(fields, ))
                atLeastOneIssue = True
                continue

            fields.append('X')

            data_dict = {}
            data_dict['name'] = fields[pos.get('name', -1)]
            data_dict['numar_masina'] = fields[pos.get('numar_masina', -1)]
            data_dict['tip_asigurare'] = fields[pos.get('tip_asigurare', -1)]
            data_dict['numar_telefon'] = fields[pos.get('numar_telefon', -1)]
            data_dict['valabilitate_sfarsit'] = fields[pos.get('valabilitate_sfarsit', -1)]
            
            # TODO: Change hardcoded value 
            data_dict['sucursala'] = 'Alba'

            logger.error('here3')

            # Doar polite RCA deocamdata
            if data_dict['tip_asigurare'] != 'RCA':
                messages.warning(request, 'Polita {} pe numele {} nu a putut fi incarcata.'.format(data_dict['tip_asigurare'], data_dict['name']))
                atLeastOneIssue = True
                continue

            if data_dict['numar_telefon'].startswith('7'):
                data_dict['numar_telefon'] = '+40' + data_dict['numar_telefon']
            elif data_dict['numar_telefon'].startswith('07'):
                data_dict['numar_telefon'] = '+4' + data_dict['numar_telefon']

            try:
                form = ExpirariForm(data_dict)
                if form.is_valid():
                    form.save()                 
                else:
                    messages.warning(request, '''Randul urmator nu a putut fi incarcat: {}. 
                                            Una dintre celule nu are formatul corespunzator'''.format(fields))
                    logger.error(form.errors.as_json())
                    atLeastOneIssue = True
            except Exception as e:
                logger.error(str(e))
                messages.warning(request, 'Randul urmator nu a putut fi incarcat: {}. Eroarea: {}'.format(fields, str(e)))                    
                atLeastOneIssue = True
                pass

        if atLeastOneIssue:
            messages.success(request, 'Restul randurilor au fost incarcate cu success')
        else:
            messages.success(request, 'Toate randurile au fost incarcate cu success')


    except Exception as e:
        logger.error("Unable to upload file. {} ".format(str(e)))
        messages.warning(request, 'Nu s-a putut incarca. Eroarea: {}'.format(str(e)))
        pass


    return HttpResponseRedirect(reverse("sms-incarca"))

def remove_commas_inside_fields(line):
    # Remove any commas inside fields
    while '"' in line:
        fc = line.find('"')
        line = line.replace('"', '', 1)

        sc = line.find('"')
        line = line.replace('"', '', 1)
        
        field = aux =  line[fc:sc]
        field = field.replace(',', '')

        line = line.replace(aux, field)        
    
    return line