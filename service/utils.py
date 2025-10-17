from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import connection


import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

from urllib.request import urlopen
import uuid

from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime
import secrets
import urllib.request
import re

from urllib.parse import urlparse
import requests
 

def get_lang_request(request):
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    # Déterminer la langue à utiliser
    if 'fr-FR' in accept_language:
        selected_lang = 'fr-FR'
    elif 'en-US' in accept_language:
        selected_lang = 'en-US'
    else:
        # Langue par défaut
        selected_lang = 'fr-FR'
    return selected_lang


 
def send_mail(to_emails, title, text_content, html_content, company):
    """Docstring for send_mail."""
    from_email = settings.EMAIL_HOST_USER
    for to_email in to_emails:
        if company:
            msg = EmailMultiAlternatives(
                title,
                text_content,
                company+' Via Klivar <' + from_email + '>',
                [to_email],
                reply_to=None,
            )
        else:
            msg = EmailMultiAlternatives(
                title,
                text_content,
                'Klivar <' + from_email + '>',
                [to_email],
                reply_to=None,
            ) 
         
        if html_content:
            msg.attach_alternative(html_content, 'text/html')

        msg.send()
    return True

# def send_mail_created(to_emails, title, text_content, html_content, company=None):
#     """Docstring for send_mail."""
#     from_email = settings.EMAIL_HOST_USER
#     for to_email in to_emails: 
#         if company :
#             msg = EmailMultiAlternatives(
#                 title,
#                 text_content,
#                 company+' Via Klivar <' + from_email + '>',
#                 [to_email],
#                 reply_to=None,
#             )
#         else:
#             msg = EmailMultiAlternatives(
#                 title,
#                 text_content,
#                 'Klivar <' + from_email + '>',
#                 [to_email],
#                 reply_to=None,
#             )
#         if html_content:
#             msg.attach_alternative(html_content, 'text/html')

#         msg.send()
#     return True

def send_mail_created(to_emails, title, text_content, html_content,   company=None):
    """
    Envoie un email à plusieurs destinataires en utilisant Django's EmailMultiAlternatives.
    
    Args:
        to_emails (list): Liste des adresses email des destinataires
        title (str): Sujet de l'email
        text_content (str): Contenu en format texte
        html_content (str): Contenu en format HTML (optionnel)
        company (str, optional): Nom de l'entreprise expéditrice. Défaut à None.
    
    Returns:
        bool: True si l'envoi a réussi
    """
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings
    import uuid
    
    from_email = settings.EMAIL_HOST_USER
    sender_name = company + ' Via Klivar' if company else 'Klivar'
    from_formatted = f'{sender_name} <{from_email}>'
    
    # Ajout d'options d'en-têtes pour améliorer la délivrabilité
    headers = {
        'Reply-To': from_email,
        'X-Entity-Ref-ID': str(uuid.uuid4()),  # ID unique pour chaque message
        'List-Unsubscribe': f'<mailto:{from_email}?subject=unsubscribe>'
    }
    
    success = True
    
    for to_email in to_emails:
        try:
            # Création du message avec les en-têtes optimisés
            cc_filtered = [email for email in to_emails if email != to_email]
            msg = EmailMultiAlternatives(
                subject=title,
                body=text_content,
                from_email=from_formatted,
                to=[to_email],
                cc= cc_filtered,
                headers=headers
            )
            
            # Ajout de la version HTML si disponible
            if html_content:
                msg.attach_alternative(html_content, 'text/html')
            
            # Envoi du message
            msg.send(fail_silently=False)
            
        except Exception as e:
            # Journalisation des erreurs sans arrêter le processus
            print(f"Erreur lors de l'envoi à {to_email}: {str(e)}")
            success = False
    
    return success
