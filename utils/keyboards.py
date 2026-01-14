"""
Keyboard layouts for Hackathon Bot
Includes both inline and reply keyboards
"""

from typing import List, Optional, Dict, Any
from telegram import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from locales.translations import t, LANGUAGES


def remove_keyboard():
    """Remove custom keyboard"""
    return ReplyKeyboardRemove()


# =============================================================================
# MAIN MENU KEYBOARD
# =============================================================================

def main_menu_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Main menu reply keyboard shown at bottom"""
    keyboard = [
        [
            KeyboardButton(t('btn_hackathons', lang)),
            KeyboardButton(t('btn_settings', lang))
        ],
        [
            KeyboardButton(t('btn_my_hackathons', lang)),
            KeyboardButton(t('btn_help', lang))
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True,
        is_persistent=True
    )


def main_menu_inline(lang: str = 'uz') -> InlineKeyboardMarkup:
    """Main menu as inline keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(t('btn_hackathons', lang), callback_data='hackathons'),
            InlineKeyboardButton(t('btn_settings', lang), callback_data='settings')
        ],
        [
            InlineKeyboardButton(t('btn_my_hackathons', lang), callback_data='my_hackathons'),
            InlineKeyboardButton(t('btn_help', lang), callback_data='help')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# =============================================================================
# REGISTRATION KEYBOARDS
# =============================================================================

def phone_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Keyboard with phone number request button"""
    keyboard = [
        [KeyboardButton(t('btn_send_phone', lang), request_contact=True)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def gender_keyboard(lang: str = 'uz') -> InlineKeyboardMarkup:
    """Gender selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(t('gender_male', lang), callback_data='gender_male'),
            InlineKeyboardButton(t('gender_female', lang), callback_data='gender_female')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def skip_keyboard(lang: str = 'uz') -> InlineKeyboardMarkup:
    """Skip button for optional fields"""
    keyboard = [
        [InlineKeyboardButton("⏭️ Skip", callback_data='skip')]
    ]
    return InlineKeyboardMarkup(keyboard)


def portfolio_keyboard(lang: str = 'uz') -> InlineKeyboardMarkup:
    """Portfolio prompt keyboard with skip option"""
    keyboard = [
        [InlineKeyboardButton(t('btn_no_portfolio', lang), callback_data='no_portfolio')]
    ]
    return InlineKeyboardMarkup(keyboard)


def privacy_consent_keyboard(lang: str = 'uz') -> InlineKeyboardMarkup:
    """Privacy consent keyboard"""
    keyboard = [
        [InlineKeyboardButton(t('btn_accept_privacy', lang), callback_data='accept_privacy')],
        [InlineKeyboardButton(t('btn_decline_privacy', lang), callback_data='decline_privacy')]
    ]
    return InlineKeyboardMarkup(keyboard)


# =============================================================================
# LANGUAGE KEYBOARDS
# =============================================================================

def language_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(
                f"{LANGUAGES['uz']['flag']} {LANGUAGES['uz']['name']}", 
                callback_data='lang_uz'
            ),
            InlineKeyboardButton(
                f"{LANGUAGES['ru']['flag']} {LANGUAGES['ru']['name']}", 
                callback_data='lang_ru'
            ),
            InlineKeyboardButton(
                f"{LANGUAGES['en']['flag']} {LANGUAGES['en']['name']}", 
                callback_data='lang_en'
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# =============================================================================
# HACKATHON KEYBOARDS
# =============================================================================

def hackathons_list_keyboard(
    hackathons: List[Dict[str, Any]], 
    lang: str = 'uz'
) -> InlineKeyboardMarkup:
    """List of available hackathons"""
    keyboard = []
    for h in hackathons:
        keyboard.append([
            InlineKeyboardButton(
                f"🏆 {h['name']}", 
                callback_data=f"hackathon_{h['id']}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton(t('btn_back', lang), callback_data='main_menu')
    ])
    return InlineKeyboardMarkup(keyboard)


def hackathon_detail_keyboard(
    hackathon_id: int,
    is_registered: bool = False,
    active_stage: Optional[Dict] = None,
    lang: str = 'uz'
) -> InlineKeyboardMarkup:
    """Hackathon detail view keyboard"""
    keyboard = []
    
    # Show register button if not registered
    if not is_registered:
        keyboard.append([
            InlineKeyboardButton(
                t('btn_register', lang), 
                callback_data=f"register_{hackathon_id}"
            )
        ])
    
    # Show active stage button if registered and stage is active
    if is_registered and active_stage:
        stage_num = active_stage['stage_number']
        keyboard.append([
            InlineKeyboardButton(
                f"{stage_num} Stage {stage_num}",
                callback_data=f"stage_{active_stage['id']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(t('btn_back', lang), callback_data='hackathons')
    ])
    
    return InlineKeyboardMarkup(keyboard)


def user_hackathons_keyboard(
    teams: List[Dict[str, Any]], 
    lang: str = 'uz'
) -> InlineKeyboardMarkup:
    """List of user's hackathons/teams"""
    keyboard = []
    for team in teams:
        keyboard.append([
            InlineKeyboardButton(
                f"🏆 {team['hackathon_name']}", 
                callback_data=f"my_team_{team['id']}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton(t('btn_back', lang), callback_data='main_menu')
    ])
    return InlineKeyboardMarkup(keyboard)


# =============================================================================
# TEAM KEYBOARDS
# =============================================================================

def team_detail_keyboard(
    team_id: int,
    is_owner: bool = False,
    hackathon_id: int = None,
    active_stage: Optional[Dict] = None,
    lang: str = 'uz'
) -> InlineKeyboardMarkup:
    """Team detail view keyboard"""
    keyboard = []
    
    # See hackathon details
    keyboard.append([
        InlineKeyboardButton(t('btn_see_details', lang), callback_data=f"hackathon_{hackathon_id}")
    ])
    
    # Active stage button
    if active_stage:
        stage_num = active_stage['stage_number']
        keyboard.append([
            InlineKeyboardButton(
                f"{stage_num} Stage {stage_num}",
                callback_data=f"stage_{active_stage['id']}"
            )
        ])
    
    # Leave team
    keyboard.append([
        InlineKeyboardButton(t('btn_leave_team', lang), callback_data=f"leave_team_{team_id}")
    ])
    
    # Remove member (only for owner)
    if is_owner:
        keyboard.append([
            InlineKeyboardButton(
                t('btn_remove_member', lang), 
                callback_data=f"remove_member_{team_id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(t('btn_back', lang), callback_data='my_hackathons')
    ])
    
    return InlineKeyboardMarkup(keyboard)


def team_members_keyboard(
    members: List[Dict[str, Any]],
    team_id: int,
    lang: str = 'uz'
) -> InlineKeyboardMarkup:
    """Select team member to remove"""
    keyboard = []
    for member in members:
        if not member['is_team_lead']:  # Can't remove team lead
            name = f"{member['first_name']} {member.get('last_name', '')}".strip()
            keyboard.append([
                InlineKeyboardButton(
                    f"❌ {name}", 
                    callback_data=f"kick_{team_id}_{member['telegram_id']}"
                )
            ])
    keyboard.append([
        InlineKeyboardButton(t('btn_back', lang), callback_data=f"my_team_{team_id}")
    ])
    return InlineKeyboardMarkup(keyboard)


def confirm_leave_keyboard(team_id: int, lang: str = 'uz') -> InlineKeyboardMarkup:
    """Confirm leaving team"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Ha / Да / Yes", callback_data=f"confirm_leave_{team_id}"),
            InlineKeyboardButton("❌ Yo'q / Нет / No", callback_data=f"my_team_{team_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# =============================================================================
# STAGE KEYBOARDS
# =============================================================================

def stage_keyboard(
    stage_id: int,
    team_id: int,
    has_submission: bool = False,
    lang: str = 'uz'
) -> InlineKeyboardMarkup:
    """Stage view keyboard"""
    keyboard = []
    
    if not has_submission:
        keyboard.append([
            InlineKeyboardButton(
                "📤 Submit / Topshirish / Отправить", 
                callback_data=f"submit_{stage_id}_{team_id}"
            )
        ])
    else:
        keyboard.append([
            InlineKeyboardButton(
                "✏️ Update submission", 
                callback_data=f"submit_{stage_id}_{team_id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(t('btn_back', lang), callback_data='my_hackathons')
    ])
    
    return InlineKeyboardMarkup(keyboard)


# =============================================================================
# SETTINGS KEYBOARDS
# =============================================================================

def settings_keyboard(lang: str = 'uz') -> InlineKeyboardMarkup:
    """Settings menu keyboard"""
    keyboard = [
        [InlineKeyboardButton(t('btn_change_language', lang), callback_data='change_language')],
        [InlineKeyboardButton(t('btn_edit_personal_data', lang), callback_data='edit_personal_data')],
        [InlineKeyboardButton(t('btn_back', lang), callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)


def edit_data_keyboard(lang: str = 'uz') -> InlineKeyboardMarkup:
    """Edit personal data keyboard"""
    keyboard = [
        [InlineKeyboardButton(t('btn_change_first_name', lang), callback_data='edit_first_name')],
        [InlineKeyboardButton(t('btn_change_last_name', lang), callback_data='edit_last_name')],
        [InlineKeyboardButton(t('btn_change_birth_date', lang), callback_data='edit_birth_date')],
        [InlineKeyboardButton(t('btn_change_gender', lang), callback_data='edit_gender')],
        [InlineKeyboardButton(t('btn_change_location', lang), callback_data='edit_location')],
        [InlineKeyboardButton(t('btn_back', lang), callback_data='settings')]
    ]
    return InlineKeyboardMarkup(keyboard)


# =============================================================================
# ADMIN KEYBOARDS
# =============================================================================

def admin_keyboard(lang: str = 'uz') -> InlineKeyboardMarkup:
    """Admin panel keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Statistics", callback_data='admin_stats'),
            InlineKeyboardButton("📢 Broadcast", callback_data='admin_broadcast')
        ],
        [
            InlineKeyboardButton("📥 Export Users", callback_data='admin_export_users'),
            InlineKeyboardButton("📥 Export Teams", callback_data='admin_export_teams')
        ],
        [
            InlineKeyboardButton("➕ Add Hackathon", callback_data='admin_add_hackathon'),
            InlineKeyboardButton("📋 Manage Stages", callback_data='admin_manage_stages')
        ],
        [InlineKeyboardButton(t('btn_back', lang), callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)


def hackathon_select_keyboard(
    hackathons: List[Dict[str, Any]],
    action: str,
    lang: str = 'uz'
) -> InlineKeyboardMarkup:
    """Select hackathon for admin actions"""
    keyboard = []
    for h in hackathons:
        keyboard.append([
            InlineKeyboardButton(
                h['name'], 
                callback_data=f"{action}_{h['id']}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton(t('btn_back', lang), callback_data='admin_panel')
    ])
    return InlineKeyboardMarkup(keyboard)


# =============================================================================
# CONFIRMATION KEYBOARDS
# =============================================================================

def yes_no_keyboard(
    yes_callback: str,
    no_callback: str,
    lang: str = 'uz'
) -> InlineKeyboardMarkup:
    """Generic yes/no confirmation"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes", callback_data=yes_callback),
            InlineKeyboardButton("❌ No", callback_data=no_callback)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def cancel_keyboard(lang: str = 'uz') -> InlineKeyboardMarkup:
    """Cancel button"""
    keyboard = [
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel')]
    ]
    return InlineKeyboardMarkup(keyboard)


def back_keyboard(callback: str, lang: str = 'uz') -> InlineKeyboardMarkup:
    """Single back button"""
    keyboard = [
        [InlineKeyboardButton(t('btn_back', lang), callback_data=callback)]
    ]
    return InlineKeyboardMarkup(keyboard)
