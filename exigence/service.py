

import threading
from exigence.utils import send_mail_created

from django.template.loader import render_to_string


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


def exigence_responsable( object, description, dest_email, sender_name, dest_name, company, url, back_url=None ):
    # object and description
    path = "notification/tasks/new-email-responsable.html" 
    path_txt = "notification/tasks/new-email-responsable.txt" 
    context = {
        "sender_name":sender_name, 
        "dest_name": dest_name,
        "task_title": object, 
        "url": url,
        "description":description,
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
    x = threading.Thread(target= send_mail_created, args=([dest_email], object, text_content, html_content, company,))
    x.start() 
    
    return True


 