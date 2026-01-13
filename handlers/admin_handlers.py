"""
Admin handlers for Hackathon Bot
Admin-only commands for management and exports
"""

import logging
from datetime import datetime
from telegram import Update, InputFile
from telegram.ext import ContextTypes

import database as db
from locales.translations import t
from utils.keyboards import (
    admin_keyboard, hackathon_select_keyboard, back_keyboard,
    main_menu_keyboard
)
from utils.helpers import UserState
from exports.csv_export import (
    export_users_csv, export_teams_csv, export_team_members_csv,
    export_submissions_csv, get_export_filename
)

logger = logging.getLogger(__name__)

# Admin telegram IDs - add your admin IDs here
ADMIN_IDS = []  # Will be loaded from database


async def is_admin(telegram_id: int) -> bool:
    """Check if user is an admin."""
    user = await db.get_user(telegram_id)
    return user and user.get('is_admin', False)


async def admin_required(update: Update) -> bool:
    """Check admin status and send error if not admin."""
    telegram_id = update.effective_user.id
    if not await is_admin(telegram_id):
        user = await db.get_user(telegram_id)
        lang = user.get('language', 'uz') if user else 'uz'
        
        if update.callback_query:
            await update.callback_query.answer(t('admin_only', lang), show_alert=True)
        else:
            await update.message.reply_text(t('admin_only', lang))
        return False
    return True


# =============================================================================
# ADMIN COMMANDS
# =============================================================================

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command - show admin panel."""
    if not await admin_required(update):
        return
    
    telegram_id = update.effective_user.id
    user = await db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    
    await update.message.reply_text(
        "🔐 Admin Panel",
        reply_markup=admin_keyboard(lang)
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - show statistics."""
    if not await admin_required(update):
        return
    
    stats = await db.get_stats()
    
    text = (
        "📊 **Bot Statistics**\n\n"
        f"👥 Total Users: {stats['total_users']}\n"
        f"👥 Total Teams: {stats['total_teams']}\n"
        f"🏆 Active Hackathons: {stats['active_hackathons']}\n"
        f"📤 Total Submissions: {stats['total_submissions']}\n"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command - send message to all users."""
    if not await admin_required(update):
        return
    
    telegram_id = update.effective_user.id
    user = await db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    
    # Check if message is provided
    if context.args:
        message = ' '.join(context.args)
        await send_broadcast(update, context, message)
    else:
        # Set state to wait for message
        await db.set_registration_state(telegram_id, UserState.ADMIN_BROADCAST, {})
        await update.message.reply_text(t('broadcast_prompt', lang))


async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    """Send broadcast message to all active users."""
    telegram_id = update.effective_user.id
    user = await db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    
    users = await db.get_all_users(active_only=True)
    sent_count = 0
    failed_count = 0
    
    status_msg = await update.message.reply_text("📤 Sending broadcast...")
    
    for u in users:
        try:
            await context.bot.send_message(
                chat_id=u['telegram_id'],
                text=message
            )
            sent_count += 1
        except Exception as e:
            logger.warning(f"Failed to send to {u['telegram_id']}: {e}")
            failed_count += 1
        
        # Update status every 50 messages
        if (sent_count + failed_count) % 50 == 0:
            await status_msg.edit_text(
                f"📤 Sending... {sent_count + failed_count}/{len(users)}"
            )
    
    await db.log_action(telegram_id, 'broadcast', {
        'message': message[:100],
        'sent': sent_count,
        'failed': failed_count
    })
    
    await status_msg.edit_text(
        t('broadcast_sent', lang, count=sent_count) + f"\n❌ Failed: {failed_count}"
    )


async def export_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /export_users command - export users to CSV."""
    if not await admin_required(update):
        return
    
    telegram_id = update.effective_user.id
    user = await db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    
    await update.message.reply_text("📤 Generating export...")
    
    csv_data = await export_users_csv(db)
    filename = get_export_filename('users')
    
    await update.message.reply_document(
        document=InputFile(csv_data, filename=filename),
        caption=t('export_complete', lang)
    )
    
    await db.log_action(telegram_id, 'exported_users', {'filename': filename})


async def export_teams_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /export_teams command - export teams to CSV."""
    if not await admin_required(update):
        return
    
    telegram_id = update.effective_user.id
    user = await db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    
    await update.message.reply_text("📤 Generating export...")
    
    csv_data = await export_teams_csv(db)
    filename = get_export_filename('teams')
    
    await update.message.reply_document(
        document=InputFile(csv_data, filename=filename),
        caption=t('export_complete', lang)
    )
    
    await db.log_action(telegram_id, 'exported_teams', {'filename': filename})


async def export_members_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /export_members command - export team members to CSV."""
    if not await admin_required(update):
        return
    
    telegram_id = update.effective_user.id
    user = await db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    
    await update.message.reply_text("📤 Generating export...")
    
    csv_data = await export_team_members_csv(db)
    filename = get_export_filename('team_members')
    
    await update.message.reply_document(
        document=InputFile(csv_data, filename=filename),
        caption=t('export_complete', lang)
    )
    
    await db.log_action(telegram_id, 'exported_members', {'filename': filename})


async def export_submissions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /export_submissions command - export submissions to CSV."""
    if not await admin_required(update):
        return
    
    telegram_id = update.effective_user.id
    user = await db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    
    await update.message.reply_text("📤 Generating export...")
    
    csv_data = await export_submissions_csv(db)
    filename = get_export_filename('submissions')
    
    await update.message.reply_document(
        document=InputFile(csv_data, filename=filename),
        caption=t('export_complete', lang)
    )
    
    await db.log_action(telegram_id, 'exported_submissions', {'filename': filename})


async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addadmin command - add new admin by telegram ID."""
    if not await admin_required(update):
        return
    
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("Usage: /addadmin <telegram_id>")
        return
    
    try:
        new_admin_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid telegram ID")
        return
    
    success = await db.set_admin(new_admin_id, True)
    if success:
        await db.log_action(update.effective_user.id, 'added_admin', {'new_admin': new_admin_id})
        await update.message.reply_text(f"✅ User {new_admin_id} is now an admin")
    else:
        await update.message.reply_text("Failed to add admin. User might not exist.")


async def remove_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /removeadmin command - remove admin status."""
    if not await admin_required(update):
        return
    
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("Usage: /removeadmin <telegram_id>")
        return
    
    try:
        admin_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid telegram ID")
        return
    
    success = await db.set_admin(admin_id, False)
    if success:
        await db.log_action(update.effective_user.id, 'removed_admin', {'removed_admin': admin_id})
        await update.message.reply_text(f"✅ User {admin_id} is no longer an admin")
    else:
        await update.message.reply_text("Failed to remove admin.")


# =============================================================================
# HACKATHON MANAGEMENT
# =============================================================================

async def create_hackathon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /create_hackathon command."""
    if not await admin_required(update):
        return
    
    # Parse arguments: /create_hackathon "Name" "Description" "Prize"
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Usage: /create_hackathon <name>\n"
            "Example: /create_hackathon AI500!"
        )
        return
    
    name = ' '.join(context.args)
    
    hackathon = await db.create_hackathon(name=name)
    
    await db.log_action(update.effective_user.id, 'created_hackathon', {'hackathon_id': hackathon['id']})
    
    await update.message.reply_text(
        f"✅ Hackathon created!\n\n"
        f"ID: {hackathon['id']}\n"
        f"Name: {hackathon['name']}\n\n"
        f"Use /edit_hackathon {hackathon['id']} to add more details."
    )


