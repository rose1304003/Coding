"""
Main handlers for Hackathon Bot
Handles user commands and callback queries
"""

import logging
from datetime import datetime
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import database as db
from locales.translations import t
from utils.keyboards import (
    main_menu_keyboard, main_menu_inline, language_keyboard,
    hackathons_list_keyboard, hackathon_detail_keyboard,
    user_hackathons_keyboard, team_detail_keyboard,
    settings_keyboard, edit_data_keyboard, phone_keyboard,
    gender_keyboard, portfolio_keyboard, stage_keyboard,
    confirm_leave_keyboard, team_members_keyboard,
    back_keyboard, remove_keyboard
)
from utils.helpers import (
    validate_date, validate_pinfl, validate_url, validate_phone,
    format_date, format_gender, format_member_list,
    UserState, clean_name
)

logger = logging.getLogger(__name__)


# =============================================================================
# COMMAND HANDLERS
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - register user or show welcome back."""
    user = update.effective_user
    telegram_id = user.id
    
    # Check for deep link (team join)
    if context.args and context.args[0].startswith('join_'):
        team_code = context.args[0].replace('join_', '')
        await handle_team_join(update, context, team_code)
        return
    
    # Check if user exists
    existing_user = await db.get_user(telegram_id)
    
    if existing_user:
        # Welcome back existing user
        lang = existing_user.get('language', 'uz')
        await update.message.reply_text(
            t('welcome_back', lang),
            reply_markup=main_menu_keyboard(lang)
        )
        await db.log_action(telegram_id, 'returned', {'via': 'start_command'})
    else:
        # New user - show welcome message first
        await db.add_user(
            telegram_id=telegram_id,
            first_name=user.first_name or "User",
            username=user.username,
            last_name=user.last_name
        )
        
        # Show welcome message (in English by default, user will select language next)
        await update.message.reply_text(
            t('welcome', 'en'),
            reply_markup=language_keyboard()
        )
        
        await db.log_action(telegram_id, 'started_registration', {})


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    user = await db.get_user(update.effective_user.id)
    lang = user.get('language', 'uz') if user else 'uz'
    
    await update.message.reply_text(
        t('help_message', lang),
        reply_markup=main_menu_keyboard(lang)
    )


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command."""
    user = await db.get_user(update.effective_user.id)
    lang = user.get('language', 'uz') if user else 'uz'
    
    await update.message.reply_text(
        t('settings_menu', lang),
        reply_markup=settings_keyboard(lang)
    )


