"""
Localization module for Hackathon Bot
Supports: Uzbek (uz), Russian (ru), English (en)
"""

from typing import Dict

# Language display names with flags
LANGUAGES = {
    'uz': {'name': "O'zbekcha", 'flag': '🇺🇿'},
    'ru': {'name': 'Русский', 'flag': '🇷🇺'},
    'en': {'name': 'English', 'flag': '🇬🇧'}
}

# All translations
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # ==========================================================================
    # WELCOME & GENERAL
    # ==========================================================================
    'welcome': {
        'uz': "👋 IT Community Hackathons Botiga xush kelibsiz!\n\n"
              "Bu bot sizga hackathonlarimizda samarali ishtirok etishga yordam beradi 💡\n\n"
              "Bu yerda siz:\n"
              "• Kelgusi hackathonlarga ro'yxatdan o'tishingiz mumkin 📝\n"
              "• Vazifalarni qabul qilish va topshirish 🎯\n"
              "• O'z jamoangiz natijalarini kuzatish 📊\n"
              "• Yangiliklar va e'lonlardan xabardor bo'lish 📢\n\n"
              "Yordam kerakmi? ai500@itcommunity.uz ga yozing.\n\n"
              "Omad va hackathonlarimizda ajoyib narsalar yarating! 💚",
        'ru': "👋 Добро пожаловать в IT Community Hackathons Bot!\n\n"
              "Этот бот помогает эффективно участвовать в наших хакатонах 💡\n\n"
              "Здесь вы можете:\n"
              "• Зарегистрироваться на предстоящие хакатоны 📝\n"
              "• Получать и отправлять задания 🎯\n"
              "• Отслеживать прогресс и результаты 📊\n"
              "• Быть в курсе объявлений 📢\n\n"
              "Нужна помощь? Пишите на ai500@itcommunity.uz\n\n"
              "Удачи и создавайте что-то потрясающее! 💚",
        'en': "👋 Welcome to IT Community Hackathons Bot!\n\n"
              "This bot helps you participate in our hackathons effectively 💡\n\n"
              "Here you can:\n"
              "• Register for upcoming hackathons 📝\n"
              "• Receive and submit tasks 🎯\n"
              "• Track your progress and results 📊\n"
              "• Stay updated with announcements 📢\n\n"
              "Need help? Send your question to ai500@itcommunity.uz\n\n"
              "Good luck and build something amazing with our hackathons! 💚"
    },
    
    'welcome_back': {
        'uz': "👋 Qaytib kelganingizdan xursandmiz!",
        'ru': "👋 С возвращением!",
        'en': "👋 Welcome back!"
    },
    
    'main_menu': {
        'uz': "🏠 Asosiy menyu",
        'ru': "🏠 Главное меню",
        'en': "🏠 Main Menu"
    },
    
    # ==========================================================================
    # BUTTONS
    # ==========================================================================
    'btn_hackathons': {
        'uz': "🚀 Hackathonlar",
        'ru': "🚀 Хакатоны",
        'en': "🚀 Hackathons"
    },
    
    'btn_my_hackathons': {
        'uz': "📁 Mening hackathonlarim",
        'ru': "📁 Мои хакатоны",
        'en': "📁 My hackathons"
    },
    
    'btn_settings': {
        'uz': "⚙️ Sozlamalar",
        'ru': "⚙️ Настройки",
        'en': "⚙️ Settings"
    },
    
    'btn_help': {
        'uz': "❓ Yordam",
        'ru': "❓ Помощь",
        'en': "❓ Help"
    },
    
    'btn_back': {
        'uz': "⬅️ Orqaga",
        'ru': "⬅️ Назад",
        'en': "⬅️ Back"
    },
    
    'btn_register': {
        'uz': "✅ Ro'yxatdan o'tish",
        'ru': "✅ Зарегистрироваться",
        'en': "✅ Register"
    },
    
    'btn_see_details': {
        'uz': "ℹ️ Batafsil ko'rish",
        'ru': "ℹ️ Подробнее",
        'en': "ℹ️ See details"
    },
    
    'btn_leave_team': {
        'uz': "🚪 Jamoani tark etish",
        'ru': "🚪 Покинуть команду",
        'en': "🚪 Leave team"
    },
    
    'btn_remove_member': {
        'uz': "❌ A'zoni o'chirish",
        'ru': "❌ Удалить участника",
        'en': "❌ Remove member"
    },
    
    'btn_change_language': {
        'uz': "🌐 Tilni o'zgartirish",
        'ru': "🌐 Изменить язык",
        'en': "🌐 Change language"
    },
    
    'btn_edit_personal_data': {
        'uz': "👤 Shaxsiy ma'lumotlarni tahrirlash",
        'ru': "👤 Редактировать личные данные",
        'en': "👤 Edit personal data"
    },
    
    'btn_no_portfolio': {
        'uz': "🚫 Portfolio yo'q",
        'ru': "🚫 Нет портфолио",
        'en': "🚫 No portfolio"
    },
    
    # ==========================================================================
    # REGISTRATION FLOW
    # ==========================================================================
    'enter_first_name': {
        'uz': "Ismingizni kiriting (masalan, Robiya)",
        'ru': "Введите ваше имя (например, Робия)",
        'en': "Enter your first name (e.g. Robiya)"
    },
    
    'enter_last_name': {
        'uz': "Familiyangizni kiriting (masalan, Axmedova)",
        'ru': "Введите вашу фамилию (например, Ахмедова)",
        'en': "Enter your last name (e.g. Akhmedova)"
    },
    
    'enter_birth_date': {
        'uz': "Tug'ilgan sanangizni kiriting (masalan, 23.10.2003)",
        'ru': "Введите дату рождения (например, 23.10.2003)",
        'en': "Enter your birth date (e.g. 23.10.2003)"
    },
    
    'enter_gender': {
        'uz': "Jinsingizni tanlang:",
        'ru': "Выберите ваш пол:",
        'en': "Select your gender:"
    },
    
    'gender_male': {
        'uz': "👨 Erkak",
        'ru': "👨 Мужской",
        'en': "👨 Male"
    },
    
    'gender_female': {
        'uz': "👩 Ayol",
        'ru': "👩 Женский",
        'en': "👩 Female"
    },
    
    'enter_location': {
        'uz': "Joylashuvingizni kiriting (masalan, Toshkent shahri)",
        'ru': "Введите ваше местоположение (например, город Ташкент)",
        'en': "Enter your location (e.g. City of Tashkent)"
    },
    
    'enter_phone': {
        'uz': "📱 Telefon raqamingizni yuboring (tugma orqali)",
        'ru': "📱 Отправьте ваш номер телефона (через кнопку)",
        'en': "📱 Send your phone number (via button)"
    },
    
    'btn_send_phone': {
        'uz': "📱 Telefon raqamini yuborish",
        'ru': "📱 Отправить номер телефона",
        'en': "📱 Send phone number"
    },
    
    'enter_pinfl': {
        'uz': "JSHSHIR raqamingizni kiriting - 14 raqam.\n\n"
              "JSHSHIR nima uchun kerak:\n"
              "- yoshingizni tekshirish\n"
              "- final tadbirida ishtirokingizni tashkil qilish (mehmonxona band qilish, chipta sotib olish)",
        'ru': "Введите ваш ПИНФЛ - 14 цифр.\n\n"
              "Зачем нужен ПИНФЛ:\n"
              "- для проверки возраста\n"
              "- для организации участия в финальном мероприятии (бронирование отеля, покупка билетов)",
        'en': "Please enter your Personal Identification Number (PINFL) - 14 digits.\n\n"
              "Why we require your PINFL:\n"
              "- to verify your age\n"
              "- to organize your participation in the final event if needed (booking accommodation and purchasing tickets)"
    },
    
    'registration_almost_done': {
        'uz': "Deyarli tayyor! ⏳\n\n"
              "Ishtirokingizni tasdiqlash uchun hackathonni tanlang:\n"
              "Menu → 🚀 Hackathonlar → Hackathonni tanlang → Ro'yxatdan o'tish ✅\n\n"
              "⚠️ Hackathon tanlamasdan ro'yxatdan o'tish yaroqsiz",
        'ru': "Почти готово! ⏳\n\n"
              "Для подтверждения участия выберите хакатон:\n"
              "Меню → 🚀 Хакатоны → Выберите хакатон → Зарегистрироваться ✅\n\n"
              "⚠️ Регистрация без выбора хакатона недействительна",
        'en': "You're almost done! ⏳\n\n"
              "To confirm your participation, please choose your hackathon:\n"
              "Menu → 🚀 Hackathons → Select hackathon → Register ✅\n\n"
              "⚠️ Registration without selecting a hackathon is not valid"
    },
    
    # ==========================================================================
    # TEAM FLOW
    # ==========================================================================
    'enter_team_name': {
        'uz': "Jamoa nomini kiriting:",
        'ru': "Введите название команды:",
        'en': "Enter your team name:"
    },
    
    'enter_team_role': {
        'uz': "Jamodagi rolingizni kiriting:\n(masalan, Backend Developer, Designer, Project Manager)",
        'ru': "Введите вашу роль в команде:\n(например, Backend Developer, Designer, Project Manager)",
        'en': "Enter your role in the team:\n(e.g. Backend Developer, Designer, Project Manager)"
    },
    
    'enter_field': {
        'uz': "Qaysi sohada ishlaysiz yoki o'qiysiz?\n(masalan, NLP, Machine Learning, AI, Web, Mobile va h.k.)",
        'ru': "В какой области вы работаете или учитесь?\n(например, NLP, Machine Learning, AI, Web, Mobile и т.д.)",
        'en': "What field are you working or studying in?\n(e.g. NLP, Machine Learning, AI, Web, Mobile, etc.)"
    },
    
    'enter_portfolio': {
        'uz': "Portfolio havolangizni yuboring (ixtiyoriy, lekin tavsiya etiladi).\n"
              "Agar yo'q bo'lsa, pastdagi tugmani bosing 👇\n\n"
              "Portfolio veb-sayt, LinkedIn, Behance, GitHub yoki loyihalaringizga havolalar bo'lishi mumkin",
        'ru': "Пожалуйста, предоставьте ссылку на ваше портфолио (опционально, но рекомендуется).\n"
              "Если его нет, нажмите кнопку ниже 👇\n\n"
              "Портфолио может быть вашим сайтом, LinkedIn, Behance, GitHub или ссылками на проекты",
        'en': "Please provide a link to your portfolio (optional but recommended).\n"
              "If you don't have one, click the button below 👇\n\n"
              "Your portfolio can be a website, LinkedIn, Behance, GitHub, or links to your projects"
    },
    
    'team_created': {
        'uz': "✅ Jamoa yaratildi!",
        'ru': "✅ Команда создана!",
        'en': "✅ Team created!"
    },
    
    'team_info': {
        'uz': "🏆 {hackathon}\n\n"
              "👥 Jamoangiz:\n"
              "📛 Nomi: {name}\n"
              "🎟 Kod: {code}\n\n"
              "👤 A'zolar:\n{members}\n\n"
              "Bu hackathon haqida ko'proq bilish uchun pastdagi tugmadan foydalaning 👇",
        'ru': "🏆 {hackathon}\n\n"
              "👥 Ваша команда:\n"
              "📛 Название: {name}\n"
              "🎟 Код: {code}\n\n"
              "👤 Участники:\n{members}\n\n"
              "Чтобы узнать больше об этом хакатоне, используйте кнопку ниже 👇",
        'en': "🏆 {hackathon}\n\n"
              "👥 Your team:\n"
              "📛 Name: {name}\n"
              "🎟 Code: {code}\n\n"
              "👤 Members:\n{members}\n\n"
              "To see more about this hackathon, use the button below 👇"
    },
    
    # ==========================================================================
    # HACKATHONS
    # ==========================================================================
    'no_hackathons': {
        'uz': "❌ Hozircha mavjud hackathonlar yo'q",
        'ru': "❌ Нет доступных хакатонов",
        'en': "❌ No hackathons available"
    },
    
    'your_hackathons': {
        'uz': "📁 Sizning hackathonlaringiz:",
        'ru': "📁 Ваши хакатоны:",
        'en': "📁 Your hackathons:"
    },
    
    'no_registered_hackathons': {
        'uz': "Siz hali birorta hackathonga ro'yxatdan o'tmagansiz.",
        'ru': "Вы пока не зарегистрированы ни на один хакатон.",
        'en': "You haven't registered for any hackathons yet."
    },
    
    'hackathon_info': {
        'uz': "🏆 {name}\n\n"
              "📋 {description}\n\n"
              "🏅 Sovrin jamg'armasi: {prize}\n"
              "📅 Sana: {start} — {end}\n"
              "⏰ Ro'yxatdan o'tish muddati: {deadline}",
        'ru': "🏆 {name}\n\n"
              "📋 {description}\n\n"
              "🏅 Призовой фонд: {prize}\n"
              "📅 Даты: {start} — {end}\n"
              "⏰ Дедлайн регистрации: {deadline}",
        'en': "🏆 {name}\n\n"
              "📋 {description}\n\n"
              "🏅 Prize pool: {prize}\n"
              "📅 Dates: {start} — {end}\n"
              "⏰ Registration deadline: {deadline}"
    },
    
    # ==========================================================================
    # STAGES & TASKS
    # ==========================================================================
    'stage_info': {
        'uz': "📍 {hackathon} — {stage}\n"
              "📅 {start} — {end}\n\n"
              "🎉 {stage} ga kirganingiz bilan tabriklaymiz!\n\n"
              "📝 Vazifa: {task}\n\n"
              "❗ Muddat: {deadline}\n"
              "❗ Topshirish: Demo veb-sayt havolasini ushbu botda yuboring ({stage} tugmasi)",
        'ru': "📍 {hackathon} — {stage}\n"
              "📅 {start} — {end}\n\n"
              "🎉 Поздравляем с прохождением в {stage}!\n\n"
              "📝 Задание: {task}\n\n"
              "❗ Дедлайн: {deadline}\n"
              "❗ Отправка: Пришлите ссылку на демо-сайт в этот бот (кнопка {stage})",
        'en': "📍 {hackathon} — {stage}\n"
              "📅 {start} — {end}\n\n"
              "🎉 Congratulations on making it to {stage}!\n\n"
              "📝 Your task: {task}\n\n"
              "❗ Deadline: {deadline}\n"
              "❗ Submission: Send the link to your live demo website in this bot ({stage} button)"
    },
    
    'deadline_passed': {
        'uz': "⏰ {stage} muddati allaqachon o'tdi :(",
        'ru': "⏰ Дедлайн {stage} уже прошел :(",
        'en': "⏰ {stage} deadline has already passed :("
    },
    
    'deadline_approaching': {
        'uz': "⏳ {stage} muddati yaqinlashmoqda!\n\n"
              "Bugun {time} gacha — {stage} javoblarini topshirish uchun oxirgi imkoniyat. "
              "{hackathon} Tanlash jamoasi {review_dates} da topshiriqlarni ko'rib chiqadi.\n\n"
              "{announce_date} — {next_stage} ga o'tgan jamoalar e'lon qilinadi! ✨",
        'ru': "⏳ Приближается дедлайн {stage}!\n\n"
              "Сегодня до {time} — последний шанс отправить ответы {stage}. "
              "Команда отбора {hackathon} рассмотрит заявки {review_dates}.\n\n"
              "{announce_date} — будут объявлены команды, прошедшие в {next_stage}! ✨",
        'en': "⏳ {stage} deadline approaching!\n\n"
              "Today until {time} — the final chance to submit your {stage} answers. "
              "The {hackathon} Selection Team will review submissions on {review_dates}.\n\n"
              "{announce_date} — teams advancing to {next_stage} will be announced! ✨"
    },
    
    'btn_stage': {
        'uz': "📋 {stage}",
        'ru': "📋 {stage}",
        'en': "📋 {stage}"
    },
    
    'submit_prompt': {
        'uz': "Demo veb-sayt havolangizni yuboring:",
        'ru': "Отправьте ссылку на ваш демо-сайт:",
        'en': "Send the link to your demo website:"
    },
    
    'submission_received': {
        'uz': "✅ Topshiriq qabul qilindi!\n\nHavola: {link}",
        'ru': "✅ Заявка принята!\n\nСсылка: {link}",
        'en': "✅ Submission received!\n\nLink: {link}"
    },
    
    # ==========================================================================
    # SETTINGS
    # ==========================================================================
    'settings_menu': {
        'uz': "⚙️ Sozlamalar menyusi:",
        'ru': "⚙️ Меню настроек:",
        'en': "⚙️ Settings menu:"
    },
    
    'choose_language': {
        'uz': "🌐 Tilni tanlang:",
        'ru': "🌐 Выберите язык:",
        'en': "🌐 Choose your language:"
    },
    
    'language_changed': {
        'uz': "✅ Til o'zgartirildi: O'zbekcha",
        'ru': "✅ Язык изменен: Русский",
        'en': "✅ Language changed: English"
    },
    
    'your_data': {
        'uz': "👤 Sizning ma'lumotlaringiz:\n\n"
              "• Ism: {first_name}\n"
              "• Familiya: {last_name}\n"
              "• Tug'ilgan sana: {birth_date}\n"
              "• Jins: {gender}\n"
              "• Joylashuv: {location}",
        'ru': "👤 Ваши данные:\n\n"
              "• Имя: {first_name}\n"
              "• Фамилия: {last_name}\n"
              "• Дата рождения: {birth_date}\n"
              "• Пол: {gender}\n"
              "• Местоположение: {location}",
        'en': "👤 Your data:\n\n"
              "• First name: {first_name}\n"
              "• Last name: {last_name}\n"
              "• Birth date: {birth_date}\n"
              "• Gender: {gender}\n"
              "• Location: {location}"
    },
    
    'btn_change_first_name': {
        'uz': "✏️ Ismni o'zgartirish",
        'ru': "✏️ Изменить имя",
        'en': "✏️ Change first name"
    },
    
    'btn_change_last_name': {
        'uz': "✏️ Familiyani o'zgartirish",
        'ru': "✏️ Изменить фамилию",
        'en': "✏️ Change last name"
    },
    
    'btn_change_birth_date': {
        'uz': "✏️ Tug'ilgan sanani o'zgartirish",
        'ru': "✏️ Изменить дату рождения",
        'en': "✏️ Change birth date"
    },
    
    'btn_change_gender': {
        'uz': "✏️ Jinsni o'zgartirish",
        'ru': "✏️ Изменить пол",
        'en': "✏️ Change gender"
    },
    
    'btn_change_location': {
        'uz': "✏️ Joylashuvni o'zgartirish",
        'ru': "✏️ Изменить местоположение",
        'en': "✏️ Change location"
    },
    
    'data_updated': {
        'uz': "✅ Ma'lumot yangilandi!",
        'ru': "✅ Данные обновлены!",
        'en': "✅ Data updated!"
    },
    
    # ==========================================================================
    # HELP
    # ==========================================================================
    'help_message': {
        'uz': "💡 Yordam kerakmi yoki xato topdingizmi?\n\n"
              "Agar savollaringiz bo'lsa, botdan foydalanishda yordam kerak bo'lsa yoki "
              "takomillashtirish bo'yicha takliflaringiz bo'lsa, biz bilan bog'laning:\n"
              "📧 ai500@itcommunity.uz\n\n"
              "Muammoni batafsil tasvirlab bering va iloji bo'lsa skrinshot qo'shing.\n"
              "Tez orada javob beramiz ✅",
        'ru': "💡 Нужна помощь или нашли ошибку?\n\n"
              "Если у вас есть вопросы, нужна помощь в использовании бота или есть "
              "предложения по улучшению, свяжитесь с нами:\n"
              "📧 ai500@itcommunity.uz\n\n"
              "Опишите проблему подробно и приложите скриншоты, если возможно.\n"
              "Мы скоро вернемся к вам ✅",
        'en': "💡 Need help or found a bug?\n\n"
              "If you have questions, need assistance using the bot or have "
              "suggestions for improvement, please contact us at:\n"
              "📧 ai500@itcommunity.uz\n\n"
              "Describe the problem in detail and attach screenshots if possible.\n"
              "We will get back to you soon ✅"
    },
    
    # ==========================================================================
    # ADMIN
    # ==========================================================================
    'admin_only': {
        'uz': "⛔ Bu buyruq faqat adminlar uchun",
        'ru': "⛔ Эта команда только для админов",
        'en': "⛔ This command is for admins only"
    },
    
    'broadcast_prompt': {
        'uz': "📢 Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:",
        'ru': "📢 Введите сообщение для отправки всем пользователям:",
        'en': "📢 Enter the message to send to all users:"
    },
    
    'broadcast_sent': {
        'uz': "✅ Xabar {count} foydalanuvchiga yuborildi",
        'ru': "✅ Сообщение отправлено {count} пользователям",
        'en': "✅ Message sent to {count} users"
    },
    
    'export_complete': {
        'uz': "✅ Eksport tayyor",
        'ru': "✅ Экспорт готов",
        'en': "✅ Export complete"
    },
    
    # ==========================================================================
    # ERRORS & VALIDATION
    # ==========================================================================
    'invalid_date': {
        'uz': "❌ Noto'g'ri sana formati. Iltimos, DD.MM.YYYY formatida kiriting (masalan, 23.10.2003)",
        'ru': "❌ Неверный формат даты. Пожалуйста, введите в формате ДД.ММ.ГГГГ (например, 23.10.2003)",
        'en': "❌ Invalid date format. Please enter in DD.MM.YYYY format (e.g. 23.10.2003)"
    },
    
    'invalid_pinfl': {
        'uz': "❌ JSHSHIR 14 ta raqamdan iborat bo'lishi kerak",
        'ru': "❌ ПИНФЛ должен состоять из 14 цифр",
        'en': "❌ PINFL must be exactly 14 digits"
    },
    
    'invalid_link': {
        'uz': "❌ Noto'g'ri havola. Iltimos, to'g'ri URL kiriting (http:// yoki https:// bilan boshlanishi kerak)",
        'ru': "❌ Неверная ссылка. Пожалуйста, введите корректный URL (должен начинаться с http:// или https://)",
        'en': "❌ Invalid link. Please enter a valid URL (must start with http:// or https://)"
    },
    
    'error_occurred': {
        'uz': "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
        'ru': "❌ Произошла ошибка. Пожалуйста, попробуйте снова.",
        'en': "❌ An error occurred. Please try again."
    },
    
    'operation_cancelled': {
        'uz': "❌ Amal bekor qilindi",
        'ru': "❌ Операция отменена",
        'en': "❌ Operation cancelled"
    },
    
    # ==========================================================================
    # NOTIFICATIONS
    # ==========================================================================
    'days_left': {
        'uz': "⏳ Birinchi vazifagacha {days} kun qoldi!\n\n"
              "Birinchi vazifangiz tez orada keladi, shuning uchun hozir loyiha g'oyangizni aniqlash uchun yaxshi vaqt.\n\n"
              "Agar aniq yo'nalishingiz bo'lmasa, qishloq xo'jaligi 🌾 yo'nalishini o'rganishni o'ylab ko'ring — "
              "bizning hamkorlarimiz bu sohaga alohida qiziqish bildirmoqda.\n\n"
              "Agar g'oyangiz tayyor bo'lsa, davom eting.\n\n"
              "🏆 {hackathon}da eng kuchli loyiha g'olib bo'ladi — yo'nalishdan qat'i nazar.\n\n"
              "Savollar bormi? ai500@itcommunity.uz ga murojaat qiling 📧",
        'ru': "⏳ До первого задания осталось {days} дней!\n\n"
              "Ваше первое задание скоро появится, так что сейчас самое время определиться с идеей проекта.\n\n"
              "Если у вас еще нет четкого направления, можете рассмотреть сельское хозяйство 🌾 — "
              "наши партнеры особенно заинтересованы в этой области.\n\n"
              "Если идея уже есть, продолжайте работать.\n\n"
              "🏆 В {hackathon} побеждает сильнейший проект — независимо от направления.\n\n"
              "Вопросы? Обращайтесь на ai500@itcommunity.uz 📧",
        'en': "⏳ {days} days left until the first task!\n\n"
              "Your first task is coming up soon, so now is a good time to settle on your project idea.\n\n"
              "If you don't yet have a clear direction, you may consider exploring agriculture 🌾 — "
              "our partners have a special interest in this area.\n\n"
              "If you already have your idea, just keep going.\n\n"
              "🏆 At {hackathon}, the strongest project wins — regardless of the track.\n\n"
              "Questions? Contact support at ai500@itcommunity.uz 📧"
    },
    
    'first_task_soon': {
        'uz': "⏳ Ikki kundan keyin birinchi vazifangizni olasiz!",
        'ru': "⏳ Через два дня вы получите свое первое задание!",
        'en': "⏳ In just two days you will receive your first task!"
    },
}


def get_text(key: str, lang: str = 'uz', **kwargs) -> str:
    """
    Get translated text for a given key and language.
    
    Args:
        key: Translation key
        lang: Language code (uz, ru, en)
        **kwargs: Format arguments for the text
    
    Returns:
        Translated and formatted text
    """
    if key not in TRANSLATIONS:
        return f"[Missing translation: {key}]"
    
    translations = TRANSLATIONS[key]
    
    # Fallback to Uzbek if language not found
    if lang not in translations:
        lang = 'uz'
    
    text = translations.get(lang, translations.get('uz', f"[Missing: {key}]"))
    
    # Format with provided arguments
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError as e:
            pass  # Return unformatted if args missing
    
    return text


def t(key: str, lang: str = 'uz', **kwargs) -> str:
    """Shorthand alias for get_text()"""
    return get_text(key, lang, **kwargs)
