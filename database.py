"""
Database module for CBU Coding Hackathon Telegram Bot
Unified schema compatible with Web Team's DDL
Production-ready PostgreSQL implementation with UUID primary keys
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
from uuid import UUID

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


# ============================================================================
# SCHEMA CREATION (for fresh installations)
# ============================================================================

async def create_tables():
    """Create all tables using the unified schema."""
    async with get_connection() as conn:
        # Read and execute the migration file
        schema_path = os.path.join(os.path.dirname(__file__), 'migrations', '001_unified_schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            await conn.execute(schema_sql)
            print("✅ Database tables created from unified schema!")
        else:
            # Fallback: create tables inline if migration file not found
            await _create_tables_inline(conn)
            print("✅ Database tables created (inline)!")


async def _create_tables_inline(conn):
    """Fallback table creation if migration file is not available."""
    await conn.execute("""
        -- User table
        CREATE TABLE IF NOT EXISTS "public"."user" (
            "id" UUID NOT NULL DEFAULT gen_random_uuid(),
            "telegram_id" BIGINT UNIQUE,
            "username" VARCHAR(255),
            "phone" VARCHAR(50),
            "first_name" VARCHAR(255) NOT NULL,
            "last_name" VARCHAR(255),
            "email" VARCHAR(255),
            "birth_date" DATE,
            "gender" VARCHAR(20),
            "living_place" VARCHAR(500),
            "pinfl" VARCHAR(20),
            "role" VARCHAR(50) DEFAULT 'participant',
            "language" VARCHAR(10) DEFAULT 'uz',
            "consent_given" BOOLEAN DEFAULT FALSE,
            "consent_given_at" TIMESTAMP WITH TIME ZONE,
            "consent_version" VARCHAR(20) DEFAULT '1.0',
            "is_active" BOOLEAN DEFAULT TRUE,
            "is_admin" BOOLEAN DEFAULT FALSE,
            "registration_complete" BOOLEAN DEFAULT FALSE,
            "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            "created_by" VARCHAR(255) DEFAULT 'system',
            "modified_at" TIMESTAMP WITH TIME ZONE,
            "modified_by" VARCHAR(255),
            CONSTRAINT "pk_user_id" PRIMARY KEY ("id")
        );
        CREATE INDEX IF NOT EXISTS idx_user_telegram_id ON "public"."user"(telegram_id);
        
        -- Group table (teams)
        CREATE TABLE IF NOT EXISTS "public"."group" (
            "id" UUID NOT NULL DEFAULT gen_random_uuid(),
            "name" VARCHAR(255) NOT NULL,
            "code" VARCHAR(20) NOT NULL UNIQUE,
            "owner_id" UUID,
            "field" VARCHAR(255),
            "portfolio_link" TEXT,
            "is_active" BOOLEAN DEFAULT TRUE,
            "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            "created_by" VARCHAR(255) DEFAULT 'system',
            "modified_at" TIMESTAMP WITH TIME ZONE,
            "modified_by" VARCHAR(255),
            CONSTRAINT "pk_group_id" PRIMARY KEY ("id")
        );
        CREATE INDEX IF NOT EXISTS idx_group_code ON "public"."group"(code);
        
        -- Group user table (team members)
        CREATE TABLE IF NOT EXISTS "public"."group_user" (
            "id" UUID NOT NULL DEFAULT gen_random_uuid(),
            "user_id" UUID NOT NULL,
            "group_id" UUID NOT NULL,
            "user_role_in_group" VARCHAR(50) NOT NULL DEFAULT 'member',
            "is_team_lead" BOOLEAN DEFAULT FALSE,
            "joined_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            CONSTRAINT "pk_group_user_id" PRIMARY KEY ("id")
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_group_user_unique ON "public"."group_user" (user_id, group_id);
        
        -- Hackaton table
        CREATE TABLE IF NOT EXISTS "public"."hackaton" (
            "id" UUID NOT NULL DEFAULT gen_random_uuid(),
            "name" VARCHAR(255) NOT NULL,
            "description" TEXT,
            "prize_pool" VARCHAR(100),
            "starts_at" TIMESTAMP WITH TIME ZONE,
            "ends_at" TIMESTAMP WITH TIME ZONE,
            "registration_deadline" TIMESTAMP WITH TIME ZONE,
            "banner_file_id" TEXT,
            "status" VARCHAR(50) NOT NULL DEFAULT 'draft',
            "is_active" BOOLEAN DEFAULT TRUE,
            "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            "created_by" VARCHAR(255) DEFAULT 'system',
            "modified_at" TIMESTAMP WITH TIME ZONE,
            "modified_by" VARCHAR(255),
            CONSTRAINT "pk_hackaton_id" PRIMARY KEY ("id")
        );
        
        -- Hackaton language table
        CREATE TABLE IF NOT EXISTS "public"."hackaton_language" (
            "id" UUID NOT NULL DEFAULT gen_random_uuid(),
            "hackaton_id" UUID NOT NULL,
            "lang" VARCHAR(5) NOT NULL,
            "name" VARCHAR(255) NOT NULL,
            "description" TEXT,
            "prize_pool" VARCHAR(100),
            CONSTRAINT "pk_hackaton_language_id" PRIMARY KEY ("id")
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_hackaton_language_unique ON "public"."hackaton_language" (lang, hackaton_id);
        
        -- Hackaton group table
        CREATE TABLE IF NOT EXISTS "public"."hackaton_group" (
            "id" UUID NOT NULL DEFAULT gen_random_uuid(),
            "hackaton_id" UUID NOT NULL,
            "group_id" UUID NOT NULL,
            "registered_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            CONSTRAINT "pk_hackaton_group_id" PRIMARY KEY ("id")
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_hackaton_group_unique ON "public"."hackaton_group" (hackaton_id, group_id);
        
        -- Hackaton task table (stages)
        CREATE TABLE IF NOT EXISTS "public"."hackaton_task" (
            "id" UUID NOT NULL DEFAULT gen_random_uuid(),
            "hackaton_id" UUID NOT NULL,
            "name" VARCHAR(255) NOT NULL,
            "stage_number" INT NOT NULL,
            "deadline" TIMESTAMP WITH TIME ZONE,
            "start_date" TIMESTAMP WITH TIME ZONE,
            "is_active" BOOLEAN DEFAULT FALSE,
            "task_file_id" TEXT,
            "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            "created_by" VARCHAR(255) DEFAULT 'system',
            "modified_at" TIMESTAMP WITH TIME ZONE,
            "modified_by" VARCHAR(255),
            CONSTRAINT "pk_hackaton_task_id" PRIMARY KEY ("id")
        );
        
        -- Hackaton task language table
        CREATE TABLE IF NOT EXISTS "public"."hackaton_task_language" (
            "id" UUID NOT NULL DEFAULT gen_random_uuid(),
            "hackaton_task_id" UUID NOT NULL,
            "lang" VARCHAR(5) NOT NULL,
            "name" VARCHAR(255) NOT NULL,
            "description" TEXT NOT NULL,
            "task_description" TEXT,
            CONSTRAINT "pk_hackaton_task_language_id" PRIMARY KEY ("id")
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_hackaton_task_language_unique ON "public"."hackaton_task_language" (hackaton_task_id, lang);
        
        -- Task source table
        CREATE TABLE IF NOT EXISTS "public"."task_source" (
            "id" UUID NOT NULL DEFAULT gen_random_uuid(),
            "hackaton_task_id" UUID NOT NULL,
            "type" VARCHAR(50) NOT NULL,
            "source_path" VARCHAR(500) NOT NULL,
            "file_id" TEXT,
            "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            "created_by" VARCHAR(255) DEFAULT 'system',
            "modified_at" TIMESTAMP WITH TIME ZONE,
            "modified_by" VARCHAR(255),
            CONSTRAINT "pk_task_source_id" PRIMARY KEY ("id")
        );
        
        -- Submission table
        CREATE TABLE IF NOT EXISTS "public"."submission" (
            "id" UUID NOT NULL DEFAULT gen_random_uuid(),
            "group_id" UUID NOT NULL,
            "hackaton_task_id" UUID NOT NULL,
            "submission_type" VARCHAR(50) NOT NULL DEFAULT 'link',
            "content" TEXT,
            "file_id" TEXT,
            "file_name" VARCHAR(255),
            "file_type" VARCHAR(50),
            "submitted_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            "submitted_by" UUID,
            "score" DECIMAL(5,2),
            "feedback" TEXT,
            "reviewed_at" TIMESTAMP WITH TIME ZONE,
            "reviewed_by" UUID,
            CONSTRAINT "pk_submission_id" PRIMARY KEY ("id")
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_submission_unique ON "public"."submission"(group_id, hackaton_task_id);
        
        -- Notification table
        CREATE TABLE IF NOT EXISTS "public"."notification" (
            "id" UUID NOT NULL DEFAULT gen_random_uuid(),
            "hackaton_id" UUID,
            "title" VARCHAR(255) NOT NULL,
            "message" TEXT NOT NULL,
            "sent_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            "sent_by" UUID,
            "recipient_count" INTEGER DEFAULT 0,
            CONSTRAINT "pk_notification_id" PRIMARY KEY ("id")
        );
        
        -- Registration state table
        CREATE TABLE IF NOT EXISTS "public"."registration_state" (
            "telegram_id" BIGINT PRIMARY KEY,
            "current_step" VARCHAR(50) NOT NULL,
            "data" JSONB DEFAULT '{}',
            "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Audit log table
        CREATE TABLE IF NOT EXISTS "public"."audit_log" (
            "id" UUID NOT NULL DEFAULT gen_random_uuid(),
            "user_id" UUID,
            "telegram_id" BIGINT,
            "action" VARCHAR(100) NOT NULL,
            "details" JSONB,
            "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            CONSTRAINT "pk_audit_log_id" PRIMARY KEY ("id")
        );
        CREATE INDEX IF NOT EXISTS idx_audit_log_telegram ON "public"."audit_log"(telegram_id);
    """)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _to_dict(record) -> Optional[Dict[str, Any]]:
    """Convert asyncpg Record to dict, handling UUID conversion."""
    if record is None:
        return None
    d = dict(record)
    # Convert UUID objects to strings for JSON serialization
    for key, value in d.items():
        if isinstance(value, UUID):
            d[key] = str(value)
    return d


def _to_dict_list(records) -> List[Dict[str, Any]]:
    """Convert list of asyncpg Records to list of dicts."""
    return [_to_dict(r) for r in records]


def json_serializer(obj):
    """JSON serializer for objects not serializable by default."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


# ============================================================================
# USER OPERATIONS
# ============================================================================

async def add_user(telegram_id: int, first_name: str, username: str = None, last_name: str = None) -> Dict[str, Any]:
    """Add or update a user by telegram_id."""
    async with get_connection() as conn:
        # Check if user exists
        existing = await conn.fetchrow(
            'SELECT id FROM "user" WHERE telegram_id = $1', telegram_id
        )
        
        if existing:
            # Update existing user
            user = await conn.fetchrow("""
                UPDATE "user" SET
                    username = COALESCE($2, username),
                    first_name = COALESCE($3, first_name),
                    last_name = COALESCE($4, last_name),
                    modified_at = NOW(),
                    modified_by = 'telegram_bot'
                WHERE telegram_id = $1
                RETURNING *
            """, telegram_id, username, first_name, last_name)
        else:
            # Create new user
            user = await conn.fetchrow("""
                INSERT INTO "user" (telegram_id, username, first_name, last_name, created_by)
                VALUES ($1, $2, $3, $4, 'telegram_bot')
                RETURNING *
            """, telegram_id, username, first_name, last_name)
        
        return _to_dict(user)


async def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Get user by telegram_id."""
    async with get_connection() as conn:
        user = await conn.fetchrow('SELECT * FROM "user" WHERE telegram_id = $1', telegram_id)
        return _to_dict(user)


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by UUID."""
    async with get_connection() as conn:
        user = await conn.fetchrow('SELECT * FROM "user" WHERE id = $1', user_id)
        return _to_dict(user)


async def update_user(telegram_id: int, **kwargs) -> bool:
    """Update user fields by telegram_id."""
    if not kwargs:
        return False
    
    # Build SET clause
    set_parts = []
    values = []
    for i, (key, value) in enumerate(kwargs.items(), 1):
        set_parts.append(f'"{key}" = ${i}')
        values.append(value)
    
    values.append(telegram_id)
    query = f"""
        UPDATE "user" SET {', '.join(set_parts)}, modified_at = NOW(), modified_by = 'telegram_bot'
        WHERE telegram_id = ${len(values)}
    """
    
    async with get_connection() as conn:
        result = await conn.execute(query, *values)
        return result == "UPDATE 1"


async def set_user_consent(telegram_id: int, consented: bool, version: str = "1.0") -> bool:
    """Set user's GDPR consent status."""
    async with get_connection() as conn:
        if consented:
            result = await conn.execute("""
                UPDATE "user" SET 
                    consent_given = TRUE, 
                    consent_given_at = NOW(), 
                    consent_version = $2,
                    modified_at = NOW(),
                    modified_by = 'telegram_bot'
                WHERE telegram_id = $1
            """, telegram_id, version)
        else:
            result = await conn.execute("""
                UPDATE "user" SET 
                    consent_given = FALSE, 
                    consent_given_at = NULL, 
                    is_active = FALSE,
                    modified_at = NOW(),
                    modified_by = 'telegram_bot'
                WHERE telegram_id = $1
            """, telegram_id)
        
        await log_action(telegram_id, 'consent_decision', {'consented': consented, 'version': version})
        return result == "UPDATE 1"


async def has_user_consented(telegram_id: int) -> bool:
    """Check if user has given consent."""
    async with get_connection() as conn:
        result = await conn.fetchval('SELECT consent_given FROM "user" WHERE telegram_id = $1', telegram_id)
        return result is True


async def get_all_active_users() -> List[Dict[str, Any]]:
    """Get all active users."""
    async with get_connection() as conn:
        users = await conn.fetch('SELECT * FROM "user" WHERE is_active = TRUE ORDER BY created_at')
        return _to_dict_list(users)


async def get_all_consented_users() -> List[Dict[str, Any]]:
    """Get all users who have given consent."""
    async with get_connection() as conn:
        users = await conn.fetch('SELECT * FROM "user" WHERE is_active = TRUE AND consent_given = TRUE')
        return _to_dict_list(users)


async def is_admin(telegram_id: int) -> bool:
    """Check if user is an admin."""
    # First check environment variable (for initial setup)
    if telegram_id in get_env_admin_ids():
        return True
    # Then check database
    async with get_connection() as conn:
        result = await conn.fetchval('SELECT is_admin FROM "user" WHERE telegram_id = $1', telegram_id)
        return result is True


async def set_admin(telegram_id: int, is_admin_status: bool) -> bool:
    """Set user's admin status."""
    return await update_user(telegram_id, is_admin=is_admin_status)


# ============================================================================
# HACKATHON OPERATIONS
# ============================================================================

async def create_hackathon(name: str, description: str = None, prize_pool: str = None,
                           start_date=None, end_date=None, registration_deadline=None,
                           name_ru: str = None, name_en: str = None,
                           description_ru: str = None, description_en: str = None,
                           prize_pool_ru: str = None, prize_pool_en: str = None) -> Dict[str, Any]:
    """Create a new hackathon with optional translations."""
    async with get_connection() as conn:
        async with conn.transaction():
            # Create main hackathon record
            h = await conn.fetchrow("""
                INSERT INTO "hackaton" (name, description, prize_pool, starts_at, ends_at, 
                                        registration_deadline, status, created_by)
                VALUES ($1, $2, $3, $4, $5, $6, 'active', 'telegram_bot')
                RETURNING *
            """, name, description, prize_pool, start_date, end_date, registration_deadline)
            
            hackaton_id = h['id']
            
            # Add Russian translation if provided
            if name_ru or description_ru or prize_pool_ru:
                await conn.execute("""
                    INSERT INTO "hackaton_language" (hackaton_id, lang, name, description, prize_pool)
                    VALUES ($1, 'ru', $2, $3, $4)
                """, hackaton_id, name_ru or name, description_ru, prize_pool_ru)
            
            # Add English translation if provided
            if name_en or description_en or prize_pool_en:
                await conn.execute("""
                    INSERT INTO "hackaton_language" (hackaton_id, lang, name, description, prize_pool)
                    VALUES ($1, 'en', $2, $3, $4)
                """, hackaton_id, name_en or name, description_en, prize_pool_en)
            
            return _to_dict(h)


async def get_hackathon(hackathon_id) -> Optional[Dict[str, Any]]:
    """Get hackathon by ID with translations."""
    async with get_connection() as conn:
        h = await conn.fetchrow('SELECT * FROM "hackaton" WHERE id = $1', hackathon_id)
        if not h:
            return None
        
        result = _to_dict(h)
        
        # Fetch translations
        langs = await conn.fetch(
            'SELECT * FROM "hackaton_language" WHERE hackaton_id = $1', hackathon_id
        )
        for lang in langs:
            suffix = f"_{lang['lang']}"
            result[f'name{suffix}'] = lang['name']
            result[f'description{suffix}'] = lang['description']
            result[f'prize_pool{suffix}'] = lang['prize_pool']
        
        # Map field names for backward compatibility
        result['start_date'] = result.get('starts_at')
        result['end_date'] = result.get('ends_at')
        
        return result


async def get_active_hackathons() -> List[Dict[str, Any]]:
    """Get all active hackathons."""
    async with get_connection() as conn:
        hs = await conn.fetch("""
            SELECT * FROM "hackaton" WHERE is_active = TRUE 
            ORDER BY starts_at
        """)
        
        results = []
        for h in hs:
            result = _to_dict(h)
            # Fetch translations
            langs = await conn.fetch(
                'SELECT * FROM "hackaton_language" WHERE hackaton_id = $1', h['id']
            )
            for lang in langs:
                suffix = f"_{lang['lang']}"
                result[f'name{suffix}'] = lang['name']
                result[f'description{suffix}'] = lang['description']
                result[f'prize_pool{suffix}'] = lang['prize_pool']
            
            result['start_date'] = result.get('starts_at')
            result['end_date'] = result.get('ends_at')
            results.append(result)
        
        return results


def get_localized_field(hackathon: dict, field: str, lang: str) -> str:
    """Get localized field value with fallback to default (uz)."""
    if lang == 'ru':
        return hackathon.get(f'{field}_ru') or hackathon.get(field) or '—'
    elif lang == 'en':
        return hackathon.get(f'{field}_en') or hackathon.get(field) or '—'
    else:  # uz (default)
        return hackathon.get(field) or '—'


# ============================================================================
# STAGE/TASK OPERATIONS
# ============================================================================

async def create_stage(hackathon_id, stage_number: int, name: str, description: str = None,
                       task_description: str = None, start_date=None, deadline=None,
                       name_ru: str = None, name_en: str = None,
                       description_ru: str = None, description_en: str = None,
                       task_description_ru: str = None, task_description_en: str = None) -> Dict[str, Any]:
    """Create a new hackathon task/stage."""
    async with get_connection() as conn:
        async with conn.transaction():
            # Create main task record
            s = await conn.fetchrow("""
                INSERT INTO "hackaton_task" (hackaton_id, name, stage_number, deadline, start_date, created_by)
                VALUES ($1, $2, $3, $4, $5, 'telegram_bot')
                RETURNING *
            """, hackathon_id, name, stage_number, deadline, start_date)
            
            task_id = s['id']
            
            # Add default (uz) translation
            await conn.execute("""
                INSERT INTO "hackaton_task_language" (hackaton_task_id, lang, name, description, task_description)
                VALUES ($1, 'uz', $2, $3, $4)
            """, task_id, name, description or '', task_description)
            
            # Add Russian translation if provided
            if name_ru or description_ru or task_description_ru:
                await conn.execute("""
                    INSERT INTO "hackaton_task_language" (hackaton_task_id, lang, name, description, task_description)
                    VALUES ($1, 'ru', $2, $3, $4)
                """, task_id, name_ru or name, description_ru or '', task_description_ru)
            
            # Add English translation if provided
            if name_en or description_en or task_description_en:
                await conn.execute("""
                    INSERT INTO "hackaton_task_language" (hackaton_task_id, lang, name, description, task_description)
                    VALUES ($1, 'en', $2, $3, $4)
                """, task_id, name_en or name, description_en or '', task_description_en)
            
            return _to_dict(s)


async def get_stage(stage_id) -> Optional[Dict[str, Any]]:
    """Get stage/task by ID with translations."""
    async with get_connection() as conn:
        s = await conn.fetchrow('SELECT * FROM "hackaton_task" WHERE id = $1', stage_id)
        if not s:
            return None
        
        result = _to_dict(s)
        
        # Fetch translations
        langs = await conn.fetch(
            'SELECT * FROM "hackaton_task_language" WHERE hackaton_task_id = $1', stage_id
        )
        for lang in langs:
            if lang['lang'] == 'uz':
                result['description'] = lang['description']
                result['task_description'] = lang['task_description']
            else:
                suffix = f"_{lang['lang']}"
                result[f'name{suffix}'] = lang['name']
                result[f'description{suffix}'] = lang['description']
                result[f'task_description{suffix}'] = lang['task_description']
        
        return result


async def get_stages(hackathon_id) -> List[Dict[str, Any]]:
    """Get all stages for a hackathon."""
    async with get_connection() as conn:
        stages = await conn.fetch("""
            SELECT * FROM "hackaton_task" WHERE hackaton_id = $1 
            ORDER BY stage_number
        """, hackathon_id)
        
        results = []
        for s in stages:
            result = _to_dict(s)
            langs = await conn.fetch(
                'SELECT * FROM "hackaton_task_language" WHERE hackaton_task_id = $1', s['id']
            )
            for lang in langs:
                if lang['lang'] == 'uz':
                    result['description'] = lang['description']
                    result['task_description'] = lang['task_description']
                else:
                    suffix = f"_{lang['lang']}"
                    result[f'name{suffix}'] = lang['name']
                    result[f'description{suffix}'] = lang['description']
                    result[f'task_description{suffix}'] = lang['task_description']
            results.append(result)
        
        return results


async def get_active_stage(hackathon_id) -> Optional[Dict[str, Any]]:
    """Get the currently active stage for a hackathon."""
    async with get_connection() as conn:
        s = await conn.fetchrow("""
            SELECT * FROM "hackaton_task" 
            WHERE hackaton_id = $1 AND is_active = TRUE 
            ORDER BY stage_number LIMIT 1
        """, hackathon_id)
        
        if not s:
            return None
        
        return await get_stage(s['id'])


async def activate_stage(stage_id) -> bool:
    """Activate a stage (deactivates all others in the hackathon)."""
    async with get_connection() as conn:
        async with conn.transaction():
            # Get hackathon ID
            hid = await conn.fetchval(
                'SELECT hackaton_id FROM "hackaton_task" WHERE id = $1', stage_id
            )
            if not hid:
                return False
            
            # Deactivate all stages in this hackathon
            await conn.execute(
                'UPDATE "hackaton_task" SET is_active = FALSE WHERE hackaton_id = $1', hid
            )
            
            # Activate the specified stage
            result = await conn.execute(
                'UPDATE "hackaton_task" SET is_active = TRUE WHERE id = $1', stage_id
            )
            return result == "UPDATE 1"


# ============================================================================
# TEAM/GROUP OPERATIONS
# ============================================================================

def generate_team_code(length: int = 6) -> str:
    """Generate a random team code."""
    return ''.join(random.choices(string.digits, k=length))


async def create_team(hackathon_id, name: str, owner_id: int, owner_role: str = "Team Lead",
                      field: str = None, portfolio_link: str = None) -> Dict[str, Any]:
    """Create a new team and register it for a hackathon."""
    async with get_connection() as conn:
        async with conn.transaction():
            # Get user's UUID from telegram_id
            user = await conn.fetchrow('SELECT id FROM "user" WHERE telegram_id = $1', owner_id)
            if not user:
                raise ValueError(f"User with telegram_id {owner_id} not found")
            
            user_uuid = user['id']
            
            # Generate unique code
            code = generate_team_code()
            while await conn.fetchval('SELECT 1 FROM "group" WHERE code = $1', code):
                code = generate_team_code()
            
            # Create the group
            team = await conn.fetchrow("""
                INSERT INTO "group" (name, code, owner_id, field, portfolio_link, created_by)
                VALUES ($1, $2, $3, $4, $5, 'telegram_bot')
                RETURNING *
            """, name, code, user_uuid, field, portfolio_link)
            
            group_id = team['id']
            
            # Add owner as team lead
            await conn.execute("""
                INSERT INTO "group_user" (user_id, group_id, user_role_in_group, is_team_lead)
                VALUES ($1, $2, $3, TRUE)
            """, user_uuid, group_id, owner_role)
            
            # Register team for hackathon
            await conn.execute("""
                INSERT INTO "hackaton_group" (hackaton_id, group_id)
                VALUES ($1, $2)
            """, hackathon_id, group_id)
            
            result = _to_dict(team)
            result['hackathon_id'] = str(hackathon_id)
            result['owner_telegram_id'] = owner_id
            
            return result


async def get_team(team_id) -> Optional[Dict[str, Any]]:
    """Get team by ID with hackathon info."""
    async with get_connection() as conn:
        t = await conn.fetchrow("""
            SELECT g.*, h.name as hackathon_name, hg.hackaton_id as hackathon_id,
                   u.telegram_id as owner_telegram_id
            FROM "group" g
            LEFT JOIN "hackaton_group" hg ON g.id = hg.group_id
            LEFT JOIN "hackaton" h ON hg.hackaton_id = h.id
            LEFT JOIN "user" u ON g.owner_id = u.id
            WHERE g.id = $1
        """, team_id)
        return _to_dict(t)


async def get_team_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Get team by code."""
    async with get_connection() as conn:
        t = await conn.fetchrow("""
            SELECT g.*, h.name as hackathon_name, hg.hackaton_id as hackathon_id,
                   u.telegram_id as owner_telegram_id
            FROM "group" g
            LEFT JOIN "hackaton_group" hg ON g.id = hg.group_id
            LEFT JOIN "hackaton" h ON hg.hackaton_id = h.id
            LEFT JOIN "user" u ON g.owner_id = u.id
            WHERE g.code = $1 AND g.is_active = TRUE
        """, code)
        return _to_dict(t)


async def get_user_teams(telegram_id: int) -> List[Dict[str, Any]]:
    """Get all teams for a user."""
    async with get_connection() as conn:
        ts = await conn.fetch("""
            SELECT g.*, h.name as hackathon_name, gu.is_team_lead, gu.user_role_in_group as role,
                   hg.hackaton_id as hackathon_id
            FROM "group" g
            JOIN "group_user" gu ON g.id = gu.group_id
            JOIN "user" u ON gu.user_id = u.id
            LEFT JOIN "hackaton_group" hg ON g.id = hg.group_id
            LEFT JOIN "hackaton" h ON hg.hackaton_id = h.id
            WHERE u.telegram_id = $1 AND g.is_active = TRUE
            ORDER BY g.created_at DESC
        """, telegram_id)
        return _to_dict_list(ts)


async def get_user_team_for_hackathon(telegram_id: int, hackathon_id) -> Optional[Dict[str, Any]]:
    """Get user's team for a specific hackathon."""
    async with get_connection() as conn:
        t = await conn.fetchrow("""
            SELECT g.*, gu.is_team_lead, gu.user_role_in_group as role
            FROM "group" g
            JOIN "group_user" gu ON g.id = gu.group_id
            JOIN "user" u ON gu.user_id = u.id
            JOIN "hackaton_group" hg ON g.id = hg.group_id
            WHERE u.telegram_id = $1 AND hg.hackaton_id = $2 AND g.is_active = TRUE
        """, telegram_id, hackathon_id)
        return _to_dict(t)


async def add_team_member(team_id, user_id: int, role: str = "Member") -> bool:
    """Add a user to a team (max 5 members)."""
    async with get_connection() as conn:
        try:
            # Get user UUID
            user = await conn.fetchrow('SELECT id FROM "user" WHERE telegram_id = $1', user_id)
            if not user:
                return False
            
            user_uuid = user['id']
            
            # Check member count
            count = await conn.fetchval(
                'SELECT COUNT(*) FROM "group_user" WHERE group_id = $1', team_id
            )
            if count >= 5:
                return False
            
            # Add member
            await conn.execute("""
                INSERT INTO "group_user" (user_id, group_id, user_role_in_group, is_team_lead)
                VALUES ($1, $2, $3, FALSE)
            """, user_uuid, team_id, role)
            return True
        except Exception:
            return False


async def get_team_members(team_id) -> List[Dict[str, Any]]:
    """Get all members of a team."""
    async with get_connection() as conn:
        ms = await conn.fetch("""
            SELECT gu.*, u.first_name, u.last_name, u.username, u.telegram_id
            FROM "group_user" gu
            JOIN "user" u ON gu.user_id = u.id
            WHERE gu.group_id = $1
            ORDER BY gu.is_team_lead DESC, gu.joined_at
        """, team_id)
        return _to_dict_list(ms)


async def remove_team_member(team_id, user_id: int) -> bool:
    """Remove a non-lead member from a team."""
    async with get_connection() as conn:
        # Get user UUID
        user = await conn.fetchrow('SELECT id FROM "user" WHERE telegram_id = $1', user_id)
        if not user:
            return False
        
        result = await conn.execute("""
            DELETE FROM "group_user" 
            WHERE group_id = $1 AND user_id = $2 AND is_team_lead = FALSE
        """, team_id, user['id'])
        return result == "DELETE 1"


async def leave_team(team_id, user_id: int) -> Dict[str, Any]:
    """Leave a team. If team lead leaves, deactivate the team."""
    async with get_connection() as conn:
        async with conn.transaction():
            # Get user UUID
            user = await conn.fetchrow('SELECT id FROM "user" WHERE telegram_id = $1', user_id)
            if not user:
                return {"success": False, "reason": "user_not_found"}
            
            user_uuid = user['id']
            
            # Check membership
            member = await conn.fetchrow("""
                SELECT is_team_lead FROM "group_user" 
                WHERE group_id = $1 AND user_id = $2
            """, team_id, user_uuid)
            
            if not member:
                return {"success": False, "reason": "not_member"}
            
            if member['is_team_lead']:
                # Deactivate team if lead leaves
                await conn.execute(
                    'UPDATE "group" SET is_active = FALSE, modified_at = NOW() WHERE id = $1', 
                    team_id
                )
                return {"success": True, "team_deactivated": True}
            else:
                # Remove member
                await conn.execute("""
                    DELETE FROM "group_user" WHERE group_id = $1 AND user_id = $2
                """, team_id, user_uuid)
                return {"success": True, "team_deactivated": False}


# ============================================================================
# SUBMISSION OPERATIONS
# ============================================================================

async def create_submission(team_id, stage_id, submitted_by: int, content: str = None,
                            submission_type: str = 'link', file_id: str = None,
                            file_name: str = None, file_type: str = None) -> Dict[str, Any]:
    """Create or update a submission."""
    async with get_connection() as conn:
        # Get user UUID
        user = await conn.fetchrow('SELECT id FROM "user" WHERE telegram_id = $1', submitted_by)
        user_uuid = user['id'] if user else None
        
        # Check if submission exists
        existing = await conn.fetchrow("""
            SELECT id FROM "submission" WHERE group_id = $1 AND hackaton_task_id = $2
        """, team_id, stage_id)
        
        if existing:
            # Update
            s = await conn.fetchrow("""
                UPDATE "submission" SET
                    content = $3, submission_type = $4, file_id = $5,
                    file_name = $6, file_type = $7, submitted_by = $8, submitted_at = NOW()
                WHERE group_id = $1 AND hackaton_task_id = $2
                RETURNING *
            """, team_id, stage_id, content, submission_type, file_id, file_name, file_type, user_uuid)
        else:
            # Insert
            s = await conn.fetchrow("""
                INSERT INTO "submission" (group_id, hackaton_task_id, content, submission_type, 
                                          file_id, file_name, file_type, submitted_by)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING *
            """, team_id, stage_id, content, submission_type, file_id, file_name, file_type, user_uuid)
        
        return _to_dict(s)


async def get_submission(team_id, stage_id) -> Optional[Dict[str, Any]]:
    """Get a submission."""
    async with get_connection() as conn:
        s = await conn.fetchrow("""
            SELECT * FROM "submission" WHERE group_id = $1 AND hackaton_task_id = $2
        """, team_id, stage_id)
        return _to_dict(s)


async def get_stage_submissions(stage_id) -> List[Dict[str, Any]]:
    """Get all submissions for a stage."""
    async with get_connection() as conn:
        ss = await conn.fetch("""
            SELECT s.*, g.name as team_name, g.code as team_code
            FROM "submission" s
            JOIN "group" g ON s.group_id = g.id
            WHERE s.hackaton_task_id = $1
            ORDER BY s.submitted_at DESC
        """, stage_id)
        return _to_dict_list(ss)


async def get_all_submissions() -> List[Dict[str, Any]]:
    """Get all submissions with full context."""
    async with get_connection() as conn:
        ss = await conn.fetch("""
            SELECT s.*, g.name as team_name, g.code as team_code,
                   ht.name as stage_name, ht.stage_number, h.name as hackathon_name
            FROM "submission" s
            JOIN "group" g ON s.group_id = g.id
            JOIN "hackaton_task" ht ON s.hackaton_task_id = ht.id
            JOIN "hackaton" h ON ht.hackaton_id = h.id
            ORDER BY s.submitted_at DESC
        """)
        return _to_dict_list(ss)


# ============================================================================
# REGISTRATION STATE
# ============================================================================

async def set_registration_state(telegram_id: int, step: str, data: dict = None) -> None:
    """Set registration state for a user."""
    async with get_connection() as conn:
        data_json = json.dumps(data, default=json_serializer) if data else '{}'
        
        # Check if exists
        existing = await conn.fetchval(
            'SELECT 1 FROM "registration_state" WHERE telegram_id = $1', telegram_id
        )
        
        if existing:
            await conn.execute("""
                UPDATE "registration_state" 
                SET current_step = $2, data = $3::jsonb, updated_at = NOW()
                WHERE telegram_id = $1
            """, telegram_id, step, data_json)
        else:
            await conn.execute("""
                INSERT INTO "registration_state" (telegram_id, current_step, data)
                VALUES ($1, $2, $3::jsonb)
            """, telegram_id, step, data_json)


async def get_registration_state(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Get registration state for a user."""
    async with get_connection() as conn:
        s = await conn.fetchrow(
            'SELECT * FROM "registration_state" WHERE telegram_id = $1', telegram_id
        )
        if s:
            r = dict(s)
            if isinstance(r.get('data'), str):
                r['data'] = json.loads(r['data'])
            return r
        return None


async def clear_registration_state(telegram_id: int) -> None:
    """Clear registration state for a user."""
    async with get_connection() as conn:
        await conn.execute(
            'DELETE FROM "registration_state" WHERE telegram_id = $1', telegram_id
        )


# ============================================================================
# NOTIFICATIONS & LOGGING
# ============================================================================

async def get_hackathon_participants(hackathon_id) -> List[int]:
    """Get telegram_ids of all participants in a hackathon."""
    async with get_connection() as conn:
        rows = await conn.fetch("""
            SELECT DISTINCT u.telegram_id
            FROM "user" u
            JOIN "group_user" gu ON u.id = gu.user_id
            JOIN "group" g ON gu.group_id = g.id
            JOIN "hackaton_group" hg ON g.id = hg.group_id
            WHERE hg.hackaton_id = $1 AND g.is_active = TRUE
        """, hackathon_id)
        return [r['telegram_id'] for r in rows if r['telegram_id']]


async def log_action(telegram_id: int, action: str, details: dict = None) -> None:
    """Log an audit action."""
    async with get_connection() as conn:
        # Try to get user UUID
        user = await conn.fetchrow('SELECT id FROM "user" WHERE telegram_id = $1', telegram_id)
        user_uuid = user['id'] if user else None
        
        await conn.execute("""
            INSERT INTO "audit_log" (user_id, telegram_id, action, details)
            VALUES ($1, $2, $3, $4::jsonb)
        """, user_uuid, telegram_id, action, json.dumps(details) if details else None)


async def get_stats() -> Dict[str, Any]:
    """Get system statistics."""
    async with get_connection() as conn:
        stats = await conn.fetchrow("""
            SELECT 
                (SELECT COUNT(*) FROM "user" WHERE is_active = TRUE) as total_users,
                (SELECT COUNT(*) FROM "user" WHERE consent_given = TRUE) as consented_users,
                (SELECT COUNT(*) FROM "group" WHERE is_active = TRUE) as total_teams,
                (SELECT COUNT(*) FROM "hackaton" WHERE is_active = TRUE) as active_hackathons,
                (SELECT COUNT(*) FROM "submission") as total_submissions
        """)
        return dict(stats)