async def exit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /exit command - deactivate user."""
    telegram_id = update.effective_user.id
    user = await db.get_user(telegram_id)
    
    if user:
        await db.deactivate_user(telegram_id)
        await db.log_action(telegram_id, 'deactivated', {'via': 'exit_command'})
        await update.message.reply_text(
            "👋 Goodbye! Your account has been deactivated.\n"
            "You can return anytime with /start",
            reply_markup=remove_keyboard()
        )
    else:
        await update.message.reply_text("You don't have an active account.")


# =============================================================================
# MESSAGE HANDLERS (for reply keyboard and text input)
# =============================================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages - route to appropriate handler based on state or button."""
    telegram_id = update.effective_user.id
    text = update.message.text
    
    user = await db.get_user(telegram_id)
    if not user:
        await update.message.reply_text(
            "Please start the bot first with /start",
            reply_markup=remove_keyboard()
        )
        return
    
    lang = user.get('language', 'uz')
    
    # Check if it's a menu button press
    if text == t('btn_hackathons', lang):
        await show_hackathons(update, context, lang)
        return
    elif text == t('btn_my_hackathons', lang):
        await show_my_hackathons(update, context, lang)
        return
    elif text == t('btn_settings', lang):
        await update.message.reply_text(
            t('settings_menu', lang),
            reply_markup=settings_keyboard(lang)
        )
        return
    elif text == t('btn_help', lang):
        await update.message.reply_text(
            t('help_message', lang),
            reply_markup=main_menu_keyboard(lang)
        )
        return
    
    # Check registration state
    state = await db.get_registration_state(telegram_id)
    if state:
        await handle_registration_input(update, context, state, lang)
        return
    
    # Default response
    await update.message.reply_text(
        t('main_menu', lang),
        reply_markup=main_menu_keyboard(lang)
    )


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle shared contact (phone number)."""
    telegram_id = update.effective_user.id
    contact = update.message.contact
    
    user = await db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    
    state = await db.get_registration_state(telegram_id)
    
    if state and state['current_step'] == UserState.REG_PHONE:
        # Save phone number
        await db.update_user(telegram_id, phone=contact.phone_number)
        
        # Move to PINFL
        await db.set_registration_state(telegram_id, UserState.REG_PINFL, state.get('data', {}))
        await update.message.reply_text(
            t('enter_pinfl', lang),
            reply_markup=main_menu_keyboard(lang)
        )


# =============================================================================
# REGISTRATION FLOW
# =============================================================================

async def handle_registration_input(update: Update, context: ContextTypes.DEFAULT_TYPE, state: dict, lang: str):
    """Handle registration flow text inputs."""
    telegram_id = update.effective_user.id
    text = update.message.text.strip()
    current_step = state['current_step']
    data = state.get('data', {})
    
    if current_step == UserState.REG_FIRST_NAME:
        await db.update_user(telegram_id, first_name=clean_name(text))
        await db.set_registration_state(telegram_id, UserState.REG_LAST_NAME, data)
        await update.message.reply_text(t('enter_last_name', lang))
        
    elif current_step == UserState.REG_LAST_NAME:
        await db.update_user(telegram_id, last_name=clean_name(text))
        await db.set_registration_state(telegram_id, UserState.REG_BIRTH_DATE, data)
        await update.message.reply_text(t('enter_birth_date', lang))
        
    elif current_step == UserState.REG_BIRTH_DATE:
        is_valid, parsed_date = validate_date(text)
        if not is_valid:
            await update.message.reply_text(t('invalid_date', lang))
            return
        await db.update_user(telegram_id, birth_date=parsed_date)
        await db.set_registration_state(telegram_id, UserState.REG_GENDER, data)
        await update.message.reply_text(
            t('enter_gender', lang),
            reply_markup=gender_keyboard(lang)
        )
        
    elif current_step == UserState.REG_LOCATION:
        await db.update_user(telegram_id, location=text)
        await db.set_registration_state(telegram_id, UserState.REG_PHONE, data)
        await update.message.reply_text(
            t('enter_phone', lang),
            reply_markup=phone_keyboard(lang)
        )
        
    elif current_step == UserState.REG_PINFL:
        if not validate_pinfl(text):
            await update.message.reply_text(t('invalid_pinfl', lang))
            return
        await db.update_user(telegram_id, pinfl=text)
        await db.clear_registration_state(telegram_id)
        await db.log_action(telegram_id, 'completed_registration', {})
        await update.message.reply_text(
            t('registration_almost_done', lang),
            reply_markup=main_menu_keyboard(lang)
        )
        
    # Team creation flow
    elif current_step == UserState.TEAM_NAME:
        data['team_name'] = text
        await db.set_registration_state(telegram_id, UserState.TEAM_ROLE, data)
        await update.message.reply_text(t('enter_team_role', lang))
        
    elif current_step == UserState.TEAM_ROLE:
        data['team_role'] = text
        await db.set_registration_state(telegram_id, UserState.TEAM_FIELD, data)
        await update.message.reply_text(t('enter_field', lang))
        
    elif current_step == UserState.TEAM_FIELD:
        data['team_field'] = text
        await db.set_registration_state(telegram_id, UserState.TEAM_PORTFOLIO, data)
        await update.message.reply_text(
            t('enter_portfolio', lang),
            reply_markup=portfolio_keyboard(lang)
        )
        
    elif current_step == UserState.TEAM_PORTFOLIO:
        if not validate_url(text):
            await update.message.reply_text(t('invalid_link', lang))
            return
        data['portfolio'] = text
        await complete_team_creation(update, context, data, lang)
        
    elif current_step == UserState.SUBMIT_LINK:
        if not validate_url(text):
            await update.message.reply_text(t('invalid_link', lang))
            return
        stage_id = data.get('stage_id')
        team_id = data.get('team_id')
        await db.create_submission(team_id, stage_id, text)
        await db.clear_registration_state(telegram_id)
        await db.log_action(telegram_id, 'submitted', {'stage_id': stage_id, 'link': text})
        await update.message.reply_text(
            t('submission_received', lang, link=text),
            reply_markup=main_menu_keyboard(lang)
        )
        
    # Edit flows
    elif current_step == UserState.EDIT_FIRST_NAME:
        await db.update_user(telegram_id, first_name=clean_name(text))
        await db.clear_registration_state(telegram_id)
        await update.message.reply_text(t('data_updated', lang))
        await show_personal_data(update, context, lang)
        
    elif current_step == UserState.EDIT_LAST_NAME:
        await db.update_user(telegram_id, last_name=clean_name(text))
        await db.clear_registration_state(telegram_id)
        await update.message.reply_text(t('data_updated', lang))
        await show_personal_data(update, context, lang)
        
    elif current_step == UserState.EDIT_BIRTH_DATE:
        is_valid, parsed_date = validate_date(text)
        if not is_valid:
            await update.message.reply_text(t('invalid_date', lang))
            return
        await db.update_user(telegram_id, birth_date=parsed_date)
        await db.clear_registration_state(telegram_id)
        await update.message.reply_text(t('data_updated', lang))
        await show_personal_data(update, context, lang)
        
    elif current_step == UserState.EDIT_LOCATION:
        await db.update_user(telegram_id, location=text)
        await db.clear_registration_state(telegram_id)
        await update.message.reply_text(t('data_updated', lang))
        await show_personal_data(update, context, lang)


async def complete_team_creation(update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict, lang: str):
    """Complete team creation process."""
    telegram_id = update.effective_user.id
    
    team = await db.create_team(
        hackathon_id=data['hackathon_id'],
        name=data['team_name'],
        owner_id=telegram_id,
        owner_role=data['team_role'],
        field=data.get('team_field'),
        portfolio_link=data.get('portfolio')
    )
    
    await db.clear_registration_state(telegram_id)
    await db.log_action(telegram_id, 'created_team', {'team_id': team['id']})
    
    # Show team creation confirmation with code
    await update.message.reply_text(
        t('team_created', lang, name=team['name'], code=team['code']),
        reply_markup=main_menu_keyboard(lang)
    )
    
    # Show team info with buttons
    await show_team_details(update, context, team['id'], lang, is_callback=False)


# =============================================================================
# DISPLAY HELPERS
# =============================================================================

async def show_hackathons(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    """Show list of available hackathons."""
    hackathons = await db.get_active_hackathons()
    
    if not hackathons:
        await update.message.reply_text(
            t('no_hackathons', lang),
            reply_markup=main_menu_keyboard(lang)
        )
        return
    
    await update.message.reply_text(
        t('btn_hackathons', lang),
        reply_markup=hackathons_list_keyboard(hackathons, lang)
    )


async def show_my_hackathons(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    """Show user's hackathons/teams."""
    telegram_id = update.effective_user.id
    teams = await db.get_user_teams(telegram_id)
    
    if not teams:
        await update.message.reply_text(
            t('no_registered_hackathons', lang),
            reply_markup=main_menu_keyboard(lang)
        )
        return
    
    await update.message.reply_text(
        t('your_hackathons', lang),
        reply_markup=user_hackathons_keyboard(teams, lang)
    )


