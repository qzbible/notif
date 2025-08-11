

import threading

from django.template.loader import render_to_string
 
from datetime import datetime, timedelta
from icalendar import Calendar, Event, vCalAddress, vText
import os
import uuid
import secrets
from django.conf import settings

from service.utils import send_mail_created
 
def mail_new_devise_service(  name, dest_email, company,  os_name, device_type, browser_name, url_verification, back_url=None, lang=None ):
    # object and description
    if lang == "fr-FR" :
        path = "notification/alert_security/index-fr.html" 
        path_txt = "notification/alert_security/index-fr.txt" 
        object = "🔒 [Alerte sécurité] Nouvelle connexion détectée sur votre compte Klivar"
    elif lang == "en-US":
        path = "notification/alert_security/index-en.html" 
        path_txt = "notification/alert_security/index-en.txt" 
        object = "🔒 [Security Alert] New login detected on your Klivar account"
    else:
        path = "notification/alert_security/index-fr.html"
        path_txt = "notification/alert_security/index-fr.txt"  
        object = "🔒 [Alerte sécurité] Nouvelle connexion détectée sur votre compte Klivar"
    
   
    context = {
        "name":name,  
        "os_name": os_name, 
        "device_type":device_type,
        "browser_name":browser_name,
        "url_verification":url_verification,
       
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



def mail_new_network_service(  name, dest_email, company,  os_name, device_name, browser_name, ip_address, connection_time, back_url=None, lang=None ):
    # object and description
    if lang == "fr-FR" :
        path = "notification/alert_security/notif-network-fr.html" 
        path_txt = "notification/alert_security/index-fr.txt" 
        object = "Notification de sécurité – Nouvelle localisation/réseau détecté"
    elif lang == "en-US":
        path = "notification/alert_security/notif-network-en.html" 
        path_txt = "notification/alert_security/index-en.txt" 
        object = "Security Notification – New Location/Network Detected"
    else:
        path = "notification/alert_security/notif-network-fr.html"
        path_txt = "notification/alert_security/index-fr.txt"  
        object = "Notification de sécurité – Nouvelle localisation/réseau détecté"
    
   
    context = {
        "name":name,  
        "device_name":device_name,  
        "os_name": os_name, 
        "browser_name":browser_name,
        "ip_address":ip_address,
        "connection_time":connection_time,
       
        "back_url" :  "https://dev-backend.app.klivar.com/" if back_url == None else back_url
    }
 
    print('data context', context)
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



