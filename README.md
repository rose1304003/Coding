# 🏆 ITCom Hackathons Bot

A production-ready Telegram bot for managing hackathons, built with Python and PostgreSQL.

## 📋 Features

### For Users
- 🌐 **Multi-language support** (Uzbek, Russian, English)
- 📝 **Easy registration** with step-by-step flow
- 👥 **Team management** (create, join, leave teams)
- 📤 **Task submissions** for each hackathon stage
- 📊 **Progress tracking** and results viewing
- 📢 **Push notifications** for deadlines and announcements

### For Admins
- 📊 **Statistics dashboard**
- 📢 **Broadcast messages** to all users
- 📥 **CSV exports** (users, teams, submissions)
- 🏆 **Hackathon management** (create, edit, manage stages)
- 👤 **Admin management** (add/remove admins)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     TELEGRAM USER                           │
│                    (Mobile/Desktop)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   TELEGRAM API                              │
│              (api.telegram.org)                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   BOT APPLICATION                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    bot.py                             │  │
│  │            (Main entry point)                         │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      │                                      │
│  ┌───────────────────┼───────────────────────────────────┐  │
│  │                   │                                   │  │
│  │   ┌───────────────▼───────────────┐                   │  │
│  │   │      handlers/                │                   │  │
│  │   │  • main_handlers.py          │                   │  │
│  │   │  • admin_handlers.py         │                   │  │
│  │   └───────────────┬───────────────┘                   │  │
│  │                   │                                   │  │
│  │   ┌───────────────▼───────────────┐                   │  │
│  │   │        utils/                 │                   │  │
│  │   │  • keyboards.py              │                   │  │
│  │   │  • helpers.py                │                   │  │
│  │   └───────────────────────────────┘                   │  │
│  │                                                       │  │
│  │   ┌───────────────────────────────┐                   │  │
│  │   │       locales/                │                   │  │
│  │   │  • translations.py           │                   │  │
│  │   └───────────────────────────────┘                   │  │
│  │                                                       │  │
│  │   ┌───────────────────────────────┐                   │  │
│  │   │       exports/                │                   │  │
│  │   │  • csv_export.py             │                   │  │
│  │   └───────────────────────────────┘                   │  │
│  │                                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                      │                                      │
│  ┌───────────────────▼───────────────────────────────────┐  │
│  │               database.py                             │  │
│  │         (PostgreSQL operations)                       │  │
│  └───────────────────┬───────────────────────────────────┘  │
└──────────────────────┼──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 RAILWAY POSTGRESQL                          │
│                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   users     │ │   teams     │ │ hackathons  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │team_members │ │ submissions │ │   stages    │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐                           │
│  │notifications│ │  audit_log  │                           │
│  └─────────────┘ └─────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
hackathon_bot/
├── bot.py                 # Main entry point
├── database.py            # PostgreSQL operations (asyncpg)
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── railway.json          # Railway deployment config
├── .env.example          # Environment variables template
│
├── handlers/             # Telegram handlers
│   ├── __init__.py
│   ├── main_handlers.py  # User commands & callbacks
│   └── admin_handlers.py # Admin commands & exports
│
├── utils/                # Utility modules
│   ├── __init__.py
│   ├── keyboards.py      # Inline & reply keyboards
│   └── helpers.py        # Validation & formatting
│
├── locales/              # Internationalization
│   ├── __init__.py
│   └── translations.py   # UZ/RU/EN translations
│
└── exports/              # Export functionality
    ├── __init__.py
    └── csv_export.py     # CSV export functions
```

## 🗄️ Database Schema

```sql
-- Core tables
users              -- Telegram users with profile data
hackathons         -- Hackathon events
hackathon_stages   -- Stages within hackathons
teams              -- Teams registered for hackathons
team_members       -- Many-to-many: users in teams
submissions        -- Team submissions for stages
notifications      -- Broadcast notification log
registration_states -- Conversation state management
audit_log          -- Action logging for security
```

## 🚀 Deployment to Railway

### 1. Prerequisites
- Railway account (https://railway.app)
- Telegram Bot Token (from @BotFather)

### 2. Setup Steps

```bash
# 1. Create new project on Railway
# 2. Add PostgreSQL database from Railway dashboard
# 3. Connect your GitHub repo or deploy from Railway CLI

# Railway will automatically:
# - Detect the Dockerfile
# - Set DATABASE_URL environment variable
# - Build and deploy the container
```

### 3. Environment Variables (set in Railway dashboard)
```
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://... (auto-set by Railway)
LOG_LEVEL=INFO
```

### 4. Make yourself admin
```bash
# After first /start, run this SQL in Railway's database GUI:
UPDATE users SET is_admin = TRUE WHERE telegram_id = YOUR_TELEGRAM_ID;
```

## 💻 Local Development

### 1. Clone and Setup
```bash
git clone <your-repo>
cd hackathon_bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Local PostgreSQL
```bash
# Option 1: Docker
docker run -d \
  --name hackathon_postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=hackathon_bot \
  -p 5432:5432 \
  postgres:15

# Option 2: Install PostgreSQL locally
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your values:
# BOT_TOKEN=your_bot_token
# DATABASE_URL=postgresql://postgres:password@localhost:5432/hackathon_bot
```

### 4. Run the Bot
```bash
python bot.py
```

## 📱 Bot Commands

### User Commands
| Command | Description |
|---------|-------------|
| `/start` | Start the bot / Register |
| `/help` | Get help information |
| `/settings` | Open settings menu |
| `/exit` | Deactivate account |

### Admin Commands
| Command | Description |
|---------|-------------|
| `/admin` | Open admin panel |
| `/stats` | View statistics |
| `/broadcast <msg>` | Send to all users |
| `/export_users` | Export users CSV |
| `/export_teams` | Export teams CSV |
| `/export_members` | Export members CSV |
| `/export_submissions` | Export submissions CSV |
| `/addadmin <id>` | Add admin |
| `/removeadmin <id>` | Remove admin |
| `/create_hackathon <name>` | Create hackathon |
| `/create_stage <h_id> <num> <name>` | Create stage |
| `/activate_stage <stage_id>` | Activate stage |
| `/notify_hackathon <h_id> <msg>` | Notify participants |

## 🔒 Security Features

- ✅ No hardcoded credentials
- ✅ Environment variables for secrets
- ✅ Admin-only command protection
- ✅ Audit logging for sensitive actions
- ✅ SQL injection protection (parameterized queries)
- ✅ Input validation
- ✅ Non-root Docker user

## 📈 Scalability Considerations

### Current Limits
- Single bot instance (Railway free tier)
- Connection pool: 2-10 connections
- Suitable for: ~10,000 users

### Future Improvements
- Add Redis for session caching
- Implement webhook instead of polling
- Add Supabase for real-time features
- Horizontal scaling with multiple instances

## 🛠️ Troubleshooting

### Bot not responding
1. Check `BOT_TOKEN` is correct
2. Check Railway logs for errors
3. Verify database connection

### Database errors
1. Ensure `DATABASE_URL` is set
2. Check PostgreSQL is running
3. Verify network connectivity

### Messages not sending
1. Check bot has necessary permissions
2. Verify user hasn't blocked the bot
3. Check rate limiting

## 📞 Support

For questions or issues:
- 📧 Email: ai500@itcommunity.uz
- 💬 Telegram: @itcommunity_uz

## 📄 License

MIT License - feel free to use and modify!

---

Built with ❤️ for ITCommunity Uzbekistan
