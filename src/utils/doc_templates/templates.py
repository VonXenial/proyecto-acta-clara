"""
Módulo de Plantillas de Actas de Reunión
Este archivo contiene la estructura lógica para mapear 
la información extraída de las transcripciones al exportar.
"""

from src.utils.i18n import translate # type: ignore

MEETING_TEMPLATES = {
    "corporativa_formal": {
        "title": "Corporativa formal",
        "fields": [
            "purpose", "date", "start_time", "location", 
            "attendees", "agenda_items"
        ]
    },
    "team_meeting": {
        "title": "Acta de Reunión de Equipo",
        "fields": [
            "purpose", "date", "start_time", "end_time", "location", 
            "attendees", "absentees", "agenda_items", "next_meeting_date"
        ],
        "structure": {
            "agenda_item_format": ["topic", "discussion_points", "decisions", "action_items"]
        }
    },
    
    "board_meeting": {
        "title": "Acta de Reunión de la Junta",
        "fields": [
            "organization_name", "date", "start_time", "location", 
            "called_by", "secretary", "attendees", 
            "financial_report", "committee_reports", "old_business", "new_business", 
            "adjournment_time"
        ]
    },
    
    "project_meeting": {
        "title": "Acta de Reunión de Proyecto",
        "fields": [
            "project_name", "date", "location", 
            "called_by", "purpose", "participants", "project_status_update", 
            "issues_challenges"
        ]
    },
    
    "agm_meeting": {
        "title": "Acta de Reunión Anual (AGM)",
        "fields": [
            "organization_name", "date", "location", 
            "called_by", "secretary", "attendees", "chairperson", 
            "year_summary", "financial_report", "strategic_plan"
        ]
    },
    
    "client_meeting": {
        "title": "Acta de Reunión con Clientes",
        "fields": [
            "meeting_title", "date", "location", 
            "client_name", "attendees", "objectives", "project_status_update", 
            "client_feedback"
        ]
    },
    
    "financial_meeting": {
        "title": "Acta de Reunión Financiera",
        "fields": [
            "meeting_title", "date", "location", 
            "called_by", "attendees", "objectives", 
            "financial_performance_review", "budget_discussion", 
            "financial_strategy"
        ]
    }
}

def get_template(template_type):
    """Retorna la estructura de la plantilla solicitada."""
    return MEETING_TEMPLATES.get(template_type, MEETING_TEMPLATES["corporativa_formal"])

def get_template_names(lang="Español"):
    """Retorna una lista de nombres de las plantillas disponibles, traducidos según el idioma."""
    return [translate(config["title"], lang) for config in MEETING_TEMPLATES.values()]

def get_template_key_by_name(title, lang="Español"):
    for key, val in MEETING_TEMPLATES.items():
        if translate(str(val.get("title")), lang) == title: # type: ignore
            return key
    
    # Fallback in case the setting was saved in a different language
    from src.utils.i18n import TRANSLATIONS # type: ignore
    for key, val in MEETING_TEMPLATES.items():
        for lang_dict in TRANSLATIONS.values():
            if str(val.get("title")) == title or lang_dict.get(str(val.get("title"))) == title: # type: ignore
                return key
                
    return "corporativa_formal"
