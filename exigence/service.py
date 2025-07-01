

import threading
# from exigence.utils import send_mail_created, send_mail_with_ics

from django.template.loader import render_to_string
 
from datetime import datetime, timedelta
from icalendar import Calendar, Event, vCalAddress, vText
import os
import uuid
import secrets
from django.conf import settings

from service.utils import send_mail_created, send_mail_with_ics 
from celery import shared_task
 
#  Exigence data start 2025-06-16

def is_valid_date_string(date_string, format="%Y-%m-%dT%H:%M:%S.%fZ"):
    try:
        if date_string == "" or date_string == None:
            return False
        date_string = date_string.split(" ")[0]
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False

def start_date(in_date, time):
    """This function return start time for activity"""
    # 2022-12-09T14:43:33+01:00
    res = in_date.split("T")
    date_out = res[0]
    date_out = date_out.replace("-", ",")
    # date_out = datetime.strptime(date_out, '%m-%d-%Y').date()
    # time = "14:30:00"
    time = time.replace(":", ",")
    date_out = date_out + '-' + time
    date_out = date_out.replace(":", ",")
    begin_str = date_out.replace("-", ",")
    begin_str = begin_str.replace(" ", ",")
    begin_int = tuple(map(int, begin_str.split(',')))
    time_begin = datetime(*begin_int[0:6])
    return time_begin

def add_calendar(title, description, date_begin, date_end, company):
    event = Event()
    event.add('summary', title)
    event.add('description', description)

    # Variables attendues
    in_date = date_begin  # La date
    # time = begin_hour # Le debut
    # duration = duration # La duree
    list_date_begin = in_date.split(" ")
    list_date_end = date_end.split(" ")
    begin = start_date(list_date_begin[0], list_date_begin[1])
    end = start_date(list_date_end[0], list_date_end[1])

    event.add('dtstart', begin)
    event.add('dtend', end)
    # 2022-12-09T14:43:33+01:00

    event['uid'] = secrets.token_urlsafe(8) + '@klivar.com'
    event.add('priority', 5)

    organizer = vCalAddress('MAILTO:' + settings.EMAIL_HOST_USER)
    organizer.params['cn'] = vText(company)
    organizer.params['role'] = vText("Utilisateur Klivar")
    event['organizer'] = organizer

    cal = Calendar()
    cal.add_component(event)

    dirpath = uuid.uuid4().hex[:6].lower()
    save_as = "media/calendar/" + dirpath

    if not os.path.exists(save_as):
        os.makedirs(save_as)

    filename = save_as + "/" + 'icalendar.ics'

    if os.path.exists(filename):
        os.remove(filename)
    f = open(filename, 'wb')
    f.write(cal.to_ical())
    f.close()

    return filename

def verifier_presence_t(chaine):
    """
    Vérifie si le caractère 'T' est présent dans la chaîne donnée.
    
    Args:
        chaine (str): La chaîne à vérifier
        
    Returns:
        bool: True si 'T' est présent, False sinon
    """
    return 'T' in chaine

@shared_task
def exigence_responsable( object, type_task, description, dest_email, sender_name, dest_name, company, url, scope=[], time="", deadline="", start_date="", back_url=None, lang=None ):
    # object and description

    deadline_text = "non défini" 
    if lang == "fr-FR" :
        deadline_text = "non défini"
    elif lang == "en-US":
        deadline_text = "not defined"
    
    if verifier_presence_t(deadline):
        new_deadline = deadline 
    else: 
        new_deadline = deadline+"T07:30:00.000Z"
    new_start_date = start_date+"T07:30:00.000Z"
    if is_valid_date_string(new_deadline):
        parsed_date = datetime.strptime(new_deadline, "%Y-%m-%dT%H:%M:%S.%fZ")
        deadline_text = parsed_date.strftime("%Y-%m-%d")
    
    filename = None
    if is_valid_date_string(new_start_date):
        start_date = new_start_date.split(" ")[0]
        # Analyser la date ISO 8601
        parsed_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        # Reformater au format souhaité
        formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M")
        date_begin = datetime.strptime(formatted_date,  "%Y-%m-%d %H:%M")
        date_end = date_begin + timedelta(minutes=int(time))
        # configuration iCalendar
        if company != None: 
            filename = add_calendar(
                    object, description, str(date_begin), str(date_end), company) # add_calendar(title, description, date_begin, date_end, company_denomination) construction du icalenda avec le nom de la compagnie
        else:
            filename = add_calendar(
                object, description, str(date_begin), str(date_end), "Klivar") # add_calendar(title, description, date_begin, date_end, company_denomination) construction du icalenda avec le nom de la compagnie
        
    if lang == "fr-FR" :
        path = "notification/evaluation/responsable-exigence-fr.html" 
    elif lang == "en-US":
        path = "notification/evaluation/responsable-exigence-en.html" 
    else:
        path = "notification/evaluation/responsable-exigence-fr.html" 

    path_txt = "notification/evaluation/responsable-exigence.txt" 
    context = {
        "sender_name":sender_name, 
        "name": dest_name,
        "title": object, 
        "url": url,
        "description":description,
        "time": time,
        "scope": scope,
        "deadline": deadline_text,
        "company": company,
        "type_task": type_task,
        "back_url" :  "https://dev-backend.app.klivar.com/" if back_url == None else back_url
    } 
    body_content = render_to_string(
        path,
        context
    )
    text_content = render_to_string(
            path_txt,
            context
    )
    if filename != None:
        print("filename", filename)
        x = threading.Thread(target= send_mail_with_ics, args=([dest_email], object, text_content, body_content, filename, company,))
        x.start() 
    else:
        x = threading.Thread(target= send_mail_created, args=([dest_email], object, text_content, body_content, company,))
        x.start() 
    return True


