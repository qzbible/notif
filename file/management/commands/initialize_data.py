import os
from django.core.management.base import BaseCommand
 

from urllib.parse import urlparse
 
from django.db import connection

from file.models import File

class Command(BaseCommand):
    help = 'Initialize data in the database with images from a directory'
    def handle(self, *args, **options):
        # --------------------File——————————————————————————————
        self.stdout.write(self.style.WARNING('--------------------------------ICON——————————————————————————————'))  
        File.initialize_data(directory_path='file/icons_mail', destination='icons' )
        self.stdout.write(self.style.SUCCESS('Data initialized successfully icons '))

        