def send_mail_test(to_emails, title, text_content, html_content, filename):
    """Docstring for send_mail."""
    from_email = settings.EMAIL_HOST_USER

    for to_email in to_emails:

        msg = EmailMultiAlternatives(
            title,
            text_content,
            'Klivar App No Replay <' + from_email + '>',
            [to_email],
            reply_to=None,
        )
        if html_content:
            msg.attach_alternative(html_content, 'text/html')
            # msg.attach(filename, 'text/*')
            # msg.attach(filename, "text/calendar; method=REQUEST; charset=\"UTF-8\"")
            msg.attach(
                filename, "text/calendar; method=REQUEST; charset=\"UTF-8\"")
            msg.content_subtype = 'calendar'

        msg.send()
    os.remove(filename)
    return True


def send_mail_file(to_emails, title, text_content, html_content, files, company):
    """Docstring for send_mail."""
    from_email = settings.EMAIL_HOST_USER

    for to_email in to_emails:

        msg = EmailMultiAlternatives(
            title,
            text_content,
            company + ' Via Klivar <' + from_email + '>',
            [to_email],
            reply_to=None,
        )
        if html_content:
            msg.attach_alternative(html_content, 'text/html')
        if files:
            for file in files:
                msg.attach_file(file)

        msg.send()
    # os.remove(filename)
    return True


# def send_mail_with_ics(to_emails, title, text_content, html_content, filename, company):
#     """Docstring for send_mail."""

#     from_email = settings.EMAIL_HOST_USER

#     for to_email in to_emails:

#         # Create a multipart message and set headers
#         msg = MIMEMultipart()
#         # message = EmailMultiAlternatives()
#         msg["From"] = company + ' Via Klivar <' + from_email + '>'
#         msg["To"] = to_email
#         msg["Subject"] = title
#         if html_content:
#             # msg.attach_alternative(html_content, 'text/html')
#             msg.attach(MIMEText(html_content, "html"))
#             msg.attach(MIMEText("", "plain"))
#             if os.path.exists(filename):
#                 with open(filename, "rb") as attachment:
#                     # Add file as application/octet-stream
#                     # Email client can usually download this automatically as attachment
#                     part = MIMEBase("application", "octet-stream")
#                     part.set_payload(attachment.read())
#                 # Encode file in ASCII characters to send by email
#                 encoders.encode_base64(part)

#                 # Add header as key/value pair to attachment part
#                 file_name = filename.rsplit('/', 1)[-1]
#                 part.add_header(
#                     "Content-Disposition",
#                     f"attachment; filename= {file_name}",
#                 )

#                 msg.attach(part)

#                 text = msg.as_string()
#                 # Log in to server using secure context and send email
#                 context = ssl.create_default_context()
#                 # server smtp and port
#                 EMAIL_HOST = settings.EMAIL_HOST
#                 EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
#                 with smtplib.SMTP_SSL(EMAIL_HOST, context=context) as server:
#                     server.login(from_email, EMAIL_HOST_PASSWORD)
#                     server.sendmail(from_email, to_email, text)
#             else:
#                 return False
#     os.remove(filename)
#     return True


