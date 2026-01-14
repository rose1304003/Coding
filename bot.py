"""
IT Community Hackathons Bot - Complete Version
Features: Multi-language, File uploads, Team management, Admin panel
"""

import os
import logging
import csv
from io import StringIO, BytesIO
from datetime import datetime, timedelta
from typing import Optional
import asyncio
import random
import string

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, filters
)
from telegram.constants import ParseMode

import asyncpg
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

# Conversation states
(START, LANGUAGE, CONSENT, FIRST_NAME, LAST_NAME, BIRTH_DATE, GENDER, 
 LOCATION, PHONE, PINFL, TEAM_NAME_INPUT, TEAM_CODE_INPUT, SUBMISSION_INPUT) = range(13)

# Translation dictionary
TRANSLATIONS = {
    'uz': {
        'welcome': "👋 IT Community Hackathon Botiga xush kelibsiz!\n\nTilni tanlang:",
        'consent_title': "📋 Shaxsiy ma'lumotlardan foydalanish",
        'consent_text': """Hurmatli ishtirokchi!

Hackathonda ishtirok etish uchun shaxsiy ma'lumotlaringizni to'plash va qayta ishlash zarur.

Biz quyidagi ma'lumotlarni yig'amiz:
• Ism va familiya
• Tug'ilgan sana
• Jins
• Joylashuv
• Telefon raqam
• PINFL (shaxsni tasdiqlash uchun)

Ushbu ma'lumotlar faqat hackathon tashkil etish va ishtirokchilarni ro'yxatdan o'tkazish maqsadida ishlatiladi.

Ma'lumotlaringiz xavfsiz saqlanadi va uchinchi shaxslarga uzatilmaydi.

Davom etish orqali siz shaxsiy ma'lumotlaringizni qayta ishlashga rozilik bildirasiz.""",
        'consent_agree': "✅ Roziman",
        'consent_decline': "❌ Rad etaman",
        'consent_declined': "Afsuski, rozilik berilmasa hackathonda ishtirok eta olmaysiz. /start buyrug'i bilan qaytadan boshlashingiz mumkin.",
        'enter_first_name': "Ismingizni kiriting (masalan: Robiya):",
        'enter_last_name': "Familiyangizni kiriting (masalan: Obidjonova):",
        'enter_birth_date': "Tug'ilgan sanangizni kiriting (masalan: 23.10.2007):",
        'invalid_date': "Noto'g'ri format! Iltimos, DD.MM.YYYY formatida kiriting.",
        'enter_gender': "Jinsingizni tanlang:",
        'male': "Erkak",
        'female': "Ayol",
        'enter_location': "Shahar yoki viloyatingizni kiriting (masalan: Toshkent):",
        'enter_phone': "📱 Telefon raqamingizni yuboring:",
        'share_contact': "📱 Telefon yuborish",
        'enter_pinfl': """PINFL (Shaxsiy identifikatsiya raqami) ni kiriting - 14 raqam.

Nima uchun PINFL kerak?
• Yoshingizni tasdiqlash uchun
• Agar kerak bo'lsa, yakuniy tadbirda ishtirok etish uchun (turar joy va chipta)""",
        'invalid_pinfl': "Noto'g'ri PINFL! 14 raqam bo'lishi kerak.",
        'registration_complete': "🎉 Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!",
        'almost_done': "Siz deyarli tayyor 😊",
        'confirm_participation': """Ishtirokingizni tasdiqlash uchun hackathonni tanlang:
Menyu → 🚀 Hackathonlar → AI500! → Ro'yxatdan o'tish ✅

⚠️ Hackathon tanlanmasa ro'yxatdan o'tish yaroqsiz!""",
        'main_menu': "🏠 Asosiy menyu",
        'hackathons': "🚀 Hackathonlar",
        'my_hackathons': "📋 Mening hackathonlarim",
        'settings': "⚙️ Sozlamalar",
        'help': "❓ Yordam",
        'no_hackathons': "❌ Hozircha hackathonlar yo'q",
        'your_hackathons': "📋 Sizning hackathonlaringiz:",
        'team_created': "✅ Jamoa yaratildi!",
        'team_name': "👥 Nomi",
        'team_code': "🔑 Kod",
        'share_code': "Ushbu kodni jamoadoshlaringiz bilan bo'lishing, ular jamoaga qo'shilishlari mumkin.",
        'stage_info': "ℹ️ Tez orada keyingi bosqichlar haqida xabarlar olasiz.\nIltimos, botni bloklamang!",
        'change_first_name': "✏️ Ismni o'zgartirish",
        'change_last_name': "✏️ Familiyani o'zgartirish",
        'change_language': "🌐 Tilni o'zgartirish",
        'your_data': "👤 Sizning ma'lumotlaringiz:",
        'help_text': """💡 Botdan yordam kerak yoki xatolik topdingizmi?

Agar savollar bo'lsa, bot bilan ishlashda yordam kerak bo'lsa yoki takliflaringiz bo'lsa, bizga murojaat qiling:
📧 ai500@itcommunity.uz

Muammoni batafsil tasvirlab bering va agar mumkin bo'lsa, skrinshotlar ilova qiling.
Tez orada javob beramiz ✅""",
        'back': "🔙 Orqaga",
        'register': "📝 Ro'yxatdan o'tish",
        'create_team': "➕ Jamoa yaratish",
        'join_team': "🔗 Jamoaga qo'shilish",
        'already_registered': "Siz allaqachon ro'yxatdan o'tgansiz!",
        'enter_team_name': "Jamoa nomini kiriting:",
        'enter_team_code': "Jamoa kodini kiriting:",
        'team_not_found': "❌ Jamoa topilmadi. Kodni tekshiring.",
        'team_joined': "✅ Jamoaga qo'shildingiz!",
        'team_full': "❌ Jamoa to'ldi.",
        'leave_team': "🚪 Jamoani tark etish",
        'remove_member': "❌ A'zoni o'chirish",
        'team_members': "👥 Jamoa a'zolari:",
        'team_lead': "👑 Rahbar",
        'see_details': "ℹ️ Tafsilotlar",
        'stage': "📊 Bosqich",
        'deadline': "⏰ Muddat",
        'submit': "📤 Topshirish",
        'submission_sent': "✅ Topshirildi!",
        'deadline_passed': "⏰ Muddat o'tib ketdi",
        'submit_link': "Demo website linkini yuboring:",
        'invalid_url': "❌ Noto'g'ri link! URL yuborishingiz kerak.",
    },
    'ru': {
        'welcome': "👋 Добро пожаловать в бот IT Community Hackathons!\n\nВыберите язык:",
        'consent_title': "📋 Использование персональных данных",
        'consent_text': """Уважаемый участник!

Для участия в хакатоне необходимо собрать и обработать ваши персональные данные.

Мы собираем следующую информацию:
• Имя и фамилия
• Дата рождения
• Пол
• Местоположение
• Номер телефона
• ПИНФЛ (для идентификации личности)

Эти данные используются только для организации хакатона и регистрации участников.

Ваши данные хранятся в безопасности и не передаются третьим лицам.

Продолжая, вы соглашаетесь на обработку ваших персональных данных.""",
        'consent_agree': "✅ Согласен",
        'consent_decline': "❌ Отклонить",
        'consent_declined': "К сожалению, без согласия вы не можете участвовать в хакатоне. Вы можете начать заново с команды /start.",
        'enter_first_name': "Введите ваше имя (например: Robiya):",
        'enter_last_name': "Введите вашу фамилию (например: Obidjonova):",
        'enter_birth_date': "Введите вашу дату рождения (например: 23.10.2007):",
        'invalid_date': "Неверный формат! Пожалуйста, введите в формате ДД.ММ.ГГГГ.",
        'enter_gender': "Выберите ваш пол:",
        'male': "Мужской",
        'female': "Женский",
        'enter_location': "Введите ваш город или область (например: Ташкент):",
        'enter_phone': "📱 Отправьте ваш номер телефона:",
        'share_contact': "📱 Поделиться номером",
        'enter_pinfl': """Введите ПИНФЛ (Персональный идентификационный номер) - 14 цифр.

Зачем нужен ПИНФЛ?
• Для подтверждения возраста
• Для организации участия в финальном мероприятии, если потребуется (бронирование жилья и покупка билетов)""",
        'invalid_pinfl': "Неверный ПИНФЛ! Должно быть 14 цифр.",
        'registration_complete': "🎉 Регистрация успешно завершена!",
        'almost_done': "Вы почти готовы 😊",
        'confirm_participation': """Чтобы подтвердить ваше участие, выберите хакатон:
Меню → 🚀 Хакатоны → AI500! → Зарегистрироваться ✅

⚠️ Регистрация недействительна без выбора хакатона!""",
        'main_menu': "🏠 Главное меню",
        'hackathons': "🚀 Хакатоны",
        'my_hackathons': "📋 Мои хакатоны",
        'settings': "⚙️ Настройки",
        'help': "❓ Помощь",
        'no_hackathons': "❌ Пока нет доступных хакатонов",
        'your_hackathons': "📋 Ваши хакатоны:",
        'team_created': "✅ Команда создана!",
        'team_name': "👥 Название",
        'team_code': "🔑 Код",
        'share_code': "Поделитесь этим кодом с вашими товарищами по команде, чтобы они могли присоединиться.",
        'stage_info': "ℹ️ Скоро вы получите обновления о следующих этапах.\nПожалуйста, не блокируйте бота!",
        'change_first_name': "✏️ Изменить имя",
        'change_last_name': "✏️ Изменить фамилию",
        'change_language': "🌐 Изменить язык",
        'your_data': "👤 Ваши данные:",
        'help_text': """💡 Нужна помощь или нашли ошибку?

Если у вас есть вопросы, нужна помощь в использовании бота или есть предложения по улучшению, свяжитесь с нами:
📧 ai500@itcommunity.uz

Опишите проблему подробно и прикрепите скриншоты, если возможно.
Мы скоро ответим ✅""",
        'back': "🔙 Назад",
        'register': "📝 Зарегистрироваться",
        'create_team': "➕ Создать команду",
        'join_team': "🔗 Присоединиться к команде",
        'already_registered': "Вы уже зарегистрированы!",
        'enter_team_name': "Введите название команды:",
        'enter_team_code': "Введите код команды:",
        'team_not_found': "❌ Команда не найдена. Проверьте код.",
        'team_joined': "✅ Вы присоединились к команде!",
        'team_full': "❌ Команда заполнена.",
        'leave_team': "🚪 Покинуть команду",
        'remove_member': "❌ Удалить участника",
        'team_members': "👥 Члены команды:",
        'team_lead': "👑 Лидер",
        'see_details': "ℹ️ Подробности",
        'stage': "📊 Этап",
        'deadline': "⏰ Срок",
        'submit': "📤 Отправить",
        'submission_sent': "✅ Отправлено!",
        'deadline_passed': "⏰ Срок истёк",
        'submit_link': "Отправьте ссылку на демо-сайт:",
        'invalid_url': "❌ Неверная ссылка! Вы должны отправить URL.",
    },
    'en': {
        'welcome': "👋 Welcome to the IT Community Hackathons Bot!\n\nChoose your language:",
        'consent_title': "📋 Personal Data Usage",
        'consent_text': """Dear participant!

To participate in the hackathon, we need to collect and process your personal data.

We collect the following information:
• First and last name
• Date of birth
• Gender
• Location
• Phone number
• PINFL (for identity verification)

This data is used only for organizing the hackathon and registering participants.

Your data is stored securely and is not shared with third parties.

By continuing, you agree to the processing of your personal data.""",
        'consent_agree': "✅ I Agree",
        'consent_decline': "❌ Decline",
        'consent_declined': "Unfortunately, without consent you cannot participate in the hackathon. You can start over with the /start command.",
        'enter_first_name': "Enter your first name (e.g. Robiya):",
        'enter_last_name': "Enter your last name (e.g. Obidjonova):",
        'enter_birth_date': "Enter your birth date (e.g. 23.10.2007):",
        'invalid_date': "Invalid format! Please enter in DD.MM.YYYY format.",
        'enter_gender': "Choose your gender:",
        'male': "Male",
        'female': "Female",
        'enter_location': "Enter your city or region (e.g. Tashkent):",
        'enter_phone': "📱 Send your phone number:",
        'share_contact': "📱 Share contact",
        'enter_pinfl': """Enter your PINFL (Personal Identification Number) - 14 digits.

Why do we require your PINFL?
• To verify your age
• To organize your participation in the final event if needed (booking accommodation and purchasing tickets)""",
        'invalid_pinfl': "Invalid PINFL! Must be 14 digits.",
        'registration_complete': "🎉 Registration completed successfully!",
        'almost_done': "You're almost done 😊",
        'confirm_participation': """To confirm your participation, please choose your hackathon:
Menu → 🚀 Hackathons → AI500! → Register ✅

⚠️ Registration without selecting a hackathon is not valid!""",
        'main_menu': "🏠 Main menu",
        'hackathons': "🚀 Hackathons",
        'my_hackathons': "📋 My hackathons",
        'settings': "⚙️ Settings",
        'help': "❓ Help",
        'no_hackathons': "❌ No hackathons available",
        'your_hackathons': "📋 Your hackathons:",
        'team_created': "✅ Team created!",
        'team_name': "👥 Name",
        'team_code': "🔑 Code",
        'share_code': "Share this code with your teammates so they can join the team.",
        'stage_info': "ℹ️ Soon you will receive updates about the next stages of this hackathon.\nPlease do not block the bot!",
        'change_first_name': "✏️ Change first name",
        'change_last_name': "✏️ Change last name",
        'change_language': "🌐 Change language",
        'your_data': "👤 Your data:",
        'help_text': """💡 Need help or found a bug?

If you have questions, need assistance using the bot or have suggestions for improvement, please contact us at:
📧 ai500@itcommunity.uz

Describe the problem in detail and attach screenshots if possible.
We will get back to you soon ✅""",
        'back': "🔙 Back",
        'register': "📝 Register",
        'create_team': "➕ Create team",
        'join_team': "🔗 Join team",
        'already_registered': "You are already registered!",
        'enter_team_name': "Enter team name:",
        'enter_team_code': "Enter team code:",
        'team_not_found': "❌ Team not found. Check the code.",
        'team_joined': "✅ You joined the team!",
        'team_full': "❌ Team is full.",
        'leave_team': "🚪 Leave team",
        'remove_member': "❌ Remove member",
        'team_members': "👥 Team members:",
        'team_lead': "👑 Lead",
        'see_details': "ℹ️ See details",
        'stage': "📊 Stage",
        'deadline': "⏰ Deadline",
        'submit': "📤 Submit",
        'submission_sent': "✅ Submitted!",
        'deadline_passed': "⏰ Deadline passed",
        'submit_link': "Send your demo website link:",
        'invalid_url': "❌ Invalid link! You must send a URL.",
    }
}