def task_responsable( object, type_task, description, dest_email, sender_name, dest_name, company, url, scope=[], during="", start_date="", back_url=None, lang=None ):
    # object and description
    deadline_text = "non défini" 
    filename = None
    print("start data", start_date )
    if is_valid_date_string(start_date):
        start_date = start_date.split(" ")[0]
        # Analyser la date ISO 8601
        parsed_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        # Reformater au format souhaité
        formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M")
        date_begin = datetime.strptime(formatted_date,  "%Y-%m-%d %H:%M")
        date_end = date_begin + timedelta(minutes=int(during))
        deadline_text = date_end.strftime("%Y-%m-%d %H:%M" )
        # configuration iCalendar
        if company != None: 
            filename = add_calendar(
                    object, description, str(date_begin), str(date_end), company) # add_calendar(title, description, date_begin, date_end, company_denomination) construction du icalenda avec le nom de la compagnie
        else:
            filename = add_calendar(
                object, description, str(date_begin), str(date_end), "Klivar") # add_calendar(title, description, date_begin, date_end, company_denomination) construction du icalenda avec le nom de la compagnie
    
    if lang == "fr-FR" :
        path = "notification/evaluation/tache-conformite-fr.html" 
    elif lang == "en-US":
        path = "notification/evaluation/tache-conformite-en.html" 
    else:
        path = "notification/evaluation/tache-conformite-fr.html" 

    path_txt = "notification/evaluation/tache-conformite.txt" 
    context = {
        "sender_name":sender_name, 
        "name": dest_name,
        "title": object, 
        "url": url,
        "description":description,
        "time": during,
        "scope":scope,
        "deadline": deadline_text,
        "company": company,
        "type_task": type_task,
        "back_url" :  "https://dev-backend.app.klivar.com/" if back_url == None else back_url
    }
    
    body_content = render_to_string(
        path,
        context
    )
    text_content = render_to_string(
            path_txt,
            context
    )
    # send_mail_created([dest_email], object, text_content, html_content, company)
    if filename != None:
        x = threading.Thread(target= send_mail_with_ics, args=([dest_email], object, text_content, body_content, filename, company,))
        x.start() 
    else:
        x = threading.Thread(target= send_mail_created, args=([dest_email], object, text_content, body_content, company,))
        x.start() 
    
    return True


def exigence_approver( object, type_task, description, dest_email, sender_name, dest_name, company, url, scope=[],  time="", deadline="", start_date="", back_url=None, lang=None ):
    # object and description

    deadline_text = "non défini" 
    if is_valid_date_string(deadline):
        parsed_date = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S.%fZ")
        deadline_text = parsed_date.strftime("%Y-%m-%d")

    filename = None

    if is_valid_date_string(start_date):
        start_date = start_date.split(" ")[0]

        # Analyser la date ISO 8601
        parsed_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")

        # Reformater au format souhaité
        formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M")

        date_begin = datetime.strptime(formatted_date,  "%Y-%m-%d %H:%M")
        date_end = date_begin + timedelta(minutes=int(time))
        
    
        # configuration iCalendar
        if company != None: 
            filename = add_calendar(
                    object, description, str(date_begin), str(date_end), company) # add_calendar(title, description, date_begin, date_end, company_denomination) construction du icalenda avec le nom de la compagnie
        else:
            filename = add_calendar(
                object, description, str(date_begin), str(date_end), "Klivar") # add_calendar(title, description, date_begin, date_end, company_denomination) construction du icalenda avec le nom de la compagnie
        
    
    if lang == "fr-FR" :
        path = "notification/evaluation/exigence-approbation-fr.html" 
    elif lang == "en-US":
        path = "notification/evaluation/exigence-approbation-en.html" 
    else:
        path = "notification/evaluation/exigence-approbation-fr.html" 

    # path = "notification/evaluation/exigence-approbation.html" 
    path_txt = "notification/evaluation/exigence-approbation.txt" 
    context = {
        "sender_name":sender_name, 
        "name": dest_name,
        "title": object, 
        "url": url,
        "description":description,
        "time": time,
        "scope":scope,
        "deadline": deadline_text,
        "company": company,
        "type_task": type_task,
        "back_url" :  "https://dev-backend.app.klivar.com/" if back_url == None else back_url
    }
 
    body_content = render_to_string(
        path,
        context
    )
 
    text_content = render_to_string(
            path_txt,
            context
    )
    # send_mail_created([dest_email], object, text_content, html_content, company)
    if filename != None:
        print("filename", filename)
        x = threading.Thread(target= send_mail_with_ics, args=([dest_email], object, text_content, body_content, filename, company,))
        x.start() 
    else:
        x = threading.Thread(target= send_mail_created, args=([dest_email], object, text_content, body_content, company,))
        x.start() 
    
    return True


