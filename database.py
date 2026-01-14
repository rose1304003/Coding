"""
Database module for Hackathon Telegram Bot
Production-ready PostgreSQL implementation with automatic schema creation
"""

import os
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import asyncpg
from asyncpg import Pool, Connection
import json
from typing import Any, Optional

# Get DATABASE_URL from environment (Railway injects this automatically)
DATABASE_URL = os.getenv("DATABASE_URL")

# Connection pool for efficient database access
_pool: Optional[Pool] = None


async def get_pool() -> Pool:
    """Get or create the connection pool."""
    global _pool
    if _pool is None:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        # Handle Railway's postgres:// vs postgresql:// URL format
        db_url = DATABASE_URL
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        
        _pool = await asyncpg.create_pool(
            db_url,
            min_size=2,
            max_size=10,
            command_timeout=60,
            statement_cache_size=0  # Disable for Railway compatibility
        )
    return _pool


@asynccontextmanager
async def get_connection():
    """Context manager for database connections."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn


async def close_pool():
    """Close the connection pool gracefully."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def create_tables():
    """
    Create all database tables automatically on startup.
    This is idempotent - safe to run multiple times.
    """
    async with get_connection() as conn:
        await conn.execute("""
            -- Users table: stores all Telegram users
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
                is_active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE,
                consent_accepted BOOLEAN DEFAULT FALSE,
                consent_accepted_at TIMESTAMP WITH TIME ZONE,
                consent_version VARCHAR(50) DEFAULT 'v1',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Index for fast lookups by telegram_id
            CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
            CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin) WHERE is_admin = TRUE;
            
            -- Hackathons table: stores hackathon events
            CREATE TABLE IF NOT EXISTS hackathons (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                prize_pool VARCHAR(100),
                start_date DATE,
                end_date DATE,
                registration_deadline TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_hackathons_active ON hackathons(is_active);
            
            -- Hackathon stages table
            CREATE TABLE IF NOT EXISTS hackathon_stages (
                id SERIAL PRIMARY KEY,
                hackathon_id INTEGER REFERENCES hackathons(id) ON DELETE CASCADE,
                stage_number INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                task_description TEXT,
                start_date TIMESTAMP WITH TIME ZONE,
                deadline TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_stages_hackathon ON hackathon_stages(hackathon_id);
            
            -- Teams table: stores team information
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
            CREATE INDEX IF NOT EXISTS idx_teams_owner ON teams(owner_id);
            CREATE INDEX IF NOT EXISTS idx_teams_code ON teams(code);
            
            -- Team members table: many-to-many relationship
            CREATE TABLE IF NOT EXISTS team_members (
                id SERIAL PRIMARY KEY,
                team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
                user_id BIGINT NOT NULL,
                role VARCHAR(255) DEFAULT 'member',
                is_team_lead BOOLEAN DEFAULT FALSE,
                joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_team_members_team ON team_members(team_id);
            CREATE INDEX IF NOT EXISTS idx_team_members_user ON team_members(user_id);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_team_members_unique 
                ON team_members(team_id, user_id);
            
            -- Submissions table: stores stage submissions
            CREATE TABLE IF NOT EXISTS submissions (
                id SERIAL PRIMARY KEY,
                team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
                stage_id INTEGER REFERENCES hackathon_stages(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                submission_type VARCHAR(30) DEFAULT 'url',
                file_id TEXT,
                file_name TEXT,
                mime_type TEXT,
                submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                score DECIMAL(5,2),
                feedback TEXT,
                reviewed_at TIMESTAMP WITH TIME ZONE,
                reviewed_by BIGINT
            );
            
            CREATE INDEX IF NOT EXISTS idx_submissions_team ON submissions(team_id);
            CREATE INDEX IF NOT EXISTS idx_submissions_stage ON submissions(stage_id);
            CREATE INDEX IF NOT EXISTS idx_submissions_type ON submissions(submission_type);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_submissions_unique 
                ON submissions(team_id, stage_id);
            
            -- Notifications table: for push notifications
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                hackathon_id INTEGER REFERENCES hackathons(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                sent_by BIGINT
            );
            
            -- User registration states for conversation flow
            CREATE TABLE IF NOT EXISTS registration_states (
                telegram_id BIGINT PRIMARY KEY,
                current_step VARCHAR(50) NOT NULL,
                data JSONB DEFAULT '{}',
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Audit log for important actions
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT,
                action VARCHAR(100) NOT NULL,
                details JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_audit_telegram ON audit_log(telegram_id);
            CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);
        """)

        # ---------------------------------------------------------------------
        # Lightweight migrations (safe to run repeatedly)
        # ---------------------------------------------------------------------
        # Users consent columns (if bot was deployed before consent feature)
        await conn.execute("""
            ALTER TABLE users
                ADD COLUMN IF NOT EXISTS consent_accepted BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS consent_accepted_at TIMESTAMP WITH TIME ZONE,
                ADD COLUMN IF NOT EXISTS consent_version VARCHAR(50) DEFAULT 'v1';
        """)

        # Submission file metadata columns (for file uploads)
        await conn.execute("""
            ALTER TABLE submissions
                ADD COLUMN IF NOT EXISTS submission_type VARCHAR(30) DEFAULT 'url',
                ADD COLUMN IF NOT EXISTS file_id TEXT,
                ADD COLUMN IF NOT EXISTS file_name TEXT,
                ADD COLUMN IF NOT EXISTS mime_type TEXT;
        """)

        print("✅ Database tables created successfully!")


