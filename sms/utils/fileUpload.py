from django.contrib import messages
from sms.forms import ExpirariForm

import csv
import logging
import os


# Get an instance of a logger
logger = logging.getLogger(__name__)


def uploadCSV(request, csv_file, eFileName):

    noOfErrors = 0
    try: 
        eFile = open(eFileName, 'w')
        file_data = csv_file.read().decode("utf-8")     
        lines = file_data.split("\n")

        headers = lines[0].split(',')

        writer = csv.writer(eFile)
        writer.writerow(headers + ['Eroare'])

        # Get the position of each header
        noOfColumns = len(headers)
        noOfRows = len(lines)-1
        pos = {}
        for i, h in enumerate(headers):
                h = h.replace('\n', '')
                if h == 'Asigurat':
                    pos['nume'] = i
                elif h == 'Telefon Asigurat':
                    pos['numar_telefon'] = i
                elif h == 'Nr.Inmatriculare':
                    pos['numar_masina'] = i
                elif h == 'Tip polita':
                    pos['tip_asigurare'] = i
                elif h == 'Valabilitate Sfarsit':
                    pos['valabilitate_sfarsit'] = i

        # Parse fields and insert them into the database
        for i in range(1, noOfRows+1):
            
            line = lines[i]
            line = remove_commas_inside_fields(line)

            fields = line.split(",")
            if len(fields) != noOfColumns:
                messages.warning(request, 'Randul urmator nu a putut fi incarcat: {}. Numarul de celule nu corespunde'.format(fields))
                fields.append['Numarul de celule nu corespunde']
                writer.writerow(fields)
                noOfErrors += 1
                continue

            for f in fields:
                f = f.replace('\n', '')

            fields.append('X')

            data_dict = {}
            data_dict['tip_asigurare'] = fields[pos.get('tip_asigurare', -1)]
            

            # Doar polite 'RCA', 'CASCO', 'INCENDIU' deocamdata
            if data_dict['tip_asigurare'] not in ('RCA', 'CASCO', 'INCENDIU'):
                fields[-1] = 'Polite te tipul {} nu pot fi incarcate.'.format(data_dict['tip_asigurare'])
                writer.writerow(fields)
                noOfErrors += 1
                continue

            data_dict['numar_masina'] = fields[pos.get('numar_masina', -1)]
            data_dict['nume'] = fields[pos.get('nume', -1)]
            data_dict['numar_telefon'] = fields[pos.get('numar_telefon', -1)]
            data_dict['valabilitate_sfarsit'] = fields[pos.get('valabilitate_sfarsit', -1)]
           
            # TODO: Schimba valoarea hardcodata 
            data_dict['sucursala'] = 'Alba'
            
            # Curata numarul de telefon
            try:
                data_dict['numar_telefon'] = get_clean_phone_number(data_dict['numar_telefon'])
            except ValueError as e:
                fields[-1] = str(e)
                writer.writerow(fields)
                noOfErrors += 1
                continue

            try:
                form = ExpirariForm(data_dict)
                if form.is_valid():
                    form.save()                 
                else:
                    fields[-1] = 'Una dintre celule nu are formatul corespunzator'
                    logger.error(form.errors.as_json())
                    writer.writerow(fields)
                    noOfErrors += 1
            except Exception as e:
                fields[-1] = str(e)
                writer.writerow(fields)
                noOfErrors += 1

    except Exception as e:
        messages.warning(request, 'Eroare: {} din {} au fost incarcate'.format(noOfRows-noOfErrors, noOfRows))
        logger.error('Upload Error: {}'.format(str(e)))
    finally:
        logger.error(noOfErrors)  
        if noOfErrors > 0:
            messages.success(request, '{} din {} polite au fost incarcate'.format(noOfRows-noOfErrors, noOfRows))
        else:
            messages.success(request, 'Toate cele {} polite au fost incarcate cu success'.format(noOfRows))
        eFile.close()
        return noOfErrors

def remove_commas_inside_fields(line):

    line = line.replace('\n', '')
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


def get_clean_phone_number(numar):

    numar = numar.replace(' ', '')

    if numar == '':
        raise ValueError('Numarul de telefon trebuie specificat.')

    if numar.startswith(('0258', '258')):
        raise ValueError('Nu se pot introduce numere de telefon fix')

    # Daca nu are prefixul de tara, presupune ca tara e Romania 
    if numar.startswith('7'):
        return '+40' + numar
    
    if numar.startswith('07'):
        return '+4' + numar

    if numar.startswith(('40', '+40', '+44', '44', '0040', '0044')):
        return numar

    raise ValueError('Numarul de telefon are un format necunoscut')
    