def exigence_notification( object, type_task, description, dest_email, sender_name, dest_name, company, url, scope=[],  time="", deadline="", start_date="", back_url=None, lang=None ):
    # object and description

    deadline_text = "non défini" 
    if is_valid_date_string(deadline):
        parsed_date = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S.%fZ")
        deadline_text = parsed_date.strftime("%Y-%m-%d")

    filename = None

    if is_valid_date_string(start_date):
        start_date = start_date.split(" ")[0]

        # Analyser la date ISO 8601
        parsed_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")

        # Reformater au format souhaité
        formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M")

        date_begin = datetime.strptime(formatted_date,  "%Y-%m-%d %H:%M")
        date_end = date_begin + timedelta(minutes=int(time))
        
    
        # configuration iCalendar
        if company != None: 
            filename = add_calendar(
                    object, description, str(date_begin), str(date_end), company) # add_calendar(title, description, date_begin, date_end, company_denomination) construction du icalenda avec le nom de la compagnie
        else:
            filename = add_calendar(
                object, description, str(date_begin), str(date_end), "Klivar") # add_calendar(title, description, date_begin, date_end, company_denomination) construction du icalenda avec le nom de la compagnie
        


    if lang == "fr-FR" :
        path = "notification/evaluation/exigence-notification-fr.html" 
    elif lang == "en-US":
        path = "notification/evaluation/exigence-notification-en.html" 
    else:
        path = "notification/evaluation/exigence-notification-fr.html" 

    # path = "notification/evaluation/exigence-notification.html" 
    path_txt = "notification/evaluation/exigence-notification.txt" 
    context = {
        "sender_name":sender_name, 
        "name": dest_name,
        "title": object, 
        "url": url,
        "description":description,
        "time": time,
        "scope":scope,
        "deadline": deadline_text,
        "company": company,
        "type_task": type_task,
        "back_url" :  "https://dev-backend.app.klivar.com/" if back_url == None else back_url
    }
 
    body_content = render_to_string(
        path,
        context
    )
 
    text_content = render_to_string(
            path_txt,
            context
    )
    # send_mail_created([dest_email], object, text_content, html_content, company)
    if filename != None:
        print("filename", filename)
        x = threading.Thread(target= send_mail_with_ics, args=([dest_email], object, text_content, body_content, filename, company,))
        x.start() 
    else:
        x = threading.Thread(target= send_mail_created, args=([dest_email], object, text_content, body_content, company,))
        x.start() 
    
    return True
 

def accept_anwser( object, email,  type_task, description, title, dest_name, company, back_url=None, lang=None ):
    # object and description 
    if lang == "fr-FR" :
        path = "notification/evaluation/accept_answer-fr.html" 
    elif lang == "en-US":
        path = "notification/evaluation/accept_answer-en.html" 
    else:
        path = "notification/evaluation/accept_answer-fr.html"  

    path_txt = "notification/evaluation/exigence-notification.txt" 
    context = {
        "name": dest_name,
        "title": title,  
        "description":description, 
        "company": company,
        "type_task": type_task,
        "back_url" :  "https://dev-backend.app.klivar.com/" if back_url == None else back_url
    }
    html_content = render_to_string(
        path,
        context
    )
    text_content = render_to_string(
            path_txt,
            context
    )
    send_mail_created(
        [email], 
        object, 
        text_content, 
        html_content,
        company
    )     
    return True
 

def rejet_anwser( object, email,  type_task, description, title, dest_name, company, back_url=None, lang=None ):
    # object and description 
    if lang == "fr-FR" :
        path = "notification/evaluation/rejet_answer-fr.html" 
    elif lang == "en-US":
        path = "notification/evaluation/rejet_answer-en.html" 
    else:
        path = "notification/evaluation/rejet_answer-fr.html"  
        
    path_txt = "notification/evaluation/exigence-notification.txt" 
    context = { 
        "name": dest_name,
        "title": title,  
        "description":description, 
        "company": company,
        "type_task": type_task,
        "back_url" :  "https://dev-backend.app.klivar.com/" if back_url == None else back_url
    }
    html_content = render_to_string(
        path,
        context
    )
    text_content = render_to_string(
            path_txt,
            context
    )
    send_mail_created(
        [email], 
        object, 
        text_content, 
        html_content,
        company
    )
    return True
 

 