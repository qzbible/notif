import os
from urllib.parse import urlparse
from django.shortcuts import render

from file.models import File
from file.serializers import FileSerializer
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny  # ← Importer

from rest_framework import viewsets, status
 
from rest_framework.response import Response
# Create your views here.

class FileViewSet(viewsets.ModelViewSet):
    # Définit le modèle et le sérialiseur pour le ViewSet
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        # Configure la connexion avec la fonction set_connexion
        # File.objects.all().delete()
        # Récupère la requête)
        # Filtrer et récupérer le queryset
        queryset = self.filter_queryset(self.get_queryset()) 
        # Sérialise le queryset et retourne les données
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    # parser_classes = (MultiPartParser, FormParser)
 
 
    
     
    