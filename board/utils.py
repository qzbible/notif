from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import calendar

from django.utils import timezone
from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser

from datetime import datetime
from typing import Optional
import zoneinfo  # Python 3.9+, ou installer tzdata

def _parse_date(date_str: str, default_tz: str = 'UTC') -> Optional[datetime]:
    """
    Parse une date avec gestion robuste du timezone.
    
    Args:
        date_str: Date au format ISO (avec ou sans timezone)
        default_tz: Timezone par défaut si absente ('UTC', 'Europe/Paris', etc.)
    
    Returns:
        datetime aware (avec timezone) ou None
    """
    if not date_str:
        return None
    
    try:
        # Nettoyer la chaîne
        date_str = date_str.strip()
        
        # Cas 1: Date avec 'Z' (UTC)
        if date_str.endswith('Z'):
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        
        # Cas 2: Date avec timezone explicite (+00:00, -05:00, etc.)
        if '+' in date_str or date_str.rfind('-') > 10:
            return datetime.fromisoformat(date_str)
        
        # Cas 3: Date sans timezone
        dt_naive = datetime.fromisoformat(date_str)
        
        # Ajouter le timezone par défaut
        tz = zoneinfo.ZoneInfo(default_tz)
        return dt_naive.replace(tzinfo=tz)
        
    except (ValueError, KeyError) as e:
        # Log l'erreur si nécessaire
        print(f"Erreur de parsing pour '{date_str}': {e}")
        return None


# Fonctions utilitaires supplémentaires

def convert_to_timezone(dt: datetime, target_tz: str = 'Europe/Paris') -> datetime:
    """Convertit un datetime vers un autre fuseau horaire."""
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        # Si pas de timezone, assumer UTC
        dt = dt.replace(tzinfo=zoneinfo.ZoneInfo('UTC'))
    
    return dt.astimezone(zoneinfo.ZoneInfo(target_tz))


def normalize_to_utc(dt: datetime) -> datetime:
    """Normalise un datetime en UTC pour stockage/comparaisons."""
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=zoneinfo.ZoneInfo('UTC'))
    
    return dt.astimezone(zoneinfo.ZoneInfo('UTC'))


