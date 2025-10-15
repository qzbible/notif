

import threading

from django.template.loader import render_to_string
 
from datetime import datetime, timedelta
from icalendar import Calendar, Event, vCalAddress, vText
import os
import uuid
import secrets
from django.conf import settings

from service.utils import send_mail_created


def mail_decision_service(
    name,
    committee_name,
    committee_date,
    decisions_list,
    dest_email,
    url_connect,
    instance_name,
    instance_description,
    company,
    date_debut,
    date_fin,
    lieu_reunion,
    participants,
    back_host,
    lang=None
):
    """
    Service d'envoi d'email pour les décisions du comité
    
    Args:
        name: Nom du destinataire
        committee_name: Nom du comité
        committee_date: Date de la réunion
        decisions_list: Liste des décisions (array)
        dest_email: Email du destinataire
        url_connect: URL de connexion
        instance_name: Nom de l'instance
        instance_description: Description de l'instance
        company: Nom de l'entreprise
        date_debut: Date de début
        date_fin: Date de fin
        lieu_reunion: Lieu de réunion
        participants: Liste des participants
        back_host: URL de base du backend
        lang: Langue (fr-FR ou en-US)
    
    Returns:
        bool: True si l'envoi a réussi
    """
    
    # Déterminer les templates selon la langue
    if lang == "fr-FR":
        path = "board/decision/create-decision-fr.html"
        path_txt = "board/decision/create-decision-fr.txt"
        object_email = f"Décisions du comité : {committee_name}"
    elif lang == "en-US":
        path = "board/decision/create-decision-en.html"
        path_txt = "board/decision/create-decision-en.txt"
        object_email = f"Committee decisions: {committee_name}"
    else:
        path = "board/decision/create-decision-fr.html"
        path_txt = "board/decision/create-decision-fr.txt"
        object_email = f"Décisions du comité : {committee_name}"
    
    # Contexte pour le template
    context = {
        "name": name,
        "committee_name": committee_name,
        "committee_date": committee_date,
        "decisions_list": decisions_list,
        "url_connect": url_connect,
        "instance_name": instance_name,
        "instance_description": instance_description,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "lieu_reunion": lieu_reunion,
        "participants": participants,
        "company": company,
        "back_host": back_host
    }
    
    try:
        # Rendu des templates
        body_content = render_to_string(path, context)
        text_content = render_to_string(path_txt, context)
        
        # Envoi asynchrone de l'email
        email_thread = threading.Thread(
            target=send_mail_created,
            args=([dest_email], object_email, text_content, body_content, company,)
        )
        email_thread.start()
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {str(e)}")
        return False

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

 