async def create_stage_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /create_stage command."""
    if not await admin_required(update):
        return
    
    # Parse: /create_stage <hackathon_id> <stage_number> <name>
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "Usage: /create_stage <hackathon_id> <stage_number> <name>\n"
            "Example: /create_stage 1 1 Stage 1"
        )
        return
    
    try:
        hackathon_id = int(context.args[0])
        stage_number = int(context.args[1])
        name = ' '.join(context.args[2:])
    except ValueError:
        await update.message.reply_text("Invalid hackathon_id or stage_number")
        return
    
    stage = await db.create_stage(
        hackathon_id=hackathon_id,
        stage_number=stage_number,
        name=name
    )
    
    await db.log_action(update.effective_user.id, 'created_stage', {'stage_id': stage['id']})
    
    await update.message.reply_text(
        f"✅ Stage created!\n\n"
        f"ID: {stage['id']}\n"
        f"Stage {stage['stage_number']}: {stage['name']}"
    )


async def activate_stage_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /activate_stage command."""
    if not await admin_required(update):
        return
    
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("Usage: /activate_stage <stage_id>")
        return
    
    try:
        stage_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid stage_id")
        return
    
    success = await db.activate_stage(stage_id)
    if success:
        await db.log_action(update.effective_user.id, 'activated_stage', {'stage_id': stage_id})
        await update.message.reply_text(f"✅ Stage {stage_id} is now active")
    else:
        await update.message.reply_text("Failed to activate stage")


# =============================================================================
# NOTIFICATION COMMANDS
# =============================================================================

