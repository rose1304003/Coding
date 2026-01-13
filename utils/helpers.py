"""
Utility helpers for Hackathon Bot
Validation, formatting, and common functions
"""

import re
from datetime import datetime, date
from typing import Optional, Tuple
import urllib.parse


def validate_date(date_str: str) -> Tuple[bool, Optional[date]]:
    """
    Validate date string in DD.MM.YYYY format.
    
    Returns:
        Tuple of (is_valid, parsed_date or None)
    """
    # Accept various separators
    date_str = date_str.strip()
    date_str = date_str.replace('/', '.').replace('-', '.')
    
    try:
        parsed = datetime.strptime(date_str, '%d.%m.%Y')
        # Sanity check - not in future, not too old
        if parsed.date() > date.today():
            return False, None
        if parsed.year < 1900:
            return False, None
        return True, parsed.date()
    except ValueError:
        return False, None


def validate_pinfl(pinfl: str) -> bool:
    """Validate PINFL (14-digit Uzbek ID number)."""
    pinfl = pinfl.strip()
    return len(pinfl) == 14 and pinfl.isdigit()


def validate_url(url: str) -> bool:
    """Validate URL format."""
    url = url.strip()
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except:
        return False


def validate_phone(phone: str) -> bool:
    """Validate phone number (basic check)."""
    # Remove common formatting
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    return len(cleaned) >= 9 and cleaned.isdigit()


def format_date(d: date, lang: str = 'uz') -> str:
    """Format date for display."""
    if not d:
        return "—"
    return d.strftime('%d.%m.%Y')


def format_datetime(dt: datetime, lang: str = 'uz') -> str:
    """Format datetime for display."""
    if not dt:
        return "—"
    return dt.strftime('%d.%m.%Y %H:%M')


def format_phone(phone: str) -> str:
    """Format phone number for display."""
    if not phone:
        return "—"
    # Try to format as +998 XX XXX XX XX
    cleaned = re.sub(r'[^\d]', '', phone)
    if len(cleaned) == 12 and cleaned.startswith('998'):
        return f"+{cleaned[:3]} {cleaned[3:5]} {cleaned[5:8]} {cleaned[8:10]} {cleaned[10:]}"
    return phone


def format_gender(gender: str, lang: str = 'uz') -> str:
    """Format gender for display."""
    if not gender:
        return "—"
    
    gender_map = {
        'uz': {'male': 'Erkak', 'female': 'Ayol'},
        'ru': {'male': 'Мужской', 'female': 'Женский'},
        'en': {'male': 'Male', 'female': 'Female'}
    }
    
    lang_map = gender_map.get(lang, gender_map['uz'])
    return lang_map.get(gender.lower(), gender)


def escape_markdown(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2."""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
    )


def truncate(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_member_list(members: list, lang: str = 'uz') -> str:
    """Format team member list for display."""
    lines = []
    for i, member in enumerate(members, 1):
        name = member.get('first_name', '')
        last_name = member.get('last_name', '')
        full_name = f"{name} {last_name}".strip()
        role = member.get('role', 'Member')
        
        if member.get('is_team_lead'):
            lines.append(f"{i}. {full_name} - {role} (TeamLead)")
        else:
            lines.append(f"{i}. {full_name} - {role}")
    
    return '\n'.join(lines) if lines else "—"


def calculate_days_until(target_date: date) -> int:
    """Calculate days until a target date."""
    today = date.today()
    delta = target_date - today
    return delta.days


def is_deadline_passed(deadline: datetime) -> bool:
    """Check if a deadline has passed."""
    if not deadline:
        return False
    return datetime.now(deadline.tzinfo) > deadline


def generate_team_invite_link(bot_username: str, team_code: str) -> str:
    """Generate deep link for team invite."""
    return f"https://t.me/{bot_username}?start=join_{team_code}"


def parse_callback_data(data: str) -> Tuple[str, list]:
    """
    Parse callback data into action and arguments.
    
    Example: "hackathon_123" -> ("hackathon", ["123"])
    """
    parts = data.split('_')
    if len(parts) == 1:
        return parts[0], []
    return parts[0], parts[1:]


def chunk_list(lst: list, chunk_size: int) -> list:
    """Split list into chunks."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def clean_name(name: str) -> str:
    """Clean and normalize a name."""
    if not name:
        return ""
    # Remove extra whitespace, capitalize properly
    return ' '.join(name.strip().split()).title()


class UserState:
    """User conversation state constants."""
    IDLE = 'idle'
    
    # Registration flow
    REG_FIRST_NAME = 'reg_first_name'
    REG_LAST_NAME = 'reg_last_name'
    REG_BIRTH_DATE = 'reg_birth_date'
    REG_GENDER = 'reg_gender'
    REG_LOCATION = 'reg_location'
    REG_PHONE = 'reg_phone'
    REG_PINFL = 'reg_pinfl'
    
    # Team creation flow
    TEAM_NAME = 'team_name'
    TEAM_ROLE = 'team_role'
    TEAM_FIELD = 'team_field'
    TEAM_PORTFOLIO = 'team_portfolio'
    
    # Submission flow
    SUBMIT_LINK = 'submit_link'
    
    # Edit flows
    EDIT_FIRST_NAME = 'edit_first_name'
    EDIT_LAST_NAME = 'edit_last_name'
    EDIT_BIRTH_DATE = 'edit_birth_date'
    EDIT_GENDER = 'edit_gender'
    EDIT_LOCATION = 'edit_location'
    
    # Admin flows
    ADMIN_BROADCAST = 'admin_broadcast'
    ADMIN_ADD_HACKATHON = 'admin_add_hackathon'


# Error messages for logging
ERROR_MESSAGES = {
    'db_connection': 'Failed to connect to database',
    'db_query': 'Database query failed',
    'user_not_found': 'User not found in database',
    'team_not_found': 'Team not found',
    'hackathon_not_found': 'Hackathon not found',
    'permission_denied': 'User does not have permission',
    'invalid_input': 'Invalid user input',
    'telegram_error': 'Telegram API error',
}
