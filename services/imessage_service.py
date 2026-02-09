import logging
import subprocess

logger = logging.getLogger(__name__)

class iMessageService:
    """iMessage service for Mac"""
    
    def __init__(self, ai_service, email_service, calendar_service, reminder_service):
        self.ai_service = ai_service
        self.email_service = email_service
        self.calendar_service = calendar_service
        self.reminder_service = reminder_service
    
    async def handle_message(self, data: dict):
        """Handle incoming iMessage"""
        try:
            from_contact = data.get('from', '')
            message_body = data.get('body', '')
            
            response = await self.ai_service.ask(message_body)
            await self.send_imessage(from_contact, response)
        except Exception as e:
            logger.error(f"iMessage error: {e}")
    
    async def send_imessage(self, to_contact: str, message: str) -> bool:
        """Send an iMessage on Mac"""
        try:
            script = f'''
            tell application "Messages"
                send "{message}" to buddy "{to_contact}"
            end tell
            '''
            subprocess.run(
                ['osascript', '-e', script],
                check=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send iMessage: {e}")
            return False
