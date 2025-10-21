from rest_framework import serializers

from datetime import datetime, timezone
class DecisionSerializer(serializers.Serializer):
    """Serializer pour la création et l'envoi des décisions du comité"""
    
    # Informations destinataire
    dest_email = serializers.EmailField(
        required=True,
        help_text="Adresse email du destinataire"
    )
    name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom du destinataire"
    )
    
    # Informations du comité
    committee_name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom du comité"
    )
    committee_date = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Date de la réunion du comité"
    )
    
    # Liste des décisions
    decisions_list = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=True,
        help_text="Liste des décisions prises"
    )
    
    # Informations de l'instance
    instance_name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom de l'instance"
    )
    instance_description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Description de l'instance"
    )
    
    # Détails de la réunion
    date_debut = serializers.CharField(
        required=True,
        max_length=100,
        help_text="Date de début (format: DD-MM-YYYY)"
    )
    date_fin = serializers.CharField(
        required=True,
        max_length=100,
        help_text="Date de fin (format: DD-MM-YYYY)"
    )
    lieu_reunion = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Lieu ou lien de réunion"
    )
    participants = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Liste des participants (séparés par des virgules)"
    )
    
    # Informations de connexion
    url_connect = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="URL de connexion"
    )
    
    # Informations entreprise
    company = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom de l'entreprise"
    )
    
    # URL de base
    base_url = serializers.URLField(
        required=True,
        help_text="URL de base du backend"
    )
    
    # Configuration
    client_id = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Identifiant unique du client"
    )
    lang = serializers.ChoiceField(
        choices=['fr-FR', 'en-US'],
        default='fr-FR',
        help_text="Langue de l'email (fr-FR ou en-US)"
    )
    
    def validate_decisions_list(self, value):
        """Valider que la liste des décisions n'est pas vide"""
        if not value or len(value) == 0:
            raise serializers.ValidationError("La liste des décisions ne peut pas être vide")
        return value
    
    def validate_dest_email(self, value):
        """Valider le format de l'email"""
        if not value:
            raise serializers.ValidationError("L'adresse email est requise")
        return value.lower()
    


class MeetingReminderSerializer(serializers.Serializer):
    """Serializer pour le rappel de réunion du comité"""
    
    # Informations destinataire
    dest_email = serializers.EmailField(
        required=True,
        help_text="Adresse email du destinataire"
    )
    name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom du destinataire"
    )
    
    # Informations de la réunion
    committee_name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom du comité"
    )
    date_reunion = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Date de la réunion"
    )
    heure_reunion = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Heure de la réunion"
    )
    lieu_reunion = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Lieu ou lien de réunion"
    )
    participants = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Liste des participants (séparés par des virgules)"
    )
    
    # Informations de l'instance
    instance_name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom de l'instance"
    )
    instance_description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Description de l'instance"
    )
    
    # Détails de l'instance
    date_debut = serializers.CharField(
        required=True,
        max_length=100,
        help_text="Date de début (format: DD-MM-YYYY)"
    )
    date_fin = serializers.CharField(
        required=True,
        max_length=100,
        help_text="Date de fin (format: DD-MM-YYYY)"
    )
    
    # URL et entreprise
    url_connect = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="URL pour accéder à la session"
    )
    company = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom de l'entreprise"
    )
    
    # URL de base
    base_url = serializers.URLField(
        required=True,
        help_text="URL de base du backend"
    )
    
    # Configuration
    client_id = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Identifiant unique du client"
    )
    lang = serializers.ChoiceField(
        choices=['fr-FR', 'en-US'],
        default='fr-FR',
        help_text="Langue de l'email (fr-FR ou en-US)"
    )
    
    def validate_dest_email(self, value):
        """Valider le format de l'email"""
        if not value:
            raise serializers.ValidationError("L'adresse email est requise")
        return value.lower()



class CommitteeCreatedSerializer(serializers.Serializer):
    """Serializer pour la notification de création de comité d'instance"""

    id_instance = serializers.CharField(
        required=True,
        max_length=255,
        help_text="id de l'instance"
    )
    # Informations du comité
    title = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Titre du comité"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Description du comité"
    ) 
    # URL et entreprise
    url_connect = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="URL de connexion pour accéder au comité"
    ) 
   
    # Configuration
    type = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Identifiant unique du client"
    )
    # 
    format = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Identifiant unique du client"
    )

    link = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Identifiant unique du client"
    )

    lang = serializers.ChoiceField(
        choices=['fr-FR', 'en-US'],
        default='fr-FR',
        help_text="Langue de l'email (fr-FR ou en-US)"
    )
    client = serializers.JSONField(
        required=False,
        help_text="Fichier JSON optionnel"
    )
    recurrence_config = serializers.JSONField(
        required=False,
        allow_null=True,
        help_text="Fichier JSON optionnel"
    )
    ponctuel_config = serializers.JSONField(
        required=False,
        allow_null=True,
        help_text="Fichier JSON optionnel"
    )
 
    actors = serializers.ListField(
        child=serializers.JSONField(),
        required=False,
        allow_null=True,
        help_text="Liste des participants au format JSON pour le modèle. Si non fourni, peut être dérivé de 'participants'."
    )
     
    
    
    def validate_dest_email(self, value):
        """Valider le format de l'email"""
        if not value:
            raise serializers.ValidationError("L'adresse email est requise")
        return value.lower()
    

