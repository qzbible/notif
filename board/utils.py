from datetime import datetime, timedelta
from typing import Dict, List, Optional
import calendar


def _parse_date(date_str: str) -> Optional[datetime]:
    """Parse une date avec gestion du timezone"""
    if not date_str:
        return None
    
    # Si la date contient 'Z' ou un timezone
    if 'Z' in date_str or '+' in date_str or date_str.count('-') > 2:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    else:
        # Date sans timezone, ajouter minuit en UTC
        return datetime.fromisoformat(date_str + 'T00:00:00+00:00')


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
    
    # Construire la phrase
    if lang == "fr":
        phrase = _build_french_sentence(interval, unit, recurrence_config, end_type, end_date, occurrence_count)
    else:
        phrase = _build_english_sentence(interval, unit, recurrence_config, end_type, end_date, occurrence_count)
    
    return phrase


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
    
    print("\n\n" + "=" * 70)
    print("ENGLISH EXAMPLES:")
    print("=" * 70)
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {explain_recurrence_simple(example, 'en')}")