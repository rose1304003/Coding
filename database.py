"""
Database module for CBU Coding Hackathon Telegram Bot
Production-ready PostgreSQL implementation
"""

import os
import json
import random
import string
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import asyncpg
from asyncpg import Pool

DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_IDS = os.getenv("ADMIN_IDS", "")  # Comma-separated list of admin Telegram IDs
_pool: Optional[Pool] = None


def get_env_admin_ids() -> set:
    """Get admin IDs from environment variable."""
    if not ADMIN_IDS:
        return set()
    try:
        return {int(id.strip()) for id in ADMIN_IDS.split(",") if id.strip()}
    except ValueError:
        return set()


async def get_pool() -> Pool:
    global _pool
    if _pool is None:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set")
        db_url = DATABASE_URL
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        _pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10, command_timeout=60, statement_cache_size=0)
    return _pool


@asynccontextmanager
async def get_connection():
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def create_tables():
    async with get_connection() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(255),
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255),
                phone VARCHAR(50),
                birth_date DATE,
                gender VARCHAR(20),
                location VARCHAR(255),
                pinfl VARCHAR(20),
                language VARCHAR(10) DEFAULT 'uz',
                consent_given BOOLEAN DEFAULT FALSE,
                consent_given_at TIMESTAMP WITH TIME ZONE,
                consent_version VARCHAR(20) DEFAULT '1.0',
                is_active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE,
                registration_complete BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
            CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin) WHERE is_admin = TRUE;
            
            CREATE TABLE IF NOT EXISTS hackathons (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                prize_pool VARCHAR(100),
                start_date DATE,
                end_date DATE,
                registration_deadline TIMESTAMP WITH TIME ZONE,
                banner_file_id TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_hackathons_active ON hackathons(is_active);
            
            CREATE TABLE IF NOT EXISTS hackathon_stages (
                id SERIAL PRIMARY KEY,
                hackathon_id INTEGER REFERENCES hackathons(id) ON DELETE CASCADE,
                stage_number INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                task_description TEXT,
                task_file_id TEXT,
                start_date TIMESTAMP WITH TIME ZONE,
                deadline TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_stages_hackathon ON hackathon_stages(hackathon_id);
            
            CREATE TABLE IF NOT EXISTS teams (
                id SERIAL PRIMARY KEY,
                hackathon_id INTEGER REFERENCES hackathons(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                code VARCHAR(10) UNIQUE NOT NULL,
                owner_id BIGINT NOT NULL,
                field VARCHAR(255),
                portfolio_link TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_teams_hackathon ON teams(hackathon_id);
            CREATE INDEX IF NOT EXISTS idx_teams_code ON teams(code);
            
            CREATE TABLE IF NOT EXISTS team_members (
                id SERIAL PRIMARY KEY,
                team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
                user_id BIGINT NOT NULL,
                role VARCHAR(255) DEFAULT 'Member',
                is_team_lead BOOLEAN DEFAULT FALSE,
                joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_team_members_team ON team_members(team_id);
            CREATE INDEX IF NOT EXISTS idx_team_members_user ON team_members(user_id);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_team_members_unique ON team_members(team_id, user_id);
            
            CREATE TABLE IF NOT EXISTS submissions (
                id SERIAL PRIMARY KEY,
                team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
                stage_id INTEGER REFERENCES hackathon_stages(id) ON DELETE CASCADE,
                submission_type VARCHAR(50) NOT NULL DEFAULT 'link',
                content TEXT,
                file_id TEXT,
                file_name VARCHAR(255),
                file_type VARCHAR(50),
                submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                submitted_by BIGINT,
                score DECIMAL(5,2),
                feedback TEXT,
                reviewed_at TIMESTAMP WITH TIME ZONE,
                reviewed_by BIGINT
            );
            CREATE INDEX IF NOT EXISTS idx_submissions_team ON submissions(team_id);
            CREATE INDEX IF NOT EXISTS idx_submissions_stage ON submissions(stage_id);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_submissions_unique ON submissions(team_id, stage_id);
            
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                hackathon_id INTEGER REFERENCES hackathons(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                sent_by BIGINT,
                recipient_count INTEGER DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS registration_states (
                telegram_id BIGINT PRIMARY KEY,
                current_step VARCHAR(50) NOT NULL,
                data JSONB DEFAULT '{}',
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT,
                action VARCHAR(100) NOT NULL,
                details JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_audit_telegram ON audit_log(telegram_id);
        """)
        print("✅ Database tables created!")


# USER OPERATIONS
async def add_user(telegram_id: int, first_name: str, username: str = None, last_name: str = None) -> Dict[str, Any]:
    async with get_connection() as conn:
        user = await conn.fetchrow("""
            INSERT INTO users (telegram_id, username, first_name, last_name)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (telegram_id) DO UPDATE SET
                username = EXCLUDED.username, first_name = COALESCE(EXCLUDED.first_name, users.first_name),
                last_name = COALESCE(EXCLUDED.last_name, users.last_name), updated_at = NOW()
            RETURNING *
        """, telegram_id, username, first_name, last_name)
        return dict(user)


async def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
        return dict(user) if user else None


async def update_user(telegram_id: int, **kwargs) -> bool:
    if not kwargs:
        return False
    set_clauses = [f"{k} = ${i}" for i, k in enumerate(kwargs.keys(), 1)]
    values = list(kwargs.values()) + [telegram_id]
    query = f"UPDATE users SET {', '.join(set_clauses)}, updated_at = NOW() WHERE telegram_id = ${len(values)}"
    async with get_connection() as conn:
        result = await conn.execute(query, *values)
        return result == "UPDATE 1"


async def set_user_consent(telegram_id: int, consented: bool, version: str = "1.0") -> bool:
    async with get_connection() as conn:
        if consented:
            result = await conn.execute("""
                UPDATE users SET consent_given = TRUE, consent_given_at = NOW(), consent_version = $2, updated_at = NOW()
                WHERE telegram_id = $1
            """, telegram_id, version)
        else:
            result = await conn.execute("""
                UPDATE users SET consent_given = FALSE, consent_given_at = NULL, is_active = FALSE, updated_at = NOW()
                WHERE telegram_id = $1
            """, telegram_id)
        await log_action(telegram_id, 'consent_decision', {'consented': consented, 'version': version})
        return result == "UPDATE 1"


async def has_user_consented(telegram_id: int) -> bool:
    async with get_connection() as conn:
        result = await conn.fetchval("SELECT consent_given FROM users WHERE telegram_id = $1", telegram_id)
        return result is True


async def get_all_active_users() -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        users = await conn.fetch("SELECT * FROM users WHERE is_active = TRUE ORDER BY created_at")
        return [dict(u) for u in users]


async def get_all_consented_users() -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        users = await conn.fetch("SELECT * FROM users WHERE is_active = TRUE AND consent_given = TRUE")
        return [dict(u) for u in users]


async def is_admin(telegram_id: int) -> bool:
    # First check environment variable (for initial setup)
    if telegram_id in get_env_admin_ids():
        return True
    # Then check database
    async with get_connection() as conn:
        result = await conn.fetchval("SELECT is_admin FROM users WHERE telegram_id = $1", telegram_id)
        return result is True


async def set_admin(telegram_id: int, is_admin_status: bool) -> bool:
    return await update_user(telegram_id, is_admin=is_admin_status)


# HACKATHON OPERATIONS
async def create_hackathon(name: str, description: str = None, prize_pool: str = None,
                           start_date=None, end_date=None, registration_deadline=None) -> Dict[str, Any]:
    async with get_connection() as conn:
        h = await conn.fetchrow("""
            INSERT INTO hackathons (name, description, prize_pool, start_date, end_date, registration_deadline)
            VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
        """, name, description, prize_pool, start_date, end_date, registration_deadline)
        return dict(h)


async def get_hackathon(hackathon_id: int) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        h = await conn.fetchrow("SELECT * FROM hackathons WHERE id = $1", hackathon_id)
        return dict(h) if h else None


async def get_active_hackathons() -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        hs = await conn.fetch("SELECT * FROM hackathons WHERE is_active = TRUE ORDER BY start_date")
        return [dict(h) for h in hs]


# STAGE OPERATIONS
async def create_stage(hackathon_id: int, stage_number: int, name: str, description: str = None,
                       task_description: str = None, start_date=None, deadline=None) -> Dict[str, Any]:
    async with get_connection() as conn:
        s = await conn.fetchrow("""
            INSERT INTO hackathon_stages (hackathon_id, stage_number, name, description, task_description, start_date, deadline)
            VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *
        """, hackathon_id, stage_number, name, description, task_description, start_date, deadline)
        return dict(s)


async def get_stage(stage_id: int) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        s = await conn.fetchrow("SELECT * FROM hackathon_stages WHERE id = $1", stage_id)
        return dict(s) if s else None


async def get_stages(hackathon_id: int) -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        ss = await conn.fetch("SELECT * FROM hackathon_stages WHERE hackathon_id = $1 ORDER BY stage_number", hackathon_id)
        return [dict(s) for s in ss]


async def get_active_stage(hackathon_id: int) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        s = await conn.fetchrow("""
            SELECT * FROM hackathon_stages WHERE hackathon_id = $1 AND is_active = TRUE ORDER BY stage_number LIMIT 1
        """, hackathon_id)
        return dict(s) if s else None


async def activate_stage(stage_id: int) -> bool:
    async with get_connection() as conn:
        async with conn.transaction():
            hid = await conn.fetchval("SELECT hackathon_id FROM hackathon_stages WHERE id = $1", stage_id)
            if not hid:
                return False
            await conn.execute("UPDATE hackathon_stages SET is_active = FALSE WHERE hackathon_id = $1", hid)
            result = await conn.execute("UPDATE hackathon_stages SET is_active = TRUE WHERE id = $1", stage_id)
            return result == "UPDATE 1"


def generate_team_code(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


# TEAM OPERATIONS
async def create_team(hackathon_id: int, name: str, owner_id: int, owner_role: str = "Team Lead",
                      field: str = None, portfolio_link: str = None) -> Dict[str, Any]:
    async with get_connection() as conn:
        async with conn.transaction():
            code = generate_team_code()
            while await conn.fetchval("SELECT 1 FROM teams WHERE code = $1", code):
                code = generate_team_code()
            team = await conn.fetchrow("""
                INSERT INTO teams (hackathon_id, name, code, owner_id, field, portfolio_link)
                VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
            """, hackathon_id, name, code, owner_id, field, portfolio_link)
            await conn.execute("""
                INSERT INTO team_members (team_id, user_id, role, is_team_lead) VALUES ($1, $2, $3, TRUE)
            """, team['id'], owner_id, owner_role)
            return dict(team)


async def get_team(team_id: int) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        t = await conn.fetchrow("""
            SELECT t.*, h.name as hackathon_name FROM teams t
            JOIN hackathons h ON t.hackathon_id = h.id WHERE t.id = $1
        """, team_id)
        return dict(t) if t else None


async def get_team_by_code(code: str) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        t = await conn.fetchrow("""
            SELECT t.*, h.name as hackathon_name FROM teams t
            JOIN hackathons h ON t.hackathon_id = h.id WHERE t.code = $1 AND t.is_active = TRUE
        """, code)
        return dict(t) if t else None


async def get_user_teams(telegram_id: int) -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        ts = await conn.fetch("""
            SELECT t.*, h.name as hackathon_name, tm.is_team_lead, tm.role FROM teams t
            JOIN team_members tm ON t.id = tm.team_id JOIN hackathons h ON t.hackathon_id = h.id
            WHERE tm.user_id = $1 AND t.is_active = TRUE ORDER BY t.created_at DESC
        """, telegram_id)
        return [dict(t) for t in ts]


async def get_user_team_for_hackathon(telegram_id: int, hackathon_id: int) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        t = await conn.fetchrow("""
            SELECT t.*, tm.is_team_lead, tm.role FROM teams t
            JOIN team_members tm ON t.id = tm.team_id
            WHERE tm.user_id = $1 AND t.hackathon_id = $2 AND t.is_active = TRUE
        """, telegram_id, hackathon_id)
        return dict(t) if t else None


async def add_team_member(team_id: int, user_id: int, role: str = "Member") -> bool:
    async with get_connection() as conn:
        try:
            count = await conn.fetchval("SELECT COUNT(*) FROM team_members WHERE team_id = $1", team_id)
            if count >= 5:
                return False
            await conn.execute("INSERT INTO team_members (team_id, user_id, role) VALUES ($1, $2, $3)", team_id, user_id, role)
            return True
        except:
            return False


async def get_team_members(team_id: int) -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        ms = await conn.fetch("""
            SELECT tm.*, u.first_name, u.last_name, u.username, u.telegram_id FROM team_members tm
            JOIN users u ON tm.user_id = u.telegram_id WHERE tm.team_id = $1
            ORDER BY tm.is_team_lead DESC, tm.joined_at
        """, team_id)
        return [dict(m) for m in ms]


async def remove_team_member(team_id: int, user_id: int) -> bool:
    async with get_connection() as conn:
        result = await conn.execute("""
            DELETE FROM team_members WHERE team_id = $1 AND user_id = $2 AND is_team_lead = FALSE
        """, team_id, user_id)
        return result == "DELETE 1"


async def leave_team(team_id: int, user_id: int) -> Dict[str, Any]:
    async with get_connection() as conn:
        async with conn.transaction():
            member = await conn.fetchrow("SELECT is_team_lead FROM team_members WHERE team_id = $1 AND user_id = $2", team_id, user_id)
            if not member:
                return {"success": False, "reason": "not_member"}
            if member['is_team_lead']:
                await conn.execute("UPDATE teams SET is_active = FALSE WHERE id = $1", team_id)
                return {"success": True, "team_deactivated": True}
            else:
                await conn.execute("DELETE FROM team_members WHERE team_id = $1 AND user_id = $2", team_id, user_id)
                return {"success": True, "team_deactivated": False}


# SUBMISSION OPERATIONS
async def create_submission(team_id: int, stage_id: int, submitted_by: int, content: str = None,
                            submission_type: str = 'link', file_id: str = None,
                            file_name: str = None, file_type: str = None) -> Dict[str, Any]:
    async with get_connection() as conn:
        s = await conn.fetchrow("""
            INSERT INTO submissions (team_id, stage_id, content, submission_type, file_id, file_name, file_type, submitted_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (team_id, stage_id) DO UPDATE SET
                content = EXCLUDED.content, submission_type = EXCLUDED.submission_type,
                file_id = EXCLUDED.file_id, file_name = EXCLUDED.file_name, file_type = EXCLUDED.file_type,
                submitted_by = EXCLUDED.submitted_by, submitted_at = NOW()
            RETURNING *
        """, team_id, stage_id, content, submission_type, file_id, file_name, file_type, submitted_by)
        return dict(s)


async def get_submission(team_id: int, stage_id: int) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        s = await conn.fetchrow("SELECT * FROM submissions WHERE team_id = $1 AND stage_id = $2", team_id, stage_id)
        return dict(s) if s else None


async def get_stage_submissions(stage_id: int) -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        ss = await conn.fetch("""
            SELECT s.*, t.name as team_name, t.code as team_code FROM submissions s
            JOIN teams t ON s.team_id = t.id WHERE s.stage_id = $1 ORDER BY s.submitted_at DESC
        """, stage_id)
        return [dict(s) for s in ss]


async def get_all_submissions() -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        ss = await conn.fetch("""
            SELECT s.*, t.name as team_name, t.code as team_code, hs.name as stage_name,
                   hs.stage_number, h.name as hackathon_name
            FROM submissions s JOIN teams t ON s.team_id = t.id
            JOIN hackathon_stages hs ON s.stage_id = hs.id
            JOIN hackathons h ON hs.hackathon_id = h.id ORDER BY s.submitted_at DESC
        """)
        return [dict(s) for s in ss]


# REGISTRATION STATE
async def set_registration_state(telegram_id: int, step: str, data: dict = None) -> None:
    async with get_connection() as conn:
        data_json = json.dumps(data) if data else '{}'
        await conn.execute("""
            INSERT INTO registration_states (telegram_id, current_step, data)
            VALUES ($1, $2, $3::jsonb)
            ON CONFLICT (telegram_id) DO UPDATE SET current_step = $2, data = $3::jsonb, updated_at = NOW()
        """, telegram_id, step, data_json)


async def get_registration_state(telegram_id: int) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        s = await conn.fetchrow("SELECT * FROM registration_states WHERE telegram_id = $1", telegram_id)
        if s:
            r = dict(s)
            if isinstance(r.get('data'), str):
                r['data'] = json.loads(r['data'])
            return r
        return None


async def clear_registration_state(telegram_id: int) -> None:
    async with get_connection() as conn:
        await conn.execute("DELETE FROM registration_states WHERE telegram_id = $1", telegram_id)


# NOTIFICATIONS & STATS
async def get_hackathon_participants(hackathon_id: int) -> List[int]:
    async with get_connection() as conn:
        rows = await conn.fetch("""
            SELECT DISTINCT tm.user_id FROM team_members tm
            JOIN teams t ON tm.team_id = t.id WHERE t.hackathon_id = $1 AND t.is_active = TRUE
        """, hackathon_id)
        return [r['user_id'] for r in rows]


async def log_action(telegram_id: int, action: str, details: dict = None) -> None:
    async with get_connection() as conn:
        await conn.execute("INSERT INTO audit_log (telegram_id, action, details) VALUES ($1, $2, $3)",
                           telegram_id, action, json.dumps(details) if details else None)


async def get_stats() -> Dict[str, Any]:
    async with get_connection() as conn:
        stats = await conn.fetchrow("""
            SELECT 
                (SELECT COUNT(*) FROM users WHERE is_active = TRUE) as total_users,
                (SELECT COUNT(*) FROM users WHERE consent_given = TRUE) as consented_users,
                (SELECT COUNT(*) FROM teams WHERE is_active = TRUE) as total_teams,
                (SELECT COUNT(*) FROM hackathons WHERE is_active = TRUE) as active_hackathons,
                (SELECT COUNT(*) FROM submissions) as total_submissions
        """)
        return dict(stats)