# =============================================================================
# USER OPERATIONS
# =============================================================================

async def add_user(
    telegram_id: int,
    first_name: str,
    username: Optional[str] = None,
    last_name: Optional[str] = None,
    language: str = 'uz'
) -> Dict[str, Any]:
    """Add a new user or return existing one."""
    async with get_connection() as conn:
        # Try to insert, on conflict update and return
        user = await conn.fetchrow("""
            INSERT INTO users (telegram_id, username, first_name, last_name, language)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (telegram_id) 
            DO UPDATE SET 
                username = COALESCE(EXCLUDED.username, users.username),
                first_name = COALESCE(EXCLUDED.first_name, users.first_name),
                last_name = COALESCE(EXCLUDED.last_name, users.last_name),
                is_active = TRUE,
                updated_at = NOW()
            RETURNING *
        """, telegram_id, username, first_name, last_name, language)
        return dict(user)


async def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Get user by Telegram ID."""
    async with get_connection() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE telegram_id = $1",
            telegram_id
        )
        return dict(user) if user else None


async def update_user(telegram_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """Update user fields dynamically."""
    if not kwargs:
        return await get_user(telegram_id)
    
    # Build dynamic update query
    set_clauses = []
    values = []
    for i, (key, value) in enumerate(kwargs.items(), start=1):
        set_clauses.append(f"{key} = ${i}")
        values.append(value)
    
    values.append(telegram_id)
    query = f"""
        UPDATE users 
        SET {', '.join(set_clauses)}, updated_at = NOW()
        WHERE telegram_id = ${len(values)}
        RETURNING *
    """
    
    async with get_connection() as conn:
        user = await conn.fetchrow(query, *values)
        return dict(user) if user else None


async def deactivate_user(telegram_id: int) -> bool:
    """Mark user as inactive (soft delete)."""
    async with get_connection() as conn:
        result = await conn.execute("""
            UPDATE users SET is_active = FALSE, updated_at = NOW()
            WHERE telegram_id = $1
        """, telegram_id)
        return result == "UPDATE 1"


async def get_all_users(active_only: bool = True) -> List[Dict[str, Any]]:
    """Get all users, optionally filtered by active status."""
    async with get_connection() as conn:
        if active_only:
            users = await conn.fetch(
                "SELECT * FROM users WHERE is_active = TRUE ORDER BY created_at DESC"
            )
        else:
            users = await conn.fetch("SELECT * FROM users ORDER BY created_at DESC")
        return [dict(u) for u in users]


async def get_admins() -> List[Dict[str, Any]]:
    """Get all admin users."""
    async with get_connection() as conn:
        admins = await conn.fetch(
            "SELECT * FROM users WHERE is_admin = TRUE AND is_active = TRUE"
        )
        return [dict(a) for a in admins]


async def set_admin(telegram_id: int, is_admin: bool = True) -> bool:
    """Set or remove admin status for a user."""
    async with get_connection() as conn:
        result = await conn.execute("""
            UPDATE users SET is_admin = $1, updated_at = NOW()
            WHERE telegram_id = $2
        """, is_admin, telegram_id)
        return result == "UPDATE 1"


# =============================================================================
# HACKATHON OPERATIONS
# =============================================================================

async def create_hackathon(
    name: str,
    description: str = None,
    prize_pool: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    registration_deadline: datetime = None
) -> Dict[str, Any]:
    """Create a new hackathon."""
    async with get_connection() as conn:
        hackathon = await conn.fetchrow("""
            INSERT INTO hackathons 
            (name, description, prize_pool, start_date, end_date, registration_deadline)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
        """, name, description, prize_pool, start_date, end_date, registration_deadline)
        return dict(hackathon)


async def get_hackathon(hackathon_id: int) -> Optional[Dict[str, Any]]:
    """Get hackathon by ID."""
    async with get_connection() as conn:
        h = await conn.fetchrow(
            "SELECT * FROM hackathons WHERE id = $1",
            hackathon_id
        )
        return dict(h) if h else None


async def get_active_hackathons() -> List[Dict[str, Any]]:
    """Get all active hackathons."""
    async with get_connection() as conn:
        hackathons = await conn.fetch("""
            SELECT * FROM hackathons 
            WHERE is_active = TRUE 
            ORDER BY start_date DESC
        """)
        return [dict(h) for h in hackathons]


async def get_hackathon_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get hackathon by name."""
    async with get_connection() as conn:
        h = await conn.fetchrow(
            "SELECT * FROM hackathons WHERE name ILIKE $1 AND is_active = TRUE",
            f"%{name}%"
        )
        return dict(h) if h else None


