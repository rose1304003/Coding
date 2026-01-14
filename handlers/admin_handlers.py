"""
Admin handlers for CBU Coding Hackathon Bot
"""

import logging
import csv
import io
from datetime import datetime
from telegram import Update, InputFile
from telegram.ext import ContextTypes

import database as db
from locales.translations import t
from utils.keyboards import main_menu_keyboard, cancel_keyboard
from utils.helpers import UserState, validate_date, format_datetime


import zipfile
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_IDS  # or however you store admins
from database import db       # adapt to your Database instance


logger = logging.getLogger(__name__)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        user = await db.get_user(telegram_id)
        lang = user.get('language', 'uz') if user else 'uz'
        await update.message.reply_text(t('admin_only', lang))
        return
    user = await db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    await update.message.reply_text(t('admin_menu', lang))


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return
    user = await db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    stats = await db.get_stats()
    await update.message.reply_text(t('stats_message', lang,
        total_users=stats['total_users'],
        consented_users=stats['consented_users'],
        total_teams=stats['total_teams'],
        active_hackathons=stats['active_hackathons'],
        total_submissions=stats['total_submissions']
    ))


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return
    user = await db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    await db.set_registration_state(telegram_id, UserState.ADMIN_BROADCAST, {})
    await update.message.reply_text(t('broadcast_prompt', lang), reply_markup=cancel_keyboard(lang))


async def export_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export users to CSV."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return
    users = await db.get_all_consented_users()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Telegram ID', 'Username', 'First Name', 'Last Name', 'Phone', 
                     'Birth Date', 'Gender', 'Location', 'PINFL', 'Language', 'Consent', 'Created'])
    for u in users:
        writer.writerow([u['id'], u['telegram_id'], u.get('username', ''), u.get('first_name', ''),
            u.get('last_name', ''), u.get('phone', ''), str(u.get('birth_date', '')),
            u.get('gender', ''), u.get('location', ''), u.get('pinfl', ''),
            u.get('language', ''), u.get('consent_given', ''), str(u.get('created_at', ''))])
    output.seek(0)
    await update.message.reply_document(
        document=InputFile(io.BytesIO(output.getvalue().encode('utf-8')), filename='users.csv'),
        caption=f"✅ {len(users)} users exported")


async def export_teams_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export teams to CSV."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return
    async with db.get_connection() as conn:
        teams = await conn.fetch("""
            SELECT t.*, h.name as hackathon_name,
                   (SELECT COUNT(*) FROM team_members WHERE team_id = t.id) as member_count
            FROM teams t JOIN hackathons h ON t.hackathon_id = h.id ORDER BY t.created_at DESC
        """)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Hackathon', 'Team Name', 'Code', 'Owner ID', 'Field', 'Portfolio', 'Members', 'Active', 'Created'])
    for t in teams:
        writer.writerow([t['id'], t['hackathon_name'], t['name'], t['code'], t['owner_id'],
            t.get('field', ''), t.get('portfolio_link', ''), t['member_count'], t['is_active'], str(t.get('created_at', ''))])
    output.seek(0)
    await update.message.reply_document(
        document=InputFile(io.BytesIO(output.getvalue().encode('utf-8')), filename='teams.csv'),
        caption=f"✅ {len(teams)} teams exported")


async def export_members_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export team members to CSV."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return
    async with db.get_connection() as conn:
        members = await conn.fetch("""
            SELECT tm.*, u.first_name, u.last_name, u.username, u.phone, t.name as team_name, t.code as team_code
            FROM team_members tm
            JOIN users u ON tm.user_id = u.telegram_id
            JOIN teams t ON tm.team_id = t.id
            ORDER BY t.id, tm.is_team_lead DESC
        """)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Team', 'Code', 'Member Name', 'Username', 'Phone', 'Role', 'Is Lead', 'Joined'])
    for m in members:
        name = f"{m.get('first_name', '')} {m.get('last_name', '')}".strip()
        writer.writerow([m['team_name'], m['team_code'], name, m.get('username', ''), m.get('phone', ''),
            m.get('role', ''), m['is_team_lead'], str(m.get('joined_at', ''))])
    output.seek(0)
    await update.message.reply_document(
        document=InputFile(io.BytesIO(output.getvalue().encode('utf-8')), filename='team_members.csv'),
        caption=f"✅ {len(members)} members exported")


