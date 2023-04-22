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

from celery import app, Celery
from celery import shared_task

from datetime import datetime, timedelta

from urllib.request import urlopen
import uuid

from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime
import secrets

app = Celery('send_mail', broker='pyamqp://root@localhost//')

@shared_task
def send_mail(to_emails, title, text_content, html_content, company):
    """Docstring for send_mail."""
    from_email = settings.EMAIL_HOST_USER
    for to_email in to_emails:
        print("***** ",to_email)
        msg = EmailMultiAlternatives(
            title,
            text_content,
            company+' Via Klivar <'+ from_email +'>',
            [to_email],
            reply_to=None,
        )
        if html_content:
            msg.attach_alternative(html_content, 'text/html')

        msg.send()
    return True


def send_mail_test(to_emails, title, text_content, html_content, filename):
    """Docstring for send_mail."""
    from_email = settings.EMAIL_HOST_USER

    for to_email in to_emails:
        
        msg = EmailMultiAlternatives(
            title,
            text_content,
            'Klivar App No Replay <'+ from_email +'>',
            [to_email],
            reply_to=None,
        )
        if html_content:
            msg.attach_alternative(html_content, 'text/html')
            #msg.attach(filename, 'text/*')
            # msg.attach(filename, "text/calendar; method=REQUEST; charset=\"UTF-8\"")
            msg.attach(filename, "text/calendar; method=REQUEST; charset=\"UTF-8\"")
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
            company + ' Via Klivar <'+ from_email +'>',
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

def send_mail_with_ics(to_emails, title, text_content, html_content, filename, company):
    """Docstring for send_mail."""
    
    from_email = settings.EMAIL_HOST_USER

    for to_email in to_emails:
        
        # Create a multipart message and set headers
        msg = MIMEMultipart()
        # message = EmailMultiAlternatives()
        msg["From"] = company +' Via Klivar <'+ from_email +'>'
        msg["To"] = to_email
        msg["Subject"] = title
        if html_content:
            # msg.attach_alternative(html_content, 'text/html')
            msg.attach(MIMEText(html_content, "html"))
            msg.attach(MIMEText("", "plain"))
            if os.path.exists(filename):
                with open(filename, "rb") as attachment:
                    # Add file as application/octet-stream
                    # Email client can usually download this automatically as attachment
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                # Encode file in ASCII characters to send by email
                encoders.encode_base64(part)

                # Add header as key/value pair to attachment part
                file_name = filename.rsplit('/', 1)[-1]
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {file_name}",
                )

                msg.attach(part)

                text = msg.as_string()
                # Log in to server using secure context and send email
                context = ssl.create_default_context()
                # server smtp and port
                EMAIL_HOST = settings.EMAIL_HOST
                EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
                with smtplib.SMTP_SSL(EMAIL_HOST, context=context) as server:
                    server.login(from_email, EMAIL_HOST_PASSWORD)
                    server.sendmail(from_email, to_email, text)
            else:
                return False
    os.remove(filename)
    return True

def send_mail_with_ics_file(to_emails, title, files, html_content, filename, company):
    """Docstring for send_mail."""
    
    from_email = settings.EMAIL_HOST_USER

    for to_email in to_emails:
        
        # Create a multipart message and set headers
        msg = MIMEMultipart()
        # message = EmailMultiAlternatives()
        msg["From"] = company +' Via Klivar <'+ from_email +'>'
        msg["To"] = to_email
        msg["Subject"] = title

        if html_content:
            # msg.attach_alternative(html_content, 'text/html')
            msg.attach(MIMEText(html_content, "html"))
            msg.attach(MIMEText("", "plain"))
            # print("ffffff44fff1-------------",os.listdir("/app/media"))
            # print("ffffff44fff1-------------",os.listdir("/app/media/calendar"))
            if files:
                for file in files:
                    
                    with open(file, "rb") as attachment:
                        # Add file as application/octet-stream
                        # Email client can usually download this automatically as attachment
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                    # Encode file in ASCII characters to send by email
                    encoders.encode_base64(part)

                    # Add header as key/value pair to attachment part
                    """part.add_header(
                        "Content-Disposition",
                        f"attachment; file= {file}",
                    )"""
                    part.add_header('content-disposition', 'attachment', filename=file.split('/')[-1])
                    msg.attach(part)
                    text = msg.as_string()

                    # print(msg)

            if os.path.exists(filename):
                with open(filename, "rb") as attachment:
                    # Add file as application/octet-stream
                    # Email client can usually download this automatically as attachment
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                # Encode file in ASCII characters to send by email
                encoders.encode_base64(part)

                # Add header as key/value pair to attachment part
                file_name = filename.rsplit('/', 1)[-1]
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {file_name}",
                )

                msg.attach(part)

                text = msg.as_string()
                # Log in to server using secure context and send email
                context = ssl.create_default_context()
                # server smtp and port
                EMAIL_HOST = settings.EMAIL_HOST
                EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
                with smtplib.SMTP_SSL(EMAIL_HOST, context=context) as server:
                    server.login(from_email, EMAIL_HOST_PASSWORD)
                    server.sendmail(from_email, to_email, text)
            else:
                return False
    os.remove(filename)
    return True


def start_date(in_date, time):
    """This function return start time for activity"""

    # 2022-12-09T14:43:33+01:00

    res = in_date.split("T")
    date_out=res[0]
    date_out = date_out.replace("-", ",")
    # date_out = datetime.strptime(date_out, '%m-%d-%Y').date()
    # time = "14:30:00"
    time = time.replace(":", ",")

    date_out = date_out +'-'+ time
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
    time_end = begin + timedelta(hours=int(res[0]), minutes=int(res[1]),seconds=0)
    return time_end

def start_date_test(in_date, time):
    """This function return start time for activity"""
    # import datetime
    
    # 2022-12-09T14:43:33+01:00

    dateee = "2022-12-09 14:43:33"
    """in_date = in_date.replace("T", " ")"""

    res = in_date.split("T")
    in_date=res[0]

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

    if not os.path.exists(save_as):
        os.makedirs(save_as)

    save_as = save_as + "/" + filename

    # Download from URL
    with urlopen(url) as file:
        content = file.read()

    # Save to file
    with open(save_as, 'wb') as download:
        download.write(content)

    return dirpath, save_as


def add_calendar(title, description, date_begin, begin_hour, duration, company):
    event = Event()
    event.add('summary',title)
    event.add('description', description)

    # Variables attendues
    in_date = date_begin # La date
    time = begin_hour # Le debut
    duration = duration # La duree

    begin = start_date(in_date, time)
    # begin = datetime(2022,12,9,16,0,0)
    # begin = datetime(begin_str)
    end = end_date(begin, duration)
    # end = datetime(2022,12,10,8,0,0)
    
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

    return filename, end