# =============================================================================
# STAGE OPERATIONS
# =============================================================================

async def create_stage(
    hackathon_id: int,
    stage_number: int,
    name: str,
    description: str = None,
    task_description: str = None,
    start_date: datetime = None,
    deadline: datetime = None
) -> Dict[str, Any]:
    """Create a new stage for a hackathon."""
    async with get_connection() as conn:
        stage = await conn.fetchrow("""
            INSERT INTO hackathon_stages 
            (hackathon_id, stage_number, name, description, task_description, start_date, deadline)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """, hackathon_id, stage_number, name, description, task_description, start_date, deadline)
        return dict(stage)


async def get_active_stage(hackathon_id: int) -> Optional[Dict[str, Any]]:
    """Get the currently active stage for a hackathon."""
    async with get_connection() as conn:
        stage = await conn.fetchrow("""
            SELECT * FROM hackathon_stages 
            WHERE hackathon_id = $1 AND is_active = TRUE
            ORDER BY stage_number
            LIMIT 1
        """, hackathon_id)
        return dict(stage) if stage else None


async def get_stages(hackathon_id: int) -> List[Dict[str, Any]]:
    """Get all stages for a hackathon."""
    async with get_connection() as conn:
        stages = await conn.fetch("""
            SELECT * FROM hackathon_stages 
            WHERE hackathon_id = $1
            ORDER BY stage_number
        """, hackathon_id)
        return [dict(s) for s in stages]


async def activate_stage(stage_id: int) -> bool:
    """Activate a stage (deactivates others in same hackathon)."""
    async with get_connection() as conn:
        async with conn.transaction():
            # Get hackathon_id for this stage
            stage = await conn.fetchrow(
                "SELECT hackathon_id FROM hackathon_stages WHERE id = $1",
                stage_id
            )
            if not stage:
                return False
            
            # Deactivate all stages for this hackathon
            await conn.execute("""
                UPDATE hackathon_stages SET is_active = FALSE
                WHERE hackathon_id = $1
            """, stage['hackathon_id'])
            
            # Activate the specified stage
            await conn.execute("""
                UPDATE hackathon_stages SET is_active = TRUE
                WHERE id = $1
            """, stage_id)
            
            return True