async def export_submissions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export submissions to CSV."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return
    submissions = await db.get_all_submissions()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Hackathon', 'Stage', 'Team', 'Code', 'Type', 'Content/File', 'File ID', 'Submitted At', 'Score', 'Feedback'])
    for s in submissions:
        writer.writerow([s.get('hackathon_name', ''), f"Stage {s.get('stage_number', '')}", s.get('team_name', ''),
            s.get('team_code', ''), s.get('submission_type', ''), s.get('content', '') or s.get('file_name', ''),
            s.get('file_id', ''), str(s.get('submitted_at', '')), s.get('score', ''), s.get('feedback', '')])
    output.seek(0)
    await update.message.reply_document(
        document=InputFile(io.BytesIO(output.getvalue().encode('utf-8')), filename='submissions.csv'),
        caption=f"✅ {len(submissions)} submissions exported")


async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addadmin <telegram_id>."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /addadmin <telegram_id>")
        return
    try:
        new_admin_id = int(context.args[0])
        await db.set_admin(new_admin_id, True)
        await update.message.reply_text(f"✅ User {new_admin_id} is now an admin")
    except ValueError:
        await update.message.reply_text("❌ Invalid telegram_id")


async def remove_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /removeadmin <telegram_id>."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /removeadmin <telegram_id>")
        return
    try:
        admin_id = int(context.args[0])
        await db.set_admin(admin_id, False)
        await update.message.reply_text(f"✅ User {admin_id} is no longer an admin")
    except ValueError:
        await update.message.reply_text("❌ Invalid telegram_id")


async def create_hackathon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /create_hackathon."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return
    await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_HACKATHON_NAME, {})
    await update.message.reply_text("📝 Enter hackathon name:", reply_markup=cancel_keyboard('uz'))


async def create_stage_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /create_stage."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return
    hackathons = await db.get_active_hackathons()
    if not hackathons:
        await update.message.reply_text("❌ No active hackathons")
        return
    await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_STAGE_HACKATHON, {})
    text = "Select hackathon:\n" + "\n".join([f"{h['id']}. {h['name']}" for h in hackathons])
    await update.message.reply_text(text)


async def activate_stage_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /activate_stage <stage_id>."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /activate_stage <stage_id>")
        return
    try:
        stage_id = int(context.args[0])
        success = await db.activate_stage(stage_id)
        if success:
            await update.message.reply_text(f"✅ Stage {stage_id} activated")
        else:
            await update.message.reply_text("❌ Stage not found")
    except ValueError:
        await update.message.reply_text("❌ Invalid stage_id")


async def notify_hackathon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /notify_hackathon <hackathon_id> <message>."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /notify_hackathon <hackathon_id> <message>")
        return
    try:
        hackathon_id = int(context.args[0])
        message = ' '.join(context.args[1:])
        participants = await db.get_hackathon_participants(hackathon_id)
        sent = 0
        for user_id in participants:
            try:
                await context.bot.send_message(chat_id=user_id, text=message)
                sent += 1
            except Exception as e:
                logger.error(f"Failed to send to {user_id}: {e}")
        await update.message.reply_text(f"✅ Sent to {sent}/{len(participants)} participants")
    except ValueError:
        await update.message.reply_text("❌ Invalid hackathon_id")