def t(lang: str, key: str) -> str:
    """Get translation"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

def generate_team_code():
    """Generate random 6-digit team code"""
    return ''.join(random.choices(string.digits, k=6))

# Database connection pool
db_pool = None

async def init_db():
    """Initialize database connection pool"""
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    
    # Create tables
    async with db_pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                language TEXT DEFAULT 'uz',
                first_name TEXT,
                last_name TEXT,
                birth_date DATE,
                gender TEXT,
                location TEXT,
                phone TEXT,
                pinfl TEXT,
                consent_given BOOLEAN DEFAULT FALSE,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS hackathons (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                status TEXT DEFAULT 'open',
                max_team_size INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS stages (
                id SERIAL PRIMARY KEY,
                hackathon_id INTEGER REFERENCES hackathons(id),
                stage_number INTEGER,
                name TEXT,
                description TEXT,
                deadline TIMESTAMP,
                task_details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id SERIAL PRIMARY KEY,
                hackathon_id INTEGER REFERENCES hackathons(id),
                name TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                lead_id BIGINT REFERENCES users(user_id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS team_members (
                team_id INTEGER REFERENCES teams(id),
                user_id BIGINT REFERENCES users(user_id),
                role TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (team_id, user_id)
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                user_id BIGINT REFERENCES users(user_id),
                hackathon_id INTEGER REFERENCES hackathons(id),
                team_id INTEGER REFERENCES teams(id),
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, hackathon_id)
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id SERIAL PRIMARY KEY,
                team_id INTEGER REFERENCES teams(id),
                stage_id INTEGER REFERENCES stages(id),
                submission_type TEXT,
                content TEXT,
                file_id TEXT,
                file_name TEXT,
                submitted_by BIGINT REFERENCES users(user_id),
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                hackathon_id INTEGER REFERENCES hackathons(id),
                message TEXT,
                send_date TIMESTAMP,
                sent BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

async def get_user(user_id: int):
    """Get user from database"""
    async with db_pool.acquire() as conn:
        return await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)

async def create_user(user_id: int, username: str = None):
    """Create new user"""
    async with db_pool.acquire() as conn:
        await conn.execute(
            'INSERT INTO users (user_id, username) VALUES ($1, $2) ON CONFLICT (user_id) DO NOTHING',
            user_id, username
        )

async def update_user(user_id: int, **kwargs):
    """Update user data"""
    fields = ', '.join([f"{k} = ${i+2}" for i, k in enumerate(kwargs.keys())])
    values = list(kwargs.values())
    
    async with db_pool.acquire() as conn:
        await conn.execute(
            f'UPDATE users SET {fields} WHERE user_id = $1',
            user_id, *values
        )

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    await create_user(user.id, user.username)
    
    # Language selection
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data='lang_uz'),
            InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru'),
            InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Welcome to IT Community Hackathons Bot!\n"
        "Добро пожаловать в бот IT Community Hackathons!\n"
        "IT Community Hackathon Botiga xush kelibsiz!\n\n"
        "Choose your language / Выберите язык / Tilni tanlang:",
        reply_markup=reply_markup
    )
    
    return LANGUAGE

async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection"""
    query = update.callback_query
    await query.answer()
    
    lang = query.data.split('_')[1]
    user_id = query.from_user.id
    
    await update_user(user_id, language=lang)
    context.user_data['language'] = lang
    
    # Check if user already registered
    user = await get_user(user_id)
    if user and user['consent_given']:
        await show_main_menu(query, context, lang)
        return ConversationHandler.END
    
    # Show consent form
    keyboard = [
        [InlineKeyboardButton(t(lang, 'consent_agree'), callback_data='consent_agree')],
        [InlineKeyboardButton(t(lang, 'consent_decline'), callback_data='consent_decline')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"**{t(lang, 'consent_title')}**\n\n{t(lang, 'consent_text')}",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return CONSENT

async def consent_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle consent response"""
    query = update.callback_query
    await query.answer()
    
    lang = context.user_data.get('language', 'uz')
    
    if query.data == 'consent_decline':
        await query.edit_message_text(t(lang, 'consent_declined'))
        return ConversationHandler.END
    
    # Consent given, start registration
    await update_user(query.from_user.id, consent_given=True)
    await query.edit_message_text(t(lang, 'enter_first_name'))
    
    return FIRST_NAME

async def first_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle first name input"""
    lang = context.user_data.get('language', 'uz')
    context.user_data['first_name'] = update.message.text
    
    await update.message.reply_text(t(lang, 'enter_last_name'))
    return LAST_NAME

async def last_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle last name input"""
    lang = context.user_data.get('language', 'uz')
    context.user_data['last_name'] = update.message.text
    
    await update.message.reply_text(t(lang, 'enter_birth_date'))
    return BIRTH_DATE

async def birth_date_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle birth date input"""
    lang = context.user_data.get('language', 'uz')
    
    try:
        birth_date = datetime.strptime(update.message.text, '%d.%m.%Y')
        context.user_data['birth_date'] = birth_date
        
        # Gender selection
        keyboard = [
            [InlineKeyboardButton(t(lang, 'male'), callback_data='gender_male')],
            [InlineKeyboardButton(t(lang, 'female'), callback_data='gender_female')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            t(lang, 'enter_gender'),
            reply_markup=reply_markup
        )
        return GENDER
    except ValueError:
        await update.message.reply_text(t(lang, 'invalid_date'))
        return BIRTH_DATE

async def gender_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle gender selection"""
    query = update.callback_query
    await query.answer()
    
    lang = context.user_data.get('language', 'uz')
    gender = query.data.split('_')[1]
    context.user_data['gender'] = gender
    
    await query.edit_message_text(t(lang, 'enter_location'))
    return LOCATION

async def location_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle location input"""
    lang = context.user_data.get('language', 'uz')
    context.user_data['location'] = update.message.text
    
    # Request phone number
    keyboard = [[KeyboardButton(t(lang, 'share_contact'), request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        t(lang, 'enter_phone'),
        reply_markup=reply_markup
    )
    return PHONE

async def phone_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone number"""
    lang = context.user_data.get('language', 'uz')
    
    if update.message.contact:
        context.user_data['phone'] = update.message.contact.phone_number
    else:
        context.user_data['phone'] = update.message.text
    
    await update.message.reply_text(
        t(lang, 'enter_pinfl'),
        reply_markup=ReplyKeyboardRemove()
    )
    return PINFL

async def pinfl_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle PINFL input"""
    lang = context.user_data.get('language', 'uz')
    pinfl = update.message.text.strip()
    
    if not pinfl.isdigit() or len(pinfl) != 14:
        await update.message.reply_text(t(lang, 'invalid_pinfl'))
        return PINFL
    
    # Save all data
    await update_user(
        update.effective_user.id,
        first_name=context.user_data['first_name'],
        last_name=context.user_data['last_name'],
        birth_date=context.user_data['birth_date'],
        gender=context.user_data['gender'],
        location=context.user_data['location'],
        phone=context.user_data['phone'],
        pinfl=pinfl
    )
    
    await update.message.reply_text(
        f"🎉 {t(lang, 'registration_complete')}\n\n"
        f"😊 {t(lang, 'almost_done')}\n\n"
        f"{t(lang, 'confirm_participation')}"
    )
    
    # Show main menu
    await show_main_menu(update.message, context, lang)
    
    return ConversationHandler.END

async def show_main_menu(message_or_query, context: ContextTypes.DEFAULT_TYPE, lang: str):
    """Show main menu"""
    keyboard = [
        [
            InlineKeyboardButton(t(lang, 'hackathons'), callback_data='menu_hackathons'),
            InlineKeyboardButton(t(lang, 'my_hackathons'), callback_data='menu_my_hackathons')
        ],
        [
            InlineKeyboardButton(t(lang, 'settings'), callback_data='menu_settings'),
            InlineKeyboardButton(t(lang, 'help'), callback_data='menu_help')
        ]
    ]
    
    # Check if user is admin
    user_id = message_or_query.from_user.id if hasattr(message_or_query, 'from_user') else message_or_query.chat.id
    user = await get_user(user_id)
    if user and user['is_admin']:
        keyboard.append([InlineKeyboardButton("👨‍💼 Admin Panel", callback_data='admin_panel')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = t(lang, 'main_menu')
    
    if hasattr(message_or_query, 'edit_message_text'):
        await message_or_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await message_or_query.reply_text(text, reply_markup=reply_markup)

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu callbacks"""
    query = update.callback_query
    await query.answer()
    
    user = await get_user(query.from_user.id)
    lang = user['language'] if user else 'uz'
    
    if query.data == 'menu_hackathons':
        await show_hackathons(query, lang)
    elif query.data == 'menu_my_hackathons':
        await show_my_hackathons(query, lang)
    elif query.data == 'menu_settings':
        await show_settings(query, lang)
    elif query.data == 'menu_help':
        await show_help(query, lang)
    elif query.data == 'admin_panel':
        await show_admin_panel(query, lang)
    elif query.data == 'back_main':
        await show_main_menu(query, context, lang)
    elif query.data.startswith('hackathon_'):
        await hackathon_details(query, context)
    elif query.data.startswith('register_'):
        await register_hackathon(query, context)
    elif query.data.startswith('team_create_'):
        await create_team_start(query, context)
    elif query.data.startswith('team_join_'):
        await join_team_start(query, context)
    elif query.data.startswith('team_view_'):
        await view_team(query, context)
    elif query.data.startswith('stages_'):
        await show_stages(query, context)
    elif query.data.startswith('stage_view_'):
        await view_stage(query, context)
    elif query.data.startswith('submit_start_'):
        await submit_start(query, context)
    elif query.data == 'admin_stats':
        await admin_statistics(query, context)
    elif query.data == 'admin_export_users':
        await export_users(query, context)
    elif query.data == 'admin_export_teams':
        await export_teams(query, context)
    elif query.data == 'admin_export_submissions':
        await export_submissions(query, context)

async def show_hackathons(query, lang: str):
    """Show available hackathons"""
    async with db_pool.acquire() as conn:
        hackathons = await conn.fetch(
            "SELECT * FROM hackathons WHERE status = 'open' ORDER BY start_date"
        )
    
    if not hackathons:
        keyboard = [[InlineKeyboardButton(t(lang, 'back'), callback_data='back_main')]]
        await query.edit_message_text(
            t(lang, 'no_hackathons'),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    keyboard = []
    for h in hackathons:
        keyboard.append([InlineKeyboardButton(
            f"🏆 {h['name']}",
            callback_data=f"hackathon_{h['id']}"
        )])
    keyboard.append([InlineKeyboardButton(t(lang, 'back'), callback_data='back_main')])
    
    await query.edit_message_text(
        t(lang, 'hackathons'),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_my_hackathons(query, lang: str):
    """Show user's hackathons"""
    async with db_pool.acquire() as conn:
        registrations = await conn.fetch('''
            SELECT h.*, t.name as team_name, t.code as team_code
            FROM registrations r
            JOIN hackathons h ON r.hackathon_id = h.id
            LEFT JOIN teams t ON r.team_id = t.id
            WHERE r.user_id = $1
            ORDER BY h.start_date
        ''', query.from_user.id)
    
    if not registrations:
        keyboard = [[InlineKeyboardButton(t(lang, 'back'), callback_data='back_main')]]
        await query.edit_message_text(
            t(lang, 'no_hackathons'),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    keyboard = []
    for r in registrations:
        keyboard.append([InlineKeyboardButton(
            f"🏆 {r['name']}",
            callback_data=f"my_hackathon_{r['id']}"
        )])
    keyboard.append([InlineKeyboardButton(t(lang, 'back'), callback_data='back_main')])
    
    await query.edit_message_text(
        t(lang, 'your_hackathons'),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_settings(query, lang: str):
    """Show settings menu"""
    user = await get_user(query.from_user.id)
    
    text = f"{t(lang, 'your_data')}\n\n"
    text += f"• First name: {user['first_name']}\n"
    text += f"• Last name: {user['last_name']}\n"
    text += f"• Birth date: {user['birth_date'].strftime('%d.%m.%Y') if user['birth_date'] else 'N/A'}\n"
    text += f"• Gender: {user['gender']}\n"
    text += f"• Location: {user['location']}\n"
    
    keyboard = [
        [InlineKeyboardButton(t(lang, 'change_first_name'), callback_data='edit_first_name')],
        [InlineKeyboardButton(t(lang, 'change_last_name'), callback_data='edit_last_name')],
        [InlineKeyboardButton(t(lang, 'change_language'), callback_data='edit_language')],
        [InlineKeyboardButton(t(lang, 'back'), callback_data='back_main')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_help(query, lang: str):
    """Show help information"""
    keyboard = [[InlineKeyboardButton(t(lang, 'back'), callback_data='back_main')]]
    await query.edit_message_text(
        t(lang, 'help_text'),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def show_admin_panel(query, lang: str):
    """Show admin panel"""
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
            InlineKeyboardButton("📥 Export Submissions", callback_data='admin_export_submissions'),
        ],
        [
            InlineKeyboardButton("➕ Add Hackathon", callback_data='admin_add_hackathon'),
            InlineKeyboardButton("📋 Manage Stages", callback_data='admin_stages')
        ],
        [InlineKeyboardButton("🔙 Back", callback_data='back_main')]
    ]
    
    await query.edit_message_text(
        "👨‍💼 **Admin Panel**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def hackathon_details(query, context: ContextTypes.DEFAULT_TYPE):
    """Show hackathon details"""
    hackathon_id = int(query.data.split('_')[1])
    user = await get_user(query.from_user.id)
    lang = user['language']
    
    async with db_pool.acquire() as conn:
        hackathon = await conn.fetchrow(
            'SELECT * FROM hackathons WHERE id = $1', hackathon_id
        )
        
        # Check if user is registered
        registration = await conn.fetchrow(
            'SELECT * FROM registrations WHERE user_id = $1 AND hackathon_id = $2',
            query.from_user.id, hackathon_id
        )
    
    text = f"🏆 **{hackathon['name']}**\n\n"
    text += f"{hackathon['description']}\n\n"
    text += f"📅 Start: {hackathon['start_date'].strftime('%d.%m.%Y')}\n"
    text += f"📅 End: {hackathon['end_date'].strftime('%d.%m.%Y')}\n"
    text += f"👥 Max team size: {hackathon['max_team_size']}\n"
    
    keyboard = []
    
    if not registration:
        keyboard.append([InlineKeyboardButton(
            t(lang, 'register'),
            callback_data=f'register_{hackathon_id}'
        )])
    else:
        # Show team options
        if registration['team_id']:
            keyboard.append([InlineKeyboardButton(
                t(lang, 'team_members'),
                callback_data=f'team_view_{registration["team_id"]}'
            )])
        else:
            keyboard.append([
                InlineKeyboardButton(
                    t(lang, 'create_team'),
                    callback_data=f'team_create_{hackathon_id}'
                ),
                InlineKeyboardButton(
                    t(lang, 'join_team'),
                    callback_data=f'team_join_{hackathon_id}'
                )
            ])
        
        # Show stages
        keyboard.append([InlineKeyboardButton(
            "📊 Stages",
            callback_data=f'stages_{hackathon_id}'
        )])
    
    keyboard.append([InlineKeyboardButton(t(lang, 'back'), callback_data='menu_hackathons')])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def register_hackathon(query, context: ContextTypes.DEFAULT_TYPE):
    """Register user for hackathon"""
    hackathon_id = int(query.data.split('_')[1])
    user = await get_user(query.from_user.id)
    lang = user['language']
    
    async with db_pool.acquire() as conn:
        # Check if already registered
        existing = await conn.fetchrow(
            'SELECT * FROM registrations WHERE user_id = $1 AND hackathon_id = $2',
            query.from_user.id, hackathon_id
        )
        
        if existing:
            await query.answer(t(lang, 'already_registered'), show_alert=True)
            return
        
        # Register user
        await conn.execute(
            'INSERT INTO registrations (user_id, hackathon_id) VALUES ($1, $2)',
            query.from_user.id, hackathon_id
        )
    
    keyboard = [
        [
            InlineKeyboardButton(t(lang, 'create_team'), callback_data=f'team_create_{hackathon_id}'),
            InlineKeyboardButton(t(lang, 'join_team'), callback_data=f'team_join_{hackathon_id}')
        ],
        [InlineKeyboardButton(t(lang, 'back'), callback_data=f'hackathon_{hackathon_id}')]
    ]
    
    await query.edit_message_text(
        f"✅ {t(lang, 'registration_complete')}\n\n"
        f"{t(lang, 'create_team')} or {t(lang, 'join_team')}?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def create_team_start(query, context: ContextTypes.DEFAULT_TYPE):
    """Start team creation"""
    hackathon_id = int(query.data.split('_')[2])
    context.user_data['hackathon_id'] = hackathon_id
    context.user_data['awaiting_team_name'] = True
    
    user = await get_user(query.from_user.id)
    lang = user['language']
    
    await query.edit_message_text(t(lang, 'enter_team_name'))

async def join_team_start(query, context: ContextTypes.DEFAULT_TYPE):
    """Start joining team"""
    hackathon_id = int(query.data.split('_')[2])
    context.user_data['hackathon_id'] = hackathon_id
    context.user_data['awaiting_team_code'] = True
    
    user = await get_user(query.from_user.id)
    lang = user['language']
    
    await query.edit_message_text(t(lang, 'enter_team_code'))

async def team_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle team name or code input"""
    user = await get_user(update.effective_user.id)
    lang = user['language']
    
    if context.user_data.get('awaiting_team_name'):
        # Creating team
        team_name = update.message.text
        hackathon_id = context.user_data['hackathon_id']
        team_code = generate_team_code()
        
        async with db_pool.acquire() as conn:
            # Create team
            team = await conn.fetchrow('''
                INSERT INTO teams (hackathon_id, name, code, lead_id)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            ''', hackathon_id, team_name, team_code, update.effective_user.id)
            
            team_id = team['id']
            
            # Add creator as team member
            await conn.execute('''
                INSERT INTO team_members (team_id, user_id, role)
                VALUES ($1, $2, $3)
            ''', team_id, update.effective_user.id, 'Team Lead')
            
            # Update registration
            await conn.execute('''
                UPDATE registrations
                SET team_id = $1
                WHERE user_id = $2 AND hackathon_id = $3
            ''', team_id, update.effective_user.id, hackathon_id)
        
        text = f"✅ {t(lang, 'team_created')}\n\n"
        text += f"👥 {t(lang, 'team_name')}: **{team_name}**\n"
        text += f"🔑 {t(lang, 'team_code')}: `{team_code}`\n\n"
        text += f"{t(lang, 'share_code')}\n\n"
        text += f"ℹ️ {t(lang, 'stage_info')}"
        
        keyboard = [[InlineKeyboardButton(t(lang, 'back'), callback_data='menu_my_hackathons')]]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        
        context.user_data['awaiting_team_name'] = False
        
    elif context.user_data.get('awaiting_team_code'):
        # Joining team
        team_code = update.message.text.strip()
        hackathon_id = context.user_data['hackathon_id']
        
        async with db_pool.acquire() as conn:
            # Find team
            team = await conn.fetchrow('''
                SELECT t.*, h.max_team_size,
                       COUNT(tm.user_id) as current_size
                FROM teams t
                JOIN hackathons h ON t.hackathon_id = h.id
                LEFT JOIN team_members tm ON t.id = tm.team_id
                WHERE t.code = $1 AND t.hackathon_id = $2
                GROUP BY t.id, h.max_team_size
            ''', team_code, hackathon_id)
            
            if not team:
                await update.message.reply_text(t(lang, 'team_not_found'))
                return
            
            if team['current_size'] >= team['max_team_size']:
                await update.message.reply_text(t(lang, 'team_full'))
                context.user_data['awaiting_team_code'] = False
                return
            
            # Add user to team
            await conn.execute('''
                INSERT INTO team_members (team_id, user_id, role)
                VALUES ($1, $2, $3)
            ''', team['id'], update.effective_user.id, 'Member')
            
            # Update registration
            await conn.execute('''
                UPDATE registrations
                SET team_id = $1
                WHERE user_id = $2 AND hackathon_id = $3
            ''', team['id'], update.effective_user.id, hackathon_id)
        
        text = f"✅ {t(lang, 'team_joined')}\n\n"
        text += f"👥 {t(lang, 'team_name')}: **{team['name']}**\n\n"
        text += f"ℹ️ {t(lang, 'stage_info')}"
        
        keyboard = [[InlineKeyboardButton(t(lang, 'back'), callback_data='menu_my_hackathons')]]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        
        context.user_data['awaiting_team_code'] = False
        
    elif context.user_data.get('awaiting_submission'):
        # Handle submission
        await submission_received(update, context)

async def view_team(query, context: ContextTypes.DEFAULT_TYPE):
    """View team members"""
    team_id = int(query.data.split('_')[2])
    user = await get_user(query.from_user.id)
    lang = user['language']
    
    async with db_pool.acquire() as conn:
        team = await conn.fetchrow('SELECT * FROM teams WHERE id = $1', team_id)
        members = await conn.fetch('''
            SELECT u.first_name, u.last_name, tm.role
            FROM team_members tm
            JOIN users u ON tm.user_id = u.user_id
            WHERE tm.team_id = $1
            ORDER BY tm.joined_at
        ''', team_id)
    
    text = f"👥 **{team['name']}**\n"
    text += f"🔑 Code: `{team['code']}`\n\n"
    text += f"{t(lang, 'team_members')}:\n"
    
    for i, member in enumerate(members, 1):
        role_icon = "👑" if member['role'] == 'Team Lead' else "👤"
        text += f"{i}. {role_icon} {member['first_name']} {member['last_name']} - {member['role']}\n"
    
    keyboard = []
    
    # If team lead, show management options
    if team['lead_id'] == query.from_user.id:
        keyboard.append([InlineKeyboardButton(
            t(lang, 'remove_member'),
            callback_data=f'team_manage_{team_id}'
        )])
    else:
        keyboard.append([InlineKeyboardButton(
            t(lang, 'leave_team'),
            callback_data=f'team_leave_{team_id}'
        )])
    
    keyboard.append([InlineKeyboardButton(t(lang, 'back'), callback_data='menu_my_hackathons')])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def show_stages(query, context: ContextTypes.DEFAULT_TYPE):
    """Show hackathon stages"""
    hackathon_id = int(query.data.split('_')[1])
    user = await get_user(query.from_user.id)
    lang = user['language']
    
    async with db_pool.acquire() as conn:
        stages = await conn.fetch('''
            SELECT * FROM stages
            WHERE hackathon_id = $1
            ORDER BY stage_number
        ''', hackathon_id)
    
    if not stages:
        keyboard = [[InlineKeyboardButton(t(lang, 'back'), callback_data=f'hackathon_{hackathon_id}')]]
        await query.edit_message_text(
            "No stages available yet.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    keyboard = []
    for stage in stages:
        status = "⏰" if stage['deadline'] > datetime.now() else "✅"
        keyboard.append([InlineKeyboardButton(
            f"{status} Stage {stage['stage_number']}: {stage['name']}",
            callback_data=f'stage_view_{stage["id"]}'
        )])
    
    keyboard.append([InlineKeyboardButton(t(lang, 'back'), callback_data=f'hackathon_{hackathon_id}')])
    
    await query.edit_message_text(
        "📊 **Stages**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def view_stage(query, context: ContextTypes.DEFAULT_TYPE):
    """View stage details"""
    stage_id = int(query.data.split('_')[2])
    user = await get_user(query.from_user.id)
    lang = user['language']
    
    async with db_pool.acquire() as conn:
        stage = await conn.fetchrow('SELECT * FROM stages WHERE id = $1', stage_id)
        
        # Check if user's team has submitted
        registration = await conn.fetchrow('''
            SELECT team_id FROM registrations
            WHERE user_id = $1 AND hackathon_id = $2
        ''', query.from_user.id, stage['hackathon_id'])
        
        submission = None
        if registration and registration['team_id']:
            submission = await conn.fetchrow('''
                SELECT * FROM submissions
                WHERE team_id = $1 AND stage_id = $2
            ''', registration['team_id'], stage_id)
    
    text = f"📊 **Stage {stage['stage_number']}: {stage['name']}**\n\n"
    text += f"{stage['description']}\n\n"
    text += f"**Task:**\n{stage['task_details']}\n\n"
    text += f"⏰ Deadline: {stage['deadline'].strftime('%d.%m.%Y %H:%M')}\n"
    
    if submission:
        text += f"\n✅ Submitted at: {submission['submitted_at'].strftime('%d.%m.%Y %H:%M')}"
    
    keyboard = []
    
    # Allow submission if deadline not passed and not already submitted
    if datetime.now() < stage['deadline'] and not submission:
        keyboard.append([InlineKeyboardButton(
            t(lang, 'submit'),
            callback_data=f'submit_start_{stage_id}'
        )])
    elif submission:
        keyboard.append([InlineKeyboardButton(
            "✅ Submitted",
            callback_data='noop'
        )])
    else:
        keyboard.append([InlineKeyboardButton(
            t(lang, 'deadline_passed'),
            callback_data='noop'
        )])
    
    keyboard.append([InlineKeyboardButton(t(lang, 'back'), callback_data=f'stages_{stage["hackathon_id"]}')])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def submit_start(query, context: ContextTypes.DEFAULT_TYPE):
    """Start submission process"""
    stage_id = int(query.data.split('_')[2])
    context.user_data['stage_id'] = stage_id
    context.user_data['awaiting_submission'] = True
    
    user = await get_user(query.from_user.id)
    lang = user['language']
    
    text = f"📤 **{t(lang, 'submit')}**\n\n"
    text += "You can send:\n"
    text += "• 🔗 Link (URL)\n"
    text += "• 📄 PDF file\n"
    text += "• 🖼 Image\n"
    text += "• 📊 PowerPoint (PPTX)\n"
    text += "• 📝 Word document (DOCX)\n"
    text += "• 🎥 Video\n"
    text += "• 🎵 Audio\n"
    text += "• 📁 Any document\n"
    
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)

async def submission_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle submission (link or file)"""
    if not context.user_data.get('awaiting_submission'):
        return
    
    stage_id = context.user_data['stage_id']
    user = await get_user(update.effective_user.id)
    lang = user['language']
    
    # Get user's team
    async with db_pool.acquire() as conn:
        stage = await conn.fetchrow('SELECT * FROM stages WHERE id = $1', stage_id)
        
        registration = await conn.fetchrow('''
            SELECT team_id FROM registrations
            WHERE user_id = $1 AND hackathon_id = $2
        ''', update.effective_user.id, stage['hackathon_id'])
        
        if not registration or not registration['team_id']:
            await update.message.reply_text("❌ You must be in a team to submit!")
            context.user_data['awaiting_submission'] = False
            return
        
        team_id = registration['team_id']
        
        # Determine submission type and content
        submission_type = None
        content = None
        file_id = None
        file_name = None
        
        if update.message.text:
            # Text message (should be a link)
            if update.message.text.startswith('http'):
                submission_type = 'link'
                content = update.message.text
            else:
                await update.message.reply_text(t(lang, 'invalid_url'))
                return
        elif update.message.document:
            submission_type = 'document'
            file_id = update.message.document.file_id
            file_name = update.message.document.file_name
        elif update.message.photo:
            submission_type = 'photo'
            file_id = update.message.photo[-1].file_id
            file_name = 'photo.jpg'
        elif update.message.video:
            submission_type = 'video'
            file_id = update.message.video.file_id
            file_name = update.message.video.file_name or 'video.mp4'
        elif update.message.audio:
            submission_type = 'audio'
            file_id = update.message.audio.file_id
            file_name = update.message.audio.file_name or 'audio.mp3'
        elif update.message.voice:
            submission_type = 'voice'
            file_id = update.message.voice.file_id
            file_name = 'voice.ogg'
        else:
            await update.message.reply_text("❌ Unsupported file type!")
            return
        
        # Save submission
        await conn.execute('''
            INSERT INTO submissions (team_id, stage_id, submission_type, content, file_id, file_name, submitted_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        ''', team_id, stage_id, submission_type, content, file_id, file_name, update.effective_user.id)
    
    text = f"✅ {t(lang, 'submission_sent')}\n\n"
    if submission_type == 'link':
        text += f"🔗 Link: {content}"
    else:
        text += f"📎 File: {file_name}"
    
    keyboard = [[InlineKeyboardButton(t(lang, 'back'), callback_data='menu_my_hackathons')]]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    context.user_data['awaiting_submission'] = False

async def export_users(query, context: ContextTypes.DEFAULT_TYPE):
    """Export all users to CSV"""
    async with db_pool.acquire() as conn:
        users = await conn.fetch('SELECT * FROM users ORDER BY created_at')
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['User ID', 'Username', 'First Name', 'Last Name', 'Birth Date', 
                    'Gender', 'Location', 'Phone', 'PINFL', 'Language', 'Created At'])
    
    for user in users:
        writer.writerow([
            user['user_id'],
            user['username'],
            user['first_name'],
            user['last_name'],
            user['birth_date'].strftime('%d.%m.%Y') if user['birth_date'] else '',
            user['gender'],
            user['location'],
            user['phone'],
            user['pinfl'],
            user['language'],
            user['created_at'].strftime('%d.%m.%Y %H:%M')
        ])
    
    # Send file
    output.seek(0)
    await query.message.reply_document(
        document=BytesIO(output.getvalue().encode('utf-8')),
        filename=f'users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        caption=f"📥 Exported {len(users)} users"
    )

async def export_teams(query, context: ContextTypes.DEFAULT_TYPE):
    """Export all teams to CSV"""
    async with db_pool.acquire() as conn:
        teams = await conn.fetch('''
            SELECT t.*, h.name as hackathon_name,
                   COUNT(tm.user_id) as member_count
            FROM teams t
            JOIN hackathons h ON t.hackathon_id = h.id
            LEFT JOIN team_members tm ON t.id = tm.team_id
            GROUP BY t.id, h.name
            ORDER BY t.created_at
        ''')
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Team ID', 'Hackathon', 'Team Name', 'Code', 'Lead ID', 
                    'Member Count', 'Created At'])
    
    for team in teams:
        writer.writerow([
            team['id'],
            team['hackathon_name'],
            team['name'],
            team['code'],
            team['lead_id'],
            team['member_count'],
            team['created_at'].strftime('%d.%m.%Y %H:%M')
        ])
    
    # Send file
    output.seek(0)
    await query.message.reply_document(
        document=BytesIO(output.getvalue().encode('utf-8')),
        filename=f'teams_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        caption=f"📥 Exported {len(teams)} teams"
    )

async def export_submissions(query, context: ContextTypes.DEFAULT_TYPE):
    """Export all submissions to CSV"""
    async with db_pool.acquire() as conn:
        submissions = await conn.fetch('''
            SELECT s.*, t.name as team_name, h.name as hackathon_name,
                   st.name as stage_name, u.first_name, u.last_name
            FROM submissions s
            JOIN teams t ON s.team_id = t.id
            JOIN stages st ON s.stage_id = st.id
            JOIN hackathons h ON st.hackathon_id = h.id
            JOIN users u ON s.submitted_by = u.user_id
            ORDER BY s.submitted_at
        ''')
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Submission ID', 'Hackathon', 'Stage', 'Team', 'Submitted By',
                    'Type', 'Content/Link', 'File ID', 'File Name', 'Submitted At'])
    
    for sub in submissions:
        writer.writerow([
            sub['id'],
            sub['hackathon_name'],
            sub['stage_name'],
            sub['team_name'],
            f"{sub['first_name']} {sub['last_name']}",
            sub['submission_type'],
            sub['content'] or '',
            sub['file_id'] or '',
            sub['file_name'] or '',
            sub['submitted_at'].strftime('%d.%m.%Y %H:%M')
        ])
    
    # Send file
    output.seek(0)
    await query.message.reply_document(
        document=BytesIO(output.getvalue().encode('utf-8')),
        filename=f'submissions_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        caption=f"📥 Exported {len(submissions)} submissions"
    )

async def admin_statistics(query, context: ContextTypes.DEFAULT_TYPE):
    """Show admin statistics"""
    async with db_pool.acquire() as conn:
        total_users = await conn.fetchval('SELECT COUNT(*) FROM users')
        total_teams = await conn.fetchval('SELECT COUNT(*) FROM teams')
        total_hackathons = await conn.fetchval('SELECT COUNT(*) FROM hackathons')
        total_registrations = await conn.fetchval('SELECT COUNT(*) FROM registrations')
        total_submissions = await conn.fetchval('SELECT COUNT(*) FROM submissions')
    
    text = "📊 **Statistics**\n\n"
    text += f"👥 Total Users: {total_users}\n"
    text += f"👨‍👩‍👦 Total Teams: {total_teams}\n"
    text += f"🏆 Total Hackathons: {total_hackathons}\n"
    text += f"📝 Total Registrations: {total_registrations}\n"
    text += f"📤 Total Submissions: {total_submissions}\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='admin_panel')]]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

# Notification scheduler
async def send_deadline_reminders(application: Application):
    """Send automatic deadline reminders"""
    now = datetime.now()
    
    async with db_pool.acquire() as conn:
        # Get stages with upcoming deadlines
        stages = await conn.fetch('''
            SELECT s.*, h.name as hackathon_name
            FROM stages s
            JOIN hackathons h ON s.hackathon_id = h.id
            WHERE s.deadline > $1 AND s.deadline < $2
        ''', now, now + timedelta(days=3))
        
        for stage in stages:
            days_left = (stage['deadline'] - now).days
            
            # Get all registered users for this hackathon
            users = await conn.fetch('''
                SELECT u.user_id, u.language
                FROM users u
                JOIN registrations r ON u.user_id = r.user_id
                WHERE r.hackathon_id = $1
            ''', stage['hackathon_id'])
            
            for user in users:
                lang = user['language']
                message = f"⏰ {days_left} days left!\n\n"
                message += f"{stage['hackathon_name']} - {stage['name']}\n"
                message += f"Deadline: {stage['deadline'].strftime('%d.%m.%Y %H:%M')}"
                
                try:
                    await application.bot.send_message(user['user_id'], message)
                except Exception as e:
                    logger.error(f"Failed to send reminder to {user['user_id']}: {e}")

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Setup database
    application.job_queue.run_once(lambda _: init_db(), when=0)
    
    # Setup scheduler for notifications
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        lambda: asyncio.create_task(send_deadline_reminders(application)),
        'interval',
        hours=6
    )
    scheduler.start()
    
    # Conversation handler for registration
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [CallbackQueryHandler(language_selected, pattern='^lang_')],
            CONSENT: [CallbackQueryHandler(consent_response, pattern='^consent_')],
            FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_name_received)],
            LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, last_name_received)],
            BIRTH_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, birth_date_received)],
            GENDER: [CallbackQueryHandler(gender_selected, pattern='^gender_')],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location_received)],
            PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, phone_received)],
            PINFL: [MessageHandler(filters.TEXT & ~filters.COMMAND, pinfl_received)],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(menu_handler))
    application.add_handler(MessageHandler(
        filters.TEXT | filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.VOICE,
        team_input_handler
    ))
    
    # Start bot
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