# =============================================================================
# TEAM OPERATIONS
# =============================================================================

import random
import string

def generate_team_code() -> str:
    """Generate a unique 6-digit team code."""
    return ''.join(random.choices(string.digits, k=6))


async def create_team(
    hackathon_id: int,
    name: str,
    owner_id: int,
    owner_role: str = "Team Lead",
    field: str = None,
    portfolio_link: str = None
) -> Dict[str, Any]:
    """Create a new team and add owner as team lead."""
    async with get_connection() as conn:
        async with conn.transaction():
            # Generate unique code
            code = generate_team_code()
            while await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM teams WHERE code = $1)", code
            ):
                code = generate_team_code()
            
            # Create team
            team = await conn.fetchrow("""
                INSERT INTO teams (hackathon_id, name, code, owner_id, field, portfolio_link)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
            """, hackathon_id, name, code, owner_id, field, portfolio_link)
            
            # Add owner as team lead
            await conn.execute("""
                INSERT INTO team_members (team_id, user_id, role, is_team_lead)
                VALUES ($1, $2, $3, TRUE)
            """, team['id'], owner_id, owner_role)
            
            return dict(team)


async def get_team(team_id: int) -> Optional[Dict[str, Any]]:
    """Get team by ID with member count."""
    async with get_connection() as conn:
        team = await conn.fetchrow("""
            SELECT t.*, 
                   COUNT(tm.id) as member_count,
                   h.name as hackathon_name
            FROM teams t
            LEFT JOIN team_members tm ON t.id = tm.team_id
            LEFT JOIN hackathons h ON t.hackathon_id = h.id
            WHERE t.id = $1
            GROUP BY t.id, h.name
        """, team_id)
        return dict(team) if team else None


async def get_team_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Get team by join code."""
    async with get_connection() as conn:
        team = await conn.fetchrow(
            "SELECT * FROM teams WHERE code = $1 AND is_active = TRUE",
            code
        )
        return dict(team) if team else None


async def get_user_teams(telegram_id: int) -> List[Dict[str, Any]]:
    """Get all teams a user is part of."""
    async with get_connection() as conn:
        teams = await conn.fetch("""
            SELECT t.*, tm.role, tm.is_team_lead, h.name as hackathon_name
            FROM teams t
            JOIN team_members tm ON t.id = tm.team_id
            JOIN hackathons h ON t.hackathon_id = h.id
            WHERE tm.user_id = $1 AND t.is_active = TRUE
            ORDER BY t.created_at DESC
        """, telegram_id)
        return [dict(t) for t in teams]


async def get_user_team_for_hackathon(
    telegram_id: int, 
    hackathon_id: int
) -> Optional[Dict[str, Any]]:
    """Get user's team for a specific hackathon."""
    async with get_connection() as conn:
        team = await conn.fetchrow("""
            SELECT t.*, tm.role, tm.is_team_lead
            FROM teams t
            JOIN team_members tm ON t.id = tm.team_id
            WHERE tm.user_id = $1 AND t.hackathon_id = $2 AND t.is_active = TRUE
        """, telegram_id, hackathon_id)
        return dict(team) if team else None


async def add_team_member(
    team_id: int,
    user_id: int,
    role: str = "Member"
) -> bool:
    """Add a member to a team."""
    async with get_connection() as conn:
        try:
            await conn.execute("""
                INSERT INTO team_members (team_id, user_id, role)
                VALUES ($1, $2, $3)
            """, team_id, user_id, role)
            return True
        except asyncpg.UniqueViolationError:
            return False  # Already a member


