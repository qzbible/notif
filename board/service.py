

import threading

from django.template.loader import render_to_string
 
from datetime import datetime, timedelta
from board.utils import explain_recurrence_simple, format_date_hour, format_perimeter_for_email, format_ponctuel_date, format_recurrence_schedule
from icalendar import Calendar, Event, vCalAddress, vText
import os
import uuid
import secrets
from django.conf import settings

from typing import List, Dict, Tuple
from service.utils import send_mail_created
from celery import shared_task

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
 
    committee_name,
    committee_date,
    decisions_list, 
    url_connect,
    instance_name,
    instance_description,
    company,  
    lieu_reunion, 
    back_host, 
    periodicity,
    ponctuel_config,
    actors = [],
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
    periodicity_l = None 
    date_instance = ''
    # Déterminer les templates selon la langue
    if lang == "fr-FR":
        path = "board/decision/create-decision-fr.html"
        path_txt = "board/decision/create-decision-fr.txt"
        object_email = f"Décisions du comité : {committee_name}"
        periodicity_l = explain_recurrence_simple(periodicity, 'fr')
        if periodicity :
            date_instance = format_recurrence_schedule(periodicity, 'fr')
        elif ponctuel_config :
            date_instance = format_ponctuel_date(ponctuel_config, 'fr')
        else :
            date_instance = ''
    
    elif lang == "en-US":
        path = "board/decision/create-decision-en.html"
        path_txt = "board/decision/create-decision-en.txt"
        object_email = f"Committee decisions: {committee_name}"
        periodicity_l = explain_recurrence_simple(periodicity, 'en')
        if periodicity :
            date_instance = format_recurrence_schedule(periodicity, 'en')
        elif ponctuel_config :
            date_instance = format_ponctuel_date(ponctuel_config, 'en')
        else :
            date_instance = ''
    else:
        path = "board/decision/create-decision-fr.html"
        path_txt = "board/decision/create-decision-fr.txt"
        object_email = f"Décisions du comité : {committee_name}"

        periodicity_l = explain_recurrence_simple(periodicity, 'fr')
        if periodicity :
            date_instance = format_recurrence_schedule(periodicity, 'fr')
        elif ponctuel_config :
            date_instance = format_ponctuel_date(ponctuel_config, 'fr')
        else :
            date_instance = ''
    
    # Contexte pour le template
    emails, fullnames = list_actors_info(actors)
    try:
        for act in actors: 
            context = {
                    "name": act.get('first_name', '') + ' ' + act.get('last_name', ''),
                    "committee_name": committee_name,
                    "committee_date": committee_date,
                    "decisions_list": decisions_list,
                    "url_connect": url_connect,
                    "instance_name": instance_name,
                    "instance_description": instance_description,
                    "instance_date": date_instance, 
                    "lieu_reunion": lieu_reunion,
                    "participants": fullnames,
                    "company": company,
                    "periodicity": periodicity_l,
                    "back_host": back_host
                }

            # Rendu des templates
            body_content = render_to_string(path, context)
            text_content = render_to_string(path_txt, context)
            
            # Envoi asynchrone de l'email
            email_thread = threading.Thread(
                target=send_mail_created,
                args=([act.get('email')], object_email, text_content, body_content, company,)
            )
            email_thread.start()
            
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {str(e)}")
        return False
 