async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle admin-specific messages. Returns True if handled."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return False
    
    state = await db.get_registration_state(telegram_id)
    if not state:
        return False
    
    text = update.message.text.strip()
    current_step = state['current_step']
    data = state.get('data', {})
    
    # Broadcast
    if current_step == UserState.ADMIN_BROADCAST:
        users = await db.get_all_consented_users()
        sent = 0
        for u in users:
            try:
                await context.bot.send_message(chat_id=u['telegram_id'], text=text)
                sent += 1
            except Exception as e:
                logger.error(f"Broadcast failed to {u['telegram_id']}: {e}")
        await db.clear_registration_state(telegram_id)
        await update.message.reply_text(f"✅ Broadcast sent to {sent}/{len(users)} users")
        return True
    
    # Create hackathon flow - MULTI-LANGUAGE
    if current_step == UserState.ADMIN_CREATE_HACKATHON_NAME:
        data['name'] = text
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_HACKATHON_NAME_RU, data)
        await update.message.reply_text("🇷🇺 Введите название хакатона на русском (или 'skip'):")
        return True
    
    if current_step == UserState.ADMIN_CREATE_HACKATHON_NAME_RU:
        data['name_ru'] = None if text.lower() == 'skip' else text
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_HACKATHON_NAME_EN, data)
        await update.message.reply_text("🇬🇧 Enter hackathon name in English (or 'skip'):")
        return True
    
    if current_step == UserState.ADMIN_CREATE_HACKATHON_NAME_EN:
        data['name_en'] = None if text.lower() == 'skip' else text
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_HACKATHON_DESC, data)
        await update.message.reply_text("🇺🇿 Tavsifni o'zbek tilida kiriting (yoki 'skip'):")
        return True
    
    if current_step == UserState.ADMIN_CREATE_HACKATHON_DESC:
        data['description'] = None if text.lower() == 'skip' else text
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_HACKATHON_DESC_RU, data)
        await update.message.reply_text("🇷🇺 Введите описание на русском (или 'skip'):")
        return True
    
    if current_step == UserState.ADMIN_CREATE_HACKATHON_DESC_RU:
        data['description_ru'] = None if text.lower() == 'skip' else text
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_HACKATHON_DESC_EN, data)
        await update.message.reply_text("🇬🇧 Enter description in English (or 'skip'):")
        return True
    
    if current_step == UserState.ADMIN_CREATE_HACKATHON_DESC_EN:
        data['description_en'] = None if text.lower() == 'skip' else text
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_HACKATHON_PRIZE, data)
        await update.message.reply_text("🇺🇿 Mukofot fondini kiriting (masalan: '500 mln so'm'):")
        return True
    
    if current_step == UserState.ADMIN_CREATE_HACKATHON_PRIZE:
        data['prize_pool'] = text
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_HACKATHON_PRIZE_RU, data)
        await update.message.reply_text("🇷🇺 Введите призовой фонд на русском (или 'skip'):")
        return True
    
    if current_step == UserState.ADMIN_CREATE_HACKATHON_PRIZE_RU:
        data['prize_pool_ru'] = None if text.lower() == 'skip' else text
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_HACKATHON_PRIZE_EN, data)
        await update.message.reply_text("🇬🇧 Enter prize pool in English (or 'skip'):")
        return True
    
    if current_step == UserState.ADMIN_CREATE_HACKATHON_PRIZE_EN:
        data['prize_pool_en'] = None if text.lower() == 'skip' else text
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_HACKATHON_START, data)
        await update.message.reply_text("📅 Enter start date (DD.MM.YYYY):")
        return True
    
    if current_step == UserState.ADMIN_CREATE_HACKATHON_START:
        valid, date = validate_date(text)
        if not valid:
            await update.message.reply_text("❌ Invalid date. Use DD.MM.YYYY")
            return True
        data['start_date'] = date
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_HACKATHON_END, data)
        await update.message.reply_text("📅 Enter end date (DD.MM.YYYY):")
        return True
    
    if current_step == UserState.ADMIN_CREATE_HACKATHON_END:
        valid, date = validate_date(text)
        if not valid:
            await update.message.reply_text("❌ Invalid date. Use DD.MM.YYYY")
            return True
        # Parse dates back from ISO strings if needed
        start_date = data.get('start_date')
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        # Create hackathon with all language versions
        hackathon = await db.create_hackathon(
            name=data['name'],
            name_ru=data.get('name_ru'),
            name_en=data.get('name_en'),
            description=data.get('description'),
            description_ru=data.get('description_ru'),
            description_en=data.get('description_en'),
            prize_pool=data.get('prize_pool'),
            prize_pool_ru=data.get('prize_pool_ru'),
            prize_pool_en=data.get('prize_pool_en'),
            start_date=start_date,
            end_date=date
        )
        await db.clear_registration_state(telegram_id)
        await update.message.reply_text(f"✅ Hackathon '{hackathon['name']}' created! ID: {hackathon['id']}")
        return True
    
    # Create stage flow - MULTI-LANGUAGE
    if current_step == UserState.ADMIN_CREATE_STAGE_HACKATHON:
        try:
            hackathon_id = int(text)
            data['hackathon_id'] = hackathon_id
            await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_STAGE_NUMBER, data)
            await update.message.reply_text("🔢 Enter stage number (1, 2, 3...):")
            return True
        except ValueError:
            await update.message.reply_text("❌ Invalid ID")
            return True
    
    if current_step == UserState.ADMIN_CREATE_STAGE_NUMBER:
        try:
            stage_num = int(text)
            data['stage_number'] = stage_num
            await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_STAGE_NAME, data)
            await update.message.reply_text("🇺🇿 Bosqich nomini o'zbek tilida kiriting:")
            return True
        except ValueError:
            await update.message.reply_text("❌ Invalid number")
            return True
    
    if current_step == UserState.ADMIN_CREATE_STAGE_NAME:
        data['name'] = text
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_STAGE_NAME_RU, data)
        await update.message.reply_text("🇷🇺 Введите название этапа на русском (или 'skip'):")
        return True
    
    if current_step == UserState.ADMIN_CREATE_STAGE_NAME_RU:
        data['name_ru'] = None if text.lower() == 'skip' else text
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_STAGE_NAME_EN, data)
        await update.message.reply_text("🇬🇧 Enter stage name in English (or 'skip'):")
        return True
    
    if current_step == UserState.ADMIN_CREATE_STAGE_NAME_EN:
        data['name_en'] = None if text.lower() == 'skip' else text
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_STAGE_TASK, data)
        await update.message.reply_text("🇺🇿 Vazifa tavsifini o'zbek tilida kiriting:")
        return True
    
    if current_step == UserState.ADMIN_CREATE_STAGE_TASK:
        data['task_description'] = text
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_STAGE_TASK_RU, data)
        await update.message.reply_text("🇷🇺 Введите описание задания на русском (или 'skip'):")
        return True
    
    if current_step == UserState.ADMIN_CREATE_STAGE_TASK_RU:
        data['task_description_ru'] = None if text.lower() == 'skip' else text
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_STAGE_TASK_EN, data)
        await update.message.reply_text("🇬🇧 Enter task description in English (or 'skip'):")
        return True
    
    if current_step == UserState.ADMIN_CREATE_STAGE_TASK_EN:
        data['task_description_en'] = None if text.lower() == 'skip' else text
        await db.set_registration_state(telegram_id, UserState.ADMIN_CREATE_STAGE_DEADLINE, data)
        await update.message.reply_text("⏰ Enter deadline (DD.MM.YYYY HH:MM):")
        return True
    
    if current_step == UserState.ADMIN_CREATE_STAGE_DEADLINE:
        try:
            deadline = datetime.strptime(text, '%d.%m.%Y %H:%M')
            stage = await db.create_stage(
                hackathon_id=data['hackathon_id'],
                stage_number=data['stage_number'],
                name=data['name'],
                name_ru=data.get('name_ru'),
                name_en=data.get('name_en'),
                task_description=data['task_description'],
                task_description_ru=data.get('task_description_ru'),
                task_description_en=data.get('task_description_en'),
                deadline=deadline
            )
            await db.clear_registration_state(telegram_id)
            await update.message.reply_text(f"✅ Stage {stage['stage_number']} created! ID: {stage['id']}")
            return True
        except ValueError:
            await update.message.reply_text("❌ Invalid format. Use DD.MM.YYYY HH:MM")
            return True
    
    return False