async def remove_team_member(team_id: int, user_id: int) -> bool:
    """Remove a member from a team."""
    async with get_connection() as conn:
        result = await conn.execute("""
            DELETE FROM team_members 
            WHERE team_id = $1 AND user_id = $2 AND is_team_lead = FALSE
        """, team_id, user_id)
        return result == "DELETE 1"


async def get_team_members(team_id: int) -> List[Dict[str, Any]]:
    """Get all members of a team with user details."""
    async with get_connection() as conn:
        members = await conn.fetch("""
            SELECT u.telegram_id, u.username, u.first_name, u.last_name,
                   tm.role, tm.is_team_lead, tm.joined_at
            FROM team_members tm
            JOIN users u ON tm.user_id = u.telegram_id
            WHERE tm.team_id = $1
            ORDER BY tm.is_team_lead DESC, tm.joined_at
        """, team_id)
        return [dict(m) for m in members]


async def leave_team(team_id: int, user_id: int) -> Dict[str, Any]:
    """Leave a team. Returns status and info."""
    async with get_connection() as conn:
        async with conn.transaction():
            # Check if user is team lead
            member = await conn.fetchrow("""
                SELECT is_team_lead FROM team_members
                WHERE team_id = $1 AND user_id = $2
            """, team_id, user_id)
            
            if not member:
                return {"success": False, "reason": "not_member"}
            
            if member['is_team_lead']:
                # If team lead leaves, deactivate the team
                await conn.execute(
                    "UPDATE teams SET is_active = FALSE WHERE id = $1",
                    team_id
                )
                return {"success": True, "team_deactivated": True}
            else:
                # Regular member leaves
                await conn.execute("""
                    DELETE FROM team_members
                    WHERE team_id = $1 AND user_id = $2
                """, team_id, user_id)
                return {"success": True, "team_deactivated": False}


# =============================================================================
# SUBMISSION OPERATIONS
# =============================================================================

async def create_submission(
    team_id: int,
    stage_id: int,
    content: str,
    submission_type: str = 'url',
    file_id: str = None,
    file_name: str = None,
    mime_type: str = None
) -> Dict[str, Any]:
    """Create or update a submission."""
    async with get_connection() as conn:
        submission = await conn.fetchrow("""
            INSERT INTO submissions (team_id, stage_id, content, submission_type, file_id, file_name, mime_type)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (team_id, stage_id)
            DO UPDATE SET
                content = EXCLUDED.content,
                submission_type = EXCLUDED.submission_type,
                file_id = EXCLUDED.file_id,
                file_name = EXCLUDED.file_name,
                mime_type = EXCLUDED.mime_type,
                submitted_at = NOW()
            RETURNING *
        """, team_id, stage_id, content, submission_type, file_id, file_name, mime_type)
        return dict(submission)


async def get_submission(team_id: int, stage_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific submission."""
    async with get_connection() as conn:
        sub = await conn.fetchrow("""
            SELECT * FROM submissions
            WHERE team_id = $1 AND stage_id = $2
        """, team_id, stage_id)
        return dict(sub) if sub else None


async def get_stage_submissions(stage_id: int) -> List[Dict[str, Any]]:
    """Get all submissions for a stage."""
    async with get_connection() as conn:
        submissions = await conn.fetch("""
            SELECT s.*, t.name as team_name, t.code as team_code
            FROM submissions s
            JOIN teams t ON s.team_id = t.id
            WHERE s.stage_id = $1
            ORDER BY s.submitted_at DESC
        """, stage_id)
        return [dict(s) for s in submissions]


async def score_submission(
    submission_id: int,
    score: float,
    feedback: str,
    reviewer_id: int
) -> bool:
    """Score a submission."""
    async with get_connection() as conn:
        result = await conn.execute("""
            UPDATE submissions
            SET score = $1, feedback = $2, reviewed_at = NOW(), reviewed_by = $3
            WHERE id = $4
        """, score, feedback, reviewer_id, submission_id)
        return result == "UPDATE 1"


# =============================================================================
# REGISTRATION STATE (for conversation flow)
# =============================================================================

async def set_registration_state(self, telegram_id: int, state: Any, data: Optional[Any] = None):
    # Ensure data is always stored as TEXT (JSON string)
    if data is None:
        data_str = None
    elif isinstance(data, (dict, list)):
        data_str = json.dumps(data, ensure_ascii=False)
    else:
        data_str = str(data)

    async with self.pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO user_states (telegram_id, state, data, updated_at)
            VALUES ($1, $2, $3, NOW())
            ON CONFLICT (telegram_id)
            DO UPDATE SET state = EXCLUDED.state,
                          data = EXCLUDED.data,
                          updated_at = NOW()
            """,
            telegram_id,
            str(state),
            data_str,
        )

