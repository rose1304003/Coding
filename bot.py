"""
ITCom Hackathons Bot - Main Entry Point
Production-ready Telegram bot for hackathon management

Author: Robiyaxon Axmedova / Empathy Engineers
Version: 1.0.0
"""

import os
import sys
import logging
import asyncio
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

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
from handlers.main_handlers import (
    start_command,
    help_command,
    settings_command,
    exit_command,
    handle_message,
    handle_contact,
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
    handle_admin_message
)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Get bot token from environment
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL),
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Reduce noise from httpx
logging.getLogger("httpx").setLevel(logging.WARNING)


# =============================================================================
# ERROR HANDLER
# =============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and notify user."""
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    
    # Try to notify user
    if update and update.effective_user:
        try:
            if update.callback_query:
                await update.callback_query.answer(
                    "An error occurred. Please try again.",
                    show_alert=True
                )
            elif update.message:
                await update.message.reply_text(
                    "❌ An error occurred. Please try again or contact support."
                )
        except Exception as e:
            logger.error(f"Failed to notify user of error: {e}")


# =============================================================================
# MESSAGE ROUTER
# =============================================================================

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route messages - check admin handlers first, then regular handlers."""
    # Try admin handlers first
    handled = await handle_admin_message(update, context)
    if not handled:
        # Regular message handling
        await handle_message(update, context)


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route callbacks - check for admin callbacks, then regular."""
    data = update.callback_query.data
    
    # Route admin callbacks
    if data.startswith('admin_'):
        await handle_admin_callback(update, context)
    else:
        await handle_callback(update, context)


# =============================================================================
# BOT COMMANDS SETUP
# =============================================================================

async def setup_commands(application: Application):
    """Set up bot commands visible in Telegram."""
    # Only /start is visible - everything else is via buttons!
    commands = [
        BotCommand("start", "Boshlash / Начать / Start"),
    ]
    
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands set up successfully")


# =============================================================================
# STARTUP & SHUTDOWN
# =============================================================================

async def on_startup(application: Application):
    """Run on bot startup."""
    logger.info("🚀 Bot starting up...")
    
    # Initialize database and create tables
    try:
        await db.create_tables()
        logger.info("✅ Database tables ready")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Set up bot commands
    await setup_commands(application)
    
    # Log bot info
    bot_info = await application.bot.get_me()
    logger.info(f"✅ Bot started: @{bot_info.username} ({bot_info.first_name})")
    logger.info(f"📅 Started at: {datetime.now().isoformat()}")


async def on_shutdown(application: Application):
    """Run on bot shutdown."""
    logger.info("🛑 Bot shutting down...")
    
    # Close database pool
    await db.close_pool()
    logger.info("✅ Database connection closed")


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main function to run the bot."""
    logger.info("=" * 50)
    logger.info("Kod va G'oyalar Hackathons Bot")
    logger.info("=" * 50)
    
    # Build application
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )
    
    # ==========================================================================
    # REGISTER HANDLERS
    # ==========================================================================
    
    # Command handlers - User
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("exit", exit_command))
    
    # Command handlers - Admin
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
    
    # Callback query handler (inline keyboard buttons)
    application.add_handler(CallbackQueryHandler(callback_router))
    
    # Contact handler (phone number sharing)
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    # Media/file handler (submissions can be file uploads)
    application.add_handler(MessageHandler(
        filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.VOICE,
        message_router
    ))
    
    # Text message handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message_router
    ))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # ==========================================================================
    # RUN THE BOT
    # ==========================================================================
    
    logger.info("Starting polling...")
    
    # Run with polling (for development and Railway)
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True  # Ignore old messages on restart
    )


if __name__ == "__main__":
    main()