async def notify_hackathon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /notify_hackathon command - send notification to hackathon participants."""
    if not await admin_required(update):
        return
    
    # Parse: /notify_hackathon <hackathon_id> <message>
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /notify_hackathon <hackathon_id> <message>\n"
            "Example: /notify_hackathon 1 Deadline approaching!"
        )
        return
    
    try:
        hackathon_id = int(context.args[0])
        message = ' '.join(context.args[1:])
    except ValueError:
        await update.message.reply_text("Invalid hackathon_id")
        return
    
    hackathon = await db.get_hackathon(hackathon_id)
    if not hackathon:
        await update.message.reply_text("Hackathon not found")
        return
    
    participants = await db.get_hackathon_participants(hackathon_id)
    sent_count = 0
    
    status_msg = await update.message.reply_text(f"📤 Sending to {len(participants)} participants...")
    
    for user_id in participants:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 {hackathon['name']}\n\n{message}"
            )
            sent_count += 1
        except Exception as e:
            logger.warning(f"Failed to notify {user_id}: {e}")
    
    # Log notification
    await db.create_notification(
        hackathon_id=hackathon_id,
        title="Admin notification",
        message=message,
        sent_by=update.effective_user.id
    )
    
    await status_msg.edit_text(f"✅ Notification sent to {sent_count}/{len(participants)} participants")


# =============================================================================
# ADMIN CALLBACK HANDLERS
# =============================================================================

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin-specific callback queries."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = update.effective_user.id
    
    if not await is_admin(telegram_id):
        user = await db.get_user(telegram_id)
        lang = user.get('language', 'uz') if user else 'uz'
        await query.answer(t('admin_only', lang), show_alert=True)
        return
    
    user = await db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    data = query.data
    
    if data == 'admin_panel':
        await query.edit_message_text(
            "🔐 Admin Panel",
            reply_markup=admin_keyboard(lang)
        )
        return
    
    if data == 'admin_stats':
        stats = await db.get_stats()
        text = (
            "📊 **Bot Statistics**\n\n"
            f"👥 Total Users: {stats['total_users']}\n"
            f"👥 Total Teams: {stats['total_teams']}\n"
            f"🏆 Active Hackathons: {stats['active_hackathons']}\n"
            f"📤 Total Submissions: {stats['total_submissions']}\n"
        )
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=back_keyboard('admin_panel', lang)
        )
        return
    
    if data == 'admin_broadcast':
        await db.set_registration_state(telegram_id, UserState.ADMIN_BROADCAST, {})
        await query.edit_message_text(t('broadcast_prompt', lang))
        return
    
    if data == 'admin_export_users':
        await query.edit_message_text("📤 Generating users export...")
        csv_data = await export_users_csv(db)
        filename = get_export_filename('users')
        await context.bot.send_document(
            chat_id=telegram_id,
            document=InputFile(csv_data, filename=filename),
            caption=t('export_complete', lang)
        )
        await db.log_action(telegram_id, 'exported_users', {'filename': filename})
        return
    
    if data == 'admin_export_teams':
        await query.edit_message_text("📤 Generating teams export...")
        csv_data = await export_teams_csv(db)
        filename = get_export_filename('teams')
        await context.bot.send_document(
            chat_id=telegram_id,
            document=InputFile(csv_data, filename=filename),
            caption=t('export_complete', lang)
        )
        await db.log_action(telegram_id, 'exported_teams', {'filename': filename})
        return
    
    if data == 'admin_add_hackathon':
        await db.set_registration_state(telegram_id, UserState.ADMIN_ADD_HACKATHON, {})
        await query.edit_message_text(
            "Enter hackathon name:"
        )
        return
    
    if data == 'admin_manage_stages':
        hackathons = await db.get_active_hackathons()
        if not hackathons:
            await query.edit_message_text(
                "No active hackathons",
                reply_markup=back_keyboard('admin_panel', lang)
            )
            return
        await query.edit_message_text(
            "Select hackathon:",
            reply_markup=hackathon_select_keyboard(hackathons, 'admin_stages', lang)
        )
        return


async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin text input for broadcast, etc."""
    telegram_id = update.effective_user.id
    
    if not await is_admin(telegram_id):
        return False
    
    state = await db.get_registration_state(telegram_id)
    if not state:
        return False
    
    text = update.message.text
    current_step = state['current_step']
    
    if current_step == UserState.ADMIN_BROADCAST:
        await db.clear_registration_state(telegram_id)
        await send_broadcast(update, context, text)
        return True
    
    if current_step == UserState.ADMIN_ADD_HACKATHON:
        await db.clear_registration_state(telegram_id)
        hackathon = await db.create_hackathon(name=text)
        await db.log_action(telegram_id, 'created_hackathon', {'hackathon_id': hackathon['id']})
        
        user = await db.get_user(telegram_id)
        lang = user.get('language', 'uz') if user else 'uz'
        
        await update.message.reply_text(
            f"✅ Hackathon created!\n\n"
            f"ID: {hackathon['id']}\n"
            f"Name: {hackathon['name']}",
            reply_markup=main_menu_keyboard(lang)
        )
        return True
    
    return False
