"""
Export module for Hackathon Bot
Generate CSV exports for admin use
"""

import csv
import io
from datetime import datetime
from typing import List, Dict, Any


async def export_users_csv(db) -> io.BytesIO:
    """
    Export all users to CSV format.
    
    Returns:
        BytesIO object containing CSV data
    """
    users = await db.get_all_users(active_only=False)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header row
    writer.writerow([
        'ID',
        'Telegram ID',
        'Username',
        'First Name',
        'Last Name',
        'Phone',
        'Birth Date',
        'Gender',
        'Location',
        'PINFL',
        'Language',
        'Is Active',
        'Is Admin',
        'Created At',
        'Updated At'
    ])
    
    # Data rows
    for user in users:
        writer.writerow([
            user.get('id'),
            user.get('telegram_id'),
            user.get('username', ''),
            user.get('first_name', ''),
            user.get('last_name', ''),
            user.get('phone', ''),
            user.get('birth_date', ''),
            user.get('gender', ''),
            user.get('location', ''),
            user.get('pinfl', ''),
            user.get('language', 'uz'),
            'Yes' if user.get('is_active') else 'No',
            'Yes' if user.get('is_admin') else 'No',
            user.get('created_at', ''),
            user.get('updated_at', '')
        ])
    
    # Convert to bytes
    output.seek(0)
    return io.BytesIO(output.getvalue().encode('utf-8-sig'))


async def export_teams_csv(db, hackathon_id: int = None) -> io.BytesIO:
    """Export teams to CSV format."""
    from database import get_connection
    
    async with get_connection() as conn:
        if hackathon_id:
            teams = await conn.fetch("""
                SELECT t.*, h.name as hackathon_name,
                       COUNT(tm.id) as member_count
                FROM teams t
                LEFT JOIN hackathons h ON t.hackathon_id = h.id
                LEFT JOIN team_members tm ON t.id = tm.team_id
                WHERE t.hackathon_id = $1
                GROUP BY t.id, h.name
                ORDER BY t.created_at DESC
            """, hackathon_id)
        else:
            teams = await conn.fetch("""
                SELECT t.*, h.name as hackathon_name,
                       COUNT(tm.id) as member_count
                FROM teams t
                LEFT JOIN hackathons h ON t.hackathon_id = h.id
                LEFT JOIN team_members tm ON t.id = tm.team_id
                GROUP BY t.id, h.name
                ORDER BY t.created_at DESC
            """)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'ID', 'Name', 'Code', 'Hackathon', 'Owner Telegram ID',
        'Field', 'Portfolio Link', 'Member Count', 'Is Active', 'Created At'
    ])
    
    for team in teams:
        writer.writerow([
            team['id'],
            team['name'],
            team['code'],
            team.get('hackathon_name', ''),
            team['owner_id'],
            team.get('field', ''),
            team.get('portfolio_link', ''),
            team.get('member_count', 0),
            'Yes' if team.get('is_active') else 'No',
            team.get('created_at', '')
        ])
    
    output.seek(0)
    return io.BytesIO(output.getvalue().encode('utf-8-sig'))


async def export_team_members_csv(db, hackathon_id: int = None) -> io.BytesIO:
    """Export team members to CSV format."""
    from database import get_connection
    
    async with get_connection() as conn:
        if hackathon_id:
            members = await conn.fetch("""
                SELECT 
                    tm.*, t.name as team_name, t.code as team_code,
                    h.name as hackathon_name,
                    u.username, u.first_name, u.last_name, u.phone, u.location
                FROM team_members tm
                JOIN teams t ON tm.team_id = t.id
                JOIN hackathons h ON t.hackathon_id = h.id
                JOIN users u ON tm.user_id = u.telegram_id
                WHERE t.hackathon_id = $1
                ORDER BY t.name, tm.is_team_lead DESC
            """, hackathon_id)
        else:
            members = await conn.fetch("""
                SELECT 
                    tm.*, t.name as team_name, t.code as team_code,
                    h.name as hackathon_name,
                    u.username, u.first_name, u.last_name, u.phone, u.location
                FROM team_members tm
                JOIN teams t ON tm.team_id = t.id
                JOIN hackathons h ON t.hackathon_id = h.id
                JOIN users u ON tm.user_id = u.telegram_id
                ORDER BY h.name, t.name, tm.is_team_lead DESC
            """)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'Hackathon', 'Team Name', 'Team Code', 'Telegram ID', 'Username',
        'First Name', 'Last Name', 'Phone', 'Location', 'Role', 'Is Team Lead', 'Joined At'
    ])
    
    for member in members:
        writer.writerow([
            member.get('hackathon_name', ''),
            member['team_name'],
            member['team_code'],
            member['user_id'],
            member.get('username', ''),
            member.get('first_name', ''),
            member.get('last_name', ''),
            member.get('phone', ''),
            member.get('location', ''),
            member.get('role', ''),
            'Yes' if member.get('is_team_lead') else 'No',
            member.get('joined_at', '')
        ])
    
    output.seek(0)
    return io.BytesIO(output.getvalue().encode('utf-8-sig'))


async def export_submissions_csv(db, hackathon_id: int = None, stage_id: int = None) -> io.BytesIO:
    """Export submissions to CSV format."""
    from database import get_connection
    
    async with get_connection() as conn:
        query = """
            SELECT 
                s.*, t.name as team_name, t.code as team_code,
                hs.name as stage_name, hs.stage_number,
                h.name as hackathon_name
            FROM submissions s
            JOIN teams t ON s.team_id = t.id
            JOIN hackathon_stages hs ON s.stage_id = hs.id
            JOIN hackathons h ON t.hackathon_id = h.id
        """
        
        conditions = []
        params = []
        
        if hackathon_id:
            conditions.append(f"t.hackathon_id = ${len(params) + 1}")
            params.append(hackathon_id)
        
        if stage_id:
            conditions.append(f"s.stage_id = ${len(params) + 1}")
            params.append(stage_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY h.name, hs.stage_number, s.submitted_at DESC"
        
        submissions = await conn.fetch(query, *params)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'ID', 'Hackathon', 'Stage', 'Team Name', 'Team Code',
        'Submission Type', 'File Name', 'Content / File ID', 'MIME Type',
        'Submitted At', 'Score', 'Feedback', 'Reviewed At'
    ])
    
    for sub in submissions:
        writer.writerow([
            sub['id'],
            sub.get('hackathon_name', ''),
            f"Stage {sub.get('stage_number', '')} - {sub.get('stage_name', '')}",
            sub['team_name'],
            sub['team_code'],
            sub.get('submission_type', 'url'),
            sub.get('file_name', ''),
            sub.get('content') if sub.get('submission_type') == 'url' else (sub.get('file_id') or ''),
            sub.get('mime_type', ''),
            sub.get('submitted_at', ''),
            sub.get('score', ''),
            sub.get('feedback', ''),
            sub.get('reviewed_at', '')
        ])
    
    output.seek(0)
    return io.BytesIO(output.getvalue().encode('utf-8-sig'))


def get_export_filename(export_type: str, hackathon_name: str = None) -> str:
    """Generate filename for export."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if hackathon_name:
        clean_name = ''.join(c for c in hackathon_name if c.isalnum() or c in ' -_').strip()
        clean_name = clean_name.replace(' ', '_')[:30]
        return f"{export_type}_{clean_name}_{timestamp}.csv"
    return f"{export_type}_{timestamp}.csv"