async def download_submission_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /download <submission_id> - download a submission file."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /download <submission_id>\n\nGet submission IDs from /export_submissions")
        return
    
    try:
        submission_id = int(context.args[0])
        async with db.get_connection() as conn:
            sub = await conn.fetchrow("""
                SELECT s.*, t.name as team_name, hs.name as stage_name 
                FROM submissions s 
                JOIN teams t ON s.team_id = t.id
                JOIN hackathon_stages hs ON s.stage_id = hs.id
                WHERE s.id = $1
            """, submission_id)
        
        if not sub:
            await update.message.reply_text("❌ Submission not found")
            return
        
        caption = f"📋 Submission #{sub['id']}\n👥 Team: {sub['team_name']}\n📌 Stage: {sub['stage_name']}\n⏰ Submitted: {sub['submitted_at']}"
        
        if sub['submission_type'] == 'file' and sub['file_id']:
            # Send the file
            file_type = sub.get('file_type', 'document')
            if file_type == 'image':
                await update.message.reply_photo(sub['file_id'], caption=caption)
            elif file_type == 'video':
                await update.message.reply_video(sub['file_id'], caption=caption)
            elif file_type == 'audio':
                await update.message.reply_audio(sub['file_id'], caption=caption)
            else:
                await update.message.reply_document(sub['file_id'], caption=caption)
        elif sub['submission_type'] == 'link':
            await update.message.reply_text(f"{caption}\n\n🔗 Link: {sub['content']}")
        else:
            await update.message.reply_text(f"{caption}\n\n📝 Content: {sub.get('content', 'No content')}")
            
    except ValueError:
        await update.message.reply_text("❌ Invalid submission ID")