class ArbitrageCreatedSerializer(serializers.Serializer):
    """Serializer pour la notification de création de dossier d'arbitrage"""
    
    # Informations destinataire
    dest_email = serializers.EmailField(
        required=True,
        help_text="Adresse email du destinataire"
    )
    name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom du destinataire"
    )
    
    # Informations du comité
    committee_name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom du comité"
    )
    committee_date = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Date de la réunion du comité"
    )
    
    # Éléments d'arbitrage
    nomber_elements = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="Nombre d'éléments à arbitrer"
    )
    type_arbitration_elements = serializers.CharField(
        required=True,
        max_length=500,
        help_text="Types d'éléments (ex: Risques, Exigences, Incidents, etc.)"
    )
    priorite_arbitrage = serializers.CharField(
        required=True,
        max_length=100,
        help_text="Priorité (Haute / Moyenne / Basse)"
    )
    
    # Informations de l'instance
    instance_name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom de l'instance"
    )
    instance_description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Description de l'instance"
    )
    instance_start_date = serializers.CharField(
        required=True,
        max_length=100,
        help_text="Date de début de l'instance"
    )
    instance_end_date = serializers.CharField(
        required=True,
        max_length=100,
        help_text="Date de fin de l'instance"
    )
    instance_location = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Lieu ou lien de réunion de l'instance"
    )
    instance_participants = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Liste des participants de l'instance"
    )
    
    # URL et entreprise
    url_connect = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="URL de connexion pour accéder au dossier"
    )
    company = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom de l'entreprise"
    )
    
    # URL de base
    base_url = serializers.URLField(
        required=True,
        help_text="URL de base du backend"
    )
    
    # Configuration
    client_id = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Identifiant unique du client"
    )
    lang = serializers.ChoiceField(
        choices=['fr-FR', 'en-US'],
        default='fr-FR',
        help_text="Langue de l'email (fr-FR ou en-US)"
    )
    
    def validate_dest_email(self, value):
        """Valider le format de l'email"""
        if not value:
            raise serializers.ValidationError("L'adresse email est requise")
        return value.lower()
    
    def validate_nomber_elements(self, value):
        """Valider le nombre d'éléments"""
        if value < 1:
            raise serializers.ValidationError("Le nombre d'éléments doit être supérieur à 0")
        return value
    

class CommitteeBoardUpdateSerializer(serializers.Serializer):
    instance_id = serializers.IntegerField(required=True, help_text='ID de l\'instance')
    old_date = serializers.DateTimeField(required=True, help_text='Ancienne date de la réunion')
    new_date = serializers.DateTimeField(required=True, help_text='Nouvelle date de la réunion')

    perimeter = serializers.ListField(
        child=serializers.JSONField(),
        required=False,
        allow_null=True,
        help_text="Liste des participants au format JSON pour le modèle. Si non fourni, peut être dérivé de 'participants'."
    )
    def validate_new_date(self, value):
        """Valider que la nouvelle date est dans le futur"""
        now = datetime.now(timezone.utc)
        if value < now:
            raise serializers.ValidationError(
                "La nouvelle date doit être dans le futur"
            )
        return value
    
    def validate(self, data):
        """Validation croisée"""
        old_date = data.get('old_date')
        new_date = data.get('new_date')
        
        if old_date and new_date and old_date == new_date:
            raise serializers.ValidationError(
                "La nouvelle date doit être différente de l'ancienne date"
            )
        
        return data




class CommentCreatedSerializer(serializers.Serializer):
    """Serializer pour la notification de création de dossier d'arbitrage"""

    sender_name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom du destinataire"
    )
 
    actors = serializers.ListField(
        child=serializers.JSONField(),
        required=False,
        allow_null=True,
        help_text="Liste des participants au format JSON pour le modèle. Si non fourni, peut être dérivé de 'participants'."
    )
      
    # Informations du comité
    value = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom du comité"
    )

    date_send = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Date de la réunion du comité"
    )
     
    company = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom de l'entreprise"
    )
    
    lang = serializers.ChoiceField(
        choices=['fr-FR', 'en-US'],
        default='fr-FR',
        help_text="Langue de l'email (fr-FR ou en-US)"
    )
    
     