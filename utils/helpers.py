"""
Helper utilities for Hackathon Bot
"""

import re
from datetime import datetime
from typing import Tuple, Optional


class UserState:
    """User registration/conversation states."""
    # Consent flow
    AWAITING_CONSENT = "awaiting_consent"
    
    # Registration flow
    REG_FIRST_NAME = "reg_first_name"
    REG_LAST_NAME = "reg_last_name"
    REG_BIRTH_DATE = "reg_birth_date"
    REG_GENDER = "reg_gender"
    REG_LOCATION = "reg_location"
    REG_PHONE = "reg_phone"
    REG_PINFL = "reg_pinfl"
    
    # Edit flow
    EDIT_FIRST_NAME = "edit_first_name"
    EDIT_LAST_NAME = "edit_last_name"
    EDIT_BIRTH_DATE = "edit_birth_date"
    EDIT_LOCATION = "edit_location"
    
    # Team flow
    TEAM_JOIN_CODE = "team_join_code"
    TEAM_NAME = "team_name"
    TEAM_ROLE = "team_role"
    TEAM_FIELD = "team_field"
    TEAM_PORTFOLIO = "team_portfolio"
    
    # Submission flow
    SUBMIT_LINK = "submit_link"
    SUBMIT_FILE = "submit_file"
    
    # Admin flow
    ADMIN_BROADCAST = "admin_broadcast"
    ADMIN_CREATE_HACKATHON_NAME = "admin_create_hackathon_name"
    ADMIN_CREATE_HACKATHON_DESC = "admin_create_hackathon_desc"
    ADMIN_CREATE_HACKATHON_PRIZE = "admin_create_hackathon_prize"
    ADMIN_CREATE_HACKATHON_START = "admin_create_hackathon_start"
    ADMIN_CREATE_HACKATHON_END = "admin_create_hackathon_end"
    ADMIN_CREATE_HACKATHON_DEADLINE = "admin_create_hackathon_deadline"
    ADMIN_CREATE_STAGE_HACKATHON = "admin_create_stage_hackathon"
    ADMIN_CREATE_STAGE_NUMBER = "admin_create_stage_number"
    ADMIN_CREATE_STAGE_NAME = "admin_create_stage_name"
    ADMIN_CREATE_STAGE_TASK = "admin_create_stage_task"
    ADMIN_CREATE_STAGE_DEADLINE = "admin_create_stage_deadline"


def validate_date(date_str: str) -> Tuple[bool, Optional[datetime]]:
    """
    Validate date string in DD.MM.YYYY format.
    Returns (is_valid, parsed_date)
    """
    patterns = [
        r'^\d{2}\.\d{2}\.\d{4}$',  # DD.MM.YYYY
        r'^\d{2}/\d{2}/\d{4}$',    # DD/MM/YYYY
        r'^\d{2}-\d{2}-\d{4}$',    # DD-MM-YYYY
    ]
    
    for pattern in patterns:
        if re.match(pattern, date_str):
            try:
                # Normalize separators
                normalized = date_str.replace('/', '.').replace('-', '.')
                parts = normalized.split('.')
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                
                # Validate ranges
                if year < 1900 or year > datetime.now().year:
                    return False, None
                if month < 1 or month > 12:
                    return False, None
                if day < 1 or day > 31:
                    return False, None
                
                parsed = datetime(year, month, day)
                return True, parsed
            except (ValueError, IndexError):
                return False, None
    
    return False, None


def validate_pinfl(pinfl: str) -> bool:
    """Validate PINFL (14 digits)."""
    clean = pinfl.strip()
    return len(clean) == 14 and clean.isdigit()


def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
    return bool(re.match(pattern, url.strip()))


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    clean = re.sub(r'[\s\-\(\)]', '', phone)
    return len(clean) >= 9 and clean.replace('+', '').isdigit()


def clean_name(name: str) -> str:
    """Clean and capitalize name."""
    return ' '.join(word.capitalize() for word in name.strip().split())


def format_date(date_obj, lang: str = 'uz') -> str:
    """Format date for display."""
    if not date_obj:
        return '—'
    
    if isinstance(date_obj, str):
        return date_obj
    
    try:
        return date_obj.strftime('%d.%m.%Y')
    except:
        return '—'


def format_datetime(dt_obj, lang: str = 'uz') -> str:
    """Format datetime for display."""
    if not dt_obj:
        return '—'
    
    try:
        return dt_obj.strftime('%d.%m.%Y %H:%M')
    except:
        return '—'


def format_gender(gender: str, lang: str = 'uz') -> str:
    """Format gender for display."""
    if not gender:
        return '—'
    
    genders = {
        'male': {'uz': 'Erkak', 'ru': 'Мужской', 'en': 'Male'},
        'female': {'uz': 'Ayol', 'ru': 'Женский', 'en': 'Female'}
    }
    
    return genders.get(gender, {}).get(lang, gender)


def format_member_list(members: list, lang: str = 'uz') -> str:
    """Format team members list for display."""
    if not members:
        return '—'
    
    lines = []
    for i, m in enumerate(members, 1):
        name = f"{m.get('first_name', '')} {m.get('last_name', '')}".strip()
        role = m.get('role', 'Member')
        lead = " (TeamLead)" if m.get('is_team_lead') else ""
        lines.append(f"{i}. {name} - {role}{lead}")
    
    return '\n'.join(lines)


def format_submission_content(submission: dict) -> str:
    """Format submission content for display."""
    if not submission:
        return '—'
    
    sub_type = submission.get('submission_type', 'link')
    
    if sub_type == 'file':
        file_name = submission.get('file_name', 'file')
        file_type = submission.get('file_type', 'unknown')
        return f"📎 {file_name} ({file_type})"
    else:
        return submission.get('content', '—')


def get_file_type(file_name: str, mime_type: str = None) -> str:
    """Determine file type from name or mime type."""
    if not file_name:
        return 'unknown'
    
    ext = file_name.lower().split('.')[-1] if '.' in file_name else ''
    
    image_exts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg']
    video_exts = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'wmv']
    audio_exts = ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a']
    doc_exts = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'rtf']
    
    if ext in image_exts:
        return 'image'
    elif ext in video_exts:
        return 'video'
    elif ext in audio_exts:
        return 'audio'
    elif ext in doc_exts:
        return 'document'
    elif ext == 'pdf':
        return 'pdf'
    else:
        return 'file'


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis."""
    if not text or len(text) <= max_length:
        return text or ''
    return text[:max_length - 3] + '...'