async def list_submissions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /submissions [hackathon_id] - list all submissions."""
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return
    
    submissions = await db.get_all_submissions()
    
    if not submissions:
        await update.message.reply_text("📭 No submissions yet")
        return
    
    # Group by hackathon/stage
    text = "📋 **All Submissions:**\n\n"
    for s in submissions[:50]:  # Limit to 50
        file_info = f"📎 {s.get('file_name', 'file')}" if s['submission_type'] == 'file' else f"🔗 Link"
        text += f"**#{s['id']}** | {s.get('team_name', '?')} | Stage {s.get('stage_number', '?')} | {file_info}\n"
    
    if len(submissions) > 50:
        text += f"\n... and {len(submissions) - 50} more. Use /export_submissions for full list."
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin callbacks."""
    query = update.callback_query
    await query.answer()
    
    telegram_id = update.effective_user.id
    if not await db.is_admin(telegram_id):
        return
    
    data = query.data
    
    if data == 'admin_cancel':
        await db.clear_registration_state(telegram_id)
        await query.edit_message_text("❌ Cancelled")


async def export_all_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ You are not allowed to use this command.")
        return

    submissions = db.get_all_submissions()  # must return list of dicts with file_id, file_name
    if not submissions:
        await update.message.reply_text("No submissions found.")
        return

    export_dir = Path("/tmp/submissions")
    export_dir.mkdir(parents=True, exist_ok=True)

    zip_path = Path("/tmp/submissions.zip")
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for s in submissions:
            file_id = s["file_id"]
            file_name = s.get("file_name") or f"{file_id}.bin"

            tg_file = await context.bot.get_file(file_id)
            local_path = export_dir / file_name

            await tg_file.download_to_drive(custom_path=str(local_path))
            zipf.write(str(local_path), arcname=file_name)

    await update.message.reply_document(
        document=open(zip_path, "rb"),
        filename="all_submissions.zip",
        caption=f"✅ Exported {len(submissions)} files"
    )