def send_mail_with_ics(to_emails, title, text_content, html_content, filename, company):
    """
    Envoie un email avec une pièce jointe ICS (calendrier) à plusieurs destinataires.
    
    Args:
        to_emails (list): Liste des adresses email des destinataires
        title (str): Sujet de l'email
        text_content (str): Contenu en format texte (important pour éviter le spam)
        html_content (str): Contenu en format HTML (optionnel)
        filename (str): Chemin vers le fichier ICS à joindre
        company (str): Nom de l'entreprise expéditrice
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
   

    from_email = settings.EMAIL_HOST_USER
    
    # Vérification préalable que le fichier existe
    if not os.path.exists(filename):
        return False
    
    # Configuration pour la connexion SMTP
    EMAIL_HOST = settings.EMAIL_HOST
    EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
    
    # Création du contexte SSL pour une connexion sécurisée
    context = ssl.create_default_context()
    
    # Préparation de la pièce jointe ICS
    with open(filename, "rb") as attachment:
        part = MIMEBase("text", "calendar", method="REQUEST", name="meeting.ics")
        part.set_payload(attachment.read())
    
    # Encodage et ajout des en-têtes pour la pièce jointe
    encoders.encode_base64(part)
    file_name = filename.rsplit('/', 1)[-1]
    part.add_header("Content-Disposition", f"attachment; filename={file_name}")
    part.add_header("Content-ID", f"<{file_name}@klivar>")
    
    # Préparation de l'en-tête DKIM (si disponible)
    # Cette ligne est optionnelle et dépend de votre configuration
    # dkim_header = settings.EMAIL_DKIM_HEADER if hasattr(settings, 'EMAIL_DKIM_HEADER') else None
    
    success = True
    
    for to_email in to_emails:
        try:
            # Création du message multipart
            msg = MIMEMultipart("mixed")
            
            # Ajout des en-têtes essentiels
            msg["From"] = f"{company} Via Klivar <{from_email}>"
            msg["To"] = to_email
            msg["Subject"] = title
            msg["Reply-To"] = from_email
            msg["Message-ID"] = f"<{os.urandom(16).hex()}@klivar>"
            
            # Création d'une partie alternative pour le HTML et le texte
            alt_part = MIMEMultipart("alternative")
            
            # Toujours attacher une version texte (important pour éviter le spam)
            alt_part.attach(MIMEText(text_content or "Voir le contenu HTML", "plain"))
            
            # Attacher la version HTML si disponible
            if html_content:
                alt_part.attach(MIMEText(html_content, "html"))
            
            # Attacher la partie alternative au message principal
            msg.attach(alt_part)
            
            # Attacher la pièce jointe ICS
            msg.attach(part)
            
            # Conversion en chaîne de caractères
            text = msg.as_string()
            
            # Envoi du message
            with smtplib.SMTP_SSL(EMAIL_HOST, 465, context=context) as server:
                server.login(from_email, EMAIL_HOST_PASSWORD)
                server.sendmail(from_email, to_email, text)
        
        except Exception as e:
            print(f"Erreur lors de l'envoi à {to_email}: {str(e)}")
            success = False
    
    # Suppression du fichier ICS
    if os.path.exists(filename):
        os.remove(filename)
    
    return success


# def send_mail_with_ics_file(to_emails, title, files, html_content, filename, company):
#     """Docstring for send_mail."""

#     from_email = settings.EMAIL_HOST_USER

#     for to_email in to_emails:

#         # Create a multipart message and set headers
#         msg = MIMEMultipart()
#         # message = EmailMultiAlternatives()
#         msg["From"] = company + ' Via Klivar <' + from_email + '>'
#         msg["To"] = to_email
#         msg["Subject"] = title

#         if html_content:
#             # msg.attach_alternative(html_content, 'text/html')
#             msg.attach(MIMEText(html_content, "html"))
#             msg.attach(MIMEText("", "plain")) 
#             if files:
#                 for file in files:
#                     with open(file, "rb") as attachment:
#                         # Add file as application/octet-stream
#                         # Email client can usually download this automatically as attachment
#                         part = MIMEBase("application", "octet-stream")
#                         part.set_payload(attachment.read())
#                     # Encode file in ASCII characters to send by email
#                     encoders.encode_base64(part)
#                     # Add header as key/value pair to attachment part
#                     """part.add_header(
#                         "Content-Disposition",
#                         f"attachment; file= {file}",
#                     )"""
#                     part.add_header('content-disposition',
#                                     'attachment', filename=file.split('/')[-1])
#                     msg.attach(part)
#                     text = msg.as_string()

#                     # print(msg)

#             if os.path.exists(filename):
#                 with open(filename, "rb") as attachment:
#                     # Add file as application/octet-stream
#                     # Email client can usually download this automatically as attachment
#                     part = MIMEBase("application", "octet-stream")
#                     part.set_payload(attachment.read())
#                 # Encode file in ASCII characters to send by email
#                 encoders.encode_base64(part)

#                 # Add header as key/value pair to attachment part
#                 file_name = filename.rsplit('/', 1)[-1]
#                 part.add_header(
#                     "Content-Disposition",
#                     f"attachment; filename= {file_name}",
#                 )

#                 msg.attach(part)

#                 text = msg.as_string()
#                 # Log in to server using secure context and send email
#                 context = ssl.create_default_context()
#                 # server smtp and port
#                 EMAIL_HOST = settings.EMAIL_HOST
#                 EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
#                 with smtplib.SMTP_SSL(EMAIL_HOST, context=context) as server:
#                     server.login(from_email, EMAIL_HOST_PASSWORD)
#                     server.sendmail(from_email, to_email, text)
#             else:
#                 return False
#     os.remove(filename)
#     return True


def send_mail_with_ics_file(to_emails, title, files, html_content, filename, company, text_content=None):
    """
    Envoie un email avec un fichier ICS et d'autres pièces jointes optionnelles.
    
    Args:
        to_emails (list): Liste des adresses email des destinataires
        title (str): Sujet de l'email
        files (list): Liste des chemins vers les fichiers à joindre
        html_content (str): Contenu en format HTML
        filename (str): Chemin vers le fichier ICS à joindre
        company (str): Nom de l'entreprise expéditrice
        text_content (str, optional): Contenu en format texte. Si non fourni, une version sera générée.
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """

    # Fonction pour extraire du texte depuis le HTML si aucun texte n'est fourni
    def html_to_text(html):
        # Suppression basique des balises HTML
        text = re.sub('<.*?>', ' ', html)
        # Remplacement des entités HTML courantes
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        # Suppression des espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    from_email = settings.EMAIL_HOST_USER
    
    # Vérification préalable que le fichier ICS existe
    if not os.path.exists(filename):
        return False
    
    # Si aucun contenu texte n'est fourni, extraire du HTML
    if not text_content and html_content:
        text_content = html_to_text(html_content)
    elif not text_content:
        text_content = "Veuillez consulter la version HTML de cet email."
    
    # Préparation des variables pour la connexion SMTP
    EMAIL_HOST = settings.EMAIL_HOST
    EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
    
    # Création du contexte SSL pour une connexion sécurisée
    context = ssl.create_default_context()
    
    success = True
    
    for to_email in to_emails:
        try:
            # Création du message multipart
            msg = MIMEMultipart('mixed')
            
            # Ajout des en-têtes essentiels
            msg["From"] = f"{company} Via Klivar <{from_email}>"
            msg["To"] = to_email
            msg["Subject"] = title
            msg["Reply-To"] = from_email
            msg["Message-ID"] = f"<{uuid.uuid4()}@klivar>"
            msg["List-Unsubscribe"] = f"<mailto:{from_email}?subject=unsubscribe>"
            
            # Création d'une partie alternative pour le HTML et le texte
            alt_part = MIMEMultipart('alternative')
            
            # Toujours attacher une version texte (important pour éviter le spam)
            alt_part.attach(MIMEText(text_content, 'plain'))
            
            # Attacher la version HTML si disponible
            if html_content:
                alt_part.attach(MIMEText(html_content, 'html'))
            
            # Attacher la partie alternative au message principal
            msg.attach(alt_part)
            
            # Ajout des pièces jointes standard
            if files:
                for file_path in files:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            # Détecter le type MIME en fonction de l'extension
                            file_name = os.path.basename(file_path)
                            file_ext = os.path.splitext(file_name)[1].lower()
                            
                            # Déterminer le type MIME basé sur l'extension
                            mime_type = "application/octet-stream"
                            if file_ext in ['.pdf']:
                                mime_type = "application/pdf"
                            elif file_ext in ['.jpg', '.jpeg']:
                                mime_type = "image/jpeg"
                            elif file_ext in ['.png']:
                                mime_type = "image/png"
                            elif file_ext in ['.doc', '.docx']:
                                mime_type = "application/msword"
                            elif file_ext in ['.xls', '.xlsx']:
                                mime_type = "application/vnd.ms-excel"
                            
                            # Créer la pièce jointe avec le bon type MIME
                            part = MIMEBase(*mime_type.split('/'))
                            part.set_payload(attachment.read())
                            
                            # Encoder la pièce jointe
                            encoders.encode_base64(part)
                            
                            # Ajouter l'en-tête pour la pièce jointe
                            part.add_header('Content-Disposition', 'attachment', filename=file_name)
                            
                            # Ajouter la pièce jointe au message
                            msg.attach(part)
            
            # Ajout de la pièce jointe ICS
            with open(filename, "rb") as attachment:
                # Pour les fichiers ICS, utiliser le type MIME approprié
                part = MIMEBase("text", "calendar", method="REQUEST")
                part.set_payload(attachment.read())
                
                # Encoder la pièce jointe
                encoders.encode_base64(part)
                
                # Ajouter l'en-tête pour la pièce jointe ICS
                file_name = os.path.basename(filename)
                part.add_header('Content-Disposition', 'attachment', filename=file_name)
                
                # Ajouter la pièce jointe ICS au message
                msg.attach(part)
            
            # Conversion en chaîne de caractères
            text = msg.as_string()
            
            # Envoi du message
            with smtplib.SMTP_SSL(EMAIL_HOST, 465, context=context) as server:
                server.login(from_email, EMAIL_HOST_PASSWORD)
                server.sendmail(from_email, to_email, text)
                
        except Exception as e:
            print(f"Erreur lors de l'envoi à {to_email}: {str(e)}")
            success = False
    
    # Supprimer le fichier ICS après envoi
    try:
        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        print(f"Erreur lors de la suppression du fichier ICS: {str(e)}")
    
    return success


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

def end_date(begin, duration):
    """This function return end time for activity"""

    res = duration.split(":")
    # hours=res[0], minutes=res[1], seconds=0
    time_end = begin + \
        timedelta(hours=int(res[0]), minutes=int(res[1]), seconds=0)
    return time_end

def start_date_test(in_date, time):
    """This function return start time for activity"""
    # import datetime

    # 2022-12-09T14:43:33+01:00

    dateee = "2022-12-09 14:43:33"
    """in_date = in_date.replace("T", " ")"""

    res = in_date.split("T")
    in_date = res[0]

    date = datetime.strptime(in_date, "%Y-%m-%d")

    date = repr(date)

    time = datetime.strptime(time, "%H:%M:%S")
    time = repr(time)

    # begin = datetime.datetime.combine(datetime.date(2011, 1, 1), datetime.time(10, 23))
    begin = datetime.datetime.combine(datetime.date(date), datetime.time(time))

    return begin


def getfiles(url):

    # url = "https://www.shellhacks.com/file.pdf"

    filename = url.rsplit('/', 1)[-1]
    dirpath = uuid.uuid4().hex[:6].lower()
    save_as = "media/"+dirpath
    print('=====')
    if not os.path.exists(save_as):
        os.makedirs(save_as)

    save_as = save_as + "/" + filename

    # Download from URL
    with urlopen(url) as file:
        content = file.read()
    print('=====13')
    # Save to file
    with open(save_as, 'wb') as download:
        download.write(content)

    """import urllib.request
    urllib.request.urlretrieve(url, save_as)"""

    return dirpath, save_as


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

    # # begin = datetime(2022,12,9,16,0,0)
    # # begin = datetime(begin_str)
    # end = end_date(begin, duration)
    # # end = datetime(2022,12,10,8,0,0)

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


def generate_dates(start_date, recurrence):
    """
    Generate dates based on recurrence.
    
    Args:
    - start_date (str): Start date in the format 'DD/MM/YYYY'.
    - recurrence (dict): Recurrence information containing 'key' and 'label'.
    
    Returns:
    - list of str: List of generated dates with time.
    """
    if recurrence['key'] == 'UNE_SEULE_FOIS':
        return [start_date + " 13:15:00"]
    elif recurrence['key'] == 'A_CHAQUE_JOUR':
        current_date = datetime.strptime(start_date, '%d/%m/%Y')
        dates = [start_date + " 06:30:00"]
        while True:
            current_date += timedelta(days=1)
            dates.append(current_date.strftime('%d/%m/%Y') + " 06:30:00")
            if current_date.year > datetime.now().year + 1:
                break
        return dates
    elif recurrence['key'] == 'UNE_SEULS_FOIS_PAR_SEMAINE':
        current_date = datetime.strptime(start_date, '%d/%m/%Y')
        target_weekday = current_date.weekday()
        while current_date.weekday() != target_weekday:
            current_date += timedelta(days=1)
        dates = [current_date.strftime('%d/%m/%Y') + " 06:30:00"]
        while True:
            current_date += timedelta(days=7)
            dates.append(current_date.strftime('%d/%m/%Y') + " 06:30:00")
            if current_date.year > datetime.now().year + 1:
                break
        return dates
    elif recurrence['key'] == 'UNE_SEULS_FOIS_PAR_MOIS':
        current_date = datetime.strptime(start_date, '%d/%m/%Y')
        dates = [start_date + " 06:30:00"]
        while True:
            current_date = current_date.replace(day=1)
            current_date += timedelta(days=32)
            current_date = current_date.replace(day=1)
            if current_date.month == 2 and current_date.day > 28:
                current_date = current_date.replace(day=28)
            dates.append(current_date.strftime('%d/%m/%Y') + " 06:30:00")
            if current_date.year > datetime.now().year + 1:
                break
        return dates
    elif recurrence['key'] == 'UNE_SEULE_FOIS_PAR_AN':
        current_date = datetime.strptime(start_date, '%d/%m/%Y')
        dates = [start_date + " 06:30:00"]
        while True:
            current_date = current_date.replace(year=current_date.year + 1)
            dates.append(current_date.strftime('%d/%m/%Y') + " 06:30:00")
            if current_date.year > datetime.now().year + 1:
                break
        return dates
    elif recurrence['key'] == 'UNE_SEULE_FOIS_PAR_JOUR':
        return [start_date + " 06:30:00"]
    else:
        return []
 

def add_calendar_with_multiple_date(events):
    """
    Add events to an iCalendar (.ics) file and return the filename.
    
    Args:
    - events (list of dict): List of events. Each event should be a dictionary containing:
        - title (str): Title of the event.
        - description (str): Description of the event.
        - date_begin (str): Start date and time in the format 'DD/MM/YYYY HH:MM'.
        - date_end (str): End date and time in the format 'DD/MM/YYYY HH:MM'.
        - company (str): Name of the company/organizer.
    
    Returns:
    - str: Filename of the generated iCalendar (.ics) file.
    """
    cal = Calendar() 

    for event_data in events:
        event = Event()
        event.add('summary', event_data['title'])
        event.add('description', event_data['description'])

        # Parse dates
        begin_date_time = datetime.strptime(event_data['date_begin'], '%d/%m/%Y %H:%M:%S')
        end_date_time = datetime.strptime(event_data['date_end'], '%d/%m/%Y %H:%M:%S')

        event.add('dtstart', begin_date_time)
        event.add('dtend', end_date_time)

        # Generate a unique ID for the event
        event['uid'] = secrets.token_urlsafe(8) + '@klivar.com'
        
        # Set organizer information
        organizer = vCalAddress('MAILTO:' +  event_data['organizer'])
        organizer.params['cn'] = vText(event_data['company'])
        organizer.params['role'] = vText(event_data['role'])
        event['organizer'] = organizer
        cal.add_component(event)

    # Create directory for saving the calendar file
    dirpath = uuid.uuid4().hex[:4].lower()
    save_as = "media/calendar/" + dirpath
    if not os.path.exists(save_as):
        os.makedirs(save_as)
    # Write the calendar data to the file
    filename = save_as + "/" + 'icalendar.ics'
    if os.path.exists(filename):
        os.remove(filename)
    f = open(filename, 'wb')
    f.write(cal.to_ical())
    f.close() 
    return filename

 


def send_mail_with_files(to_emails, title, files, html_content, company, text_content=None):
    """
    Envoie un email avec des fichiers téléchargés depuis des URLs et d'autres pièces jointes optionnelles.
    
    Args:
        to_emails (list): Liste des adresses email des destinataires
        title (str): Sujet de l'email
        files (list): Liste des URLs ou chemins vers les fichiers à joindre
        html_content (str): Contenu en format HTML
        company (str): Nom de l'entreprise expéditrice
        text_content (str, optional): Contenu en format texte. Si non fourni, une version sera générée.
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """

    def is_url(string):
        """Vérifie si une chaîne est une URL valide"""
        try:
            result = urlparse(string)
            return all([result.scheme, result.netloc])
        except:
            return False

    def download_file_from_url(url, timeout=30):
        """
        Télécharge un fichier depuis une URL et retourne son contenu et nom
        
        Args:
            url (str): URL du fichier à télécharger
            timeout (int): Timeout en secondes pour la requête
            
        Returns:
            tuple: (content, filename) ou (None, None) en cas d'erreur
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=timeout, stream=True)
            response.raise_for_status()
            
            # Extraire le nom du fichier depuis l'URL ou les headers
            filename = None
            
            # D'abord essayer depuis Content-Disposition header
            if 'content-disposition' in response.headers:
                import re
                cd = response.headers['content-disposition']
                filename_match = re.findall('filename=(.+)', cd)
                if filename_match:
                    filename = filename_match[0].strip('"\'')
            
            # Sinon extraire depuis l'URL
            if not filename:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                
            # Si toujours pas de nom, utiliser un nom par défaut
            if not filename or filename == '':
                filename = f"attachment_{uuid.uuid4().hex[:8]}"
                
            # Lire le contenu
            content = response.content
            return content, filename
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors du téléchargement de {url}: {str(e)}")
            return None, None
        except Exception as e:
            print(f"Erreur inattendue lors du téléchargement de {url}: {str(e)}")
            return None, None

    def get_mime_type_from_filename(filename):
        """Détermine le type MIME basé sur l'extension du fichier"""
        file_ext = os.path.splitext(filename)[1].lower()
        
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo'
        }
        
        return mime_types.get(file_ext, 'application/octet-stream')

    # Fonction pour extraire du texte depuis le HTML si aucun texte n'est fourni
    def html_to_text(html):
        # Suppression basique des balises HTML
        text = re.sub('<.*?>', ' ', html)
        # Remplacement des entités HTML courantes
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        # Suppression des espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    from_email = settings.EMAIL_HOST_USER
    
    # Si aucun contenu texte n'est fourni, extraire du HTML
    if not text_content and html_content:
        text_content = html_to_text(html_content)
    elif not text_content:
        text_content = "Veuillez consulter la version HTML de cet email."
    
    # Préparation des variables pour la connexion SMTP
    EMAIL_HOST = settings.EMAIL_HOST
    EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
    
    # Création du contexte SSL pour une connexion sécurisée
    context = ssl.create_default_context() 
    success = True
    
    for to_email in to_emails:
        try:
            # Création du message multipart
            msg = MIMEMultipart('mixed') 
            # Ajout des en-têtes essentiels
            msg["From"] = f"{company} via Klivar <{from_email}>"
            msg["To"] = to_email
            msg["Subject"] = title
            msg["Reply-To"] = from_email
            msg["Message-ID"] = f"<{uuid.uuid4()}@klivar>"
            msg["List-Unsubscribe"] = f"<mailto:{from_email}?subject=unsubscribe>" 
            
            # Création d'une partie alternative pour le HTML et le texte
            alt_part = MIMEMultipart('alternative') 
            # Toujours attacher une version texte (important pour éviter le spam)
            alt_part.attach(MIMEText(text_content, 'plain')) 
            # Attacher la version HTML si disponible
            if html_content:
                alt_part.attach(MIMEText(html_content, 'html')) 
            # Attacher la partie alternative au message principal
            msg.attach(alt_part) 
            
            # Ajout des pièces jointes (URLs ou fichiers locaux)
            if files:
                for file_item in files:
                    try:
                        if is_url(file_item):
                            # C'est une URL, télécharger le fichier
                            print(f"Téléchargement du fichier depuis: {file_item}")
                            file_content, file_name = download_file_from_url(file_item)
                            
                            if file_content is None:
                                print(f"Impossible de télécharger {file_item}, ignoré.")
                                continue
                                
                            # Déterminer le type MIME
                            mime_type = get_mime_type_from_filename(file_name)
                            
                        else:
                            # C'est un chemin local, procéder comme avant
                            if not os.path.exists(file_item):
                                print(f"Fichier local {file_item} non trouvé, ignoré.")
                                continue
                                
                            with open(file_item, "rb") as attachment:
                                file_content = attachment.read()
                                file_name = os.path.basename(file_item)
                                mime_type = get_mime_type_from_filename(file_name)

                        # Créer la pièce jointe avec le bon type MIME
                        part = MIMEBase(*mime_type.split('/'))
                        part.set_payload(file_content)
                        
                        # Encoder la pièce jointe
                        encoders.encode_base64(part)
                        
                        # Ajouter l'en-tête pour la pièce jointe
                        part.add_header('Content-Disposition', 'attachment', filename=file_name)
                        
                        # Ajouter la pièce jointe au message
                        msg.attach(part)
                        print(f"Pièce jointe ajoutée: {file_name}")
                        
                    except Exception as e:
                        print(f"Erreur lors de l'ajout de la pièce jointe {file_item}: {str(e)}")
                        continue
            
            # Conversion en chaîne de caractères
            text = msg.as_string()
            
            # Envoi du message
            with smtplib.SMTP_SSL(EMAIL_HOST, 465, context=context) as server:
                server.login(from_email, EMAIL_HOST_PASSWORD)
                server.sendmail(from_email, to_email, text)
                print(f"Email envoyé avec succès à {to_email}")
                
        except Exception as e:
            print(f"Erreur lors de l'envoi à {to_email}: {str(e)}")
            success = False
            
    return success




