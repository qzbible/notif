

import threading

from django.template.loader import render_to_string
 
from datetime import datetime, timedelta
from board.utils import explain_recurrence_simple, format_recurrence_schedule
from icalendar import Calendar, Event, vCalAddress, vText
import os
import uuid
import secrets
from django.conf import settings

from typing import List, Dict, Tuple
from service.utils import send_mail_created


def list_actors_info(actors: List[Dict]) -> Tuple[List[str], str]:
    """
    Liste tous les emails et noms complets des acteurs
    
    Args:
        actors: Liste des acteurs
        
    Returns:
        Tuple (emails, fullnames)
        - emails: Liste des emails (avec doublons possibles)
        - fullnames: Chaîne avec tous les noms séparés par des virgules
    """
    emails = []
    fullnames_list = []
    
    for actor in actors:
        # Email principal
        if actor.get('email'):
            emails.append(actor['email'])
        
        # Email secondaire
        if actor.get('email_second'):
            emails.append(actor['email_second'])
        
        # Nom complet
        first_name = actor.get('first_name', '').strip()
        last_name = actor.get('last_name', '').strip()
        
        if first_name and last_name:
            full_name = f"{first_name} {last_name}"
        elif first_name:
            full_name = first_name
        elif last_name:
            full_name = last_name
        else:
            continue
        
        fullnames_list.append(full_name)
    
    # Joindre les noms avec des virgules
    fullnames = ", ".join(fullnames_list)
    
    return emails, fullnames



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
    url_connect,
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
        url_connect: URL pour accéder à la session
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
        path = "board/meeting/create-meeting-fr.html"
        path_txt = "board/meeting/create-meeting-fr.txt"
        object_email = f"Rappel : Réunion du comité {committee_name}"
    elif lang == "en-US":
        path = "board/meeting/rcreate-meeting-en.html"
        path_txt = "board/meeting/create-meeting-en.txt"
        object_email = f"Reminder: {committee_name} meeting"
    else:
        path = "board/meeting/create-meeting-fr.html"
        path_txt = "board/meeting/create-meeting-fr.txt"
        object_email = f"Rappel : Réunion du comité {committee_name}"
    
    # Contexte pour le template
    context = {
        "name": name,
        "committee_name": committee_name,
        "date_reunion": date_reunion,
        "heure_reunion": heure_reunion,
        "lieu_reunion": lieu_reunion,
        "participants": participants,
        "url_connect": url_connect,
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

 
def mail_committee_created_service( 
    title,
    description, 
    link,
  
    url_connect,
    company,
    back_host,
 
    periodicity,
    actors = [],
    lang=None
):
    """
    Service d'envoi d'email pour la création d'un comité d'instance
    
    Args:
        name: Nom du destinataire
        committee_name: Nom du comité
        committee_description: Description du comité
        start_date: Date de début
        end_date: Date de fin
        location: Lieu de réunion
        participants: Liste des participants
        dest_email: Email du destinataire
        url_connect: URL de connexion
        company: Nom de l'entreprise
        back_host: URL de base du backend
        lang: Langue (fr-FR ou en-US)
    
    Returns:
        bool: True si l'envoi a réussi
    """
    periodicity_l = None 
    date =  ''
    # Déterminer les templates selon la langue
    if lang == "fr-FR":
        path = "board/instance/create-committee-fr.html"
        path_txt = "board/instance/create-committee-fr.txt"
        object_email = f"Nouveau comité d'instance créé : {title}"
        periodicity_l = explain_recurrence_simple(periodicity, 'fr')
        date = format_recurrence_schedule(periodicity, 'fr')
    elif lang == "en-US":
        path = "board/instance/create-committe-en.html"
        path_txt = "board/instance/create-committee-en.txt"
        object_email = f"New committee instance created: {title}"
        periodicity_l = explain_recurrence_simple(periodicity, 'en')
        date = format_recurrence_schedule(periodicity, 'en')
    else:
        path = "board/instance/create-committee-fr.html"
        path_txt = "board/instance/create-committee-fr.txt"
        object_email = f"Nouveau comité d'instance créé : {title}"
        periodicity_l = explain_recurrence_simple(periodicity, 'fr')
        date = format_recurrence_schedule(periodicity, 'fr')
    
    # Contexte pour le template
     
    emails, fullnames = list_actors_info(actors)
    print("---------")
    try:
        for act in actors: 
            context = {
                "name": act.get('first_name', '') + ' ' + act.get('last_name', ''),
                "committee_name": title,
                "committee_description": description,
                "date": date, 
                "location": link,
                "participants": fullnames,
                "url_connect": url_connect,
                "company": company,
                "back_host": back_host,
                'periodicity':periodicity_l
            }
            # Rendu des templates
            body_content = render_to_string(path, context)
            text_content = render_to_string(path_txt, context)
            
            # Envoi asynchrone de l'email
            email_thread = threading.Thread(
                target=send_mail_created,
                args=([emails], object_email, text_content, body_content, company,)
            )
            email_thread.start()
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de création de comité: {str(e)}")
        return False
    

def mail_arbitrage_created_service(
    name,
    committee_name,
    committee_date,
    nomber_elements,
    type_arbitration_elements,
    priorite_arbitrage,
    instance_name,
    instance_description,
    instance_start_date,
    instance_end_date,
    instance_location,
    instance_participants,
    dest_email,
    url_connect,
    company,
    back_host,
    lang=None
):
    """
    Service d'envoi d'email pour la création d'un dossier d'arbitrage
    
    Args:
        name: Nom du destinataire
        committee_name: Nom du comité
        committee_date: Date de la réunion
        nomber_elements: Nombre d'éléments à arbitrer
        type_arbitration_elements: Types d'éléments
        priorite_arbitrage: Priorité
        instance_name: Nom de l'instance
        instance_description: Description de l'instance
        instance_start_date: Date de début
        instance_end_date: Date de fin
        instance_location: Lieu de réunion
        instance_participants: Participants
        dest_email: Email du destinataire
        url_connect: URL de connexion
        company: Nom de l'entreprise
        back_host: URL de base du backend
        lang: Langue (fr-FR ou en-US)
    
    Returns:
        bool: True si l'envoi a réussi
    """
    
    # Déterminer les templates selon la langue
    if lang == "fr-FR":
        path = "board/folders/create-folders-fr.html"
        path_txt = "board/folders/create-folders-fr.txt"
        object_email = f"Nouveau dossier d'arbitrage créé - {committee_name}"
    elif lang == "en-US":
        path = "board/folders/create-folders-en.html"
        path_txt = "board/folders/create-folders-en.txt"
        object_email = f"New arbitration file created - {committee_name}"
    else:
        path = "board/folders/create-folders-fr.html"
        path_txt = "board/folders/create-folders-fr.txt"
        object_email = f"Nouveau dossier d'arbitrage créé - {committee_name}"
    
    # Contexte pour le template
    context = {
        "name": name,
        "committee_name": committee_name,
        "committee_date": committee_date,
        "nomber_elements": nomber_elements,
        "type_arbitration_elements": type_arbitration_elements,
        "priorite_arbitrage": priorite_arbitrage,
        "instance_name": instance_name,
        "instance_description": instance_description,
        "instance_start_date": instance_start_date,
        "instance_end_date": instance_end_date,
        "instance_location": instance_location,
        "instance_participants": instance_participants,
        "url_connect": url_connect,
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
        print(f"Erreur lors de l'envoi de l'email de création de dossier d'arbitrage: {str(e)}")
        return False