@shared_task
def mail_meeting_reminder_service(
    title,
    description, 
    link,
    url_connect,
    company,
    back_host,
    periodicity,
    ponctuel_config,
    actors = [],
    perimeter = [],
    date=None,
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
    
    periodicity_l = None 
    date_instance = ''
    # Déterminer les templates selon la langue
    if lang == "fr-FR":
        path = "board/meeting/create-meeting-fr.html"
        path_txt = "board/meeting/create-meeting-fr.txt"
        object_email = f"Rappel : Réunion du comité {title}"
        periodicity_l = explain_recurrence_simple(periodicity, 'fr')
        if periodicity :
            date_instance = format_recurrence_schedule(periodicity, 'fr')
        elif ponctuel_config :
            date_instance = format_ponctuel_date(ponctuel_config, 'fr')
        else :
            date_instance = ''
        date_only, hour = format_date_hour(date, 'fr')
    
    elif lang == "en-US":
        path = "board/meeting/rcreate-meeting-en.html"
        path_txt = "board/meeting/create-meeting-en.txt"
        object_email = f"Reminder: {title} meeting"
        periodicity_l = explain_recurrence_simple(periodicity, 'en')
        if periodicity :
            date_instance = format_recurrence_schedule(periodicity, 'en')
        elif ponctuel_config :
            date_instance = format_ponctuel_date(ponctuel_config, 'en')
        else :
            date_instance = ''
        date_only, hour = format_date_hour(date, 'fr')
    else:
        path = "board/meeting/create-meeting-fr.html"
        path_txt = "board/meeting/create-meeting-fr.txt"
        object_email = f"Rappel : Réunion du comité {title}"
        periodicity_l = explain_recurrence_simple(periodicity, 'fr')
        if periodicity :
            date_instance = format_recurrence_schedule(periodicity, 'fr')
        elif ponctuel_config :
            date_instance = format_ponctuel_date(ponctuel_config, 'fr')
        else :
            date_instance = ''
        date_only, hour = format_date_hour(date, 'fr')

    emails, fullnames = list_actors_info(actors)
    # Contexte pour le template
     
    try:
        
        for act in actors: 
            # Retirer l'email du destinataire actuel de la liste des CC
            other_emails = [email for email in emails if email != act.get('email')]
            
            context = { 
                "name": act.get('first_name', '') + ' ' + act.get('last_name', ''),
                "committee_name": title + ' '+date_only+' '+hour,
                "date_reunion": date_only,
                "heure_reunion": hour,
                "lieu_reunion": link,
                "participants": fullnames,
                "url_connect": url_connect,
                "instance_name": title,
                "instance_description": description,
                "date": date_instance, 
                "company": company,
                "back_host": back_host,
                "periodicity": periodicity_l
            } 
            # Rendu des templates
            body_content = render_to_string(path, context)
            text_content = render_to_string(path_txt, context)
            
            # Envoi asynchrone de l'email avec les autres en copie cachée
            email_thread = threading.Thread(
                target=send_mail_created,
                args=([act.get('email')], object_email, text_content, body_content),
                kwargs={ 'company': company}
            )
            email_thread.start()

            # send elt arb 
            result = mail_arbitrage_created_service(
                name=act.get('first_name', '') + ' ' + act.get('last_name', ''),
                committee_name=title + ' '+date_only+' '+hour,
                committee_date= date_only+' '+hour,
                nomber_elements= len(perimeter),
                type_arbitration_elements= format_perimeter_for_email(perimeter, 'fr' if lang=="fr-FR" else "en"), 
                instance_name=title,
                instance_description=description,
                instance_date=date_instance,
                # instance_end_date=validated_data.get('instance_end_date'),
                instance_location=link,
                instance_participants=fullnames,
                dest_email=act.get('email'),
                url_connect=url_connect,
                company=company,
                back_host=os.environ.get("BACK_HOST_URL", ""),
                lang=lang
            )
        
        return True
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        # print(f"Traceback: {traceback.format_exc()}")  # ✅ Voir toute la stack
        raise  # ✅ Relancer pour que Celery puisse logger
 

def mail_arbitrage_created_service(
    name,
    committee_name,
    committee_date,
    nomber_elements,
    type_arbitration_elements,
 
    instance_name,
    instance_description,
    instance_date,
 
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
        
        "instance_name": instance_name,
        "instance_description": instance_description,
        "instance_date": instance_date, 
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

        send_mail_created(
            [dest_email], 
            object_email, 
            text_content, 
            body_content,  
            company
        )
        
        # Envoi asynchrone de l'email
        # email_thread = threading.Thread(
        #     target=send_mail_created,
        #     args=([dest_email], object_email, text_content, body_content, company,)
        # )
        # email_thread.start() 
        return True 
    except Exception as e:
        print(f"Erreur: {str(e)}")
        print(f"Traceback:  ")  # ✅ Voir toute la stack
        raise  # ✅ Relancer pour que Celery puisse logger
    
 
def mail_committee_created_service( 
    title,
    description, 
    link,
    url_connect,
    company,
    back_host,
    periodicity,
    ponctuel_config,
    actors = [],
    created=False,
    lang=None
):
    """
    Service d'envoi d'email pour la création d'un comité d'instance
    """
    periodicity_l = None 
    date = ''
    
    # Déterminer les templates selon la langue
    if lang == "fr-FR":
        path = "board/instance/create-committee-fr.html"
        path_txt = "board/instance/create-committee-fr.txt"
        if created:
            object_email = f"Nouveau comité d'instance créé : {title}"
        else:
            object_email = f"Comité d'instance mis à jour : {title}"
        periodicity_l = explain_recurrence_simple(periodicity, 'fr')
        if periodicity :
            date = format_recurrence_schedule(periodicity, 'fr')
        elif ponctuel_config :
            date = format_ponctuel_date(ponctuel_config, 'fr')
        else :
            date = ''
        
    elif lang == "en-US":
        path = "board/instance/create-committe-en.html"
        path_txt = "board/instance/create-committee-en.txt"
        if created:
            object_email = f"New committee instance created : {title}"
        else:
            object_email = f"Committee instance updated : {title}"
         
        periodicity_l = explain_recurrence_simple(periodicity, 'en')
        
        if periodicity :
            date = format_recurrence_schedule(periodicity, 'en')
        elif ponctuel_config :
            date = format_ponctuel_date(ponctuel_config, 'en')
        else :
            date = ''
    else:
        path = "board/instance/create-committee-fr.html"
        path_txt = "board/instance/create-committee-fr.txt"
        if created:
            object_email = f"Nouveau comité d'instance créé : {title}"
        else:
            object_email = f"Comité d'instance mis à jour : {title}" 

        periodicity_l = explain_recurrence_simple(periodicity, 'fr')
         
        if periodicity :
            date = format_recurrence_schedule(periodicity, 'fr')
        elif ponctuel_config :
            date = format_ponctuel_date(ponctuel_config, 'fr')
        else :
            date = ''
    
    # Récupérer tous les emails et noms
    emails, fullnames = list_actors_info(actors)
    
    try:
        for act in actors: 
            # Retirer l'email du destinataire actuel de la liste des CC
            other_emails = [email for email in emails if email != act.get('email')]
            
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
                'periodicity': periodicity_l
            }
            
            # Rendu des templates
            body_content = render_to_string(path, context)
            text_content = render_to_string(path_txt, context)
            
            # Envoi asynchrone de l'email avec les autres en copie cachée
            email_thread = threading.Thread(
                target=send_mail_created,
                args=([act.get('email')], object_email, text_content, body_content),
                kwargs={'cc_emails': other_emails, 'company': company}
            )
            email_thread.start()

            
        return True
    except Exception as e:
        print(f"Erreur dans mail_committee_created_service: {str(e)}")
        return False
    


 
def mail_comment_created_service( 
     date_send,
    title,
    comment, 
    sender_name, 
    company, 
    back_host,
    actors = [],
    
    lang=None
):
    """
    Service d'envoi d'email pour la création d'un  commentaire
    """ 
    # Déterminer les templates selon la langue
    if lang == "fr-FR":
        path = "board/comment/add-comment-fr.html"
        path_txt = "board/comment/add-comment-fr.txt"
        object_email = f"Nouveau commentaire sur une décision: {title}"
    elif lang == "en-US":
        path = "board/comment/add-comment-en.html"
        path_txt = "board/comment/add-comment-en.txt"
        object_email = f"New comment on a task : {title}" 
    else:
        path = "board/comment/add-comment-fr.html"
        path_txt = "board/comment/add-comment-fr.txt"
        object_email = f"Nouveau commentaire sur une décision:  {title}"
         
    
    try:
        for act in actors: 
            # Retirer l'email du destinataire actuel de la liste des CC 
            
            context = {
                "name": act.get('first_name', '') + ' ' + act.get('last_name', ''),
                "sender_name": sender_name, 
                "task_name": title, 
                "date_send": date_send,
                "comment": comment, 
                "company": company,
                "back_url": back_host
            }
            
            # Rendu des templates
            body_content = render_to_string(path, context)
            text_content = render_to_string(path_txt, context)
            
            # Envoi asynchrone de l'email avec les autres en copie cachée
            email_thread = threading.Thread(
                target=send_mail_created,
                args=([act.get('email')], object_email, text_content, body_content),
            )
            email_thread.start()

            
        return True
    except Exception as e:
        print(f"Erreur dans mail_committee_created_service: {str(e)}")
        return False
    


def mail_decision_one_service(
    committee_name,
    committee_date, 
    url_connect,
    company,  
    back_host,  
    title,
    description,
    perimeter,
    decision_date,
    task_list,
    actors = [],
    lang=None
):
    """
    Service d'envoi d'email pour les décisions du comité
    
    Args:
        committee_name: Nom du comité
        committee_date: Date de la réunion du comité 
        title: Titre de la décision
        description: Description de la décision
        liste_arb_element: Éléments à arbitrer
        decision_date: Date d'échéance
        task_list: Liste des tâches
        url_connect: URL de connexion
        company: Nom de l'entreprise
        back_host: URL de base du backend 
        actors: Liste des acteurs destinataires (avec email, first_name, last_name)
        lang: Langue (fr-FR ou en-US)
    
    Returns:
        bool: True si l'envoi a réussi
    """ 
    
    # Déterminer les templates selon la langue
    if lang == "en-US":
        path = "board/decision/create-decision-one-en.html"
        path_txt = "board/decision/create-decision-one-en.txt"
        object_email = f"Committee decisions: {committee_name}"
       
    else:  # Par défaut fr-FR
        path = "board/decision/create-decision-one-fr.html"
        path_txt = "board/decision/create-decision-one-fr.txt"
        object_email = f"Décisions du comité : {committee_name}"
        
    
    try:
        for act in actors: 
            # Retirer l'email du destinataire actuel de la liste des CC  
            context = {
                "name": f"{act.get('first_name', '')} {act.get('last_name', '')}".strip(),
                "committee_name": committee_name,
                "committee_date": committee_date,
                "url_connect": url_connect,
                "company_name": company,
                "back_host": back_host,
                # Informations spécifiques à la décision
                "title": title,
                "description": description,
                "liste_arb_element":  format_perimeter_for_email(perimeter, 'fr' if lang=="fr-FR" else "en"),
                "decision_date": decision_date,
                "task_list": task_list
            }

            # Rendu des templates
            body_content = render_to_string(path, context)
            text_content = render_to_string(path_txt, context)
            
            # Envoi asynchrone de l'email
            email_thread = threading.Thread(
                target=send_mail_created,
                args=(
                    [act.get('email')], 
                    object_email, 
                    text_content, 
                    body_content, 
                    company,
                )
            )
            email_thread.start()

        return True
       
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {str(e)}")
        return False
