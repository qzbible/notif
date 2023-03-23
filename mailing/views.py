from django.shortcuts import render
# Landry

from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from collections import OrderedDict

import json

# from .tasks import *

from django.template.loader import render_to_string
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django_celery_beat import querysets, validators
import uuid


class celeryViewSet(ViewSet):
    parser_classes = (MultiPartParser, JSONParser,)

    success = openapi.Schema(
        type=openapi.TYPE_OBJECT,
            properties=OrderedDict((
                ("message", openapi.Schema(type=openapi.TYPE_STRING,example = "your request was do successfully success")),
                ("status", openapi.Schema(type=openapi.TYPE_STRING,example = "success")),
                ("code", openapi.Schema(type=openapi.TYPE_INTEGER, example = status.HTTP_201_CREATED)),
            )),
            required=['results']
    )

    request_body = openapi.Schema(
        description="Cette partie decris le corp de l'API. il faut",
        type=openapi.TYPE_OBJECT,
            properties=OrderedDict((
                ("object", openapi.Schema(type=openapi.TYPE_STRING, example = "mail object (Demande de permission)")),
                ("message", openapi.Schema(type=openapi.TYPE_STRING, example = "Body of mail (your text)")),
                ("destinator", openapi.Schema(type=openapi.TYPE_STRING, example = "Emails adress of destinators",pattern=["loren@gmail.com","ipsum@klblogs.com"])),
                # ("unitime", openapi.Schema(type=openapi.TYPE_STRING,example = "minute (nimute, hour, day, week)")),
                ("start_time", openapi.Schema(type=openapi.FORMAT_DATETIME, example = ["2023-03-22T10:12:00+01:00","2023-03-22T10:13:00+01:00"])),
            )),
            required=['results']
    )

    bad_token = openapi.Schema(
        type=openapi.TYPE_OBJECT,
            properties=OrderedDict((
                ("message", openapi.Schema(type=openapi.TYPE_STRING,example = "Bad token or ...")),
                ("Gateway_code", openapi.Schema(type=openapi.TYPE_INTEGER, example = 401)),
            )),
            required=['results']
    )

    @swagger_auto_schema(
        operation_description="This API create celery task ",
        request_body=request_body,
        responses={
            status.HTTP_201_CREATED:success,
            401: bad_token ,
            400: 'Params error'
        }
    )
    def create(self, request):

        try:
            # list of dates
            start_times = request.data['start_time']
            one_off = True
            for start_time in start_times:
                # destinator = request.data['destinator'] # 'email1', email2
                object = request.data['object']
                message = request.data['message']
                # sch_time = request.data['schedul']
                destinator = request.data['destinator']
                # unitime = request.data['unitime']
                # unitime = unitime.upper()

                # one_off = request.data['one_off']

                # path = "mail/planification/celery2.html"
                path = "mail/accounts/create.html"
                # path = "mail/accounts/change_pass_word.html"
                # path = "mail/accounts/confirm_change_p_w.html"
                path_txt = "mail/planification/celery.txt"

                ctext = request.data['context']
                
                context = {
                    "title": ctext['title'],
                    "company": ctext['company'],
                    "site_url": ctext['site_url'],
                    "adress":ctext['adress'],
                    "code_postal":ctext['code_postal'],
                    "soret":ctext['soret'],
                    "numero_tva":ctext['numero_tva'],
                    "code_ape":ctext['code_ape'],
                    "effectif":ctext['effectif'],
                    "ville": ctext['ville'],
                    "pays": ctext['pays'],
                    "site_name": ctext['site_name'],

                }
                # context = {
                #     'company': 'OASIS CENTER',
                #     'site_url': 'klivar.com',
                #     'adress':message,
                #     'site_name': 'Klivar'
                # }
                
                
                html_content = render_to_string(
                    path,
                    context
                )
                
                text_content = render_to_string(
                    path_txt,
                    context
                )
                
                schedule, created = IntervalSchedule.objects.get_or_create(
                    every=30,
                    # period=unitime,
                    period=IntervalSchedule.SECONDS,
                )
                PeriodicTask.objects.update_or_create(
                    task="mailing.utils.send_mail",
                    # name="send_email",
                    name = uuid.uuid4().hex[:10].lower(),
                    args=json.dumps([destinator, object, text_content, html_content]),
                    
                    one_off = one_off,
                    start_time = start_time,
                    # last_run_at = "2023-02-28T11:19:00+01:00", + every= 1s ==> envoie le mail at 2023-02-28T11:20:00+01:00
                    # --> last_run_at = "2023-02-28T13:49:00+01:00",
                    # -->expires = "2023-02-28T21:46:00+01:00",
                    # --> total_run_count = 2,
                    # kwargs=json.dumps({
                    #    'be_careful': True,
                    #}),
                    defaults=dict(
                        interval=schedule,
                        expire_seconds=60,
                    ),
                )

            
            return Response(
                {
                    'message': 'New schedule is succefull run',
                    'status': 'success',
                    'code': status.HTTP_201_CREATED,
                },
                status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {
                    'message': 'Bad parameters',
                    'status': 'Failed',
                    'error': str(e),
                    'code': status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST)
            

    @swagger_auto_schema(
        operation_description="This API retieve specific celery task.",
        responses={
            # status.HTTP_200_OK:AnnouncementSerializer,
            status.HTTP_401_UNAUTHORIZED: 'Bad toke',
            status.HTTP_404_NOT_FOUND: 'slug not found',
        }
    )
    def retrieve(self, request, pk=None):
        # token = request.headers['Authorization']
        # id, code, shema = Histories().get_user_from_token(token)
        code = 200
        id = 2
        schema = 2
        if code == 200:
            queryset = PeriodicTask.objects.all()
            object = queryset.values()
            res = "This task no exists or has expired/ deleted"
            for item in object:
                if int(item["id"]) == int(pk):
                    res = item
            return Response(
                {
                    'message': 'Detail of Scheduler.',
                    'status': 'success',
                    'data': res,
                    'code': status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK)
        else:
            datas = {
                'message':'Bad token or ' + str(id)
            }
            return Response(datas, status=status.HTTP_401_UNAUTHORIZED)
        

    @swagger_auto_schema(
        operation_description="This API list celery task.",
        responses={
            # status.HTTP_200_OK:AnnouncementSerializer(many=True),
            status.HTTP_401_UNAUTHORIZED: 'Bad toke',
        }
    )
    def list(self, request):
        # queryset = Historique_anoModel.objects.all().filter(created_by = 1)

        # token = request.headers['Authorization']
        # id, code, shema = Histories().get_user_from_token(token)
        code = 200
        id = 2
        schema = 2
        if code == 200:
            queryset = PeriodicTask.objects.all()

            # print(queryset.values())
            return Response(
                {
                    'message': 'My Announcements.',
                    'status': 'success',
                    'data': queryset.values(),
                    'code': status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK)
        else:
            datas = {
                'message':'Bad token or ' + str(id)
            }
            return Response(datas, status=status.HTTP_401_UNAUTHORIZED)
        

