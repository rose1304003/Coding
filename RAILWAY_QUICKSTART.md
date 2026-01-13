# 🚀 Quick Start: Railway PostgreSQL Deployment

## Step 1: Get Your Bot Token

1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Follow prompts to name your bot
4. Copy the **API token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

---

## Step 2: Railway Setup

### 2.1 Create Project
1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Choose **"Deploy from GitHub repo"** or **"Empty Project"**

### 2.2 Add PostgreSQL Database
1. In your project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway auto-creates the database and sets `DATABASE_URL`

### 2.3 Add Your Bot Service
**Option A: From GitHub**
1. Click **"+ New"** → **"GitHub Repo"**
2. Select your repo with the bot code
3. Railway auto-detects the Dockerfile

**Option B: Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy
railway up
```

---

## Step 3: Set Environment Variables

In Railway dashboard → Your bot service → **Variables** tab:

```
BOT_TOKEN = your_telegram_bot_token_here
```

**Note:** `DATABASE_URL` is automatically set by Railway when you link PostgreSQL!

---

## Step 4: Verify Database Connection

Railway PostgreSQL provides a connection string like:
```
postgresql://postgres:password@containers-us-west-XXX.railway.app:5432/railway
```

The bot automatically:
- ✅ Reads `DATABASE_URL` from environment
- ✅ Creates all tables on first startup
- ✅ Handles connection pooling

---

## Step 5: Make Yourself Admin

### Option A: Railway Database GUI
1. Click on your PostgreSQL service
2. Go to **"Data"** tab
3. Run this SQL:
```sql
UPDATE users SET is_admin = TRUE WHERE telegram_id = YOUR_TELEGRAM_ID;
```

### Option B: Via psql (Railway CLI)
```bash
railway connect postgres

# Then run:
UPDATE users SET is_admin = TRUE WHERE telegram_id = YOUR_TELEGRAM_ID;
```

**How to find your Telegram ID:**
- Message @userinfobot on Telegram
- Or check bot logs after you /start

---

## Step 6: Test Your Bot

1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Complete registration flow
5. Test admin commands: `/admin`, `/stats`

---

## 🔍 Troubleshooting

### Bot not starting?
Check Railway logs:
1. Click on your bot service
2. Go to **"Deployments"** tab
3. Click latest deployment → **"View Logs"**

### Database connection error?
```
DATABASE_URL environment variable is not set!
```
**Fix:** Make sure PostgreSQL is in the same Railway project and linked.

### "No hackathons available"?
Create one as admin:
```
/create_hackathon AI500! Hackathon
```

---

## 📊 Railway PostgreSQL - How It Works

```
┌─────────────────────────────────────────────────┐
│              RAILWAY PROJECT                     │
│                                                  │
│  ┌──────────────┐      ┌──────────────────┐     │
│  │   Bot        │      │   PostgreSQL     │     │
│  │   Service    │◄────►│   Database       │     │
│  │              │      │                  │     │
│  │ BOT_TOKEN=..│      │ Auto-managed     │     │
│  │              │      │ Backups included │     │
│  └──────────────┘      └──────────────────┘     │
│         │                      │                │
│         │    DATABASE_URL      │                │
│         └──────────────────────┘                │
│           (auto-injected)                       │
└─────────────────────────────────────────────────┘
```

**Railway automatically:**
- Manages PostgreSQL server
- Provides secure connection string
- Handles backups
- Scales as needed

---

## 🎯 After Deployment Checklist

- [ ] Bot responds to `/start`
- [ ] Language selection works
- [ ] Registration flow completes
- [ ] Made yourself admin
- [ ] `/admin` shows admin panel
- [ ] `/stats` shows statistics
- [ ] Created first hackathon
- [ ] Test team creation

---

## 📞 Need Help?

- Railway Docs: https://docs.railway.app
- Bot Issues: Check deployment logs
- Database Issues: Railway's Data tab has SQL editor

Good luck! 🚀
