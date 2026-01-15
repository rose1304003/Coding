"""
CBU Coding Hackathon Bot - Main Entry Point
Production-ready Telegram bot for hackathon management

Features:
- Multi-language support (UZ/RU/EN)
- GDPR-compliant consent (Oferta)
- Team management
- Stage-based submissions
- File upload support
- Admin panel
"""

import os
import sys
import logging
from datetime import datetime

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
from handlers.main_handlers import (
    start_command,
    help_command,
    settings_command,
    handle_message,
    handle_contact,
    handle_file,
    handle_callback
)
from handlers.admin_handlers import (
    admin_command,
    stats_command,
    broadcast_command,
    export_users_command,
    export_teams_command,
    export_members_command,
    export_submissions_command,
    add_admin_command,
    remove_admin_command,
    create_hackathon_command,
    create_stage_command,
    activate_stage_command,
    notify_hackathon_command,
    handle_admin_callback,
    handle_admin_message,
    download_submission_command,
    list_submissions_command,
    export_all_files_command,
    export_team_files_command,
    export_stage_files_command
)

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL),
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and notify user."""
    logger.error(f"Exception: {context.error}", exc_info=context.error)
    if update and update.effective_user:
        try:
            if update.callback_query:
                await update.callback_query.answer("An error occurred. Please try again.", show_alert=True)
            elif update.message:
                await update.message.reply_text("❌ An error occurred. Please try again or contact support.")
        except Exception as e:
            logger.error(f"Failed to notify user: {e}")


async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route messages - check admin handlers first."""
    handled = await handle_admin_message(update, context)
    if not handled:
        await handle_message(update, context)


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route callbacks."""
    data = update.callback_query.data
    if data.startswith('admin_'):
        await handle_admin_callback(update, context)
    else:
        await handle_callback(update, context)


async def file_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route file uploads."""
    await handle_file(update, context)


async def setup_commands(application: Application):
    """Set up bot commands."""
    commands = [
        BotCommand("start", "Boshlash / Начать / Start"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands set up")


async def on_startup(application: Application):
    """Run on startup."""
    logger.info("🚀 Bot starting...")
    try:
        await db.create_tables()
        logger.info("✅ Database ready")
    except Exception as e:
        logger.error(f"❌ Database init failed: {e}")
        raise
    await setup_commands(application)
    bot_info = await application.bot.get_me()
    logger.info(f"✅ Bot: @{bot_info.username}")
    logger.info(f"📅 Started: {datetime.now().isoformat()}")


async def on_shutdown(application: Application):
    """Run on shutdown."""
    logger.info("🛑 Bot shutting down...")
    await db.close_pool()
    logger.info("✅ Database closed")


def main():
    """Main function."""
    logger.info("=" * 50)
    logger.info("CBU Coding Hackathon Bot")
    logger.info("=" * 50)
    
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )
    
    # User commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("settings", settings_command))
    
    # Admin commands
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("export_users", export_users_command))
    application.add_handler(CommandHandler("export_teams", export_teams_command))
    application.add_handler(CommandHandler("export_members", export_members_command))
    application.add_handler(CommandHandler("export_submissions", export_submissions_command))
    application.add_handler(CommandHandler("addadmin", add_admin_command))
    application.add_handler(CommandHandler("removeadmin", remove_admin_command))
    application.add_handler(CommandHandler("create_hackathon", create_hackathon_command))
    application.add_handler(CommandHandler("create_stage", create_stage_command))
    application.add_handler(CommandHandler("activate_stage", activate_stage_command))
    application.add_handler(CommandHandler("notify_hackathon", notify_hackathon_command))
    application.add_handler(CommandHandler("download", download_submission_command))
    application.add_handler(CommandHandler("submissions", list_submissions_command))
    application.add_handler(CommandHandler("export_files", export_all_files_command))
    application.add_handler(CommandHandler("export_team", export_team_files_command))
    application.add_handler(CommandHandler("export_stage", export_stage_files_command))
    
    # Callback handler
    application.add_handler(CallbackQueryHandler(callback_router))
    
    # Contact handler
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    
    # File handlers
    application.add_handler(MessageHandler(
        filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.VOICE,
        file_router
    ))
    
    # Text message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("Starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
