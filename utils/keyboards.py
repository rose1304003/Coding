"""
Keyboard layouts for Hackathon Bot
Supports both Reply and Inline keyboards
"""

from telegram import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove
)
from locales.translations import t, LANGUAGES


def remove_keyboard():
    """Remove reply keyboard."""
    return ReplyKeyboardRemove()


# =============================================================================
# REPLY KEYBOARDS (persistent menu buttons)
# =============================================================================

def main_menu_keyboard(lang: str = 'uz'):
    """Main menu reply keyboard."""
    keyboard = [
        [KeyboardButton(t('btn_hackathons', lang)), KeyboardButton(t('btn_my_hackathons', lang))],
        [KeyboardButton(t('btn_settings', lang)), KeyboardButton(t('btn_help', lang))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def phone_keyboard(lang: str = 'uz'):
    """Phone number request keyboard."""
    keyboard = [
        [KeyboardButton(t('btn_send_phone', lang), request_contact=True)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


# =============================================================================
# INLINE KEYBOARDS
# =============================================================================

def language_keyboard():
    """Language selection inline keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(f"{LANGUAGES['uz']['flag']} {LANGUAGES['uz']['name']}", callback_data='lang_uz'),
            InlineKeyboardButton(f"{LANGUAGES['ru']['flag']} {LANGUAGES['ru']['name']}", callback_data='lang_ru'),
            InlineKeyboardButton(f"{LANGUAGES['en']['flag']} {LANGUAGES['en']['name']}", callback_data='lang_en')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def offer_keyboard(lang: str = 'uz'):
    """Offer/consent keyboard with read, agree, decline buttons."""
    keyboard = [
        [InlineKeyboardButton(t('btn_read_offer', lang), callback_data='offer_read')],
        [
            InlineKeyboardButton(t('btn_agree', lang), callback_data='offer_agree'),
            InlineKeyboardButton(t('btn_decline', lang), callback_data='offer_decline')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def offer_read_keyboard(lang: str = 'uz'):
    """Keyboard shown after reading offer."""
    keyboard = [
        [
            InlineKeyboardButton(t('btn_agree', lang), callback_data='offer_agree'),
            InlineKeyboardButton(t('btn_decline', lang), callback_data='offer_decline')
        ],
        [InlineKeyboardButton(t('btn_back', lang), callback_data='offer_back')]
    ]
    return InlineKeyboardMarkup(keyboard)


def main_menu_inline(lang: str = 'uz'):
    """Main menu as inline keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(t('btn_hackathons', lang), callback_data='hackathons'),
            InlineKeyboardButton(t('btn_my_hackathons', lang), callback_data='my_hackathons')
        ],
        [
            InlineKeyboardButton(t('btn_settings', lang), callback_data='settings'),
            InlineKeyboardButton(t('btn_help', lang), callback_data='help')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def gender_keyboard(lang: str = 'uz'):
    """Gender selection keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(t('gender_male', lang), callback_data='gender_male'),
            InlineKeyboardButton(t('gender_female', lang), callback_data='gender_female')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def hackathons_list_keyboard(hackathons: list, lang: str = 'uz'):
    """List of hackathons as inline buttons."""
    keyboard = []
    for h in hackathons:
        keyboard.append([
            InlineKeyboardButton(f"🏆 {h['name']}", callback_data=f"hackathon_{h['id']}")
        ])
    keyboard.append([InlineKeyboardButton(t('btn_back', lang), callback_data='main_menu')])
    return InlineKeyboardMarkup(keyboard)


def hackathon_detail_keyboard(hackathon_id: int, is_registered: bool, lang: str = 'uz'):
    """Hackathon detail view keyboard."""
    keyboard = []
    
    if not is_registered:
        keyboard.append([InlineKeyboardButton(t('btn_register', lang), callback_data=f"register_{hackathon_id}")])
    
    keyboard.append([InlineKeyboardButton(t('btn_back', lang), callback_data='hackathons')])
    return InlineKeyboardMarkup(keyboard)


def registration_option_keyboard(hackathon_id: int, lang: str = 'uz'):
    """Registration options - create team or join existing."""
    keyboard = [
        [InlineKeyboardButton(t('btn_create_team', lang), callback_data=f"create_team_{hackathon_id}")],
        [InlineKeyboardButton(t('btn_join_team', lang), callback_data=f"join_team_{hackathon_id}")],
        [InlineKeyboardButton(t('btn_back', lang), callback_data=f"hackathon_{hackathon_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)


def user_hackathons_keyboard(teams: list, lang: str = 'uz'):
    """User's hackathons/teams list."""
    keyboard = []
    for t_info in teams:
        keyboard.append([
            InlineKeyboardButton(f"🏆 {t_info['hackathon_name']}", callback_data=f"team_{t_info['id']}")
        ])
    keyboard.append([InlineKeyboardButton(t('btn_back', lang), callback_data='main_menu')])
    return InlineKeyboardMarkup(keyboard)


def team_detail_keyboard(team_id: int, is_owner: bool, hackathon_id: int, 
                         active_stage: dict = None, lang: str = 'uz'):
    """Team detail view keyboard."""
    keyboard = []
    
    # Show active stage button if available
    if active_stage:
        keyboard.append([
            InlineKeyboardButton(
                f"📋 Stage {active_stage['stage_number']}", 
                callback_data=f"stage_{active_stage['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(t('btn_see_details', lang), callback_data=f"hackathon_{hackathon_id}")])
    
    if is_owner:
        keyboard.append([InlineKeyboardButton(t('btn_remove_member', lang), callback_data=f"remove_members_{team_id}")])
    
    keyboard.append([InlineKeyboardButton(t('btn_leave_team', lang), callback_data=f"leave_team_{team_id}")])
    keyboard.append([InlineKeyboardButton(t('btn_back', lang), callback_data='my_hackathons')])
    
    return InlineKeyboardMarkup(keyboard)


def stage_keyboard(stage_id: int, team_id: int, has_submission: bool, 
                   deadline_passed: bool = False, lang: str = 'uz'):
    """Stage view keyboard with submit button."""
    keyboard = []
    
    if not deadline_passed:
        if has_submission:
            keyboard.append([
                InlineKeyboardButton(t('btn_view_submission', lang), callback_data=f"view_submission_{stage_id}_{team_id}"),
                InlineKeyboardButton(t('btn_submit', lang), callback_data=f"submit_{stage_id}_{team_id}")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(t('btn_submit', lang), callback_data=f"submit_{stage_id}_{team_id}")
            ])
    else:
        if has_submission:
            keyboard.append([
                InlineKeyboardButton(t('btn_view_submission', lang), callback_data=f"view_submission_{stage_id}_{team_id}")
            ])
    
    keyboard.append([InlineKeyboardButton(t('btn_back', lang), callback_data=f"team_{team_id}")])
    return InlineKeyboardMarkup(keyboard)


def confirm_leave_keyboard(team_id: int, lang: str = 'uz'):
    """Confirm leave team keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(t('btn_confirm', lang), callback_data=f"confirm_leave_{team_id}"),
            InlineKeyboardButton(t('btn_cancel', lang), callback_data=f"team_{team_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def team_members_keyboard(members: list, team_id: int, lang: str = 'uz'):
    """Team members list for removal (excluding team lead)."""
    keyboard = []
    for m in members:
        if not m.get('is_team_lead'):
            name = f"{m.get('first_name', '')} {m.get('last_name', '')}".strip()
            keyboard.append([
                InlineKeyboardButton(f"❌ {name}", callback_data=f"remove_member_{team_id}_{m['user_id']}")
            ])
    keyboard.append([InlineKeyboardButton(t('btn_back', lang), callback_data=f"team_{team_id}")])
    return InlineKeyboardMarkup(keyboard)


def settings_keyboard(lang: str = 'uz'):
    """Settings menu keyboard."""
    keyboard = [
        [InlineKeyboardButton(t('btn_change_language', lang), callback_data='change_language')],
        [InlineKeyboardButton(t('btn_edit_personal_data', lang), callback_data='edit_personal_data')],
        [InlineKeyboardButton(t('btn_back', lang), callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)


def edit_data_keyboard(lang: str = 'uz'):
    """Edit personal data keyboard."""
    keyboard = [
        [InlineKeyboardButton(t('btn_change_first_name', lang), callback_data='edit_first_name')],
        [InlineKeyboardButton(t('btn_change_last_name', lang), callback_data='edit_last_name')],
        [InlineKeyboardButton(t('btn_change_birth_date', lang), callback_data='edit_birth_date')],
        [InlineKeyboardButton(t('btn_change_gender', lang), callback_data='edit_gender')],
        [InlineKeyboardButton(t('btn_change_location', lang), callback_data='edit_location')],
        [InlineKeyboardButton(t('btn_back', lang), callback_data='settings')]
    ]
    return InlineKeyboardMarkup(keyboard)


def portfolio_keyboard(lang: str = 'uz'):
    """Portfolio input keyboard with skip option."""
    keyboard = [
        [InlineKeyboardButton(t('btn_no_portfolio', lang), callback_data='no_portfolio')],
        [InlineKeyboardButton(t('btn_cancel', lang), callback_data='cancel')]
    ]
    return InlineKeyboardMarkup(keyboard)


def back_keyboard(callback_data: str, lang: str = 'uz'):
    """Simple back button keyboard."""
    keyboard = [[InlineKeyboardButton(t('btn_back', lang), callback_data=callback_data)]]
    return InlineKeyboardMarkup(keyboard)


def cancel_keyboard(lang: str = 'uz'):
    """Cancel button keyboard."""
    keyboard = [[InlineKeyboardButton(t('btn_cancel', lang), callback_data='cancel')]]
    return InlineKeyboardMarkup(keyboard)


# =============================================================================
# ADMIN KEYBOARDS
# =============================================================================

def admin_hackathons_keyboard(hackathons: list, lang: str = 'uz'):
    """Admin hackathon selection keyboard."""
    keyboard = []
    for h in hackathons:
        keyboard.append([
            InlineKeyboardButton(f"🏆 {h['name']}", callback_data=f"admin_hackathon_{h['id']}")
        ])
    keyboard.append([InlineKeyboardButton(t('btn_cancel', lang), callback_data='admin_cancel')])
    return InlineKeyboardMarkup(keyboard)


def admin_stages_keyboard(stages: list, hackathon_id: int, lang: str = 'uz'):
    """Admin stage selection keyboard."""
    keyboard = []
    for s in stages:
        status = "✅" if s.get('is_active') else "⏸"
        keyboard.append([
            InlineKeyboardButton(
                f"{status} Stage {s['stage_number']}: {s['name']}", 
                callback_data=f"admin_stage_{s['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton(t('btn_cancel', lang), callback_data='admin_cancel')])
    return InlineKeyboardMarkup(keyboard)
