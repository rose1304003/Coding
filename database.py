"""
Database module for CBU Coding Hackathon Telegram Bot
Compatible with Web Team's unified schema
Production-ready PostgreSQL with UUID primary keys
"""

import os
import json
import random
import string
import base64
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import asyncpg
from asyncpg import Pool
from uuid import UUID

DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_IDS = os.getenv("ADMIN_IDS", "")
_pool: Optional[Pool] = None

# Valid values for fields
HACKATON_STATUS = ['DRAFT', 'OPEN_TO_REGISTRATION', 'ACTIVE', 'FINISHED', 'ARCHIVED']
USER_ROLES = ['ADMIN', 'PARTICIPANT']
TEAM_ROLES = ['BACKEND', 'FRONTEND', 'DESIGNER', 'PROJECT_MANAGER']
LANGUAGES = ['uz', 'en', 'ru']


def get_env_admin_ids() -> set:
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


def _to_dict(record) -> Optional[Dict[str, Any]]:
    if record is None:
        return None
    d = dict(record)
    for key, value in d.items():
        if isinstance(value, UUID):
            d[key] = str(value)
    return d


def _to_dict_list(records) -> List[Dict[str, Any]]:
    return [_to_dict(r) for r in records]


def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def generate_password(length: int = 12) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%"
    password = ''.join(random.choices(chars, k=length))
    return base64.b64encode(password.encode()).decode()


def decode_password(encoded_password: str) -> str:
    return base64.b64decode(encoded_password.encode()).decode()


# ============================================================================
# TABLE CREATION
# ============================================================================

