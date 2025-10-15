

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
 

def mail_meeting_reminder_service(
    name,
    committee_name,
    date_reunion,
    heure_reunion,
    lieu_reunion,
    participants,
    dest_email,
    url_session,
    instance_name,
    instance_description,
    date_debut,
    date_fin,
    company,
    back_host,
    lang=None
):
    """
    Service d'envoi d'email pour le rappel de réunion du comité
    
    Args:
        name: Nom du destinataire
        committee_name: Nom du comité
        date_reunion: Date de la réunion
        heure_reunion: Heure de la réunion
        lieu_reunion: Lieu ou lien de réunion
        participants: Liste des participants
        dest_email: Email du destinataire
        url_session: URL pour accéder à la session
        instance_name: Nom de l'instance
        instance_description: Description de l'instance
        date_debut: Date de début
        date_fin: Date de fin
        company: Nom de l'entreprise
        back_url: URL de base du backend
        lang: Langue (fr-FR ou en-US)
    
    Returns:
        bool: True si l'envoi a réussi
    """
    
    # Déterminer les templates selon la langue
    if lang == "fr-FR":
        path = "board/meeting/reminder-fr.html"
        path_txt = "board/meeting/reminder-fr.txt"
        object_email = f"Rappel : Réunion du comité {committee_name}"
    elif lang == "en-US":
        path = "board/meeting/reminder-en.html"
        path_txt = "board/meeting/reminder-en.txt"
        object_email = f"Reminder: {committee_name} meeting"
    else:
        path = "board/meeting/reminder-fr.html"
        path_txt = "board/meeting/reminder-fr.txt"
        object_email = f"Rappel : Réunion du comité {committee_name}"
    
    # Contexte pour le template
    context = {
        "name": name,
        "committee_name": committee_name,
        "date_reunion": date_reunion,
        "heure_reunion": heure_reunion,
        "lieu_reunion": lieu_reunion,
        "participants": participants,
        "url_session": url_session,
        "instance_name": instance_name,
        "instance_description": instance_description,
        "date_debut": date_debut,
        "date_fin": date_fin,
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
        print(f"Erreur lors de l'envoi de l'email de rappel: {str(e)}")
        return False

 


