"""
Main handlers for CBU Coding Hackathon Bot
Handles user commands and callback queries including Offer/Consent flow
"""

import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import database as db
from database import get_localized_field
from locales.translations import t
from utils.keyboards import (
    main_menu_keyboard, main_menu_inline, language_keyboard,
    hackathons_list_keyboard, hackathon_detail_keyboard,
    user_hackathons_keyboard, team_detail_keyboard,
    settings_keyboard, edit_data_keyboard, phone_keyboard,
    gender_keyboard, portfolio_keyboard, stage_keyboard,
    confirm_leave_keyboard, team_members_keyboard,
    back_keyboard, remove_keyboard, cancel_keyboard,
    offer_keyboard, offer_read_keyboard, registration_option_keyboard,
    team_role_keyboard
)
from utils.helpers import (
    validate_date, validate_pinfl, validate_url, validate_email,
    format_date, format_datetime, format_gender, format_member_list,
    format_submission_content, get_file_type, clean_name, UserState
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
        # Check if user has given consent
        if existing_user.get('consent_given'):
            lang = existing_user.get('language', 'uz')
            await update.message.reply_text(
                t('welcome_back', lang),
                reply_markup=main_menu_keyboard(lang)
            )
            await db.log_action(telegram_id, 'returned', {'via': 'start_command'})
        else:
            # User exists but hasn't given consent - show language selection first
            await update.message.reply_text(
                t('choose_language', 'en'),
                reply_markup=language_keyboard()
            )
    else:
        # New user - create and show language selection
        await db.add_user(
            telegram_id=telegram_id,
            first_name=user.first_name or "User",
            username=user.username,
            last_name=user.last_name
        )
        
        await update.message.reply_text(
            t('choose_language', 'en'),
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
    if not user or not user.get('consent_given'):
        await update.message.reply_text(t('offer_required', 'uz'))
        return
    
    lang = user.get('language', 'uz')
    await update.message.reply_text(
        t('settings_menu', lang),
        reply_markup=settings_keyboard(lang)
    )


# =============================================================================
# MESSAGE HANDLERS
# =============================================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages - route based on state or button press."""
    telegram_id = update.effective_user.id
    text = update.message.text
    
    user = await db.get_user(telegram_id)
    if not user:
        await update.message.reply_text(t('please_start', 'en'), reply_markup=remove_keyboard())
        return
    
    lang = user.get('language', 'uz')
    
    # Check consent
    if not user.get('consent_given'):
        await update.message.reply_text(t('offer_required', lang))
        return
    
    # Check if it's a menu button press
    if text == t('btn_hackathons', lang):
        await show_hackathons(update, context, lang)
        return
    elif text == t('btn_my_hackathons', lang):
        await show_my_hackathons(update, context, lang)
        return
    elif text == t('btn_settings', lang):
        await update.message.reply_text(t('settings_menu', lang), reply_markup=settings_keyboard(lang))
        return
    elif text == t('btn_help', lang):
        await update.message.reply_text(t('help_message', lang), reply_markup=main_menu_keyboard(lang))
        return
    
    # Check registration state
    state = await db.get_registration_state(telegram_id)
    if state:
        await handle_registration_input(update, context, state, lang)
        return
    
    # Default response
    await update.message.reply_text(t('main_menu', lang), reply_markup=main_menu_keyboard(lang))


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle shared contact (phone number)."""
    telegram_id = update.effective_user.id
    contact = update.message.contact
    
    user = await db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    
    state = await db.get_registration_state(telegram_id)
    
    if state and state['current_step'] == UserState.REG_PHONE:
        await db.update_user(telegram_id, phone=contact.phone_number)
        await db.set_registration_state(telegram_id, UserState.REG_EMAIL, state.get('data', {}))
        await update.message.reply_text(t('enter_email', lang), reply_markup=remove_keyboard())


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file submissions (documents, photos, videos, audio)."""
    telegram_id = update.effective_user.id
    user = await db.get_user(telegram_id)
    
    if not user or not user.get('consent_given'):
        return
    
    lang = user.get('language', 'uz')
    state = await db.get_registration_state(telegram_id)
    
    if not state or state['current_step'] != UserState.SUBMIT_LINK:
        return
    
    # Get file info
    file_id = None
    file_name = None
    file_type = None
    
    if update.message.document:
        doc = update.message.document
        file_id = doc.file_id
        file_name = doc.file_name or "document"
        file_type = get_file_type(file_name, doc.mime_type)
    elif update.message.photo:
        photo = update.message.photo[-1]  # Get largest photo
        file_id = photo.file_id
        file_name = "photo.jpg"
        file_type = "image"
    elif update.message.video:
        video = update.message.video
        file_id = video.file_id
        file_name = video.file_name or "video.mp4"
        file_type = "video"
    elif update.message.audio:
        audio = update.message.audio
        file_id = audio.file_id
        file_name = audio.file_name or "audio.mp3"
        file_type = "audio"
    elif update.message.voice:
        voice = update.message.voice
        file_id = voice.file_id
        file_name = "voice.ogg"
        file_type = "audio"
    
    if file_id:
        data = state.get('data', {})
        stage_id = data.get('stage_id')
        team_id = data.get('team_id')
        
        await db.create_submission(
            team_id=team_id,
            stage_id=stage_id,
            submitted_by=telegram_id,
            content=file_name,
            submission_type='file',
            file_id=file_id,
            file_name=file_name,
            file_type=file_type
        )
        
        await db.clear_registration_state(telegram_id)
        await db.log_action(telegram_id, 'submitted_file', {'stage_id': stage_id, 'file_type': file_type})
        
        await update.message.reply_text(
            t('submission_received', lang, content=f"📎 {file_name}", time=datetime.now().strftime('%d.%m.%Y %H:%M')),
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
        await update.message.reply_text(t('enter_gender', lang), reply_markup=gender_keyboard(lang))
        
    elif current_step == UserState.REG_LOCATION:
        await db.update_user(telegram_id, location=text)
        await db.set_registration_state(telegram_id, UserState.REG_PHONE, data)
        await update.message.reply_text(t('enter_phone', lang), reply_markup=phone_keyboard(lang))
    
    elif current_step == UserState.REG_EMAIL:
        if not validate_email(text):
            await update.message.reply_text(t('invalid_email', lang))
            return
        await db.update_user(telegram_id, email=text)
        await db.set_registration_state(telegram_id, UserState.REG_PINFL, data)
        await update.message.reply_text(t('enter_pinfl', lang))
        
    elif current_step == UserState.REG_PINFL:
        if not validate_pinfl(text):
            await update.message.reply_text(t('invalid_pinfl', lang))
            return
        await db.update_user(telegram_id, pinfl=text, registration_complete=True)
        await db.clear_registration_state(telegram_id)
        await db.log_action(telegram_id, 'completed_registration', {})
        await update.message.reply_text(t('registration_almost_done', lang), reply_markup=main_menu_keyboard(lang))
        
    # Team creation flow
    elif current_step == UserState.TEAM_JOIN_CODE:
        team = await db.get_team_by_code(text.strip())
        if not team:
            await update.message.reply_text(t('invalid_team_code', lang))
            return
        
        # Check team size
        members = await db.get_team_members(team['id'])
        if len(members) >= 5:
            await update.message.reply_text(t('team_full', lang))
            await db.clear_registration_state(telegram_id)
            return
        
        # Check if already in a team for this hackathon
        existing = await db.get_user_team_for_hackathon(telegram_id, team['hackathon_id'])
        if existing:
            await update.message.reply_text(t('already_registered', lang))
            await db.clear_registration_state(telegram_id)
            return
        
        # Save team info and ask for role
        data['join_team_id'] = team['id']
        data['join_team_name'] = team['name']
        await db.set_registration_state(telegram_id, UserState.SELECT_TEAM_ROLE, data)
        await update.message.reply_text(
            t('select_team_role', lang),
            reply_markup=team_role_keyboard(lang)
        )
        
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
        await update.message.reply_text(t('enter_portfolio', lang), reply_markup=portfolio_keyboard(lang))
        
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
        
        await db.create_submission(
            team_id=team_id,
            stage_id=stage_id,
            submitted_by=telegram_id,
            content=text,
            submission_type='link'
        )
        await db.clear_registration_state(telegram_id)
        await db.log_action(telegram_id, 'submitted_link', {'stage_id': stage_id, 'link': text})
        await update.message.reply_text(
            t('submission_received', lang, content=text, time=datetime.now().strftime('%d.%m.%Y %H:%M')),
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
    """Complete team creation process (works for both message + callback flows)."""
    telegram_id = update.effective_user.id
    chat_id = update.effective_chat.id

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

    text = t('team_created', lang, name=team['name'], code=team['code'])

    # If this came from an inline button click, update.callback_query exists.
    if update.callback_query:
        # Stop the loading spinner on the button
        await update.callback_query.answer()

        # Optional: remove the inline keyboard from the previous message
        try:
            await update.callback_query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        # Send the final result as a normal chat message
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=main_menu_keyboard(lang)
        )
    else:
        # Normal text message flow
        await update.message.reply_text(text, reply_markup=main_menu_keyboard(lang))


# =============================================================================
# DISPLAY HELPERS
# =============================================================================

async def show_hackathons(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    """Show list of available hackathons."""
    hackathons = await db.get_active_hackathons()
    
    if not hackathons:
        await update.message.reply_text(t('no_hackathons', lang), reply_markup=main_menu_keyboard(lang))
        return
    
    await update.message.reply_text(
        t('hackathon_list_title', lang),
        reply_markup=hackathons_list_keyboard(hackathons, lang)
    )


async def show_my_hackathons(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    """Show user's hackathons/teams."""
    telegram_id = update.effective_user.id
    teams = await db.get_user_teams(telegram_id)
    
    if not teams:
        await update.message.reply_text(t('no_registered_hackathons', lang), reply_markup=main_menu_keyboard(lang))
        return
    
    await update.message.reply_text(t('your_hackathons', lang), reply_markup=user_hackathons_keyboard(teams, lang))


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
    
    await update.message.reply_text(text, reply_markup=edit_data_keyboard(lang))


# =============================================================================
# CALLBACK HANDLER
# =============================================================================

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline keyboards."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = update.effective_user.id
    data = query.data
    parts = data.split('_')
    
    user = await db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    
    # Language selection
    if data.startswith('lang_'):
        new_lang = data.replace('lang_', '')
        await db.update_user(telegram_id, language=new_lang)
        lang = new_lang
        
        # Check if user has given consent
        if not user or not user.get('consent_given'):
            # Show offer/consent
            await query.edit_message_text(
                t('offer_short', lang),
                reply_markup=offer_keyboard(lang)
            )
        else:
            await query.edit_message_text(t('language_changed', lang))
            await context.bot.send_message(
                chat_id=telegram_id,
                text=t('main_menu', lang),
                reply_markup=main_menu_keyboard(lang)
            )
        return
    
    # Offer/Consent handling
    if data == 'offer_read':
        await query.edit_message_text(
            t('offer_full_text', lang),
            reply_markup=offer_read_keyboard(lang)
        )
        return
    
    if data == 'offer_back':
        await query.edit_message_text(
            t('offer_short', lang),
            reply_markup=offer_keyboard(lang)
        )
        return
    
    if data == 'offer_agree':
        await db.set_user_consent(telegram_id, True)
        await query.edit_message_text(t('offer_accepted', lang))
        
        # Start registration
        await db.set_registration_state(telegram_id, UserState.REG_FIRST_NAME, {})
        await context.bot.send_message(
            chat_id=telegram_id,
            text=t('enter_first_name', lang),
            reply_markup=remove_keyboard()
        )
        return
    
    if data == 'offer_decline':
        await db.set_user_consent(telegram_id, False)
        await query.edit_message_text(t('offer_declined', lang))
        return
    
    # Team role selection (when joining a team)
    if data.startswith('team_role_'):
        role = data.replace('team_role_', '')
        state = await db.get_registration_state(telegram_id)
        
        if state and state['current_step'] == UserState.SELECT_TEAM_ROLE:
            state_data = state.get('data', {})
            team_id = state_data.get('join_team_id')
            team_name = state_data.get('join_team_name', 'Team')
            
            if team_id:
                success = await db.add_team_member(team_id, telegram_id, role)
                await db.clear_registration_state(telegram_id)
                
                if success:
                    await db.log_action(telegram_id, 'joined_team', {'team_id': team_id, 'role': role})
                    await query.edit_message_text(
                        t('joined_team_with_role', lang, name=team_name, role=role)
                    )
                    await context.bot.send_message(
                        chat_id=telegram_id,
                        text=t('main_menu', lang),
                        reply_markup=main_menu_keyboard(lang)
                    )
                else:
                    await query.edit_message_text(t('error_occurred', lang))
            else:
                await query.edit_message_text(t('error_occurred', lang))
        return
    
    # Check consent for all other callbacks
    if not user or not user.get('consent_given'):
        await query.edit_message_text(t('offer_required', lang))
        return
    
    # Main menu
    if data == 'main_menu':
        await query.edit_message_text(t('main_menu', lang), reply_markup=main_menu_inline(lang))
        return
    
    # Hackathons list
    if data == 'hackathons':
        hackathons = await db.get_active_hackathons()
        if not hackathons:
            await query.edit_message_text(t('no_hackathons', lang), reply_markup=back_keyboard('main_menu', lang))
        else:
            await query.edit_message_text(t('hackathon_list_title', lang), reply_markup=hackathons_list_keyboard(hackathons, lang))
        return
    
    # Hackathon detail
    if data.startswith('hackathon_'):
        hackathon_id = int(parts[1])
        hackathon = await db.get_hackathon(hackathon_id)
        if not hackathon:
            await query.edit_message_text(t('error_occurred', lang))
            return
        
        is_registered = await db.get_user_team_for_hackathon(telegram_id, hackathon_id) is not None
        
        # Get localized content based on user's language
        h_name = get_localized_field(hackathon, 'name', lang)
        h_desc = get_localized_field(hackathon, 'description', lang)
        h_prize = get_localized_field(hackathon, 'prize_pool', lang)
        
        text = t('hackathon_info', lang,
            name=h_name,
            description=h_desc,
            prize_pool=h_prize,
            start_date=format_date(hackathon.get('start_date'), lang),
            end_date=format_date(hackathon.get('end_date'), lang),
            registration_deadline=format_datetime(hackathon.get('registration_deadline'), lang)
        )
        
        await query.edit_message_text(text, reply_markup=hackathon_detail_keyboard(hackathon_id, is_registered, lang))
        return
    
    # Registration options
    if data.startswith('register_'):
        hackathon_id = int(parts[1])
        existing = await db.get_user_team_for_hackathon(telegram_id, hackathon_id)
        if existing:
            await query.answer(t('already_registered', lang), show_alert=True)
            return
        
        hackathon = await db.get_hackathon(hackathon_id)
        await query.edit_message_text(
            t('registration_option', lang, hackathon=hackathon['name']),
            reply_markup=registration_option_keyboard(hackathon_id, lang)
        )
        return
    
    # Create team
    if data.startswith('create_team_'):
        hackathon_id = int(parts[2])
        await db.set_registration_state(telegram_id, UserState.TEAM_NAME, {'hackathon_id': hackathon_id})
        await query.edit_message_text(t('enter_team_name', lang))
        return
    
    # Join team
    if data.startswith('join_team_'):
        hackathon_id = int(parts[2])
        await db.set_registration_state(telegram_id, UserState.TEAM_JOIN_CODE, {'hackathon_id': hackathon_id})
        await query.edit_message_text(t('enter_team_code', lang), reply_markup=cancel_keyboard(lang))
        return
    
    # My hackathons
    if data == 'my_hackathons':
        teams = await db.get_user_teams(telegram_id)
        if not teams:
            await query.edit_message_text(t('no_registered_hackathons', lang), reply_markup=back_keyboard('main_menu', lang))
        else:
            await query.edit_message_text(t('your_hackathons', lang), reply_markup=user_hackathons_keyboard(teams, lang))
        return
    
    # Team detail
    if data.startswith('team_') and not data.startswith('team_members'):
        team_id = int(parts[1])
        team = await db.get_team(team_id)
        if not team:
            await query.edit_message_text(t('error_occurred', lang))
            return
        
        members = await db.get_team_members(team_id)
        is_owner = team['owner_id'] == telegram_id
        active_stage = await db.get_active_stage(team['hackathon_id'])
        
        text = t('team_info', lang,
            hackathon=team.get('hackathon_name', ''),
            name=team['name'],
            code=team['code'],
            members=format_member_list(members, lang)
        )
        
        await query.edit_message_text(
            text,
            reply_markup=team_detail_keyboard(team_id, is_owner, team['hackathon_id'], active_stage, lang)
        )
        return
    
    # Stage view
    if data.startswith('stage_'):
        stage_id = int(parts[1])
        stage = await db.get_stage(stage_id)
        if not stage:
            await query.edit_message_text(t('error_occurred', lang))
            return
        
        hackathon = await db.get_hackathon(stage['hackathon_id'])
        user_team = await db.get_user_team_for_hackathon(telegram_id, stage['hackathon_id'])
        
        if not user_team:
            await query.edit_message_text(t('error_occurred', lang))
            return
        
        submission = await db.get_submission(user_team['id'], stage_id)
        deadline_passed = stage.get('deadline') and datetime.now(stage['deadline'].tzinfo) > stage['deadline'] if stage.get('deadline') else False
        
        # Get localized content
        h_name = get_localized_field(hackathon, 'name', lang)
        s_name = get_localized_field(stage, 'name', lang)
        s_task = get_localized_field(stage, 'task_description', lang)
        
        text = t('stage_info', lang,
            hackathon=h_name,
            stage=f"Stage {stage['stage_number']}: {s_name}",
            start=format_datetime(stage.get('start_date'), lang),
            deadline=format_datetime(stage.get('deadline'), lang),
            task=s_task
        )
        
        await query.edit_message_text(
            text,
            reply_markup=stage_keyboard(stage_id, user_team['id'], submission is not None, deadline_passed, lang)
        )
        return
    
    # Submit
    if data.startswith('submit_'):
        stage_id = int(parts[1])
        team_id = int(parts[2])
        
        stage = await db.get_stage(stage_id)
        if stage and stage.get('deadline'):
            if datetime.now(stage['deadline'].tzinfo) > stage['deadline']:
                await query.answer(t('deadline_passed', lang), show_alert=True)
                return
        
        await db.set_registration_state(telegram_id, UserState.SUBMIT_LINK, {'stage_id': stage_id, 'team_id': team_id})
        await query.edit_message_text(t('submit_prompt', lang), reply_markup=cancel_keyboard(lang))
        return
    
    # View submission
    if data.startswith('view_submission_'):
        stage_id = int(parts[2])
        team_id = int(parts[3])
        submission = await db.get_submission(team_id, stage_id)
        
        if submission:
            content = format_submission_content(submission)
            text = t('current_submission', lang,
                content=content,
                time=format_datetime(submission.get('submitted_at'), lang)
            )
            await query.answer()
            await context.bot.send_message(chat_id=telegram_id, text=text)
        return
    
    # Leave team
    if data.startswith('leave_team_'):
        team_id = int(parts[2])
        await query.edit_message_text(t('confirm_leave_team', lang), reply_markup=confirm_leave_keyboard(team_id, lang))
        return
    
    # Confirm leave
    if data.startswith('confirm_leave_'):
        team_id = int(parts[2])
        result = await db.leave_team(team_id, telegram_id)
        
        if result['success']:
            if result.get('team_deactivated'):
                await query.edit_message_text(t('team_deleted', lang), reply_markup=main_menu_inline(lang))
            else:
                await query.edit_message_text(t('left_team', lang), reply_markup=main_menu_inline(lang))
        return
    
    # Remove members view
    if data.startswith('remove_members_'):
        team_id = int(parts[2])
        members = await db.get_team_members(team_id)
        await query.edit_message_text(t('select_member_to_remove', lang), reply_markup=team_members_keyboard(members, team_id, lang))
        return
    
    # Remove specific member
    if data.startswith('remove_member_'):
        team_id = int(parts[2])
        member_id = int(parts[3])
        await db.remove_team_member(team_id, member_id)
        await query.answer(t('member_removed', lang), show_alert=True)
        
        # Refresh team view
        team = await db.get_team(team_id)
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
            reply_markup=team_detail_keyboard(team_id, True, team['hackathon_id'], active_stage, lang)
        )
        return
    
    # Settings
    if data == 'settings':
        await query.edit_message_text(t('settings_menu', lang), reply_markup=settings_keyboard(lang))
        return
    
    if data == 'change_language':
        await query.edit_message_text(t('choose_language', lang), reply_markup=language_keyboard())
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
    
    # Edit fields
    if data == 'edit_first_name':
        await db.set_registration_state(telegram_id, UserState.EDIT_FIRST_NAME, {})
        await query.edit_message_text(t('enter_first_name', lang), reply_markup=cancel_keyboard(lang))
        return
    
    if data == 'edit_last_name':
        await db.set_registration_state(telegram_id, UserState.EDIT_LAST_NAME, {})
        await query.edit_message_text(t('enter_last_name', lang), reply_markup=cancel_keyboard(lang))
        return
    
    if data == 'edit_birth_date':
        await db.set_registration_state(telegram_id, UserState.EDIT_BIRTH_DATE, {})
        await query.edit_message_text(t('enter_birth_date', lang), reply_markup=cancel_keyboard(lang))
        return
    
    if data == 'edit_gender':
        await db.set_registration_state(telegram_id, UserState.REG_GENDER, {'editing': True})
        await query.edit_message_text(t('enter_gender', lang), reply_markup=gender_keyboard(lang))
        return
    
    if data == 'edit_location':
        await db.set_registration_state(telegram_id, UserState.EDIT_LOCATION, {})
        await query.edit_message_text(t('enter_location', lang), reply_markup=cancel_keyboard(lang))
        return
    
    # Gender selection
    if data.startswith('gender_'):
        gender = 'male' if data == 'gender_male' else 'female'
        await db.update_user(telegram_id, gender=gender)
        
        state = await db.get_registration_state(telegram_id)
        if state and state.get('data', {}).get('editing'):
            await db.clear_registration_state(telegram_id)
            await query.edit_message_text(t('data_updated', lang))
            user = await db.get_user(telegram_id)
            text = t('your_data', lang,
                first_name=user.get('first_name', '—'),
                last_name=user.get('last_name', '—'),
                birth_date=format_date(user.get('birth_date'), lang),
                gender=format_gender(user.get('gender'), lang),
                location=user.get('location', '—')
            )
            await context.bot.send_message(chat_id=telegram_id, text=text, reply_markup=edit_data_keyboard(lang))
        else:
            # Continue registration
            await db.set_registration_state(telegram_id, UserState.REG_LOCATION, state.get('data', {}) if state else {})
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
        await query.edit_message_text(t('help_message', lang), reply_markup=back_keyboard('main_menu', lang))
        return
    
    # Cancel
    if data == 'cancel':
        await db.clear_registration_state(telegram_id)
        await query.edit_message_text(t('operation_cancelled', lang), reply_markup=main_menu_inline(lang))
        return


async def handle_team_join(update: Update, context: ContextTypes.DEFAULT_TYPE, team_code: str):
    """Handle deep link team join."""
    telegram_id = update.effective_user.id
    user = await db.get_user(telegram_id)
    
    if not user:
        await start_command(update, context)
        return
    
    if not user.get('consent_given'):
        await update.message.reply_text(t('offer_required', user.get('language', 'uz')))
        return
    
    lang = user.get('language', 'uz')
    
    team = await db.get_team_by_code(team_code)
    if not team:
        await update.message.reply_text(t('invalid_team_code', lang), reply_markup=main_menu_keyboard(lang))
        return
    
    existing = await db.get_user_team_for_hackathon(telegram_id, team['hackathon_id'])
    if existing:
        await update.message.reply_text(t('already_registered', lang), reply_markup=main_menu_keyboard(lang))
        return
    
    members = await db.get_team_members(team['id'])
    if len(members) >= 5:
        await update.message.reply_text(t('team_full', lang), reply_markup=main_menu_keyboard(lang))
        return
    
    success = await db.add_team_member(team['id'], telegram_id, "Member")
    if success:
        await db.log_action(telegram_id, 'joined_team', {'team_id': team['id']})
        await update.message.reply_text(t('joined_team', lang, name=team['name']), reply_markup=main_menu_keyboard(lang))
    else:
        await update.message.reply_text(t('error_occurred', lang), reply_markup=main_menu_keyboard(lang))