async def get_registration_state(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Get current registration state for a user."""
    async with get_connection() as conn:
        state = await conn.fetchrow(
            "SELECT * FROM registration_states WHERE telegram_id = $1",
            telegram_id
        )
        return dict(state) if state else None


async def clear_registration_state(telegram_id: int) -> None:
    """Clear registration state after completion."""
    async with get_connection() as conn:
        await conn.execute(
            "DELETE FROM registration_states WHERE telegram_id = $1",
            telegram_id
        )


# =============================================================================
# NOTIFICATIONS
# =============================================================================

async def create_notification(
    hackathon_id: int,
    title: str,
    message: str,
    sent_by: int
) -> Dict[str, Any]:
    """Create a notification record."""
    async with get_connection() as conn:
        notification = await conn.fetchrow("""
            INSERT INTO notifications (hackathon_id, title, message, sent_by)
            VALUES ($1, $2, $3, $4)
            RETURNING *
        """, hackathon_id, title, message, sent_by)
        return dict(notification)


async def get_hackathon_participants(hackathon_id: int) -> List[int]:
    """Get all telegram_ids of participants in a hackathon."""
    async with get_connection() as conn:
        rows = await conn.fetch("""
            SELECT DISTINCT tm.user_id
            FROM team_members tm
            JOIN teams t ON tm.team_id = t.id
            WHERE t.hackathon_id = $1 AND t.is_active = TRUE
        """, hackathon_id)
        return [row['user_id'] for row in rows]


# =============================================================================
# AUDIT LOG
# =============================================================================

async def log_action(
    telegram_id: int,
    action: str,
    details: dict = None
) -> None:
    """Log an action for audit purposes."""
    async with get_connection() as conn:
        await conn.execute("""
            INSERT INTO audit_log (telegram_id, action, details)
            VALUES ($1, $2, $3)
        """, telegram_id, action, details or {})


# =============================================================================
# STATISTICS
# =============================================================================

async def get_stats() -> Dict[str, Any]:
    """Get overall statistics."""
    async with get_connection() as conn:
        stats = await conn.fetchrow("""
            SELECT 
                (SELECT COUNT(*) FROM users WHERE is_active = TRUE) as total_users,
                (SELECT COUNT(*) FROM teams WHERE is_active = TRUE) as total_teams,
                (SELECT COUNT(*) FROM hackathons WHERE is_active = TRUE) as active_hackathons,
                (SELECT COUNT(*) FROM submissions) as total_submissions
        """)
        return dict(stats)


async def get_hackathon_stats(hackathon_id: int) -> Dict[str, Any]:
    """Get statistics for a specific hackathon."""
    async with get_connection() as conn:
        stats = await conn.fetchrow("""
            SELECT 
                (SELECT COUNT(*) FROM teams WHERE hackathon_id = $1 AND is_active = TRUE) as team_count,
                (SELECT COUNT(DISTINCT tm.user_id) 
                 FROM team_members tm 
                 JOIN teams t ON tm.team_id = t.id 
                 WHERE t.hackathon_id = $1) as participant_count,
                (SELECT COUNT(*) 
                 FROM submissions s 
                 JOIN hackathon_stages hs ON s.stage_id = hs.id 
                 WHERE hs.hackathon_id = $1) as submission_count
        """, hackathon_id)
        return dict(stats)
