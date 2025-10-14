import random
 
# from exigence.utils import send_mail_created
from authClient.models import ClientAuthMail, EmailVerification, authCodeClient
from authClient.serializers import  ClientAuthMailSerializer, MailVerificationSendSerializer, frogetPwdSerializer
from authClient.service import  mail_forgrt_service, mail_welcome_service
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
 
from rest_framework.permissions import IsAuthenticated
from collections import OrderedDict
 
import json
 
from rest_framework.views import APIView
import uuid
from datetime import datetime, timedelta
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
import shutil
 
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from django.template.loader import render_to_string

from django.utils import timezone

from service.utils import get_formatted_date, get_lang_request, send_mail_created
# Create your views here.


# Vue API
class welcomeMailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=ClientAuthMailSerializer,
        responses={
            201: ClientAuthMailSerializer,
            400: ClientAuthMailSerializer,
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[
                OpenApiExample(
                    'Exemple de requête valide',
                value={
                    'email': 'client@example.com',
                    'name': 'Jean Dupont',
                    'url_connect': 'https://auth.example.com/connect',
                    'url_verification': 'https://auth.example.com/connect',
                    'base_url': 'https://api.example.com',
                 
                    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
                    'client_id': 'client_12345',
                    'company' :"",
                    'surfix' :"",
                    'lang' :"Fr-fr",
                    'is_send': False
                },
                    request_only=True,
                ),
                OpenApiExample(
                    'Réponse de succès',
                    value={
                        'message': 'Mail créée avec succès',
                        'status': 'success',
                        'code': 201
                    },
                    response_only=True,
                    status_codes=['201'],
                ),
            ],
            description="",
            summary="Créer une auth code auth",
            tags=["Authentification Client"],
        )
    
    def post(self, request):
        """
            Envoie un code d'authentification à 2 facteurs par email
        """
        try:  
            auth_header = request.headers.get('Authorization')
            token = ""
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Enlever le préfixe 'Bearer '
            data = request.data
            # Générer le code de vérification 
            custom_ins = ClientAuthMail.objects.create(
                token=token,
                email = data.get('email', None),
                name = data.get('name', None),
                url_connect = data.get('url_connect', None),
                url_verification = data.get('url_verification', None),
                base_url = data.get('base_url', None),
                # url_auth_code = data.get('url_auth_code', None),
                client_id = data.get('client_id', None),
                lang = data.get('lang', None),
                company = data.get('company', None),
                surfix = data.get("surfix", None)
                )
            mail_welcome_service( 
                name = data.get('name', 'Client'),
                dest_email = data.get('email', None),
                company = data.get('company', 'klivar'),
                url=data.get('url_verification', None) + str(token) ,
                back_url=data.get('base_url', None),
                lang=data.get('lang', None)
            )
            # Inclure le token JWT dans la réponse si récupéré
            response_data = {
                "message": "your request was do successfully",
                "status": "success", 
                "code": status.HTTP_200_OK,
            } 
            return Response(response_data, status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors de l'envoi du code d'authentification",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# Vue API
class sendAuthClientCodeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
       
       tags=["Authentification Client"],
    )
    
    def get(self, request):
        """
        Envoie un code d'authentification à 2 facteurs par email
        """
        try:  
            auth_header = request.headers.get('Authorization')
            token = None
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Enlever le préfixe 'Bearer '
             
            # Générer le code de vérification
            verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            expires_at =  timezone.now() + timezone.timedelta(minutes=3)
            custom_ins = ClientAuthMail.objects.all().filter(token=token).first()
            if custom_ins == None:
                return  Response({
                    "message": "Token not found",
                    "status": "error", 
                    "code": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND
            )
            nbr = (
                authCodeClient.objects.all()
                .filter(
                    token=token,
                )
                .count()
            ) 
            current_datetime = datetime.now()
            current_datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            if nbr == 0:  
                auth_code_instance = authCodeClient.objects.create(
                    code=verification_code, 
                    token=token, 
                    expires_at=expires_at
                )
                if custom_ins !=None and custom_ins.lang == "fr-FR":
                    path = "user-management/2fa_auth/2FA-auth-fr.html"
                    object = "Code d'authentification" + "[" + get_formatted_date(custom_ins.lang)  + "]"
                elif custom_ins !=None and custom_ins.lang == "en-US":
                    path = "user-management/2fa_auth/2FA-auth-en.html"
                    object = "Authentication code" + "[" + get_formatted_date(custom_ins.lang)   + "]"
                else:
                    path = "user-management/2fa_auth/2FA-auth-fr.html"
                    object = "Code d'authentification" + "[" + get_formatted_date(custom_ins.lang)   + "]"

                path_txt = "user-management/2fa_auth/2FA-auth.txt"
                
                context = {  
                    "user_name": '',
                    "code_auth": auth_code_instance.code,
                    "company": custom_ins.company,
                    "name" : custom_ins.name,
                    "back_url" :  "https://dev-backend.app.klivar.com/"
                } 
                html_content = render_to_string(path, context)
                text_content = render_to_string(path_txt, context)  
                send_mail_created(
                    [custom_ins.email], 
                    object, 
                    text_content, 
                    html_content,
                    custom_ins.company
                )
            else: 
                auth_code_instance = authCodeClient.objects.get(token=token)
                auth_code_instance.code = verification_code
                auth_code_instance.expires_at = expires_at
                auth_code_instance.save() 
                
                if custom_ins !=None and custom_ins.lang == "fr-FR":
                    path = "user-management/2fa_auth/2FA-auth-fr.html"
                    object = "Code d'authentification" + "[" + get_formatted_date(custom_ins.lang)   + "]"
                elif custom_ins !=None and custom_ins.lang == "en-US":
                    path = "user-management/2fa_auth/2FA-auth-en.html"
                    object = "Authentication code" + "[" + get_formatted_date(custom_ins.lang)   + "]"

                else:
                    path = "user-management/2fa_auth/2FA-auth-fr.html"
                    object = "Code d'authentification" + "[" + get_formatted_date(custom_ins.lang)   + "]"

                path_txt = "user-management/2fa_auth/2FA-auth.txt" 

                context = {  
                    "user_name": "",
                    "code_auth": verification_code,
                    "company": custom_ins.company,
                    "name" : custom_ins.name,
                    "back_url" :  "https://dev-backend.app.klivar.com/"
                } 
                
                html_content = render_to_string(path, context)
                text_content = render_to_string(path_txt, context) 
                
                custom_ins = ClientAuthMail.objects.all().filter(token=token).first()
                send_mail_created(
                    [custom_ins.email], 
                    object, 
                    text_content, 
                    html_content,
                    custom_ins.company
                ) 
            # Inclure le token JWT dans la réponse si récupéré
            response_data = {
                "message": "your request was do successfully",
                "status": "success", 
                "code": status.HTTP_200_OK,
            } 
            return Response(response_data, status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors de l'envoi du code d'authentification",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# Vue API
class ValidateAuthCodeView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
       tags=["Authentification Client"],
    )
    def post(self, request):
        """
        Valide un code d'authentification à 2 facteurs
        """
        try:  
            auth_header = request.headers.get('Authorization')
            token = None
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]  
            data = request.data
            try:
                auth_code_instance = authCodeClient.objects.get(token=token, code=data['code'])
            except authCodeClient.DoesNotExist:
                return Response(
                    {
                        "message": "Code d'authentification invalide",
                        "status": "error",
                        "code": status.HTTP_404_NOT_FOUND,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                ) 
            # Vérification de l'expiration
            now = timezone.now() 
            if auth_code_instance.expires_at < now:
                auth_code_instance.delete()
                return Response(
                    {
                        "message": "Le code d'authentification a expiré",
                        "status": "error",
                        "code": status.HTTP_408_REQUEST_TIMEOUT,
                    },
                    status=status.HTTP_408_REQUEST_TIMEOUT,
                )
            # Suppression du code d'authentification après utilisation
            auth_code_instance.delete()
            instance = ClientAuthMail.objects.get(token=token) 
            return Response( 
                {
                    "path":instance.url_connect, 
                },
                status=status.HTTP_200_OK
            )   
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors de la validation du code",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

    
class MailVerificationView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
       tags=["Mail verification"],
    )

    def post(self, request):
        """
        Envoie un code d'authentification à 2 facteurs par email
        """
        try:  
            data = request.data
            # Générer le code de vérification
            verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            expires_at =  timezone.now() + timezone.timedelta(minutes=3)
            custom_ins, _ = EmailVerification.objects.get_or_create(email=data.get('email', None))
            custom_ins.code = verification_code
            custom_ins.expires_at = expires_at
            custom_ins.save()
            lang = get_lang_request(request)
            current_datetime = datetime.now()
            current_datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

            if lang !=None and  lang == "fr-FR":
                path = "user-management/2fa_auth/2FA-auth-fr.html"
                object = "Code d'authentification" + "[" + get_formatted_date(lang)   + "]"
            elif lang !=None and  lang == "en-US":
                path = "user-management/2fa_auth/2FA-auth-en.html"
                object = "Authentication code" + "[" + get_formatted_date(lang)   + "]"
            else:
                path = "user-management/2fa_auth/2FA-auth-fr.html"
                object = "Code d'authentification" + "[" + get_formatted_date(lang)   + "]"

            path_txt = "user-management/2fa_auth/2FA-auth.txt"
            
            context = {  
                "user_name": '',
                "code_auth": verification_code,
                "company": "klivar",
                "name" : "",
                "back_url" :  "https://dev-backend.app.klivar.com/"
            } 
            html_content = render_to_string(path, context)
            text_content = render_to_string(path_txt, context)  
            send_mail_created(
                [data.get('email', None)], 
                object, 
                text_content, 
                html_content,
                "klivar"
            )
            # Inclure le token JWT dans la réponse si récupéré
            response_data = {
                "message": "your request was do successfully",
                "status": "success", 
                "code": status.HTTP_200_OK,
            } 
            return Response(response_data, status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors de l'envoi du code d'authentification",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
      
# Vue API
class MailCodeValidationView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        examples=[
        OpenApiExample(
            'Exemple de requête valide',
        value={
            'email': 'client@example.com'
        },
            request_only=True,
        ),
        OpenApiExample(
            'Réponse de succès',
            value={
                'message': 'Mail créée avec succès',
                'status': 'success',
                'code': 201
            },
            response_only=True,
            status_codes=['201'],
        ),
    ],
       tags=["Mail verification"],
    )
    def post(self, request):
        """
        Valide un code d'authentification à 2 facteurs
        """
        try:  
            
            data = request.data
            try:
                auth_code_instance = EmailVerification.objects.get(email=data.get("email", None), code=data['code'])
            except EmailVerification.DoesNotExist:
                return Response(
                    {
                        "message": "Code d'authentification invalide",
                        "status": "error",
                        "code": status.HTTP_404_NOT_FOUND,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                ) 
            # Vérification de l'expiration
            now = timezone.now() 
            if auth_code_instance.expires_at < now:
                auth_code_instance.delete()
                return Response(
                    {
                        "message": "Le code d'authentification a expiré",
                        "status": "error",
                        "code": status.HTTP_408_REQUEST_TIMEOUT,
                    },
                    status=status.HTTP_408_REQUEST_TIMEOUT,
                )
            # Suppression du code d'authentification après utilisation
            auth_code_instance.delete()
            return Response(   status=status.HTTP_200_OK )   
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors de la validation du code",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
      

class MailResetPassword(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        examples=[
        OpenApiExample(
            'Exemple de requête valide',
        value={
            'email': 'client@example.com'
        },
            request_only=True,
        ),
        OpenApiExample(
            'Réponse de succès',
            value={
                'message': 'Mail créée avec succès',
                'status': 'success',
                'code': 201
            },
            response_only=True,
            status_codes=['201'],
        ),
    ],
       tags=["Mail verification"],
    )
    def post(self, request):
        """
        Valide un code d'authentification à 2 facteurs
        """
        try:  
            
            data = request.data
            try:
                auth_code_instance = EmailVerification.objects.get(email=data.get("email", None), code=data['code'])
            except EmailVerification.DoesNotExist:
                return Response(
                    {
                        "message": "Code d'authentification invalide",
                        "status": "error",
                        "code": status.HTTP_404_NOT_FOUND,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                ) 
            # Vérification de l'expiration
            now = timezone.now() 
            if auth_code_instance.expires_at < now:
                auth_code_instance.delete()
                return Response(
                    {
                        "message": "Le code d'authentification a expiré",
                        "status": "error",
                        "code": status.HTTP_408_REQUEST_TIMEOUT,
                    },
                    status=status.HTTP_408_REQUEST_TIMEOUT,
                )
            # Suppression du code d'authentification après utilisation
            auth_code_instance.delete()
            return Response(   status=status.HTTP_200_OK )   
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors de la validation du code",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

# Vue API
class changePwdMailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=frogetPwdSerializer,
        responses={
            201: frogetPwdSerializer,
            400: ClientAuthMailSerializer,
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[
                OpenApiExample(
                    'Exemple de requête valide',
                value={
                    'email': 'client@example.com', 
                    'name': 'samuel', 
                    'url': 'https://auth.example.com/connect',
                    "lang":"fr-FR",
                    "token":"yuyuehiqsuiuhqoihcisbqbsd",
                    "company":""
                },
                    request_only=True,
                ),
                OpenApiExample(
                    'Réponse de succès',
                    value={
                        'message': 'Mail créée avec succès',
                        'status': 'success',
                        'code': 201
                    },
                    response_only=True,
                    status_codes=['201'],
                ),
            ],
            description="",
            summary="Créer une auth code auth",
            tags=["Froget pwd Client"],
        )
    
    def post(self, request):
        """
            Envoie un code d'authentification à 2 facteurs par email
        """
        try:  
            auth_header = request.headers.get('Authorization')
            token = ""
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Enlever le préfixe 'Bearer '
            print("token",token )
            data = request.data
            custom_ins = ClientAuthMail.objects.create(
                token=token,
                email = data.get('email', None),
                name = data.get('name', None),
                url_connect = data.get('url', None),
                url_verification = data.get('url_verification', None),
                base_url = data.get('base_url', None),
                # url_auth_code = data.get('url_auth_code', None),
                client_id = data.get('client_id', None),
                lang = data.get('lang', None),
                company = data.get('company', None),
                surfix = data.get("surfix", None)
                )
            mail_forgrt_service( 
                name = data.get('name', 'Client'),
                dest_email = data.get('email', None),
                company = data.get('company', 'klivar'),
                url=data.get('url', None) ,
                back_url=data.get('base_url', None),
                lang=data.get('lang', None)
            )
            # Inclure le token JWT dans la réponse si récupéré
            response_data = {
                "message": "your request was do successfully",
                "status": "success", 
                "code": status.HTTP_200_OK,
            } 
            return Response(response_data, status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors de l'envoi du code d'authentification",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
 