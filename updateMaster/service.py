

from django.template.loader import render_to_string
from service.utils import send_mail_created, send_mail_with_files 
 
#  Exigence data start 2025-06-16
def send_bug_mail( to_emails, object, fichiers_urls, description, name, module, status,company=None, back_url=None, lang=None ):
    # object and description

    if lang == "fr-FR" :
        path = "client/update_master/bug_assign/assign_fr.html" 
        path_txt = "client/update_master/bug_assign/assign_fr.txt" 
    elif lang == "en-US":
        path = "client/update_master/bug_assign/assign_en.html"
        path_txt = "client/update_master/bug_assign/assign_en.txt"
    else:
        path = "client/update_master/bug_assign/assign_fr.html" 
        path_txt = "client/update_master/bug_assign/assign_fr.txt"  
    context = {
        "name":name, 
        "description": description,
        "module": module, 
        "status": status, 
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
    try:
        resultat = send_mail_with_files(
            to_emails=to_emails,
            title=object,
            files=fichiers_urls,
            html_content=body_content,
            company=company,
            text_content=text_content
            )
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
     
    return True


def send_resolve_mail( to_emails, object, old_date, module, company=None, back_url=None, lang=None ):
    # object and description
    if lang == "fr-FR" :
        path = "client/update_master/bug_resolve/resolve_fr.html" 
        path_txt = "client/update_master/bug_resolve/resolve_fr.txt" 
    elif lang == "en-US":
        path = "client/update_master/bug_resolve/resolve_en.html"
        path_txt = "client/update_master/bug_resolve/resolve_en.txt"
    else:
        path = "client/update_master/bug_resolve/resolve_fr.html" 
        path_txt = "client/update_master/bug_resolve/resolve_fr.txt" 
    context = {
        "module":module, 
        "old_date": old_date, 
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
    try:
        resultat = send_mail_created(
            to_emails=to_emails,
            title=object,
            text_content=text_content,
            html_content=body_content, 
            company=company
            )
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
     
    return True