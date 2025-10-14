

import threading

from django.template.loader import render_to_string
 
from datetime import datetime, timedelta
from icalendar import Calendar, Event, vCalAddress, vText
import os
import uuid
import secrets
from django.conf import settings

from service.utils import send_mail_created

def mail_welcome_service(  name, dest_email, company, url, back_url=None, lang=None ):
    # object and description
    if lang == "fr-FR" :
        path = "user-management/welcome/index-fr.html" 
        path_txt = "user-management/welcome/index-fr.txt" 
        object = "Bienvenue dans votre espace Klivar – Accédez dès maintenant à vos ressources clés 🚀"
    elif lang == "en-US":
        path = "user-management/welcome/index-en.html" 
        path_txt = "user-management/welcome/index-en.txt" 
        object = "Welcome to your Klivar space – Access your key resources now 🚀"
    else:
        path = "user-management/welcome/index-fr.html"
        path_txt = "user-management/welcome/index-fr.txt"  
        object = "Bienvenue sur Klivar"
    
    context = {
        "name":name,  
        "title": object, 
        "url_connect": url,
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


def mail_forgrt_service(  name, dest_email, company, url, back_url=None, lang=None ):
    # object and description
    if lang == "fr-FR" :
        path = "user-management/resetPassword/index-fr.html" 
        path_txt = "user-management/welcome/index-fr.txt" 
        object = "Modifier votre mot de passe"
    elif lang == "en-US":
        path = "user-management/resetPassword/index-en.html" 
        path_txt = "user-management/welcome/index-en.txt" 
        object = "Change your password"
    else:
        path = "user-management/resetPassword/index-fr.html"
        path_txt = "notification/welcome/index-fr.txt"  
        object = "Modifier votre mot de passe"

    context = {
        "name":name,  
        "title": object, 
        "url": url,
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

 