def _build_french_sentence(interval, unit, recurrence_config, end_type, end_date, occurrence_count):
    """Construit une phrase en français"""
    
    # Partie 1 : Fréquence
    freq = ""
    
    if unit == "days":
        if interval == 1:
            freq = "tous les jours"
        else:
            freq = f"tous les {interval} jours"
    
    elif unit == "weeks":
        weekdays = recurrence_config.get('weekdays', [])
        days_fr = {
            "monday": "lundi", "tuesday": "mardi", "wednesday": "mercredi",
            "thursday": "jeudi", "friday": "vendredi", "saturday": "samedi", "sunday": "dimanche"
        }
        
        if len(weekdays) == 5 and set(weekdays) == {"monday", "tuesday", "wednesday", "thursday", "friday"}:
            freq = "tous les jours de semaine"
        elif len(weekdays) == 2 and set(weekdays) == {"saturday", "sunday"}:
            freq = "chaque week-end"
        elif len(weekdays) == 1:
            freq = f"chaque {days_fr[weekdays[0]]}"
        elif len(weekdays) == 7:
            freq = "tous les jours"
        elif weekdays:
            days_list = ", ".join([days_fr[d] for d in weekdays[:-1]]) + f" et {days_fr[weekdays[-1]]}"
            freq = f"chaque {days_list}" if interval == 1 else f"tous les {interval} semaines le {days_list}"
        else:
            freq = f"chaque semaine" if interval == 1 else f"tous les {interval} semaines"
    
    elif unit == "months":
        if 'day_of_month' in recurrence_config:
            day = recurrence_config['day_of_month']
            if day == 1:
                freq = "le 1er de chaque mois" if interval == 1 else f"le 1er tous les {interval} mois"
            elif day == 31:
                freq = "le dernier jour de chaque mois" if interval == 1 else f"le dernier jour tous les {interval} mois"
            else:
                freq = f"le {day} de chaque mois" if interval == 1 else f"le {day} tous les {interval} mois"
        
        elif 'week_position' in recurrence_config:
            positions = {"first": "premier", "second": "deuxième", "third": "troisième", "fourth": "quatrième", "last": "dernier"}
            days = {"monday": "lundi", "tuesday": "mardi", "wednesday": "mercredi", "thursday": "jeudi", 
                   "friday": "vendredi", "saturday": "samedi", "sunday": "dimanche"}
            
            pos = positions[recurrence_config['week_position']]
            day = days[recurrence_config['weekday_of_month']]
            
            freq = f"le {pos} {day} de chaque mois" if interval == 1 else f"le {pos} {day} tous les {interval} mois"
        else:
            freq = f"chaque mois" if interval == 1 else f"tous les {interval} mois"
    
    elif unit == "years":
        months_fr = {1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
                    7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"}
        
        if 'months_of_year' in recurrence_config and 'yearly_day' in recurrence_config:
            months = recurrence_config['months_of_year']
            day = recurrence_config['yearly_day']
            
            # Événements spéciaux
            if months == [1] and day == 1:
                freq = "chaque 1er janvier"
            elif months == [12] and day == 25:
                freq = "chaque 25 décembre"
            elif months == [2] and day == 14:
                freq = "chaque 14 février"
            elif len(months) == 1:
                freq = f"le {day} {months_fr[months[0]]} de chaque année"
            elif len(months) == 2:
                freq = f"le {day} en {months_fr[months[0]]} et {months_fr[months[1]]} chaque année"
            else:
                month_names = ", ".join([months_fr[m] for m in months[:-1]]) + f" et {months_fr[months[-1]]}"
                freq = f"le {day} en {month_names} chaque année"
        
        elif 'yearly_week_position' in recurrence_config:
            positions = {"first": "premier", "second": "deuxième", "third": "troisième", "fourth": "quatrième", "last": "dernier"}
            days = {"monday": "lundi", "tuesday": "mardi", "wednesday": "mercredi", "thursday": "jeudi",
                   "friday": "vendredi", "saturday": "samedi", "sunday": "dimanche"}
            
            months = recurrence_config.get('months_of_year', [])
            pos = positions[recurrence_config['yearly_week_position']]
            day = days[recurrence_config['yearly_weekday']]
            
            if months:
                month_name = months_fr[months[0]]
                freq = f"le {pos} {day} de {month_name} chaque année"
            else:
                freq = f"le {pos} {day} de chaque année"
        
        elif 'weeks_of_year' in recurrence_config:
            weeks = recurrence_config['weeks_of_year']
            if len(weeks) <= 3:
                weeks_str = ", ".join([f"S{w}" for w in weeks])
                freq = f"semaines {weeks_str} de chaque année"
            else:
                freq = f"{len(weeks)} semaines par an"
        else:
            freq = f"chaque année" if interval == 1 else f"tous les {interval} ans"
    
    if not freq:
        freq = "régulièrement"
    
    # Partie 2 : Durée
    duration = ""
    if end_type == "never":
        duration = ""
    elif end_type == "after":
        duration = f" ({occurrence_count} fois)"
    elif end_type == "on" and end_date:
        end_date_obj = _parse_date(end_date)
        if end_date_obj:
            duration = f" jusqu'au {end_date_obj.strftime('%d/%m/%Y')}"
    
    return f"Se répète {freq}{duration}."


def _build_english_sentence(interval, unit, recurrence_config, end_type, end_date, occurrence_count):
    """Construit une phrase en anglais"""
    
    # Partie 1 : Fréquence
    freq = ""
    
    if unit == "days":
        if interval == 1:
            freq = "every day"
        else:
            freq = f"every {interval} days"
    
    elif unit == "weeks":
        weekdays = recurrence_config.get('weekdays', [])
        
        if len(weekdays) == 5 and set(weekdays) == {"monday", "tuesday", "wednesday", "thursday", "friday"}:
            freq = "every weekday"
        elif len(weekdays) == 2 and set(weekdays) == {"saturday", "sunday"}:
            freq = "every weekend"
        elif len(weekdays) == 1:
            freq = f"every {weekdays[0].capitalize()}"
        elif len(weekdays) == 7:
            freq = "every day"
        elif weekdays:
            days_list = ", ".join([d.capitalize() for d in weekdays[:-1]]) + f" and {weekdays[-1].capitalize()}"
            freq = f"every {days_list}" if interval == 1 else f"every {interval} weeks on {days_list}"
        else:
            freq = f"every week" if interval == 1 else f"every {interval} weeks"
    
    elif unit == "months":
        if 'day_of_month' in recurrence_config:
            day = recurrence_config['day_of_month']
            if day == 1:
                freq = "on the 1st of every month" if interval == 1 else f"on the 1st every {interval} months"
            elif day == 31:
                freq = "on the last day of every month" if interval == 1 else f"on the last day every {interval} months"
            else:
                freq = f"on the {day}th of every month" if interval == 1 else f"on the {day}th every {interval} months"
        
        elif 'week_position' in recurrence_config:
            positions = {"first": "first", "second": "second", "third": "third", "fourth": "fourth", "last": "last"}
            
            pos = positions[recurrence_config['week_position']]
            day = recurrence_config['weekday_of_month'].capitalize()
            
            freq = f"on the {pos} {day} of every month" if interval == 1 else f"on the {pos} {day} every {interval} months"
        else:
            freq = f"every month" if interval == 1 else f"every {interval} months"
    
    elif unit == "years":
        months_en = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
                    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
        
        if 'months_of_year' in recurrence_config and 'yearly_day' in recurrence_config:
            months = recurrence_config['months_of_year']
            day = recurrence_config['yearly_day']
            
            if months == [1] and day == 1:
                freq = "every January 1st"
            elif months == [12] and day == 25:
                freq = "every December 25th"
            elif len(months) == 1:
                freq = f"on {months_en[months[0]]} {day}th every year"
            elif len(months) == 2:
                freq = f"on {months_en[months[0]]} and {months_en[months[1]]} {day}th every year"
            else:
                month_names = ", ".join([months_en[m] for m in months[:-1]]) + f" and {months_en[months[-1]]}"
                freq = f"on {month_names} {day}th every year"
        else:
            freq = f"every year" if interval == 1 else f"every {interval} years"
    
    if not freq:
        freq = "regularly"
    
    # Partie 2 : Durée
    duration = ""
    if end_type == "never":
        duration = ""
    elif end_type == "after":
        duration = f" ({occurrence_count} times)"
    elif end_type == "on" and end_date:
        end_date_obj = _parse_date(end_date)
        if end_date_obj:
            duration = f" until {end_date_obj.strftime('%m/%d/%Y')}"
    
    return f"Repeats {freq}{duration}."


def explain_recurrence_simple(config: Dict, lang: str = "fr") -> str:
    """
    Génère une phrase simple expliquant la récurrence
    
    Args:
        config: Configuration de récurrence
        lang: Langue ("fr" ou "en")
        
    Returns:
        Une phrase simple décrivant la récurrence
    """
   
    interval = config['interval']
 
    unit = config['unit']
    end_type = config['end_type']
    end_date = config.get('end_date')
    occurrence_count = config.get('occurrence_count')
    recurrence_config = config.get('recurrence_config', {})
    phrase = "None"
    # Construire la phrase
    
    try:
        if lang == "fr":
            phrase = _build_french_sentence(interval, unit, recurrence_config, end_type, end_date, occurrence_count)
        else:
            phrase = _build_english_sentence(interval, unit, recurrence_config, end_type, end_date, occurrence_count)
    except Exception as e:
        print(f"Erreur lors de la construction de la phrase : {e}")
     
    return phrase



def format_ponctuel_date(ponctuel_config: Dict, lang: str = "fr") -> str:
    """
    Formate la date d'un événement ponctuel
    
    Args:
        ponctuel_config: Configuration ponctuelle avec:
            - date: Date de l'événement (ISO format)
            - priority: Priorité (optionnel)
        lang: Langue ("fr" ou "en")
        
    Returns:
        Date formatée avec jour, date et heure
    """
    
    date_str = ponctuel_config.get('date')
    if not date_str:
        return "Date non définie" if lang == "fr" else "Date not defined"
    
    dt = _parse_date(date_str)
    if not dt:
        return "Date invalide" if lang == "fr" else "Invalid date"
    
    # Formater selon la langue
    if lang == "fr":
        return _format_datetime_fr(dt, include_time=True)
    else:
        return _format_datetime_en(dt, include_time=True)

 

def format_date_hour(date_str: str, lang: str = "fr") -> Tuple[str, str]:
    """
    Formate la date et extrait l'heure
    
    Args:
        date_str: Date au format ISO (ex: "2025-10-17T11:35:47.233Z")
        lang: Langue ("fr" ou "en")
        
    Returns:
        Tuple (date_formatée, heure)
        - date_formatée: Date en toutes lettres
        - heure: Heure au format "HH:MM"
    """
    if not date_str:
        empty = "Date non définie" if lang == "fr" else "Date not defined"
        return (empty, "")
    
    dt = _parse_date(date_str)
    if not dt:
        invalid = "Date invalide" if lang == "fr" else "Invalid date"
        return (invalid, "")
    
    # Extraire l'heure
    time_part = dt.strftime("%H:%M")
    
    if lang == "fr":
        days_fr = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        months_fr = ['', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                     'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        
        day_name = days_fr[dt.weekday()]
        day = dt.day
        month = months_fr[dt.month]
        year = dt.year
        
        date_formatted = f"{day_name} {day} {month} {year}"
        return (date_formatted, time_part)
    
    else:  # English
        days_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        months_en = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
        
        day_name = days_en[dt.weekday()]
        day = dt.day
        month = months_en[dt.month]
        year = dt.year
        
        # Suffixe pour le jour
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        
        date_formatted = f"{day_name}, {month} {day}{suffix}, {year}"
        return (date_formatted, time_part)


def _format_datetime_fr(dt: datetime, include_time: bool = True) -> str:
    """Formate une date/heure en français"""
    days_fr = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    months_fr = ['', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    
    day_name = days_fr[dt.weekday()]
    day = dt.day
    month = months_fr[dt.month]
    year = dt.year
    
    date_str = f"{day_name} {day} {month} {year}"
    
    if include_time:
        hour = dt.hour
        minute = dt.minute
        time_str = f"{hour:02d}h{minute:02d}" if minute > 0 else f"{hour:02d}h"
        return f"{date_str} à {time_str}"
    
    return date_str


def _format_datetime_en(dt: datetime, include_time: bool = True) -> str:
    """Formate une date/heure en anglais"""
    days_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    months_en = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
    
    day_name = days_en[dt.weekday()]
    day = dt.day
    month = months_en[dt.month]
    year = dt.year
    
    # Suffixe pour le jour (1st, 2nd, 3rd, 4th, etc.)
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    
    date_str = f"{day_name}, {month} {day}{suffix}, {year}"
    
    if include_time:
        hour = dt.hour
        minute = dt.minute
        am_pm = "AM" if hour < 12 else "PM"
        hour_12 = hour if hour <= 12 else hour - 12
        hour_12 = 12 if hour_12 == 0 else hour_12
        
        if minute > 0:
            time_str = f"{hour_12}:{minute:02d} {am_pm}"
        else:
            time_str = f"{hour_12} {am_pm}"
        
        return f"{date_str} at {time_str}"
    
    return date_str


def format_recurrence_schedule(config: Dict, lang: str = "fr") -> str:
    """
    Génère une description complète avec dates et heures de début/fin
    
    Args:
        config: Configuration de récurrence
        lang: Langue ("fr" ou "en")
        
    Returns:
        Description formatée avec dates et heures
    """
    
    start_date = _parse_date(config.get('start_date'))
    end_type = config.get('end_type', 'never')
    end_date = _parse_date(config.get('end_date')) if config.get('end_date') else None
    occurrence_count = config.get('occurrence_count')
    
    if not start_date:
        return "Dates non définies" if lang == "fr" else "Dates not defined"
    
    if lang == "fr":
        start_str = _format_datetime_fr(start_date, include_time=True)
        
        if end_type == "never":
            return f" Débute le {start_str} Se termine : Jamais"
        
        elif end_type == "after" and occurrence_count:
            return f"Débute le {start_str} Se termine : Après {occurrence_count} occurrence{'s' if occurrence_count > 1 else ''}"
        
        elif end_type == "on" and end_date:
            end_str = _format_datetime_fr(end_date, include_time=False)
            return f"Débute le {start_str} Se termine le {end_str}"
        
        return f"Débute le {start_str}"
    
    else:  # English
        start_str = _format_datetime_en(start_date, include_time=True)
        
        if end_type == "never":
            return f"Starts on {start_str} Ends: Never"
        
        elif end_type == "after" and occurrence_count:
            return f"Starts on {start_str} Ends: After {occurrence_count} occurrence{'s' if occurrence_count > 1 else ''}"
        
        elif end_type == "on" and end_date:
            end_str = _format_datetime_en(end_date, include_time=False)
            return f"Starts on {start_str} Ends on {end_str}"
        
        return f"Starts on {start_str}"


def _format_to_iso(dt: datetime) -> str:
    """Formate une date en ISO avec Z"""
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def calculate_next_occurrences(config: Dict, count: int = 5) -> List[str]:
    """
    Calcule les N prochaines occurrences d'une récurrence
    
    Args:
        config: Configuration de récurrence
        count: Nombre d'occurrences à calculer (défaut: 5)
        
    Returns:
        Liste des dates au format ISO (ex: "2025-10-17T11:35:47.233Z")
    """
    start_date = _parse_date(config.get('start_date'))
    if not start_date:
        return []
    
    interval = config.get('interval', 1)
    unit = config.get('unit')
    recurrence_config = config.get('recurrence_config', {})
    end_type = config.get('end_type', 'never')
    end_date = _parse_date(config.get('end_date')) if config.get('end_date') else None
    occurrence_count = config.get('occurrence_count')
    
    occurrences = []
    current_date = start_date
    
    # Limiter le nombre d'occurrences selon end_type
    max_count = count
    if end_type == "after" and occurrence_count:
        max_count = min(count, occurrence_count)
    
    iteration = 0
    max_iterations = 1000  # Sécurité pour éviter les boucles infinies
    
    while len(occurrences) < max_count and iteration < max_iterations:
        iteration += 1
        
        # Vérifier si on dépasse la date de fin
        if end_type == "on" and end_date and current_date > end_date:
            break
        
        # Ajouter l'occurrence selon le type de récurrence
        if unit == "days":
            occurrences.append(_format_to_iso(current_date))
            current_date += timedelta(days=interval)
        
        elif unit == "weeks":
            weekdays = recurrence_config.get('weekdays', [])
            if weekdays:
                # Mapper les jours de la semaine
                day_map = {
                    'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                    'friday': 4, 'saturday': 5, 'sunday': 6
                }
                target_days = sorted([day_map[d] for d in weekdays])
                
                # Trouver le prochain jour correspondant
                current_weekday = current_date.weekday()
                
                # Chercher dans la semaine courante
                found = False
                for target_day in target_days:
                    if target_day >= current_weekday or len(occurrences) == 0:
                        days_ahead = (target_day - current_weekday) % 7
                        if days_ahead == 0 and len(occurrences) > 0:
                            days_ahead = 7
                        next_date = current_date + timedelta(days=days_ahead)
                        occurrences.append(_format_to_iso(next_date))
                        current_date = next_date + timedelta(days=1)
                        found = True
                        break
                
                if not found:
                    # Passer à la semaine suivante
                    days_to_next_week = 7 - current_weekday + target_days[0]
                    current_date += timedelta(days=days_to_next_week)
            else:
                occurrences.append(_format_to_iso(current_date))
                current_date += timedelta(weeks=interval)
        
        elif unit == "months":
            if 'day_of_month' in recurrence_config:
                day = recurrence_config['day_of_month']
                
                # Gérer le dernier jour du mois
                if day == 31:
                    last_day = calendar.monthrange(current_date.year, current_date.month)[1]
                    next_date = current_date.replace(day=last_day)
                else:
                    try:
                        next_date = current_date.replace(day=min(day, calendar.monthrange(current_date.year, current_date.month)[1]))
                    except ValueError:
                        next_date = current_date
                
                occurrences.append(_format_to_iso(next_date))
                
                # Passer au mois suivant
                month = current_date.month + interval
                year = current_date.year
                while month > 12:
                    month -= 12
                    year += 1
                current_date = current_date.replace(year=year, month=month, day=1)
            
            elif 'week_position' in recurrence_config:
                # Premier, deuxième, troisième, quatrième ou dernier jour de la semaine du mois
                occurrences.append(_format_to_iso(current_date))
                
                # Passer au mois suivant
                month = current_date.month + interval
                year = current_date.year
                while month > 12:
                    month -= 12
                    year += 1
                current_date = current_date.replace(year=year, month=month, day=1)
            else:
                occurrences.append(_format_to_iso(current_date))
                month = current_date.month + interval
                year = current_date.year
                while month > 12:
                    month -= 12
                    year += 1
                current_date = current_date.replace(year=year, month=month)
        
        elif unit == "years":
            occurrences.append(_format_to_iso(current_date))
            current_date = current_date.replace(year=current_date.year + interval)
    
    return occurrences[:max_count]



def compare_with_now(target_date, lang='en'):
    """
    Compare a date with the current date and returns whether it is in the past
    along with a readable description of the difference.
    
    Args:
        target_date: datetime object or ISO format string
        lang: 'en' for English, 'fr' for French (default: 'en')
        
    Returns:
        tuple: (is_past: bool, readable: str)
            - is_past: True if the date is in the past, False if in the future
            - readable: Readable description of the difference
    """
    try:
        # Convert to datetime if necessary
        target_date = _parse_date(target_date)

        # Date actuelle
        now = datetime.now(timezone.utc)
        
        # Determine if the date is in the past
        is_past = target_date < now 
        # Default
        return (is_past,  '')
    
    except Exception as e:
        print("----error", str(e))

        return False,  ''


def format_perimeter_for_email(perimeter, lang='fr'):
    """
    Version simplifiée avec indicateur "et X autres" et gestion sans priorité
    
    Args:
        perimeter: Liste de dictionnaires
        lang: 'fr' pour français, 'en' pour anglais
        
    Returns:
        str: Texte formaté limité à 3 types
    """
    if not perimeter:
        return "Aucun périmètre défini" if lang == 'fr' else "No perimeter defined"
    
    # Traductions des priorités
    translations = {
        'fr': {
            1: "Très faible",
            2: "Faible",
            3: "Moyen",
            4: "Élevé",
            5: "Très Élevé",
        },
        'en': {
            1: "Very Low",
            2: "Low",
            3: "Medium",
            4: "High",
            5: "Very High",
        }
    }
    
    # Traductions des types
    type_translations = {
        'fr': {
            'risk': 'Risques',
            'opportunity': 'Opportunités',
            'issue': 'Problèmes',
            'objective': 'Objectifs',
            'threat': 'Menaces',
        },
        'en': {
            'risk': 'Risks',
            'opportunity': 'Opportunities',
            'issue': 'Issues',
            'objective': 'Objectives',
            'threat': 'Threats',
        }
    }
    
    priority_labels = translations.get(lang, translations['fr'])
    type_labels = type_translations.get(lang, type_translations['fr'])
    
    # Regrouper par type_value
    grouped = {}
    has_priority = False  # Vérifier si au moins un élément a une priorité
    
    for item in perimeter:
        type_value = item.get('type_value', 'other')
        priority = item.get('priority')
        
        # Vérifier si la priorité existe et est valide
        if priority is not None and priority > 0:
            has_priority = True
            if type_value not in grouped:
                grouped[type_value] = priority
            else:
                if priority > grouped[type_value]:
                    grouped[type_value] = priority
        else:
            # Pas de priorité, juste ajouter le type
            if type_value not in grouped:
                grouped[type_value] = None
    
    # Trier par priorité décroissante (les None en dernier)
    sorted_types = sorted(
        grouped.items(), 
        key=lambda x: (x[1] is None, -(x[1] if x[1] is not None else 0))
    )
    
    total_types = len(sorted_types)
    
    # Limiter à 3
    display_types = sorted_types[:3]
    
    # Construire le texte
    result_parts = []
    for type_value, max_priority in display_types:
        type_label = type_labels.get(type_value, type_value.capitalize())
        
        # Si la priorité existe, l'afficher
        if max_priority is not None:
            priority_label = priority_labels.get(max_priority, priority_labels[1])
            result_parts.append(f"{type_label} [{priority_label}]")
        else:
            # Pas de priorité, afficher juste le type
            result_parts.append(type_label)
    
    result = ", ".join(result_parts)
    
    # Ajouter "et X autres" si plus de 3 types
    if total_types > 3:
        remaining = total_types - 3
        if lang == 'fr':
            result += f" et {remaining} autre{'s' if remaining > 1 else ''}"
        else:
            result += f" and {remaining} other{'s' if remaining > 1 else ''}"
    
    return result


# Exemple d'utilisation
if __name__ == "__main__":
    
    examples = [
        {
            "start_date": "2025-10-16T13:28:06.092Z",
            "interval": 1,
            "unit": "days",
            "recurrence_config": {},
            "end_type": "never",
            "end_date": None,
            "occurrence_count": None
        },
        {
            "start_date": "2025-10-16T13:28:06.092Z",
            "interval": 3,
            "unit": "days",
            "recurrence_config": {},
            "end_type": "after",
            "end_date": None,
            "occurrence_count": 10
        },
        {
            "start_date": "2025-10-16T13:28:06.092Z",
            "interval": 1,
            "unit": "weeks",
            "recurrence_config": {
                "weekdays": ["monday", "tuesday", "wednesday", "thursday", "friday"]
            },
            "end_type": "never",
            "end_date": None,
            "occurrence_count": None
        },
        {
            "start_date": "2025-10-16T13:28:06.092Z",
            "interval": 1,
            "unit": "months",
            "recurrence_config": {
                "day_of_month": 1
            },
            "end_type": "never",
            "end_date": None,
            "occurrence_count": None
        },
        {
            "start_date": "2025-10-16T13:28:06.092Z",
            "interval": 3,
            "unit": "months",
            "recurrence_config": {
                "day_of_month": 1
            },
            "end_type": "on",
            "end_date": "2027-12-31",
            "occurrence_count": None
        },
        {
            "start_date": "2025-10-16T13:28:06.092Z",
            "interval": 1,
            "unit": "years",
            "recurrence_config": {
                "months_of_year": [1],
                "yearly_day": 1
            },
            "end_type": "never",
            "end_date": None,
            "occurrence_count": None
        },
        {
            "start_date": "2025-10-16T13:28:06.092Z",
            "interval": 1,
            "unit": "weeks",
            "recurrence_config": {
                "weekdays": ["saturday", "sunday"]
            },
            "end_type": "after",
            "end_date": None,
            "occurrence_count": 20
        }
    ]
    
    print("EXEMPLES DE PHRASES SIMPLES:")
    print("=" * 70)
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {explain_recurrence_simple(example, 'fr')}")
        print(f'', format_recurrence_schedule(example, 'fr'))
    
    print("\n\n" + "=" * 70)
    print("ENGLISH EXAMPLES:")
    print("=" * 70)
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {explain_recurrence_simple(example, 'en')}")

        print(f'', format_recurrence_schedule(example, 'en'))
 
