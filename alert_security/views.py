from django.shortcuts import render
from alert_security.models import DeviseAuthMail, authCode
from alert_security.serializers import AlertSecurityMailSerializer
from alert_security.service import mail_new_devise_service
from external_service.call_api import validate_device_on_main_back
from rest_framework.permissions import AllowAny
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from django.utils import timezone
import random
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from service.utils import send_mail_created
# Create your views here.



# Vue API
class AlertSecurityMailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=AlertSecurityMailSerializer,
        responses={
            201: AlertSecurityMailSerializer,
            400: AlertSecurityMailSerializer,
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[
                OpenApiExample(
                    'Exemple de requête valide',
                value={
                    'email': 'client@example.com',
                    'device_name': 'Jean Dupont',
                    'os_name': 'Ziyouma',
                    'devise_type': 'Ziyouma',
                    'browser_name': 'Ziyouma',
                    'device_fingerprint': 'Ziyouma',
                    'name': 'Ziyouma',
                    'url_verification': 'https://auth.example.com/connect',
                    'url_verification': 'https://auth.example.com/connect',
                    'base_url': 'https://api.example.com',
                    'lang' :"Fr-fr" 
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
            tags=["Alert sécurity"],
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
            custom_ins = DeviseAuthMail.objects.create(
                token=token,
                email = data.get('email', None),
                device_name = data.get('device_name', None),
                device_type = data.get('device_type', None),
                os_name = data.get('os_name', None),
                browser_name = data.get('browser_name', None),
                device_fingerprint = data.get('device_fingerprint', None),
                url_connect = data.get('url_connect', None),
                url_verification = data.get('url_verification', None),
                base_url = data.get('base_url', None),
                # url_auth_code = data.get('url_auth_code', None),
                client_id = data.get('client_id', None),
                lang = data.get('lang', None),
                company = data.get('company', None),
                surfix = data.get("surfix", None),
                device_id = data.get('device_id', 0) 
                )
            
            mail_new_devise_service( 
                name = data.get('name', ''),
                dest_email = data.get('email', None),
                company = data.get('company', 'klivar'), 
                os_name= data.get('device_name', None),
                device_type = data.get('device_type', None),
                browser_name = data.get('browser_name', None),
                url_verification=data.get('url_verification', None) + str(token), 
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
class sendAuthCodeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
       
       tags=["Alert sécurity"],
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
            custom_ins = DeviseAuthMail.objects.all().filter(token=token).first()
            if custom_ins == None:
                return  Response({
                    "message": "Token not found",
                    "status": "error", 
                    "code": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND
            )
            nbr = (
                authCode.objects.all()
                .filter(
                    token=token,
                )
                .count()
            ) 
            current_datetime = datetime.now()
            current_datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            if nbr == 0:  
                auth_code_instance = authCode.objects.create(
                    code=verification_code, 
                    token=token, 
                    expires_at=expires_at
                )
                if custom_ins !=None and custom_ins.lang == "fr-FR":
                    path = "notification/2fa_auth/2FA-auth-fr.html"
                    object = "Code d'authentification" + "[" + current_datetime_string  + "]"
                elif custom_ins !=None and custom_ins.lang == "en-US":
                    path = "notification/2fa_auth/2FA-auth-en.html"
                    object = "Authentication code" + "[" + current_datetime_string  + "]"
                else:
                    path = "notification/2fa_auth/2FA-auth-fr.html"
                    object = "Code d'authentification" + "[" + current_datetime_string  + "]"

                path_txt = "notification/2fa_auth/2FA-auth.txt"
                
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
                auth_code_instance = authCode.objects.get(token=token)
                auth_code_instance.code = verification_code
                auth_code_instance.expires_at = expires_at
                auth_code_instance.save() 
                
                if custom_ins !=None and custom_ins.lang == "fr-FR":
                    path = "notification/2fa_auth/2FA-auth-fr.html"
                    object = "Code d'authentification" + "[" + current_datetime_string  + "]"
                elif custom_ins !=None and custom_ins.lang == "en-US":
                    path = "notification/2fa_auth/2FA-auth-en.html"
                    object = "Authentication code" + "[" + current_datetime_string  + "]"

                else:
                    path = "notification/2fa_auth/2FA-auth-fr.html"
                    object = "Code d'authentification" + "[" + current_datetime_string  + "]"

                path_txt = "notification/2fa_auth/2FA-auth.txt" 

                context = {  
                    "user_name": "",
                    "code_auth": verification_code,
                    "company": custom_ins.company,
                    "name" : custom_ins.name,
                    "back_url" :  "https://dev-backend.app.klivar.com/"
                } 
                
                html_content = render_to_string(path, context)
                text_content = render_to_string(path_txt, context) 
                
                custom_ins = DeviseAuthMail.objects.all().filter(token=token).first()
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
       tags=["Alert sécurity"],
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
                auth_code_instance = authCode.objects.get(token=token, code=data['code'])
            except authCode.DoesNotExist:
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
            instance = DeviseAuthMail.objects.get(token=token) 
            response = validate_device_on_main_back(instance.device_id, instance.token)
            # validate device .. 
            return Response( 
                {
                    "path":instance.url_connect, 
                },
                status=response.status_code
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
        



@api_view(["PUT"])
@permission_classes([AllowAny])
def validate_device(self, pk=None):
    try:
        response = validate_device_on_main_back(pk, "instance.token")
        return Response(status=response.status_code)
    except Exception as e:
        return Response( {"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

