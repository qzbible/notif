

import threading
from exigence.utils import send_mail_created, send_mail_with_ics

from django.template.loader import render_to_string
from datetime import datetime
from icalendar import Calendar, Event, vCalAddress, vText
import os
import uuid
import secrets
from django.conf import settings 

def exigence_approver(object, description, dest_email, sender_name, dest_name, company, url, back_url=None):
     
    path = "notification/tasks/new-email-approbateur.html" 
    path_txt = "notification/tasks/new-email-approbateur.txt" 
    context = {
        "sender_name":sender_name, 
        "dest_name": dest_name,
        "task_title": object, 
        "url": url,
        "description":description,
        "back_url" :"https://dev-backend.app.klivar.com/" if back_url == None else back_url
    }
    header_path = "notification/tasks/header.html"
    header_content = render_to_string(
        header_path,
        context
    )
    footer_path = "notification/tasks/footer.html"
    footer_content = render_to_string(
        footer_path,
        context
    )
    body_content = render_to_string(
        path,
        context
    )
    html_content  = header_content + body_content + footer_content

    text_content = render_to_string(
            path_txt,
            context
    )
    # send_mail_created([dest_email], object, text_content, html_content, company)
    x = threading.Thread(target= send_mail_created, args=([dest_email], object, text_content, html_content, company,))
    x.start() 


def is_valid_date_string(date_string, format="%Y-%m-%dT%H:%M:%S.%fZ"):
    try:
        if date_string == "" or date_string == None:
            return False
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

def exigence_responsable( object, description, dest_email, sender_name, dest_name, company, url, scope=[], time="", deadline="", start_date="", back_url=None ):
    # object and description

    deadline_text = "non défini" 
    if is_valid_date_string(deadline):
        parsed_date = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S.%fZ")
        deadline_text = parsed_date.strftime("%Y-%m-%d")

    filename = None

    if is_valid_date_string(start_date):
     
        date_begin = datetime.strptime(start_date + " " + time, "%Y-%m-%d %H:%M")
        date_end = date_begin + datetime.timedelta(minutes=int(time))
        
    
        # configuration iCalendar
        if company != None: 
            filename = add_calendar(
                    object, description, str(date_begin), str(date_end), company) # add_calendar(title, description, date_begin, date_end, company_denomination) construction du icalenda avec le nom de la compagnie
        else:
            filename = add_calendar(
                object, description, str(date_begin), str(date_end), "Klivar") # add_calendar(title, description, date_begin, date_end, company_denomination) construction du icalenda avec le nom de la compagnie
        

    path = "notification/evaluation/responsable.html" 
    path_txt = "notification/evaluation/responsable.txt" 
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
        "back_url" :  "https://dev-backend.app.klivar.com/" if back_url == None else back_url
    }
    header_path = "notification/tasks/header.html"
    header_content = render_to_string(
        header_path,
        context
    )
    footer_path = "notification/tasks/footer.html"
    footer_content = render_to_string(
        footer_path,
        context
    )
    body_content = render_to_string(
        path,
        context
    )
    html_content  = header_content + body_content + footer_content

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


 