async def show_personal_data(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    """Show user's personal data."""
    telegram_id = update.effective_user.id
    user = await db.get_user(telegram_id)
    
    text = t('your_data', lang,
        first_name=user.get('first_name', '—'),
        last_name=user.get('last_name', '—'),
        birth_date=format_date(user.get('birth_date'), lang),
        gender=format_gender(user.get('gender'), lang),
        location=user.get('location', '—')
    )
    
    if hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=edit_data_keyboard(lang)
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=edit_data_keyboard(lang)
        )


async def show_team_details(update: Update, context: ContextTypes.DEFAULT_TYPE, team_id: int, lang: str, is_callback: bool = True):
    """Show team details."""
    team = await db.get_team(team_id)
    if not team:
        return
    
    members = await db.get_team_members(team_id)
    active_stage = await db.get_active_stage(team['hackathon_id'])
    
    telegram_id = update.effective_user.id
    is_owner = team['owner_id'] == telegram_id
    
    text = t('team_info', lang,
        hackathon=team.get('hackathon_name', ''),
        name=team['name'],
        code=team['code'],
        members=format_member_list(members, lang)
    )
    
    keyboard = team_detail_keyboard(
        team_id=team_id,
        is_owner=is_owner,
        hackathon_id=team['hackathon_id'],
        active_stage=active_stage,
        lang=lang
    )
    
    if is_callback and hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=keyboard)
    else:
        await update.message.reply_text(text, reply_markup=keyboard)


