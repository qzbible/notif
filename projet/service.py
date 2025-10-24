

import threading

from django.template.loader import render_to_string
 
from datetime import datetime, timedelta
from icalendar import Calendar, Event, vCalAddress, vText
import os
import uuid
import secrets
from django.conf import settings

from service.utils import format_date_string_short, send_mail_created
from celery import shared_task

@shared_task
def mail_notification_start_projet_service(name, dest_email, title, start_date, end_date, company,  description, url, back_url=None, lang=None ):
    # object and description
    if lang == "fr-FR" :
        path = "deployer/audit_project/index-start-project-fr.html" 
        path_txt = "deployer/audit_project/index-start-project-fr.txt" 
        object = f"✅ Audit lancé : {title} ({format_date_string_short(start_date, lang) } au {format_date_string_short(end_date, lang)})"
    elif lang == "en-US":
        path = "deployer/audit_project/index-start-project-en.html" 
        path_txt = "deployer/audit_project/index-start-project-en.txt" 
        object = f" ✅ Audit launched: {title} ({format_date_string_short(start_date, lang)} at {format_date_string_short(end_date, lang)})"
    else:
        path = "deployer/audit_project/index-start-project-fr.html"
        path_txt = "deployer/audit_project/index-start-project-fr.txt"  
        object = f"✅ Audit lancé : {title} ({format_date_string_short(start_date) } au {format_date_string_short(end_date)})"
    

    context = {
        "name":name,  
        "start_date": format_date_string_short(start_date, lang),
        "end_date": format_date_string_short(end_date, lang),
        "title":title,
        "description":description,
        "company":company,
        "url":url, 
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
    x = threading.Thread(target= send_mail_created, args=([dest_email], object, text_content, body_content, company,))
    x.start() 
    
    return True



def mail_notification_end_projet_service(  name, dest_email, title,  company,  description, url, back_url=None, lang=None ):
    # object and description
    if lang == "fr-FR" :
        path = "deployer/audit_project/index-end-project-fr.html" 
        path_txt = "deployer/audit_project/index-end-project-fr.txt" 
        object = f"✅ Projet d’audit terminé – {title}"
    elif lang == "en-US":
        path = "deployer/audit_project/index-end-project-en.html" 
        path_txt = "deployer/audit_project/index-end-project-en.txt" 
        object = f"✅ Audit Project Completed – {title}"
    else:
        path = "deployer/audit_project/index-end-project-fr.html"
        path_txt = "deployer/audit_project/index-end-project-fr.txt"  
        object = f"✅ Projet d’audit terminé – {title}"
    
   
    context = {
        "name":name,   
        "title":title,
        "description":description,
         "company":company,
        "url":url, 
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
    x = threading.Thread(target= send_mail_created, args=([dest_email], object, text_content, body_content, company,))
    x.start() 
    
    return True


 


@shared_task
def mail_alert_seuil_indicator(  raporting_title, msg, title, percent_value, seuil, company, date_alert,  description, url_connect, back_host=None, lang=None, actors =[] ):
    # object and description
    if lang == "fr-FR" :
        path = "deployer/indicator/alert-seuil-percent-fr.html" 
        path_txt = "deployer/indicator/alert-seuil-percent-fr.txt" 
        object = f"🚨 🚨 🚨 Alerte - {title} "
    elif lang == "en-US":
        path = "deployer/indicator/alert-seuil-percent-en.html" 
        path_txt = "deployer/indicator/alert-seuil-percent-en.txt" 
        object = f"🚨 🚨 🚨 Alert - {title} "
    else:
        path = "deployer/indicator/alert-seuil-percent-fr.html"
        path_txt = "deployer/indicator/alert-seuil-percent-fr.txt"  
        object = f"🚨 🚨 🚨 Alerte - {title} "
    print(f"x data", company)
    context = {
        "indicator_name":title,  
        "msg":msg,  
        "seuil":seuil,   
        "date_alert": format_date_string_short(date_alert if date_alert else datetime.now(), lang),
        "raporting_name":raporting_title,
        "description":description,
        "company":company,
        "percent_value":percent_value,
        "url_connect":url_connect, 
        "back_host" :  back_host
    }
    emails = [ actor.get('email') for actor in actors if actor.get('email') ] 
    body_content = render_to_string(
        path,
        context
    )
    text_content = render_to_string(
            path_txt,
            context
    )
    x = threading.Thread(target= send_mail_created, args=(emails, object, text_content, body_content, company,))
    x.start() 
    
    return True