async def create_tables():
    async with get_connection() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS "public"."registration_state" (
                "telegram_id" BIGINT PRIMARY KEY,
                "current_step" VARCHAR(50) NOT NULL,
                "data" JSONB DEFAULT '{}',
                "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        print("✅ Database tables verified!")


# ============================================================================
# USER OPERATIONS
# ============================================================================

async def add_user(telegram_id: int, first_name: str, username: str = None, 
                   last_name: str = None, email: str = None) -> Dict[str, Any]:
    async with get_connection() as conn:
        existing = await conn.fetchrow(
            'SELECT id FROM "user" WHERE telegram_id = $1', telegram_id
        )
        
        if existing:
            user = await conn.fetchrow("""
                UPDATE "user" SET
                    username = COALESCE($2, username),
                    first_name = COALESCE($3, first_name),
                    last_name = COALESCE($4, last_name),
                    email = COALESCE($5, email),
                    modified_at = NOW(),
                    modified_by = 'telegram_bot'
                WHERE telegram_id = $1
                RETURNING *
            """, telegram_id, username, first_name, last_name, email)
        else:
            password = generate_password()
            user = await conn.fetchrow("""
                INSERT INTO "user" (id, telegram_id, username, first_name, last_name, email, password, created_at, created_by)
                VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, NOW(), 'telegram_bot')
                RETURNING *
            """, telegram_id, username, first_name, last_name, email, password)
        
        return _to_dict(user)


async def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        user = await conn.fetchrow('SELECT * FROM "user" WHERE telegram_id = $1', telegram_id)
        if user:
            result = _to_dict(user)
            result['location'] = result.get('living_place')
            return result
        return None


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        user = await conn.fetchrow('SELECT * FROM "user" WHERE id = $1', user_id)
        return _to_dict(user)


async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        user = await conn.fetchrow('SELECT * FROM "user" WHERE email = $1', email)
        return _to_dict(user)


async def update_user(telegram_id: int, **kwargs) -> bool:
    if not kwargs:
        return False
    
    field_mapping = {'location': 'living_place'}
    
    # Validate language
    if 'language' in kwargs:
        lang = kwargs['language']
        if lang and lang.lower() not in LANGUAGES:
            kwargs['language'] = 'uz'
        elif lang:
            kwargs['language'] = lang.lower()
    
    mapped_kwargs = {}
    for key, value in kwargs.items():
        new_key = field_mapping.get(key, key)
        mapped_kwargs[new_key] = value
    
    set_parts = []
    values = []
    for i, (key, value) in enumerate(mapped_kwargs.items(), 1):
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


async def set_user_password(telegram_id: int, password: str = None) -> str:
    if password is None:
        password = generate_password()
    else:
        password = base64.b64encode(password.encode()).decode()
    
    async with get_connection() as conn:
        await conn.execute("""
            UPDATE "user" SET password = $2, modified_at = NOW()
            WHERE telegram_id = $1
        """, telegram_id, password)
    
    return password


async def get_user_password(telegram_id: int) -> Optional[str]:
    async with get_connection() as conn:
        return await conn.fetchval('SELECT password FROM "user" WHERE telegram_id = $1', telegram_id)


async def set_user_consent(telegram_id: int, consented: bool, version: str = "1.0") -> bool:
    async with get_connection() as conn:
        if consented:
            result = await conn.execute("""
                UPDATE "user" SET consent_given = TRUE, consent_given_at = NOW(), 
                    consent_version = $2, modified_at = NOW(), modified_by = 'telegram_bot'
                WHERE telegram_id = $1
            """, telegram_id, version)
        else:
            result = await conn.execute("""
                UPDATE "user" SET consent_given = FALSE, consent_given_at = NULL, 
                    is_active = FALSE, modified_at = NOW(), modified_by = 'telegram_bot'
                WHERE telegram_id = $1
            """, telegram_id)
        await log_action(telegram_id, 'consent_decision', {'consented': consented, 'version': version})
        return result == "UPDATE 1"


async def has_user_consented(telegram_id: int) -> bool:
    async with get_connection() as conn:
        result = await conn.fetchval('SELECT consent_given FROM "user" WHERE telegram_id = $1', telegram_id)
        return result is True


async def get_all_active_users() -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        users = await conn.fetch('SELECT * FROM "user" WHERE is_active = TRUE ORDER BY created_at')
        return _to_dict_list(users)


async def get_all_consented_users() -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        users = await conn.fetch('SELECT * FROM "user" WHERE is_active = TRUE AND consent_given = TRUE')
        return _to_dict_list(users)


async def is_admin(telegram_id: int) -> bool:
    if telegram_id in get_env_admin_ids():
        return True
    async with get_connection() as conn:
        result = await conn.fetchval('SELECT is_admin FROM "user" WHERE telegram_id = $1', telegram_id)
        return result is True


async def set_admin(telegram_id: int, is_admin_status: bool) -> bool:
    return await update_user(telegram_id, is_admin=is_admin_status)


# ============================================================================
# HACKATHON OPERATIONS
# ============================================================================

async def create_hackathon(name: str, description: str = None, prize_pool: str = None,
                           start_date=None, end_date=None, registration_deadline=None,
                           name_ru: str = None, name_en: str = None,
                           description_ru: str = None, description_en: str = None,
                           prize_pool_ru: str = None, prize_pool_en: str = None,
                           status: str = 'DRAFT') -> Dict[str, Any]:
    if status not in HACKATON_STATUS:
        status = 'DRAFT'
    
    async with get_connection() as conn:
        async with conn.transaction():
            h = await conn.fetchrow("""
                INSERT INTO "hackaton" (id, name, description, prize_pool, starts_at, ends_at, 
                                        registration_deadline, status, is_active, created_at, created_by)
                VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, TRUE, NOW(), 'telegram_bot')
                RETURNING *
            """, name, description, prize_pool, start_date, end_date, registration_deadline, status)
            
            hackaton_id = h['id']
            
            if name_ru or description_ru or prize_pool_ru:
                await conn.execute("""
                    INSERT INTO "hackaton_language" (id, hackaton_id, lang, name, description, prize_pool)
                    VALUES (gen_random_uuid(), $1, 'ru', $2, $3, $4)
                """, hackaton_id, name_ru or name, description_ru, prize_pool_ru)
            
            if name_en or description_en or prize_pool_en:
                await conn.execute("""
                    INSERT INTO "hackaton_language" (id, hackaton_id, lang, name, description, prize_pool)
                    VALUES (gen_random_uuid(), $1, 'en', $2, $3, $4)
                """, hackaton_id, name_en or name, description_en, prize_pool_en)
            
            result = _to_dict(h)
            result['start_date'] = result.get('starts_at')
            result['end_date'] = result.get('ends_at')
            return result


async def get_hackathon(hackathon_id) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        h = await conn.fetchrow('SELECT * FROM "hackaton" WHERE id = $1', hackathon_id)
        if not h:
            return None
        
        result = _to_dict(h)
        langs = await conn.fetch('SELECT * FROM "hackaton_language" WHERE hackaton_id = $1', hackathon_id)
        for lang in langs:
            lang_code = str(lang['lang']).lower()
            result[f'name_{lang_code}'] = lang['name']
            result[f'description_{lang_code}'] = lang['description']
            if lang.get('prize_pool'):
                result[f'prize_pool_{lang_code}'] = lang['prize_pool']
        
        result['start_date'] = result.get('starts_at')
        result['end_date'] = result.get('ends_at')
        return result


async def get_active_hackathons() -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        hs = await conn.fetch("""
            SELECT * FROM "hackaton" 
            WHERE is_active = TRUE AND status IN ('OPEN_TO_REGISTRATION', 'ACTIVE')
            ORDER BY starts_at
        """)
        
        results = []
        for h in hs:
            result = _to_dict(h)
            langs = await conn.fetch('SELECT * FROM "hackaton_language" WHERE hackaton_id = $1', h['id'])
            for lang in langs:
                lang_code = str(lang['lang']).lower()
                result[f'name_{lang_code}'] = lang['name']
                result[f'description_{lang_code}'] = lang['description']
                if lang.get('prize_pool'):
                    result[f'prize_pool_{lang_code}'] = lang['prize_pool']
            result['start_date'] = result.get('starts_at')
            result['end_date'] = result.get('ends_at')
            results.append(result)
        return results


async def update_hackathon_status(hackathon_id, status: str) -> bool:
    if status not in HACKATON_STATUS:
        return False
    async with get_connection() as conn:
        result = await conn.execute("""
            UPDATE "hackaton" SET status = $2, modified_at = NOW() WHERE id = $1
        """, hackathon_id, status)
        return result == "UPDATE 1"


def get_localized_field(hackathon: dict, field: str, lang: str) -> str:
    lang = lang.lower() if lang else 'uz'
    if lang == 'ru':
        return hackathon.get(f'{field}_ru') or hackathon.get(field) or '—'
    elif lang == 'en':
        return hackathon.get(f'{field}_en') or hackathon.get(field) or '—'
    return hackathon.get(field) or '—'


# ============================================================================
# STAGE/TASK OPERATIONS
# ============================================================================

async def create_stage(hackathon_id, stage_number: int, name: str, description: str = None,
                       task_description: str = None, start_date=None, deadline=None,
                       name_ru: str = None, name_en: str = None,
                       description_ru: str = None, description_en: str = None,
                       task_description_ru: str = None, task_description_en: str = None) -> Dict[str, Any]:
    async with get_connection() as conn:
        async with conn.transaction():
            s = await conn.fetchrow("""
                INSERT INTO "hackaton_task" (id, hackaton_id, name, description, stage_number, deadline, start_date, created_at, created_by)
                VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, NOW(), 'telegram_bot')
                RETURNING *
            """, hackathon_id, name, description, stage_number, deadline, start_date)
            
            task_id = s['id']
            
            await conn.execute("""
                INSERT INTO "hackaton_task_language" (id, hackaton_task_id, lang, name, description, task_description)
                VALUES (gen_random_uuid(), $1, 'uz', $2, $3, $4)
            """, task_id, name, description or '', task_description)
            
            if name_ru or description_ru or task_description_ru:
                await conn.execute("""
                    INSERT INTO "hackaton_task_language" (id, hackaton_task_id, lang, name, description, task_description)
                    VALUES (gen_random_uuid(), $1, 'ru', $2, $3, $4)
                """, task_id, name_ru or name, description_ru or '', task_description_ru)
            
            if name_en or description_en or task_description_en:
                await conn.execute("""
                    INSERT INTO "hackaton_task_language" (id, hackaton_task_id, lang, name, description, task_description)
                    VALUES (gen_random_uuid(), $1, 'en', $2, $3, $4)
                """, task_id, name_en or name, description_en or '', task_description_en)
            
            return _to_dict(s)


async def get_stage(stage_id) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        s = await conn.fetchrow('SELECT * FROM "hackaton_task" WHERE id = $1', stage_id)
        if not s:
            return None
        
        result = _to_dict(s)
        langs = await conn.fetch('SELECT * FROM "hackaton_task_language" WHERE hackaton_task_id = $1', stage_id)
        for lang in langs:
            lang_code = str(lang['lang']).lower()
            if lang_code == 'uz':
                result['task_description'] = lang.get('task_description')
            else:
                result[f'name_{lang_code}'] = lang['name']
                result[f'description_{lang_code}'] = lang['description']
                result[f'task_description_{lang_code}'] = lang.get('task_description')
        return result


async def get_stages(hackathon_id) -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        stages = await conn.fetch("""
            SELECT * FROM "hackaton_task" WHERE hackaton_id = $1 ORDER BY stage_number
        """, hackathon_id)
        
        results = []
        for s in stages:
            result = _to_dict(s)
            langs = await conn.fetch('SELECT * FROM "hackaton_task_language" WHERE hackaton_task_id = $1', s['id'])
            for lang in langs:
                lang_code = str(lang['lang']).lower()
                if lang_code == 'uz':
                    result['task_description'] = lang.get('task_description')
                else:
                    result[f'name_{lang_code}'] = lang['name']
                    result[f'description_{lang_code}'] = lang['description']
                    result[f'task_description_{lang_code}'] = lang.get('task_description')
            results.append(result)
        return results


async def get_active_stage(hackathon_id) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        s = await conn.fetchrow("""
            SELECT * FROM "hackaton_task" WHERE hackaton_id = $1 AND is_active = TRUE 
            ORDER BY stage_number LIMIT 1
        """, hackathon_id)
        if not s:
            return None
        return await get_stage(s['id'])


async def activate_stage(stage_id) -> bool:
    async with get_connection() as conn:
        async with conn.transaction():
            hid = await conn.fetchval('SELECT hackaton_id FROM "hackaton_task" WHERE id = $1', stage_id)
            if not hid:
                return False
            await conn.execute('UPDATE "hackaton_task" SET is_active = FALSE WHERE hackaton_id = $1', hid)
            result = await conn.execute('UPDATE "hackaton_task" SET is_active = TRUE WHERE id = $1', stage_id)
            return result == "UPDATE 1"


# ============================================================================
# TEAM/GROUP OPERATIONS
# ============================================================================

def generate_team_code(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


async def create_team(hackathon_id, name: str, owner_id: int, owner_role: str = "PROJECT_MANAGER",
                      field: str = None, portfolio_link: str = None) -> Dict[str, Any]:
    if owner_role not in TEAM_ROLES:
        owner_role = "PROJECT_MANAGER"
    
    async with get_connection() as conn:
        async with conn.transaction():
            user = await conn.fetchrow('SELECT id FROM "user" WHERE telegram_id = $1', owner_id)
            if not user:
                raise ValueError(f"User with telegram_id {owner_id} not found")
            
            user_uuid = user['id']
            code = generate_team_code()
            while await conn.fetchval('SELECT 1 FROM "group" WHERE code = $1', code):
                code = generate_team_code()
            
            team = await conn.fetchrow("""
                INSERT INTO "group" (id, name, code, owner_id, field, portfolio_link, is_active, created_at, created_by)
                VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, TRUE, NOW(), 'telegram_bot')
                RETURNING *
            """, name, code, user_uuid, field, portfolio_link)
            
            group_id = team['id']
            
            await conn.execute("""
                INSERT INTO "group_user" (id, user_id, group_id, user_role_in_group, is_team_lead, joined_at)
                VALUES (gen_random_uuid(), $1, $2, $3, TRUE, NOW())
            """, user_uuid, group_id, owner_role)
            
            await conn.execute("""
                INSERT INTO "hackaton_group" (id, hackaton_id, group_id, registered_at)
                VALUES (gen_random_uuid(), $1, $2, NOW())
            """, hackathon_id, group_id)
            
            result = _to_dict(team)
            result['hackathon_id'] = str(hackathon_id)
            result['owner_telegram_id'] = owner_id
            return result


async def get_team(team_id) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        t = await conn.fetchrow("""
            SELECT g.*, h.name as hackathon_name, hg.hackaton_id as hackathon_id,
                   u.telegram_id as owner_telegram_id, u.telegram_id as owner_id
            FROM "group" g
            LEFT JOIN "hackaton_group" hg ON g.id = hg.group_id
            LEFT JOIN "hackaton" h ON hg.hackaton_id = h.id
            LEFT JOIN "user" u ON g.owner_id = u.id
            WHERE g.id = $1
        """, team_id)
        return _to_dict(t)


async def get_team_by_code(code: str) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        t = await conn.fetchrow("""
            SELECT g.*, h.name as hackathon_name, hg.hackaton_id as hackathon_id,
                   u.telegram_id as owner_telegram_id, u.telegram_id as owner_id
            FROM "group" g
            LEFT JOIN "hackaton_group" hg ON g.id = hg.group_id
            LEFT JOIN "hackaton" h ON hg.hackaton_id = h.id
            LEFT JOIN "user" u ON g.owner_id = u.id
            WHERE g.code = $1 AND g.is_active = TRUE
        """, code)
        return _to_dict(t)


async def get_user_teams(telegram_id: int) -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        ts = await conn.fetch("""
            SELECT g.*, h.name as hackathon_name, gu.is_team_lead, 
                   gu.user_role_in_group as role, hg.hackaton_id as hackathon_id
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


async def add_team_member(team_id, user_id: int, role: str = "BACKEND") -> bool:
    if role not in TEAM_ROLES:
        role = "BACKEND"
    
    async with get_connection() as conn:
        try:
            user = await conn.fetchrow('SELECT id FROM "user" WHERE telegram_id = $1', user_id)
            if not user:
                return False
            
            count = await conn.fetchval('SELECT COUNT(*) FROM "group_user" WHERE group_id = $1', team_id)
            if count >= 5:
                return False
            
            await conn.execute("""
                INSERT INTO "group_user" (id, user_id, group_id, user_role_in_group, is_team_lead, joined_at)
                VALUES (gen_random_uuid(), $1, $2, $3, FALSE, NOW())
            """, user['id'], team_id, role)
            return True
        except:
            return False


async def update_member_role(team_id, user_id: int, role: str) -> bool:
    if role not in TEAM_ROLES:
        return False
    async with get_connection() as conn:
        user = await conn.fetchrow('SELECT id FROM "user" WHERE telegram_id = $1', user_id)
        if not user:
            return False
        result = await conn.execute("""
            UPDATE "group_user" SET user_role_in_group = $3 WHERE group_id = $1 AND user_id = $2
        """, team_id, user['id'], role)
        return result == "UPDATE 1"


async def get_team_members(team_id) -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        ms = await conn.fetch("""
            SELECT gu.*, u.first_name, u.last_name, u.username, u.telegram_id, u.email,
                   gu.user_role_in_group as role
            FROM "group_user" gu
            JOIN "user" u ON gu.user_id = u.id
            WHERE gu.group_id = $1
            ORDER BY gu.is_team_lead DESC, gu.joined_at
        """, team_id)
        
        results = []
        for m in ms:
            d = _to_dict(m)
            d['user_id'] = d.get('telegram_id')
            results.append(d)
        return results


async def remove_team_member(team_id, user_id: int) -> bool:
    async with get_connection() as conn:
        user = await conn.fetchrow('SELECT id FROM "user" WHERE telegram_id = $1', user_id)
        if not user:
            return False
        result = await conn.execute("""
            DELETE FROM "group_user" WHERE group_id = $1 AND user_id = $2 AND is_team_lead = FALSE
        """, team_id, user['id'])
        return result == "DELETE 1"


async def leave_team(team_id, user_id: int) -> Dict[str, Any]:
    async with get_connection() as conn:
        async with conn.transaction():
            user = await conn.fetchrow('SELECT id FROM "user" WHERE telegram_id = $1', user_id)
            if not user:
                return {"success": False, "reason": "user_not_found"}
            
            member = await conn.fetchrow("""
                SELECT is_team_lead FROM "group_user" WHERE group_id = $1 AND user_id = $2
            """, team_id, user['id'])
            
            if not member:
                return {"success": False, "reason": "not_member"}
            
            if member['is_team_lead']:
                await conn.execute('UPDATE "group" SET is_active = FALSE, modified_at = NOW() WHERE id = $1', team_id)
                return {"success": True, "team_deactivated": True}
            else:
                await conn.execute('DELETE FROM "group_user" WHERE group_id = $1 AND user_id = $2', team_id, user['id'])
                return {"success": True, "team_deactivated": False}


# ============================================================================
# SUBMISSION OPERATIONS
# ============================================================================

async def create_submission(team_id, stage_id, submitted_by: int, content: str = None,
                            submission_type: str = 'link', file_id: str = None,
                            file_name: str = None, file_type: str = None) -> Dict[str, Any]:
    async with get_connection() as conn:
        user = await conn.fetchrow('SELECT id FROM "user" WHERE telegram_id = $1', submitted_by)
        user_uuid = user['id'] if user else None
        
        existing = await conn.fetchrow("""
            SELECT id FROM "submission" WHERE group_id = $1 AND hackaton_task_id = $2
        """, team_id, stage_id)
        
        if existing:
            s = await conn.fetchrow("""
                UPDATE "submission" SET content = $3, submission_type = $4, file_id = $5,
                    file_name = $6, file_type = $7, submitted_by = $8, submitted_at = NOW()
                WHERE group_id = $1 AND hackaton_task_id = $2
                RETURNING *
            """, team_id, stage_id, content, submission_type, file_id, file_name, file_type, user_uuid)
        else:
            s = await conn.fetchrow("""
                INSERT INTO "submission" (id, group_id, hackaton_task_id, content, submission_type, 
                                          file_id, file_name, file_type, submitted_by)
                VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING *
            """, team_id, stage_id, content, submission_type, file_id, file_name, file_type, user_uuid)
        
        result = _to_dict(s)
        result['team_id'] = result.get('group_id')
        result['stage_id'] = result.get('hackaton_task_id')
        return result


async def get_submission(team_id, stage_id) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        s = await conn.fetchrow("""
            SELECT * FROM "submission" WHERE group_id = $1 AND hackaton_task_id = $2
        """, team_id, stage_id)
        if s:
            result = _to_dict(s)
            result['team_id'] = result.get('group_id')
            result['stage_id'] = result.get('hackaton_task_id')
            return result
        return None


async def get_stage_submissions(stage_id) -> List[Dict[str, Any]]:
    async with get_connection() as conn:
        ss = await conn.fetch("""
            SELECT s.*, g.name as team_name, g.code as team_code
            FROM "submission" s JOIN "group" g ON s.group_id = g.id
            WHERE s.hackaton_task_id = $1 ORDER BY s.submitted_at DESC
        """, stage_id)
        results = []
        for s in ss:
            d = _to_dict(s)
            d['team_id'] = d.get('group_id')
            d['stage_id'] = d.get('hackaton_task_id')
            results.append(d)
        return results


async def get_all_submissions() -> List[Dict[str, Any]]:
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
        results = []
        for s in ss:
            d = _to_dict(s)
            d['team_id'] = d.get('group_id')
            d['stage_id'] = d.get('hackaton_task_id')
            results.append(d)
        return results


# ============================================================================
# REGISTRATION STATE
# ============================================================================

async def set_registration_state(telegram_id: int, step: str, data: dict = None) -> None:
    async with get_connection() as conn:
        data_json = json.dumps(data, default=json_serializer) if data else '{}'
        existing = await conn.fetchval('SELECT 1 FROM "registration_state" WHERE telegram_id = $1', telegram_id)
        if existing:
            await conn.execute("""
                UPDATE "registration_state" SET current_step = $2, data = $3::jsonb, updated_at = NOW()
                WHERE telegram_id = $1
            """, telegram_id, step, data_json)
        else:
            await conn.execute("""
                INSERT INTO "registration_state" (telegram_id, current_step, data)
                VALUES ($1, $2, $3::jsonb)
            """, telegram_id, step, data_json)


async def get_registration_state(telegram_id: int) -> Optional[Dict[str, Any]]:
    async with get_connection() as conn:
        s = await conn.fetchrow('SELECT * FROM "registration_state" WHERE telegram_id = $1', telegram_id)
        if s:
            r = dict(s)
            if isinstance(r.get('data'), str):
                r['data'] = json.loads(r['data'])
            return r
        return None


async def clear_registration_state(telegram_id: int) -> None:
    async with get_connection() as conn:
        await conn.execute('DELETE FROM "registration_state" WHERE telegram_id = $1', telegram_id)


# ============================================================================
# NOTIFICATIONS & LOGGING
# ============================================================================

async def get_hackathon_participants(hackathon_id) -> List[int]:
    async with get_connection() as conn:
        rows = await conn.fetch("""
            SELECT DISTINCT u.telegram_id FROM "user" u
            JOIN "group_user" gu ON u.id = gu.user_id
            JOIN "group" g ON gu.group_id = g.id
            JOIN "hackaton_group" hg ON g.id = hg.group_id
            WHERE hg.hackaton_id = $1 AND g.is_active = TRUE
        """, hackathon_id)
        return [r['telegram_id'] for r in rows if r['telegram_id']]


async def log_action(telegram_id: int, action: str, details: dict = None) -> None:
    async with get_connection() as conn:
        user = await conn.fetchrow('SELECT id FROM "user" WHERE telegram_id = $1', telegram_id)
        user_uuid = user['id'] if user else None
        await conn.execute("""
            INSERT INTO "audit_log" (id, user_id, telegram_id, action, details, created_at)
            VALUES (gen_random_uuid(), $1, $2, $3, $4::jsonb, NOW())
        """, user_uuid, telegram_id, action, json.dumps(details) if details else None)


async def get_stats() -> Dict[str, Any]:
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
