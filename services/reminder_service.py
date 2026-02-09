import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ReminderService:
    """Reminder service - schedules and sends reminders"""
    
    def __init__(self):
        self.reminders = {}  # In-memory storage; use database in production
    
    def schedule_reminder(self, time_str: str, message: str, platform: str, user_id: Optional[str] = None):
        """Schedule a reminder"""
        try:
            # Parse time string (e.g., '30m', '2h', '1d')
            import re
            match = re.search(r'(\d+)\s*(m|h|d)', time_str.lower())
            if not match:
                return False
            
            value = int(match.group(1))
            unit = match.group(2)
            
            # Calculate reminder time
            if unit == 'm':
                remind_at = datetime.now() + timedelta(minutes=value)
            elif unit == 'h':
                remind_at = datetime.now() + timedelta(hours=value)
            else:  # days
                remind_at = datetime.now() + timedelta(days=value)
            
            reminder_id = f"{platform}_{user_id}_{remind_at.timestamp()}"
            self.reminders[reminder_id] = {
                "message": message,
                "platform": platform,
                "user_id": user_id,
                "remind_at": remind_at.isoformat()
            }
            
            logger.info(f"Reminder scheduled: {reminder_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to schedule reminder: {e}")
            return False
    
    async def check_and_send_reminders(self):
        """Check if any reminders are due and send them"""
        now = datetime.now()
        due_reminders = []
        
        for reminder_id, reminder in list(self.reminders.items()):
            remind_time = datetime.fromisoformat(reminder["remind_at"])
            if remind_time <= now:
                due_reminders.append((reminder_id, reminder))
        
        for reminder_id, reminder in due_reminders:
            # Send reminder to appropriate platform
            logger.info(f"Sending reminder: {reminder_id}")
            del self.reminders[reminder_id]