# =============================================================================
# CALLBACK QUERY HANDLER
# =============================================================================

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries from inline keyboards."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = update.effective_user.id
    data = query.data
    
    user = await db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    
    # Parse callback data
    parts = data.split('_')
    action = parts[0]
    
    # Language selection
    if data.startswith('lang_'):
        new_lang = data.replace('lang_', '')
        await db.update_user(telegram_id, language=new_lang)
        lang = new_lang
        
        # Check if this is initial registration
        state = await db.get_registration_state(telegram_id)
        if not state:
            # Show welcome message in selected language, then start registration
            await query.edit_message_text(
                t('welcome', lang),
                reply_markup=None  # Remove keyboard after language selection
            )
            # Start registration flow
            await db.set_registration_state(telegram_id, UserState.REG_FIRST_NAME, {})
            await context.bot.send_message(
                chat_id=telegram_id,
                text=t('enter_first_name', lang)
            )
        else:
            await query.edit_message_text(
                t('language_changed', lang),
                reply_markup=settings_keyboard(lang)
            )
        return
    
    # Main menu
    if data == 'main_menu':
        await query.edit_message_text(
            t('main_menu', lang),
            reply_markup=main_menu_inline(lang)
        )
        return
    
    # Hackathons list
    if data == 'hackathons':
        hackathons = await db.get_active_hackathons()
        if not hackathons:
            await query.edit_message_text(
                t('no_hackathons', lang),
                reply_markup=back_keyboard('main_menu', lang)
            )
        else:
            await query.edit_message_text(
                t('btn_hackathons', lang),
                reply_markup=hackathons_list_keyboard(hackathons, lang)
            )
        return
    
    # My hackathons
    if data == 'my_hackathons':
        teams = await db.get_user_teams(telegram_id)
        if not teams:
            await query.edit_message_text(
                t('no_registered_hackathons', lang),
                reply_markup=back_keyboard('main_menu', lang)
            )
        else:
            await query.edit_message_text(
                t('your_hackathons', lang),
                reply_markup=user_hackathons_keyboard(teams, lang)
            )
        return
    
    # Hackathon detail
    if data.startswith('hackathon_'):
        hackathon_id = int(parts[1])
        hackathon = await db.get_hackathon(hackathon_id)
        if not hackathon:
            await query.edit_message_text(t('error_occurred', lang))
            return
        
        user_team = await db.get_user_team_for_hackathon(telegram_id, hackathon_id)
        active_stage = await db.get_active_stage(hackathon_id)
        
        text = t('hackathon_info', lang,
            name=hackathon['name'],
            description=hackathon.get('description', '—'),
            prize=hackathon.get('prize_pool', '—'),
            start=format_date(hackathon.get('start_date'), lang),
            end=format_date(hackathon.get('end_date'), lang),
            deadline=format_date(hackathon.get('registration_deadline'), lang) if hackathon.get('registration_deadline') else '—'
        )
        
        await query.edit_message_text(
            text,
            reply_markup=hackathon_detail_keyboard(
                hackathon_id,
                is_registered=user_team is not None,
                active_stage=active_stage,
                lang=lang
            )
        )
        return
    
    # Register for hackathon
    if data.startswith('register_'):
        hackathon_id = int(parts[1])
        
        # Check if already registered
        existing_team = await db.get_user_team_for_hackathon(telegram_id, hackathon_id)
        if existing_team:
            await query.answer("You're already registered!", show_alert=True)
            return
        
        # Start team creation flow
        await db.set_registration_state(telegram_id, UserState.TEAM_NAME, {'hackathon_id': hackathon_id})
        await query.edit_message_text(t('enter_team_name', lang))
        return
    
    # View team details
    if data.startswith('my_team_'):
        team_id = int(parts[2])
        team = await db.get_team(team_id)
        if not team:
            await query.edit_message_text(t('error_occurred', lang))
            return
        
        members = await db.get_team_members(team_id)
        active_stage = await db.get_active_stage(team['hackathon_id'])
        is_owner = team['owner_id'] == telegram_id
        
        text = t('team_info', lang,
            hackathon=team.get('hackathon_name', ''),
            name=team['name'],
            code=team['code'],
            members=format_member_list(members, lang)
        )
        
        await query.edit_message_text(
            text,
            reply_markup=team_detail_keyboard(
                team_id=team_id,
                is_owner=is_owner,
                hackathon_id=team['hackathon_id'],
                active_stage=active_stage,
                lang=lang
            )
        )
        return
    
    # Leave team
    if data.startswith('leave_team_'):
        team_id = int(parts[2])
        await query.edit_message_text(
            "Are you sure you want to leave this team?",
            reply_markup=confirm_leave_keyboard(team_id, lang)
        )
        return
    
    if data.startswith('confirm_leave_'):
        team_id = int(parts[2])
        result = await db.leave_team(team_id, telegram_id)
        if result['success']:
            await db.log_action(telegram_id, 'left_team', {'team_id': team_id})
            await query.edit_message_text(
                "✅ You have left the team.",
                reply_markup=back_keyboard('my_hackathons', lang)
            )
        else:
            await query.edit_message_text(t('error_occurred', lang))
        return
    
    # Remove member (team lead only)
    if data.startswith('remove_member_'):
        team_id = int(parts[2])
        team = await db.get_team(team_id)
        if team['owner_id'] != telegram_id:
            await query.answer(t('admin_only', lang), show_alert=True)
            return
        
        members = await db.get_team_members(team_id)
        await query.edit_message_text(
            "Select member to remove:",
            reply_markup=team_members_keyboard(members, team_id, lang)
        )
        return
    
    if data.startswith('kick_'):
        team_id = int(parts[1])
        user_to_kick = int(parts[2])
        team = await db.get_team(team_id)
        if team['owner_id'] != telegram_id:
            await query.answer(t('admin_only', lang), show_alert=True)
            return
        
        await db.remove_team_member(team_id, user_to_kick)
        await db.log_action(telegram_id, 'removed_member', {'team_id': team_id, 'removed': user_to_kick})
        await query.answer("Member removed", show_alert=True)
        
        # Refresh team view
        members = await db.get_team_members(team_id)
        active_stage = await db.get_active_stage(team['hackathon_id'])
        
        text = t('team_info', lang,
            hackathon=team.get('hackathon_name', ''),
            name=team['name'],
            code=team['code'],
            members=format_member_list(members, lang)
        )
        
        await query.edit_message_text(
            text,
            reply_markup=team_detail_keyboard(
                team_id=team_id,
                is_owner=True,
                hackathon_id=team['hackathon_id'],
                active_stage=active_stage,
                lang=lang
            )
        )
        return
    
    # Stage view and submission
    if data.startswith('stage_'):
        stage_id = int(parts[1])
        stages = await db.get_stages(1)  # Get hackathon ID from context
        # Find the stage
        from database import get_connection
        async with get_connection() as conn:
            stage = await conn.fetchrow("SELECT * FROM hackathon_stages WHERE id = $1", stage_id)
            if stage:
                hackathon = await db.get_hackathon(stage['hackathon_id'])
                user_team = await db.get_user_team_for_hackathon(telegram_id, stage['hackathon_id'])
                if user_team:
                    submission = await db.get_submission(user_team['id'], stage_id)
                    text = t('stage_info', lang,
                        hackathon=hackathon['name'],
                        stage=f"Stage {stage['stage_number']}",
                        start=format_date(stage.get('start_date'), lang) if stage.get('start_date') else '—',
                        end=format_date(stage.get('deadline'), lang) if stage.get('deadline') else '—',
                        task=stage.get('task_description', '—'),
                        deadline=format_date(stage.get('deadline'), lang) if stage.get('deadline') else '—'
                    )
                    await query.edit_message_text(
                        text,
                        reply_markup=stage_keyboard(stage_id, user_team['id'], submission is not None, lang)
                    )
        return
    
    # Submit
    if data.startswith('submit_'):
        stage_id = int(parts[1])
        team_id = int(parts[2])
        await db.set_registration_state(telegram_id, UserState.SUBMIT_LINK, {'stage_id': stage_id, 'team_id': team_id})
        await query.edit_message_text(t('submit_prompt', lang))
        return
    
    # Settings
    if data == 'settings':
        await query.edit_message_text(
            t('settings_menu', lang),
            reply_markup=settings_keyboard(lang)
        )
        return
    
    if data == 'change_language':
        await query.edit_message_text(
            t('choose_language', lang),
            reply_markup=language_keyboard()
        )
        return
    
    if data == 'edit_personal_data':
        user = await db.get_user(telegram_id)
        text = t('your_data', lang,
            first_name=user.get('first_name', '—'),
            last_name=user.get('last_name', '—'),
            birth_date=format_date(user.get('birth_date'), lang),
            gender=format_gender(user.get('gender'), lang),
            location=user.get('location', '—')
        )
        await query.edit_message_text(text, reply_markup=edit_data_keyboard(lang))
        return
    
    # Edit individual fields
    if data == 'edit_first_name':
        await db.set_registration_state(telegram_id, UserState.EDIT_FIRST_NAME, {})
        await query.edit_message_text(t('enter_first_name', lang))
        return
    
    if data == 'edit_last_name':
        await db.set_registration_state(telegram_id, UserState.EDIT_LAST_NAME, {})
        await query.edit_message_text(t('enter_last_name', lang))
        return
    
    if data == 'edit_birth_date':
        await db.set_registration_state(telegram_id, UserState.EDIT_BIRTH_DATE, {})
        await query.edit_message_text(t('enter_birth_date', lang))
        return
    
    if data == 'edit_gender':
        await db.set_registration_state(telegram_id, UserState.REG_GENDER, {'editing': True})
        await query.edit_message_text(
            t('enter_gender', lang),
            reply_markup=gender_keyboard(lang)
        )
        return
    
    if data == 'edit_location':
        await db.set_registration_state(telegram_id, UserState.EDIT_LOCATION, {})
        await query.edit_message_text(t('enter_location', lang))
        return
    
    # Gender selection
    if data.startswith('gender_'):
        gender = 'male' if data == 'gender_male' else 'female'
        await db.update_user(telegram_id, gender=gender)
        
        state = await db.get_registration_state(telegram_id)
        if state and state.get('data', {}).get('editing'):
            await db.clear_registration_state(telegram_id)
            await query.edit_message_text(t('data_updated', lang))
            # Show personal data again
            user = await db.get_user(telegram_id)
            text = t('your_data', lang,
                first_name=user.get('first_name', '—'),
                last_name=user.get('last_name', '—'),
                birth_date=format_date(user.get('birth_date'), lang),
                gender=format_gender(user.get('gender'), lang),
                location=user.get('location', '—')
            )
            await context.bot.send_message(
                chat_id=telegram_id,
                text=text,
                reply_markup=edit_data_keyboard(lang)
            )
        else:
            # Continue registration
            await db.set_registration_state(telegram_id, UserState.REG_LOCATION, state.get('data', {}))
            await query.edit_message_text(t('enter_location', lang))
        return
    
    # No portfolio
    if data == 'no_portfolio':
        state = await db.get_registration_state(telegram_id)
        if state and state['current_step'] == UserState.TEAM_PORTFOLIO:
            data_dict = state.get('data', {})
            data_dict['portfolio'] = None
            await complete_team_creation(update, context, data_dict, lang)
        return
    
    # Help
    if data == 'help':
        await query.edit_message_text(
            t('help_message', lang),
            reply_markup=back_keyboard('main_menu', lang)
        )
        return
    
    # Cancel
    if data == 'cancel':
        await db.clear_registration_state(telegram_id)
        await query.edit_message_text(
            t('operation_cancelled', lang),
            reply_markup=main_menu_inline(lang)
        )
        return