from datetime import datetime

# ===== MÉTHODE SIMPLE (recommandée) =====
def get_formatted_date(language='fr'):
    now = datetime.now()
    
    if 'fr' in language:
        # Français : "lundi 11 août 2025 à 14:30"
        days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        
        day_name = days[now.weekday()]
        month_name = months[now.month - 1]
        return f"{day_name} {now.day} {month_name} {now.year} à {now.hour:02d}:{now.minute:02d}"
    
    else:
        # Anglais : "Monday, August 11, 2025 at 2:30 PM"
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        day_name = days[now.weekday()]
        month_name = months[now.month - 1]
        hour_12 = now.hour if now.hour <= 12 else now.hour - 12
        hour_12 = 12 if hour_12 == 0 else hour_12
        am_pm = 'AM' if now.hour < 12 else 'PM'
        return f"{day_name}, {month_name} {now.day}, {now.year} at {hour_12}:{now.minute:02d} {am_pm}"
    



def format_date_string_short(date_string, language='fr'):
    """
    Version courte sans le jour de la semaine
    
    Returns:
        str: Date formatée courte
            - FR: "11 août 2025"
            - EN: "August 11, 2025"
    """
    
    try:
        if 'fr' in language.lower():
            # Format français DD-MM-YYYY
            if '-' in date_string:
                dt = datetime.strptime(date_string, '%d-%m-%Y')
            elif '/' in date_string:
                dt = datetime.strptime(date_string, '%d/%m/%Y')
            else:
                raise ValueError("Format de date français non reconnu")
            
            months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                     'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
            
            month_name = months[dt.month - 1]
            return f"{dt.day} {month_name} {dt.year}"
        
        else:
            # Format anglais YYYY-MM-DD
            if '-' in date_string:
                dt = datetime.strptime(date_string, '%Y-%m-%d')
            elif '/' in date_string:
                dt = datetime.strptime(date_string, '%Y/%m/%d')
            else:
                raise ValueError("Format de date anglais non reconnu")
            
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
            
            month_name = months[dt.month - 1]
            return f"{month_name} {dt.day}, {dt.year}"
    
    except ValueError:
        return date_string



 
def get_lang_request(request):
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    # Déterminer la langue à utiliser
    if 'fr' in accept_language:
        selected_lang = 'fr-FR'
    elif 'en' in accept_language:
        selected_lang = 'en-US'
    else:
        # Langue par défaut
        selected_lang = 'fr-FR'
    return selected_lang
