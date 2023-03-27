from celery import app, Celery
from celery import shared_task
from .utils import *
from django.template.loader import render_to_string
from django.conf import settings
from mailing.utils import *
from django.core.mail import EmailMessage

#  celery app
app = Celery('send_mail', broker='pyamqp://root@localhost//')

# @app.task(name="send_mail", bind=True, default_retry_delay=30, max_retries=3)


@shared_task
# def send_mail(object, message, destinator):
def send_mail():
    # email = EmailMessage(object, message, to=destinator)
    # email = EmailMessage('object du message', 'Un bon message comme ca', to=['engololandry@gmail.com','docem98802@rubeshi.com'])
    # email.send()
    to_email = ['ladopib907@vootin.com']
    title = "test template Klivar"
    # text_content = "test Un bon message comme ca"
    # s = str(settings.TEMPLATES[0]['DIRS'][0])
    path = "mail/planification/celery.html"
    # path = s +str(path)
    # print(settings.TEMPLATES[0]['DIRS'][0])
    # print(path)
    path_txt = "mail/planification/celery.txt"
    # path_txt =  s +str(path_txt)
    context = {
        'receiver': 'Prenom Nom',
        'site_url': 'klivar.com',
        'site_name': settings.APP_NAME
    }

    html_content = render_to_string(
        path,
        context
    )

    text_content = render_to_string(
        path_txt,
        context
    )

    # send_mail_test(to_email, title, text_content, html_content)
    from_email = settings.EMAIL_HOST_USER
    for email in to_email:
        msg = EmailMultiAlternatives(
            title,
            text_content,
            'Klivar App No Replay <' + from_email + '>',
            [email],
            reply_to=None,
        )
        if html_content:
            msg.attach_alternative(html_content, 'text/html')

        msg.send()
    return True
