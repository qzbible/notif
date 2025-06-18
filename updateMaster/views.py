from exigence.models import ExigenceMail
from exigence.serializers import ErrorResponseSerializer
from exigence.service import exigence_responsable
# from exigence.utils import send_mail_created

from rest_framework.response import Response
from datetime import datetime, timedelta
 
 
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample
 
from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import AllowAny


from celery import current_app
from service.utils import send_mail_with_files
from updateMaster.serializers import AssignBugSerializer, ResolveBugSerializer
from updateMaster.service import send_bug_mail, send_resolve_mail
from rest_framework import status

# Vue API
class AssignBugView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(  
        request=AssignBugSerializer,
        responses={
            201: AssignBugSerializer,
            400: ErrorResponseSerializer,
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        description=" ",
        summary="Créer une bug",
         examples=[
            OpenApiExample(
                'Exemple de requête valide',
                value={
                    'name': 'bug de test',
                    'description': 'bug de test',
                    'company': 'Test Company',
                    'module': '',
                    'fichiers_urls': ['image1.png', 'image2.png'],
                    'to_emails' : ["ex@gmail.com"],
                    'status': 'open',
                    'back_url': 'https://example.com',
                    'lang': 'fr-FR'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Exigence créée avec succès',
                    'status': 'success',
                    'code': 201
                },
                response_only=True,
                status_codes=['201'],
            ),
        ],
        tags=["bug"],
    )
    
    def post(self, request):
        """
        Valide un code d'authentification à 2 facteurs
        """
        serializer = AssignBugSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Erreur de validation des données",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # Récupération des données validées
        validated_data = serializer.validated_data  
        current_datetime = datetime.now()
        current_datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        # Envoyer l'email
        object =  "🚨 [URGENT] Incident sur le module "+ validated_data.get("name", '')
        lang = validated_data.get('lang', 'fr-FR')
        if lang != "fr-FR" :
            object = "🚨 [URGENT] Incident on module " + validated_data.get("name", '')
        url_file = []
        for file_url in validated_data.get('fichiers_urls', []): 
            url_file.append("https://dev-backend.app.klivar.com/media/" + file_url) 
        # Enregistrer l'email dans la base de données
        resultat = send_bug_mail(
            to_emails=validated_data.get('to_emails', []),
            object=object + " [" + current_datetime_string  + "]",
            fichiers_urls= url_file,
            description= validated_data.get('description', ''),
            name=validated_data.get('name', ''),
            module=validated_data.get('module', ''),
            status= validated_data.get('status', ''),
            company=validated_data.get('company', None),
            back_url= validated_data.get('back_url', None),
            lang=validated_data.get('lang', 'fr-FR')
        )

        if resultat:
            print("Tous les emails ont été envoyés avec succès!")
        else:
            print("Certains emails n'ont pas pu être envoyés.")
        # Récupérer l'ID de la tâche à annuler 
        return Response({
            'message': f'Tâche reprogrammer avec succès',
        })



# Vue API
class ResolveBugView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(  
        request=ResolveBugSerializer,
        responses={
            201: ResolveBugSerializer,
            400: ErrorResponseSerializer,
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        description=" ",
        summary="Créer une bug",
         examples=[
            OpenApiExample(
                'Exemple de requête valide',
                value={
                    'module': 'bug de test',
                    'old_date': 'bug de test',
                    'company': 'Test Company',
                    'to_emails': ["samy@exemple.com"],
                    'lang': 'fr-FR',
                    'back_url': 'https://dev-backend.app.klivar.com/'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Exigence créée avec succès',
                    'status': 'success',
                    'code': 201
                },
                response_only=True,
                status_codes=['201'],
            ),
        ],
        tags=["bug"],
    )
    
    def post(self, request):
        """
        Valide un code d'authentification à 2 facteurs
        """
        serializer = ResolveBugSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Erreur de validation des données",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # Récupération des données validées
        validated_data = serializer.validated_data 
        # Envoyer l'email
        object =  "Bug corrigé sur  " + validated_data.get("module", '')
        lang = validated_data.get('lang', 'fr-FR')
        if lang != "fr-FR" :
            object = "Bug fixed on  " + validated_data.get("module", '')

        resultat = send_resolve_mail(
            to_emails=validated_data.get('to_emails', []),
            object=object,
            old_date= validated_data.get('old_date', []), 
            module=validated_data.get('module', ''), 
            company=validated_data.get('company', None),
            back_url= validated_data.get('back_url', None),
            lang=validated_data.get('lang', 'fr-FR')
        )

        if resultat:
            print("Tous les emails ont été envoyés avec succès!")
        else:
            print("Certains emails n'ont pas pu être envoyés.")
        # Récupérer l'ID de la tâche à annuler 
        return Response({
            'message': f'Tâche reprogrammer avec succès',
        })

