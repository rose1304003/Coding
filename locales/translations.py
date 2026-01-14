"""
Localization module for CBU Coding Hackathon Bot
Supports: Uzbek (uz), Russian (ru), English (en)

Includes GDPR/Privacy consent (Oferta) in all three languages
"""

from typing import Dict

# Language display names with flags
LANGUAGES = {
    'uz': {'name': "O'zbekcha", 'flag': '🇺🇿'},
    'ru': {'name': 'Русский', 'flag': '🇷🇺'},
    'en': {'name': 'English', 'flag': '🇬🇧'}
}

# Contact email
SUPPORT_EMAIL = "itcommunityuzbekistan@gmail.com"

# All translations
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # ==========================================================================
    # OFFER / CONSENT (OFERTA) - PERSONAL DATA PROCESSING AGREEMENT
    # ==========================================================================
    'offer_title': {
        'uz': "📋 SHAXSIY MA'LUMOTLARNI QAYTA ISHLASH HAQIDA ROZILIK",
        'ru': "📋 СОГЛАСИЕ НА ОБРАБОТКУ ПЕРСОНАЛЬНЫХ ДАННЫХ",
        'en': "📋 CONSENT FOR PERSONAL DATA PROCESSING"
    },
    
    'offer_full_text': {
        'uz': """📋 SHAXSIY MA'LUMOTLARNI QAYTA ISHLASH HAQIDA ROZILIK

O'zbekiston Respublikasining "Shaxsiy ma'lumotlar to'g'risida"gi Qonuniga muvofiq, men quyidagi shartlarga rozilik bildiraman:

1. MA'LUMOTLAR EGASI
Men, Telegram foydalanuvchisi, o'z shaxsiy ma'lumotlarimni "CBU Coding Hackathon - 2026" tanlovi doirasida qayta ishlashga rozilik beraman.

2. MA'LUMOTLAR QAYTA ISHLOVCHISI
O'zbekiston Respublikasi Markaziy banki va Axborotlashtirish Bosh markazi.

3. QAYTA ISHLANADIGAN MA'LUMOTLAR
• Ism va familiya
• Tug'ilgan sana
• Jins
• Telefon raqami
• JSHSHIR (Jismoniy shaxsning shaxsiy identifikatsiya raqami)
• Joylashuv/manzil
• Telegram username va ID
• Hackathon topshiriqlari (linklar, fayllar)
• Jamoaviy ma'lumotlar

4. QAYTA ISHLASH MAQSADI
• Tanlovga ro'yxatdan o'tkazish va ishtirokni tasdiqlash
• Yoshni tekshirish (JSHSHIR orqali)
• Final tadbirda ishtirokni tashkil etish
• Aloqa va bildirishnomalar yuborish
• Natijalarni e'lon qilish va sovrinlarni topshirish

5. SAQLASH MUDDATI
Ma'lumotlar hackathon tugaganidan keyin 1 (bir) yil mobaynida saqlanadi, so'ngra avtomatik ravishda o'chiriladi.

6. FOYDALANUVCHI HUQUQLARI
Sizning huquqlaringiz:
• Ma'lumotlaringizga kirish
• Noto'g'ri ma'lumotlarni tuzatish
• Ma'lumotlarni o'chirishni so'rash
• Rozilikni bekor qilish

7. HAVFSIZLIK
Barcha ma'lumotlar shifrlangan holda saqlanadi va faqat vakolatli shaxslar tomonidan foydalaniladi.

⚠️ Diqqat: Ushbu rozilikni bekor qilsangiz, tanlovda ishtirok etishingiz bekor qilinadi.

✅ "Roziman" tugmasini bosish orqali siz yuqoridagi shartlarga to'liq rozilik bildirasiz.""",

        'ru': """📋 СОГЛАСИЕ НА ОБРАБОТКУ ПЕРСОНАЛЬНЫХ ДАННЫХ

В соответствии с Законом Республики Узбекистан «О персональных данных», я даю согласие на следующие условия:

1. СУБЪЕКТ ДАННЫХ
Я, пользователь Telegram, даю согласие на обработку моих персональных данных в рамках конкурса «CBU Coding Hackathon - 2026».

2. ОПЕРАТОР ДАННЫХ
Центральный банк Республики Узбекистан и Главный центр информатизации.

3. ОБРАБАТЫВАЕМЫЕ ДАННЫЕ
• Имя и фамилия
• Дата рождения
• Пол
• Номер телефона
• ПИНФЛ (Персональный идентификационный номер физического лица)
• Местоположение/адрес
• Telegram username и ID
• Материалы хакатона (ссылки, файлы)
• Командные данные

4. ЦЕЛЬ ОБРАБОТКИ
• Регистрация и подтверждение участия в конкурсе
• Проверка возраста (через ПИНФЛ)
• Организация участия в финальном мероприятии
• Связь и отправка уведомлений
• Объявление результатов и вручение призов

5. СРОК ХРАНЕНИЯ
Данные хранятся в течение 1 (одного) года после завершения хакатона, после чего автоматически удаляются.

6. ПРАВА ПОЛЬЗОВАТЕЛЯ
Ваши права:
• Доступ к вашим данным
• Исправление неточных данных
• Запрос на удаление данных
• Отзыв согласия

7. БЕЗОПАСНОСТЬ
Все данные хранятся в зашифрованном виде и используются только уполномоченными лицами.

⚠️ Внимание: При отзыве согласия ваше участие в конкурсе будет аннулировано.

✅ Нажимая кнопку «Согласен», вы полностью соглашаетесь с вышеуказанными условиями.""",

        'en': """📋 CONSENT FOR PERSONAL DATA PROCESSING

In accordance with the Law of the Republic of Uzbekistan "On Personal Data", I consent to the following terms:

1. DATA SUBJECT
I, the Telegram user, consent to the processing of my personal data within the framework of the "CBU Coding Hackathon - 2026" competition.

2. DATA CONTROLLER
Central Bank of the Republic of Uzbekistan and Main Center of Informatization.

3. DATA PROCESSED
• First and last name
• Date of birth
• Gender
• Phone number
• PINFL (Personal Identification Number of Individual)
• Location/address
• Telegram username and ID
• Hackathon submissions (links, files)
• Team information

4. PURPOSE OF PROCESSING
• Registration and confirmation of participation in the competition
• Age verification (via PINFL)
• Organization of participation in the final event
• Communication and sending notifications
• Announcement of results and awarding prizes

5. RETENTION PERIOD
Data is stored for 1 (one) year after the hackathon ends, then automatically deleted.

6. USER RIGHTS
Your rights:
• Access to your data
• Correction of inaccurate data
• Request for data deletion
• Withdrawal of consent

7. SECURITY
All data is stored in encrypted form and used only by authorized persons.

⚠️ Note: If you withdraw consent, your participation in the competition will be cancelled.

✅ By clicking "I Agree", you fully agree to the above terms."""
    },
    
    'offer_short': {
        'uz': "📋 Davom etish uchun shaxsiy ma'lumotlaringizni qayta ishlashga rozilik berishingiz kerak.\n\n"
              "Batafsil ma'lumot uchun quyidagi tugmani bosing:",
        'ru': "📋 Для продолжения необходимо дать согласие на обработку персональных данных.\n\n"
              "Для подробной информации нажмите кнопку ниже:",
        'en': "📋 To continue, you need to consent to the processing of your personal data.\n\n"
              "For detailed information, click the button below:"
    },
    
    'btn_read_offer': {
        'uz': "📖 Ofertani o'qish",
        'ru': "📖 Прочитать оферту",
        'en': "📖 Read the offer"
    },
    
    'btn_agree': {
        'uz': "✅ Roziman",
        'ru': "✅ Согласен",
        'en': "✅ I Agree"
    },
    
    'btn_decline': {
        'uz': "❌ Rad etaman",
        'ru': "❌ Отказываюсь",
        'en': "❌ I Decline"
    },
    
    'offer_accepted': {
        'uz': "✅ Rozilik qabul qilindi!\n\nEndi ro'yxatdan o'tishni davom ettirishingiz mumkin.",
        'ru': "✅ Согласие принято!\n\nТеперь вы можете продолжить регистрацию.",
        'en': "✅ Consent accepted!\n\nYou can now continue with registration."
    },
    
    'offer_declined': {
        'uz': "❌ Siz rozilik berishni rad etdingiz.\n\n"
              "Afsuski, rozilik bermasdan tanlovda ishtirok etish imkonsiz.\n\n"
              "Agar fikirngizni o'zgartirsangiz, /start buyrug'ini yuboring.",
        'ru': "❌ Вы отказались дать согласие.\n\n"
              "К сожалению, без согласия участие в конкурсе невозможно.\n\n"
              "Если передумаете, отправьте команду /start.",
        'en': "❌ You declined to give consent.\n\n"
              "Unfortunately, participation in the competition is not possible without consent.\n\n"
              "If you change your mind, send the /start command."
    },
    
    'offer_required': {
        'uz': "⚠️ Davom etish uchun avval ofertaga rozilik berishingiz kerak.",
        'ru': "⚠️ Для продолжения сначала необходимо принять оферту.",
        'en': "⚠️ You must accept the offer first to continue."
    },
    
    # ==========================================================================
    # WELCOME & GENERAL
    # ==========================================================================
    'welcome': {
        'uz': """👋 CBU Coding Hackathon Botiga xush kelibsiz!

🏦 O'zbekiston Respublikasi Markaziy banki va Axborotlashtirish Bosh markazi tomonidan tashkil etilgan.

Bu bot sizga hackathonlarimizda samarali ishtirok etishga yordam beradi 💡

Bu yerda siz:
• Kelgusi hackathonlarga ro'yxatdan o'tishingiz mumkin 📝
• Vazifalarni qabul qilish va topshirish 🎯
• O'z jamoangiz natijalarini kuzatish 📊
• Yangiliklar va e'lonlardan xabardor bo'lish 📢

Omad va hackathonlarimizda ajoyib narsalar yarating! 💚""",
        'ru': """👋 Добро пожаловать в CBU Coding Hackathon Bot!

🏦 Организован Центральным банком Республики Узбекистан и Главным центром информатизации.

Этот бот помогает эффективно участвовать в наших хакатонах 💡

Здесь вы можете:
• Зарегистрироваться на предстоящие хакатоны 📝
• Получать и отправлять задания 🎯
• Отслеживать прогресс и результаты 📊
• Быть в курсе объявлений 📢

Удачи и создавайте что-то потрясающее! 💚""",
        'en': """👋 Welcome to CBU Coding Hackathon Bot!

🏦 Organized by the Central Bank of the Republic of Uzbekistan and Main Center of Informatization.

This bot helps you participate in our hackathons effectively 💡

Here you can:
• Register for upcoming hackathons 📝
• Receive and submit tasks 🎯
• Track your progress and results 📊
• Stay updated with announcements 📢

Good luck and build something amazing with our hackathons! 💚"""
    },
    
    'choose_language': {
        'uz': "🌐 Tilni tanlang:",
        'ru': "🌐 Выберите язык:",
        'en': "🌐 Choose your language:"
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
    
    'btn_main_menu': {
        'uz': "🏠 Asosiy menyu",
        'ru': "🏠 Главное меню",
        'en': "🏠 Main Menu"
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
    
    'btn_cancel': {
        'uz': "❌ Bekor qilish",
        'ru': "❌ Отмена",
        'en': "❌ Cancel"
    },
    
    'btn_confirm': {
        'uz': "✅ Tasdiqlash",
        'ru': "✅ Подтвердить",
        'en': "✅ Confirm"
    },
    
    'btn_create_team': {
        'uz': "➕ Yangi jamoa yaratish",
        'ru': "➕ Создать новую команду",
        'en': "➕ Create new team"
    },
    
    'btn_join_team': {
        'uz': "🔗 Jamoaga qo'shilish",
        'ru': "🔗 Присоединиться к команде",
        'en': "🔗 Join team"
    },
    
    'btn_submit': {
        'uz': "📤 Topshirish",
        'ru': "📤 Отправить",
        'en': "📤 Submit"
    },
    
    'btn_view_submission': {
        'uz': "👁 Topshiriqni ko'rish",
        'ru': "👁 Посмотреть отправку",
        'en': "👁 View submission"
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
        'uz': """JSHSHIR raqamingizni kiriting - 14 raqam.

JSHSHIR nima uchun kerak:
• Yoshingizni tekshirish
• Final tadbirida ishtirokingizni tashkil qilish (mehmonxona band qilish, chipta sotib olish)""",
        'ru': """Введите ваш ПИНФЛ - 14 цифр.

Зачем нужен ПИНФЛ:
• Для проверки возраста
• Для организации участия в финальном мероприятии (бронирование отеля, покупка билетов)""",
        'en': """Please enter your Personal Identification Number (PINFL) - 14 digits.

Why we require your PINFL:
• To verify your age
• To organize your participation in the final event if needed (booking accommodation and purchasing tickets)"""
    },
    
    'registration_almost_done': {
        'uz': """Deyarli tayyor! ⏳

Ishtirokingizni tasdiqlash uchun hackathonni tanlang:
Menu → 🚀 Hackathonlar → Hackathonni tanlang → Ro'yxatdan o'tish ✅

⚠️ Hackathon tanlamasdan ro'yxatdan o'tish yaroqsiz""",
        'ru': """Почти готово! ⏳

Для подтверждения участия выберите хакатон:
Меню → 🚀 Хакатоны → Выберите хакатон → Зарегистрироваться ✅

⚠️ Регистрация без выбора хакатона недействительна""",
        'en': """You're almost done! ⏳

To confirm your participation, please choose your hackathon:
Menu → 🚀 Hackathons → Select hackathon → Register ✅

⚠️ Registration without selecting a hackathon is not valid"""
    },
    
    'registration_complete': {
        'uz': "✅ Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!",
        'ru': "✅ Регистрация успешно завершена!",
        'en': "✅ Registration completed successfully!"
    },
    
    # ==========================================================================
    # HACKATHON & TEAM
    # ==========================================================================
    'no_hackathons': {
        'uz': "❌ Hozirda faol hackathonlar mavjud emas",
        'ru': "❌ Нет доступных хакатонов",
        'en': "❌ No hackathons available"
    },
    
    'hackathon_list_title': {
        'uz': "🚀 Mavjud hackathonlar:",
        'ru': "🚀 Доступные хакатоны:",
        'en': "🚀 Available hackathons:"
    },
    
    'hackathon_info': {
        'uz': """🏆 {name}

📝 {description}

💰 Sovrin jamg'armasi: {prize_pool}
📅 Boshlanish: {start_date}
📅 Tugash: {end_date}
⏰ Ro'yxatdan o'tish muddati: {registration_deadline}""",
        'ru': """🏆 {name}

📝 {description}

💰 Призовой фонд: {prize_pool}
📅 Начало: {start_date}
📅 Окончание: {end_date}
⏰ Срок регистрации: {registration_deadline}""",
        'en': """🏆 {name}

📝 {description}

💰 Prize pool: {prize_pool}
📅 Start: {start_date}
📅 End: {end_date}
⏰ Registration deadline: {registration_deadline}"""
    },
    
    'your_hackathons': {
        'uz': "📁 Sizning hackathonlaringiz:",
        'ru': "📁 Ваши хакатоны:",
        'en': "📁 Your hackathons:"
    },
    
    'no_registered_hackathons': {
        'uz': "📭 Siz hali hech qanday hackathonga ro'yxatdan o'tmagansiz.",
        'ru': "📭 Вы еще не зарегистрированы ни на один хакатон.",
        'en': "📭 You haven't registered for any hackathons yet."
    },
    
    'already_registered': {
        'uz': "⚠️ Siz allaqachon ushbu hackathonga ro'yxatdan o'tgansiz.",
        'ru': "⚠️ Вы уже зарегистрированы на этот хакатон.",
        'en': "⚠️ You are already registered for this hackathon."
    },
    
    'registration_option': {
        'uz': """🚀 {hackathon} hackathoniga ro'yxatdan o'tish

Qanday ishtirok etmoqchisiz?""",
        'ru': """🚀 Регистрация на хакатон {hackathon}

Как вы хотите участвовать?""",
        'en': """🚀 Registration for {hackathon} hackathon

How would you like to participate?"""
    },
    
    'enter_team_code': {
        'uz': "🔑 Jamoaga qo'shilish uchun jamoa kodini kiriting:",
        'ru': "🔑 Введите код команды для присоединения:",
        'en': "🔑 Enter the team code to join:"
    },
    
    'invalid_team_code': {
        'uz': "❌ Noto'g'ri jamoa kodi. Tekshirib, qaytadan urinib ko'ring.",
        'ru': "❌ Неверный код команды. Проверьте и попробуйте снова.",
        'en': "❌ Invalid team code. Please check and try again."
    },
    
    'team_full': {
        'uz': "❌ Bu jamoa to'lgan (maksimal 5 a'zo).",
        'ru': "❌ Команда заполнена (максимум 5 участников).",
        'en': "❌ This team is full (maximum 5 members)."
    },
    
    'joined_team': {
        'uz': "✅ Siz '{name}' jamoasiga muvaffaqiyatli qo'shildingiz!",
        'ru': "✅ Вы успешно присоединились к команде «{name}»!",
        'en': "✅ You've successfully joined team '{name}'!"
    },
    
    'enter_team_name': {
        'uz': "📝 Jamoa nomini kiriting:",
        'ru': "📝 Введите название команды:",
        'en': "📝 Enter team name:"
    },
    
    'enter_team_role': {
        'uz': """👤 O'zingizning rolingizni kiriting:
(masalan: Backend Developer / Project Manager / Designer)""",
        'ru': """👤 Введите вашу роль:
(например: Backend Developer / Project Manager / Designer)""",
        'en': """👤 Enter your role:
(e.g. Backend Developer / Project Manager / Designer)"""
    },
    
    'enter_field': {
        'uz': """🎯 Loyihangiz yo'nalishini tanlang:

1. Smart Banking - Aqlli bank xizmatlari
2. Cybersecurity - Kiberxavfsizlik yechimlari
3. Fintech Services - Moliyaviy texnologiyalar
4. Blockchain - Blokcheyn texnologiyalari

Yo'nalish nomini kiriting:""",
        'ru': """🎯 Выберите направление вашего проекта:

1. Smart Banking - Умные банковские услуги
2. Cybersecurity - Решения кибербезопасности
3. Fintech Services - Финансовые технологии
4. Blockchain - Блокчейн технологии

Введите название направления:""",
        'en': """🎯 Choose your project direction:

1. Smart Banking - Smart banking services
2. Cybersecurity - Cybersecurity solutions
3. Fintech Services - Financial technologies
4. Blockchain - Blockchain technologies

Enter the direction name:"""
    },
    
    'enter_portfolio': {
        'uz': "🔗 Portfolio yoki GitHub havolangizni kiriting (ixtiyoriy):",
        'ru': "🔗 Введите ссылку на портфолио или GitHub (необязательно):",
        'en': "🔗 Enter your portfolio or GitHub link (optional):"
    },
    
    'team_created': {
        'uz': """✅ Jamoa yaratildi!

📌 Nomi: {name}
🔑 Kod: {code}

Bu kodni jamoadoshlaringiz bilan ulashing, ular ham qo'shilishi uchun.

ℹ️ Tez orada hackathonning keyingi bosqichlari haqida yangiliklar olasiz.
⚠️ Botni bloklamang!""",
        'ru': """✅ Команда создана!

📌 Название: {name}
🔑 Код: {code}

Поделитесь этим кодом с товарищами по команде, чтобы они могли присоединиться.

ℹ️ Скоро вы получите обновления о следующих этапах хакатона.
⚠️ Не блокируйте бота!""",
        'en': """✅ Team created!

📌 Name: {name}
🔑 Code: {code}

Share this code with your teammates so they can join the team.

ℹ️ Soon you will receive updates about the next stages of this hackathon.
⚠️ Please do not block the bot!"""
    },
    
    'team_info': {
        'uz': """📋 Jamoa ma'lumotlari

🏆 Hackathon: {hackathon}
📌 Nomi: {name}
🔑 Kod: {code}

👥 A'zolar:
{members}

ℹ️ Qo'shimcha ma'lumot uchun quyidagi tugmalardan foydalaning 👇""",
        'ru': """📋 Информация о команде

🏆 Хакатон: {hackathon}
📌 Название: {name}
🔑 Код: {code}

👥 Участники:
{members}

ℹ️ Для дополнительной информации используйте кнопки ниже 👇""",
        'en': """📋 Team information

🏆 Hackathon: {hackathon}
📌 Name: {name}
🔑 Code: {code}

👥 Members:
{members}

ℹ️ To see more about this hackathon, use the button below 👇"""
    },
    
    'confirm_leave_team': {
        'uz': "⚠️ Jamoani tark etishni xohlaysizmi?\n\nAgar siz jamoa rahbari bo'lsangiz, jamoa o'chiriladi.",
        'ru': "⚠️ Вы уверены, что хотите покинуть команду?\n\nЕсли вы лидер команды, команда будет удалена.",
        'en': "⚠️ Are you sure you want to leave the team?\n\nIf you're the team lead, the team will be deleted."
    },
    
    'left_team': {
        'uz': "👋 Siz jamoani tark etdingiz.",
        'ru': "👋 Вы покинули команду.",
        'en': "👋 You've left the team."
    },
    
    'team_deleted': {
        'uz': "🗑 Jamoa o'chirildi (rahbar jamoani tark etdi).",
        'ru': "🗑 Команда удалена (лидер покинул команду).",
        'en': "🗑 Team deleted (leader left the team)."
    },
    
    'select_member_to_remove': {
        'uz': "👥 O'chirish uchun a'zoni tanlang:",
        'ru': "👥 Выберите участника для удаления:",
        'en': "👥 Select a member to remove:"
    },
    
    'member_removed': {
        'uz': "✅ A'zo jamoadan o'chirildi.",
        'ru': "✅ Участник удален из команды.",
        'en': "✅ Member removed from the team."
    },
    
    # ==========================================================================
    # STAGES & SUBMISSIONS
    # ==========================================================================
    'stage_info': {
        'uz': """📋 {hackathon} - {stage}

📅 Boshlanish: {start}
⏰ Deadline: {deadline}

📝 Vazifa:
{task}""",
        'ru': """📋 {hackathon} - {stage}

📅 Начало: {start}
⏰ Дедлайн: {deadline}

📝 Задание:
{task}""",
        'en': """📋 {hackathon} - {stage}

📅 Start: {start}
⏰ Deadline: {deadline}

📝 Task:
{task}"""
    },
    
    'submit_prompt': {
        'uz': """📤 Topshiriqni yuborish

Quyidagilarni yuborishingiz mumkin:
• Demo website havolasi (URL)
• Fayl (PDF, DOCX, PPTX, rasm, video, audio)

Havolani kiriting yoki faylni yuboring:""",
        'ru': """📤 Отправка задания

Вы можете отправить:
• Ссылка на демо-сайт (URL)
• Файл (PDF, DOCX, PPTX, изображение, видео, аудио)

Введите ссылку или отправьте файл:""",
        'en': """📤 Submit your work

You can submit:
• Demo website link (URL)
• File (PDF, DOCX, PPTX, image, video, audio)

Enter a link or send a file:"""
    },
    
    'submission_received': {
        'uz': """✅ Topshiriqingiz qabul qilindi!

📎 Yuborilgan: {content}
📅 Vaqti: {time}

Omad tilaymiz! 🍀""",
        'ru': """✅ Ваша работа принята!

📎 Отправлено: {content}
📅 Время: {time}

Удачи! 🍀""",
        'en': """✅ Your submission received!

📎 Submitted: {content}
📅 Time: {time}

Good luck! 🍀"""
    },
    
    'submission_updated': {
        'uz': "✅ Topshiriqingiz yangilandi!",
        'ru': "✅ Ваша работа обновлена!",
        'en': "✅ Your submission updated!"
    },
    
    'deadline_passed': {
        'uz': "⏰ Afsuski, ushbu bosqichning muddati tugagan :(",
        'ru': "⏰ К сожалению, срок подачи для этого этапа истек :(",
        'en': "⏰ Unfortunately, the deadline for this stage has passed :("
    },
    
    'no_active_stage': {
        'uz': "ℹ️ Hozirda faol bosqich yo'q.",
        'ru': "ℹ️ В данный момент нет активного этапа.",
        'en': "ℹ️ There's no active stage at the moment."
    },
    
    'current_submission': {
        'uz': """📎 Joriy topshiriq:
{content}

📅 Yuborilgan: {time}""",
        'ru': """📎 Текущая работа:
{content}

📅 Отправлено: {time}""",
        'en': """📎 Current submission:
{content}

📅 Submitted: {time}"""
    },
    
    # ==========================================================================
    # SETTINGS
    # ==========================================================================
    'settings_menu': {
        'uz': "⚙️ Sozlamalar",
        'ru': "⚙️ Настройки",
        'en': "⚙️ Settings"
    },
    
    'your_data': {
        'uz': """👤 Sizning ma'lumotlaringiz:

• Ism: {first_name}
• Familiya: {last_name}
• Tug'ilgan sana: {birth_date}
• Jins: {gender}
• Joylashuv: {location}""",
        'ru': """👤 Ваши данные:

• Имя: {first_name}
• Фамилия: {last_name}
• Дата рождения: {birth_date}
• Пол: {gender}
• Местоположение: {location}""",
        'en': """👤 Your data:

• First name: {first_name}
• Last name: {last_name}
• Birth date: {birth_date}
• Gender: {gender}
• Location: {location}"""
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
    
    'language_changed': {
        'uz': "✅ Til o'zgartirildi: O'zbekcha",
        'ru': "✅ Язык изменен: Русский",
        'en': "✅ Language changed: English"
    },
    
    # ==========================================================================
    # HELP
    # ==========================================================================
    'help_message': {
        'uz': f"""💡 Yordam kerakmi yoki xato topdingizmi?

Agar savollaringiz bo'lsa, botdan foydalanishda yordam kerak bo'lsa yoki takomillashtirish bo'yicha takliflaringiz bo'lsa, biz bilan bog'laning:
📧 {SUPPORT_EMAIL}

Muammoni batafsil tasvirlab bering va iloji bo'lsa skrinshot qo'shing.
Tez orada javob beramiz ✅""",
        'ru': f"""💡 Нужна помощь или нашли ошибку?

Если у вас есть вопросы, нужна помощь в использовании бота или есть предложения по улучшению, свяжитесь с нами:
📧 {SUPPORT_EMAIL}

Опишите проблему подробно и приложите скриншоты, если возможно.
Мы скоро вернемся к вам ✅""",
        'en': f"""💡 Need help or found a bug?

If you have questions, need assistance using the bot or have suggestions for improvement, please contact us at:
📧 {SUPPORT_EMAIL}

Describe the problem in detail and attach screenshots if possible.
We will get back to you soon ✅"""
    },
    
    # ==========================================================================
    # ADMIN
    # ==========================================================================
    'admin_only': {
        'uz': "⛔ Bu buyruq faqat adminlar uchun",
        'ru': "⛔ Эта команда только для админов",
        'en': "⛔ This command is for admins only"
    },
    
    'admin_menu': {
        'uz': """🔐 Admin Panel

Mavjud buyruqlar:
/stats - Statistika
/broadcast - Xabar yuborish
/create_hackathon - Hackathon yaratish
/create_stage - Bosqich yaratish
/activate_stage - Bosqichni faollashtirish
/notify_hackathon - Eslatma yuborish
/export_users - Foydalanuvchilar CSV
/export_teams - Jamoalar CSV
/export_submissions - Topshiriqlar CSV
/addadmin <telegram_id> - Admin qo'shish
/removeadmin <telegram_id> - Adminni o'chirish""",
        'ru': """🔐 Панель администратора

Доступные команды:
/stats - Статистика
/broadcast - Рассылка
/create_hackathon - Создать хакатон
/create_stage - Создать этап
/activate_stage - Активировать этап
/notify_hackathon - Отправить напоминание
/export_users - CSV пользователей
/export_teams - CSV команд
/export_submissions - CSV работ
/addadmin <telegram_id> - Добавить админа
/removeadmin <telegram_id> - Удалить админа""",
        'en': """🔐 Admin Panel

Available commands:
/stats - Statistics
/broadcast - Broadcast message
/create_hackathon - Create hackathon
/create_stage - Create stage
/activate_stage - Activate stage
/notify_hackathon - Send reminder
/export_users - Users CSV
/export_teams - Teams CSV
/export_submissions - Submissions CSV
/addadmin <telegram_id> - Add admin
/removeadmin <telegram_id> - Remove admin"""
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
    
    'stats_message': {
        'uz': """📊 Statistika

👥 Jami foydalanuvchilar: {total_users}
✅ Rozilik berganlar: {consented_users}
👥 Jamoalar: {total_teams}
🚀 Faol hackathonlar: {active_hackathons}
📤 Topshiriqlar: {total_submissions}""",
        'ru': """📊 Статистика

👥 Всего пользователей: {total_users}
✅ Дали согласие: {consented_users}
👥 Команды: {total_teams}
🚀 Активные хакатоны: {active_hackathons}
📤 Работы: {total_submissions}""",
        'en': """📊 Statistics

👥 Total users: {total_users}
✅ Consented: {consented_users}
👥 Teams: {total_teams}
🚀 Active hackathons: {active_hackathons}
📤 Submissions: {total_submissions}"""
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
    
    'please_start': {
        'uz': "Iltimos, avval /start buyrug'ini yuboring",
        'ru': "Пожалуйста, сначала отправьте команду /start",
        'en': "Please start the bot first with /start"
    },
    
    # ==========================================================================
    # NOTIFICATIONS
    # ==========================================================================
    'days_left': {
        'uz': """⏳ Birinchi vazifagacha {days} kun qoldi!

Birinchi vazifangiz tez orada keladi, shuning uchun hozir loyiha g'oyangizni aniqlash uchun yaxshi vaqt.

Agar aniq yo'nalishingiz bo'lmasa, quyidagi yo'nalishlardan birini tanlang:
• Smart Banking
• Cybersecurity
• Fintech Services
• Blockchain

🏆 {hackathon}da eng kuchli loyiha g'olib bo'ladi — yo'nalishdan qat'i nazar.

Savollar bormi? {email} ga murojaat qiling 📧""",
        'ru': """⏳ До первого задания осталось {days} дней!

Ваше первое задание скоро появится, так что сейчас самое время определиться с идеей проекта.

Если у вас еще нет четкого направления, выберите одно из:
• Smart Banking
• Cybersecurity
• Fintech Services
• Blockchain

🏆 В {hackathon} побеждает сильнейший проект — независимо от направления.

Вопросы? Обращайтесь на {email} 📧""",
        'en': """⏳ {days} days left until the first task!

Your first task is coming up soon, so now is a good time to settle on your project idea.

If you don't yet have a clear direction, choose one of:
• Smart Banking
• Cybersecurity
• Fintech Services
• Blockchain

🏆 At {hackathon}, the strongest project wins — regardless of the track.

Questions? Contact support at {email} 📧"""
    },
    
    'stage_deadline_approaching': {
        'uz': """⏳ {stage} muddati yaqinlashmoqda!

Bugun 23:59 gacha — {stage} javoblaringizni topshirish uchun oxirgi imkoniyat.

{hackathon} Saralash jamoasi topshiriqlarni {review_dates} kunlari ko'rib chiqadi.

{next_stage_date} — keyingi bosqichga o'tuvchi jamoalar e'lon qilinadi! ✨""",
        'ru': """⏳ Срок {stage} приближается!

Сегодня до 23:59 — последний шанс отправить ваши ответы {stage}.

Команда отбора {hackathon} рассмотрит работы {review_dates}.

{next_stage_date} — будут объявлены команды, прошедшие в следующий этап! ✨""",
        'en': """⏳ {stage} deadline approaching!

Today until 23:59 — the final chance to submit your {stage} answers.

The {hackathon} Selection Team will review submissions on {review_dates}.

{next_stage_date} — teams advancing to the next stage will be announced! ✨"""
    },
    
    'stage_deadline_passed': {
        'uz': "🚫 {stage} muddati tugadi :(",
        'ru': "🚫 Срок {stage} истек :(",
        'en': "🚫 {stage} deadline has already passed :("
    },
    
    'congratulations_stage': {
        'uz': """🎉 Tabriklaymiz, {stage} bosqichiga o'tdingiz!

📋 Vazifa: {task}

⏰ Muddat: {deadline} (GMT +5)
❗ Topshirish: Bot orqali "📤 Topshirish" tugmasini bosing

💡 Maslahat: Kontentingiz aniq va to'liq bo'lsin, hech qaysi bo'limni o'tkazib yubormang.""",
        'ru': """🎉 Поздравляем, вы прошли в {stage}!

📋 Задание: {task}

⏰ Срок: {deadline} (GMT +5)
❗ Отправка: Нажмите кнопку "📤 Отправить" в боте

💡 Совет: Убедитесь, что ваш контент четкий и полный, не пропустите ни одного раздела.""",
        'en': """🎉 Congratulations on making it to {stage}!

📋 Task: {task}

⏰ Deadline: {deadline} (GMT +5)
❗ Submission: Click the "📤 Submit" button in this bot

💡 Tip: Make your content clear and complete, don't miss any section."""
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
