

import threading
# from exigence.utils import send_mail_created, send_mail_with_ics

from django.template.loader import render_to_string
 
from datetime import datetime, timedelta
from exigence.models import ActorFollow, ExigenceMail
from icalendar import Calendar, Event, vCalAddress, vText
import os
import uuid
import secrets
from django.conf import settings

from service.utils import format_date_string_short, send_mail_created, send_mail_with_ics 
from celery import shared_task
from typing import Tuple, Optional, Dict

import requests
import logging
from celery import current_app

logger = logging.getLogger(__name__)
 
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
def exigence_responsable( object, title, type_task, description, dest_email, sender_name, dest_name, company, url, scope=[], time="", deadline="", start_date="", back_url=None, lang=None ):
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
        path = "deployer/evaluation/responsable/responsable-exigence-fr.html" 
    elif lang == "en-US":
        path = "deployer/evaluation/responsable/responsable-exigence-en.html" 
    else:
        path = "deployer/evaluation/responsable/responsable-exigence-fr.html" 

    path_txt = "deployer/evaluation/responsable/responsable-exigence.txt" 
    context = {
        "sender_name":sender_name, 
        "name": dest_name,
        "title": title, 
        "url": url,
        "description":description,
        "time": time,
        "scope": scope,
        "deadline": format_date_string_short(deadline_text,lang ),
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
 
    if verifier_presence_t(start_date):
        new_deadline = start_date 
    else: 
        new_deadline = start_date+"T07:30:00.000Z"
    if is_valid_date_string(new_deadline):
        start_date = new_deadline.split(" ")[0]
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
        path = "deployer/evaluation/tache-conformite-fr.html" 
    elif lang == "en-US":
        path = "deployer/evaluation/tache-conformite-en.html" 
    else:
        path = "deployer/evaluation/tache-conformite-fr.html" 

    path_txt = "deployer/evaluation/tache-conformite.txt" 
    context = {
        "sender_name":sender_name, 
        "name": dest_name,
        "title": object, 
        "url": url,
        "description":description,
        "time": during,
        "scope":scope,
        "deadline": format_date_string_short(deadline_text,lang ),
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

   
    if verifier_presence_t(deadline):
        new_deadline = deadline 
    else: 
        new_deadline = deadline+"T07:30:00.000Z"

    if is_valid_date_string(new_deadline):
        parsed_date = datetime.strptime(new_deadline, "%Y-%m-%dT%H:%M:%S.%fZ")
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
        path = "deployer/evaluation/approuver/exigence-approbation-fr.html" 
    elif lang == "en-US":
        path = "deployer/evaluation/approuver/exigence-approbation-en.html" 
    else:
        path = "deployer/evaluation/approuver/exigence-approbation-fr.html" 

    # path = "notification/evaluation/exigence-approbation.html" 
    path_txt = "deployer/evaluation/approuver/exigence-approbation.txt" 
    # print("execution")
    context = {
        "sender_name":sender_name, 
        "name": dest_name,
        "title": object, 
        "url": url,
        "description":description,
        "time": time,
        "scope":scope,
        "deadline": format_date_string_short(deadline_text,lang ),
        "company": company,
        "type_task": type_task,
        "back_url" : os.environ.get("BACK_HOST_URL", "")
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


def exigence_notification( object, type_task, description, dest_email, sender_name, dest_name, company, url, scope=[], role="Informed", time="", deadline="", start_date="",  back_url=None, lang=None ):
    # object and description

    deadline_text = "non défini" 

    
    if verifier_presence_t(deadline):
        new_deadline = deadline 
    else: 
        new_deadline = deadline+"T07:30:00.000Z"

    if is_valid_date_string(new_deadline):
        parsed_date = datetime.strptime(new_deadline, "%Y-%m-%dT%H:%M:%S.%fZ")
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
        
    if role == "Informed": 
        if lang == "fr-FR" :
            path = "deployer/evaluation/informer/exigence-informed-fr.html" 
        elif lang == "en-US":
            path = "deployer/evaluation/exigence-informed-en.html" 
        else:
            path = "deployer/evaluation/exigence-informed-fr.html" 
        path_txt = "deployer/evaluation/exigence-informed.txt" 
    elif role == "Consulted":
        if lang == "fr-FR" :
            path = "deployer/evaluation/consulter/exigence-consulted-fr.html" 
        elif lang == "en-US":
            path = "deployer/evaluation/consulter/exigence-consulted-en.html" 
        else:
            path = "deployer/evaluation/consulter/exigence-consulted-fr.html" 
        path_txt = "deployer/evaluation/consulter/exigence-consulted.txt"
    else :
        return False
    context = {
        "sender_name":sender_name, 
        "name": dest_name,
        "title": object, 
        "url": url,
        "description":description,
        "time": time,
        "scope":scope,
        "deadline": format_date_string_short(deadline_text,lang ),
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
 

def accept_anwser( object, email,  type_task, description, title, dest_name, company, back_url=None, lang=None ):
    try:
        # object and description 
        if lang == "fr-FR" :
            path = "deployer/evaluation/approuver/answer/accept/accept_answer-fr.html" 
            path_txt = "deployer/evaluation/approuver/answer/accept/accept_answer-fr.txt" 
        elif lang == "en-US":
            path = "deployer/evaluation/approuver/answer/accept/accept_answer-en.html" 
            path_txt = "deployer/evaluation/approuver/answer/accept/accept_answer-en.txt" 
        else:
            path = "deployer/evaluation/approuver/answer/accept/accept_answer-fr.html"  
            path_txt = "deployer/evaluation/approuver/answer/accept/accept_answer-fr.txt"  

        
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
    except Exception as e:
        print(f"error -- > {str(e)}")
 

def rejet_anwser( object, email,  type_task, description, title, dest_name, company, back_url=None, lang=None ):
    # object and description 
    if lang == "fr-FR" :
        path = "deployer/evaluation/approuver/answer/rejet/rejet_answer-fr.html" 
        path_txt = "deployer/evaluation/approuver/answer/rejet/rejet_answer-fr.txt" 
    elif lang == "en-US":
        path = "deployer/evaluation/approuver/answer/rejet/rejet_answer-en.html" 
        path_txt = "deployer/evaluation/approuver/answer/rejet/rejet_answer-en.txt" 
    else:
        path = "deployer/evaluation/approuver/answer/rejet/rejet_answer-fr.html"  
        path_txt = "deployer/evaluation/approuver/answer/rejet/rejet_answer-fr.txt"  
        
      
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
 


@shared_task
def follow_up_task( id_project, id_action,role,  id_client,  dest_email, full_name, back_url, id_follow_up, user_id, token ):
    try:
        is_answer, status_code = check_response(id_action=id_action, id_project=id_project, url=back_url, user_id=user_id, token=token) 
        if status_code == 200:
            if is_answer == False :
                logger.info(f"⏳ Pas encore de réponse.") 
                # get data to  ExigenceMail 
                ins_exigence = ExigenceMail.objects.filter( id_project=id_project, id_action=id_action, id_client=id_client).first()
                logger.info(f"ins_exigence {ins_exigence} ")
                if ins_exigence:
                    logger.info(f"⏳ Pas encore de réponse. {role} - {dest_email} ")
                    if role == "Responsable":
                        exigence_responsable.delay(
                            object= ins_exigence.object,
                            type_task=ins_exigence.type_task,
                            description=ins_exigence.description,
                            dest_email=dest_email,
                            sender_name= ins_exigence.sender_name,
                            dest_name= full_name,
                            company=ins_exigence.company,
                            url=ins_exigence.url,
                            scope=ins_exigence.scope,
                            time=ins_exigence.time,
                            deadline=ins_exigence.dealine,
                            start_date=str(ins_exigence.start_date),
                            back_url=back_url,
                            lang=ins_exigence.lang
                        )
                    elif role == "Consulted": 
                        exigence_notification(
                            object= ins_exigence.object,
                            type_task=ins_exigence.type_task,
                            description=ins_exigence.description,
                            dest_email=dest_email,
                            sender_name= ins_exigence.sender_name,
                            dest_name= full_name,
                            company=ins_exigence.company,
                            url=ins_exigence.url,
                            scope=ins_exigence.scope,
                            time=ins_exigence.time,
                            deadline=ins_exigence.dealine,
                            start_date=str(ins_exigence.start_date),
                            back_url=back_url,
                            lang=ins_exigence.lang,
                            role=role
                        )
                    elif role == "Informed":
                        exigence_notification(
                            object= ins_exigence.object,
                            type_task=ins_exigence.type_task,
                            description=ins_exigence.description,
                            dest_email=dest_email,
                            sender_name= ins_exigence.sender_name,
                            dest_name= full_name,
                            company=ins_exigence.company,
                            url=ins_exigence.url,
                            scope=ins_exigence.scope,
                            time=ins_exigence.time,
                            deadline=ins_exigence.dealine,
                            start_date=str(ins_exigence.start_date),
                            back_url=back_url,
                            lang=ins_exigence.lang,
                            role=role
                        )
                    elif role == "Approver" :
                         exigence_approver(
                            object= ins_exigence.object,
                            type_task=ins_exigence.type_task,
                            description=ins_exigence.description,
                            dest_email=ins_exigence.dest_email,
                            sender_name= ins_exigence.sender_name,
                            dest_name= ins_exigence.dest_name,
                            company=ins_exigence.company,
                            url=ins_exigence.url,
                            scope=ins_exigence.scope,
                            time=ins_exigence.time,
                            deadline=ins_exigence.dealine,
                            start_date=str(ins_exigence.start_date),
                            back_url=back_url,
                            lang=ins_exigence.lang
                        )

            else:
                print("✅ Réponse déjà fournie.")
                # supprimer le follow up date 
                actor_follow_up = ActorFollow.objects.filter( id_follow_up=id_follow_up )
                for af in actor_follow_up:
                    try:
                        current_app.control.revoke(af.task_id, terminate=True)
                        print(f"Tâche {af.task_id} annulée avec succès")
                    except Exception as e:
                        print(f"Impossible d'annuler la tâche {af.task_id}: {str(e)}")

            if is_answer == True :
                print("✅ Réponse trouvée, mais délai dépassé.")

        elif status_code == 404:
            print("⚠️ Ressource non trouvée")
            logger.info(f"❌ Erreur: Code {status_code}")
        else:
            logger.info(f"❌ Erreur: Code {status_code}")
            print(f"❌ Erreur: Code {status_code}")

        return True
    except Exception as e:
        print(f"error -- > {str(e)}")
 
 

logger = logging.getLogger(__name__)


def check_response(
    id_action: int, 
    id_project: int, 
    url: str,
    user_id: Optional[int] = None,
    token: Optional[str] = None,
    timeout: int = 10,
    headers: Optional[Dict[str, str]] = None
) -> Tuple[bool, int]:
    """
    Vérifie si une réponse existe pour une action/projet donné.
    
    Args:
        id_action: ID de l'action
        id_project: ID du projet
        url: URL de base de l'API
        token: Token JWT pour l'authentification (optionnel)
        timeout: Délai d'attente en secondes
        headers: Headers HTTP supplémentaires (optionnel)
    
    Returns:
        Tuple[bool, int]: (is_answer, status_code)
            - is_answer: True si une réponse existe, False sinon
            - status_code: Code HTTP de la réponse (0 si erreur réseau)
    """
    
    # Validation des paramètres
    if not all([id_action, id_project, url]):
        logger.error("Paramètres manquants: id_action, id_project ou url")
        return False, 0
    
    # Nettoyer l'URL et construire le chemin
    url = url.rstrip('/')
    path = f"{url}/api/v1/task_answer/is-answer/{id_action}/{id_project}/{user_id}"
    
    # Préparer les headers
    request_headers = headers.copy() if headers else {}
    
    # Ajouter le token JWT si fourni
    if token:
        request_headers['Authorization'] = f'Bearer {token}'
        logger.debug("Token JWT ajouté aux headers")
    
    # Ajouter les headers par défaut
    request_headers.setdefault('Content-Type', 'application/json')
    request_headers.setdefault('Accept', 'application/json')
    
    try:
        logger.info(f"Vérification: action={id_action}, project={id_project}, url={path}")
        
        # Effectuer la requête avec timeout
        response = requests.get(
            path,
            timeout=timeout,
            headers=request_headers
        )
        
        status_code = response.status_code
        
        # Vérifier le statut
        if status_code == 200:
            try:
                data = response.json()
                is_answer = data.get('is_answer', False)
                
                logger.info(f"Réponse: is_answer={is_answer}, status={status_code}")
                return bool(is_answer), status_code
            
            except ValueError as e:
                logger.error(f"Erreur parsing JSON: {str(e)}")
                return False, status_code
        
        elif status_code == 401:
            logger.error("Erreur d'authentification (401): Token invalide ou expiré")
            return False, status_code
        
        elif status_code == 403:
            logger.error("Accès refusé (403): Permissions insuffisantes")
            return False, status_code
        
        elif status_code == 404:
            logger.warning("Ressource non trouvée (404)")
            return False, status_code
        
        else:
            logger.warning(f"Statut inattendu: {status_code}")
            return False, status_code
    
    except requests.exceptions.Timeout:
        logger.error(f"Timeout dépassé ({timeout}s) pour {path}")
        return False, 0
    
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Erreur de connexion à {path}: {str(e)}")
        return False, 0
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur requête HTTP: {str(e)}")
        return False, 0
    
    except Exception as e:
        logger.exception(f"Erreur inattendue: {str(e)}")
        return False, 0
    


def notification_approuver( object, title, type_task, description, dest_email, sender_name, dest_name, company, url, scope=[], time="", deadline="", start_date="", back_url=None, lang=None ):
    
    try: 
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
        # object and description 
        if lang == "fr-FR" :
            path = "deployer/evaluation/approuver/exigence-notification-approbateur-1-fr.html" 
            path_txt = "deployer/evaluation/approuver/exigence-notification-approbateur-1-fr.txt" 
        elif lang == "en-US":
            path = "deployer/evaluation/approuver/exigence-notification-approbateur-1-en.html" 
            path_txt = "deployer/evaluation/approuver/exigence-notification-approbateur-1-en.txt"  
        else:
            path = "deployer/evaluation/approuver/exigence-notification-approbateur-1-fr.html" 
            path_txt = "deployer/evaluation/approuver/exigence-notification-approbateur-1-fr.txt"  

        
        context = {
                "sender_name":sender_name, 
                "name": dest_name,
                "title": title, 
                "url": url,
                "description":description,
                "time": time,
                "scope": scope,
                "deadline": format_date_string_short(deadline_text,lang ),
                "company": company,
                "type_task": type_task,
                "back_url" :  "https://dev-backend.app.klivar.com/" if back_url == None else back_url
        }
        
        text_content = render_to_string(
                path_txt,
                context
        )
        body_content = render_to_string(
        path,
        context
        )
        text_content = render_to_string(
                path_txt,
                context
        )
        if filename != None: 
            x = threading.Thread(target= send_mail_with_ics, args=([dest_email], object, text_content, body_content, filename, company,))
            x.start() 
        else:
            x = threading.Thread(target= send_mail_created, args=([dest_email], object, text_content, body_content, company,))
            x.start() 
        return True
    except Exception as e:
        print(f"error -- > {str(e)}")
 




def notification_consulting( object, title, type_task, description, dest_email, sender_name, dest_name, company, url, scope=[], time="", deadline="", start_date="", back_url=None, lang=None ):
    
    try: 
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
        # object and description 
        if lang == "fr-FR" :
            path = "deployer/evaluation/consulter/exigence-notification-consultant-1-fr.html" 
            path_txt = "deployer/evaluation/consulter/exigence-notification-consultant-1-fr.txt" 
        elif lang == "en-US":
            path = "deployer/evaluation/consulter/exigence-notification-consultant-1-en.html" 
            path_txt = "deployer/evaluation/consulter/exigence-notification-consultant-1-en.txt"  
        else:
            path = "deployer/evaluation/consulter/exigence-notification-consultant-1-fr.html" 
            path_txt = "deployer/evaluation/consulter/exigence-notification-consultant-1-fr.txt"  

        
        context = {
                "sender_name":sender_name, 
                "name": dest_name,
                "title": title, 
                "url": url,
                "description":description,
                "time": time,
                "scope": scope,
                "deadline": format_date_string_short(deadline_text,lang ),
                "company": company,
                "type_task": type_task,
                "back_url" :  "https://dev-backend.app.klivar.com/" if back_url == None else back_url
        }
        
        text_content = render_to_string(
                path_txt,
                context
        )
        body_content = render_to_string(
        path,
        context
        )
        text_content = render_to_string(
                path_txt,
                context
        )
        if filename != None: 
            x = threading.Thread(target= send_mail_with_ics, args=([dest_email], object, text_content, body_content, filename, company,))
            x.start() 
        else:
            x = threading.Thread(target= send_mail_created, args=([dest_email], object, text_content, body_content, company,))
            x.start() 
        return True
    except Exception as e:
        print(f"error -- > {str(e)}")
 




def notification_informer( object, title, type_task, description, dest_email, sender_name, dest_name, company, url, scope=[], time="", deadline="", start_date="", back_url=None, lang=None ):
    
    try: 
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
        # object and description 
        if lang == "fr-FR" :
            path = "deployer/evaluation/informer/exigence-notification-informer-1-fr.html" 
            path_txt = "deployer/evaluation/informer/exigence-notification-informer-1-fr.txt" 
        elif lang == "en-US":
            path = "deployer/evaluation/informer/exigence-notification-informer-1-en.html" 
            path_txt = "deployer/evaluation/informer/exigence-notification-informer-1-en.txt"  
        else:
            path = "deployer/evaluation/informer/exigence-notification-informer-1-fr.html" 
            path_txt = "deployer/evaluation/informer/exigence-notification-informer-1-fr.txt"  

        
        context = {
                "sender_name":sender_name, 
                "name": dest_name,
                "title": title, 
                "url": url,
                "description":description,
                "time": time,
                "scope": scope,
                "deadline": format_date_string_short(deadline_text,lang ),
                "company": company,
                "type_task": type_task,
                "back_url" :  "https://dev-backend.app.klivar.com/" if back_url == None else back_url
        }
        
        text_content = render_to_string(
                path_txt,
                context
        )
        body_content = render_to_string(
        path,
        context
        )
        text_content = render_to_string(
                path_txt,
                context
        )
        if filename != None: 
            x = threading.Thread(target= send_mail_with_ics, args=([dest_email], object, text_content, body_content, filename, company,))
            x.start() 
        else:
            x = threading.Thread(target= send_mail_created, args=([dest_email], object, text_content, body_content, company,))
            x.start() 
        return True
    except Exception as e:
        print(f"error -- > {str(e)}")
 