async def handle_team_join(update: Update, context: ContextTypes.DEFAULT_TYPE, team_code: str):
    """Handle deep link team join."""
    telegram_id = update.effective_user.id
    user = await db.get_user(telegram_id)
    
    if not user:
        # Need to register first
        await start_command(update, context)
        return
    
    lang = user.get('language', 'uz')
    
    team = await db.get_team_by_code(team_code)
    if not team:
        await update.message.reply_text(
            "Team not found or no longer active.",
            reply_markup=main_menu_keyboard(lang)
        )
        return
    
    # Check if already in a team for this hackathon
    existing = await db.get_user_team_for_hackathon(telegram_id, team['hackathon_id'])
    if existing:
        await update.message.reply_text(
            "You're already in a team for this hackathon.",
            reply_markup=main_menu_keyboard(lang)
        )
        return
    
    # Add to team
    success = await db.add_team_member(team['id'], telegram_id, "Member")
    if success:
        await db.log_action(telegram_id, 'joined_team', {'team_id': team['id']})
        await update.message.reply_text(
            f"✅ You've joined team '{team['name']}'!",
            reply_markup=main_menu_keyboard(lang)
        )
    else:
        await update.message.reply_text(
            "Failed to join team. You might already be a member.",
            reply_markup=main_menu_keyboard(lang)
        )
