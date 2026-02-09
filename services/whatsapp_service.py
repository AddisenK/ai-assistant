import os
import re
import logging
from twilio.rest import Client

logger = logging.getLogger(__name__)

class WhatsAppService:
    """WhatsApp service using Twilio"""
    
    def __init__(self, ai_service, email_service, calendar_service, reminder_service):
        self.ai_service = ai_service
        self.email_service = email_service
        self.calendar_service = calendar_service
        self.reminder_service = reminder_service
        
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials not configured")
    
    async def handle_message(self, data: dict):
        """Handle incoming WhatsApp messages"""
        try:
            # Parse Twilio webhook
            from_number = data.get('From', '')
            message_body = data.get('Body', '')
            
            # Process message
            response = await self._process_whatsapp_message(message_body)
            
            # Send response
            if self.client:
                self.client.messages.create(
                    body=response,
                    from_=self.whatsapp_number,
                    to=from_number
                )
        except Exception as e:
            logger.error(f"WhatsApp error: {e}")
    
    async def _process_whatsapp_message(self, message: str) -> str:
        """Process WhatsApp message and determine response"""
        message_lower = message.lower()
        
        # Check for reminders
        if "remind" in message_lower:
            return self._handle_remind(message)
        
        # Check for emails
        elif "email" in message_lower:
            emails = self.email_service.get_recent_emails(3)
            return "Your emails:\n" + "\n".join(emails[:3]) if emails else "No emails found"
        
        # Check for calendar
        elif "calendar" in message_lower or "schedule" in message_lower:
            events = self.calendar_service.get_upcoming_events(7)
            return "Your upcoming events:\n" + "\n".join(events[:3]) if events else "No events found"
        
        # Default: ask AI
        else:
            response = await self.ai_service.ask(message)
            return response[:1000]  # WhatsApp message limit
    
    def _handle_remind(self, message: str) -> str:
        """Handle reminder requests from WhatsApp"""
        # Parse reminder: "Remind me in 30m to do something"
        time_match = re.search(r'(\d+)\s*(m|h|d)', message)
        if time_match:
            self.reminder_service.schedule_reminder(
                f"{time_match.group(1)}{time_match.group(2)}",
                message,
                "whatsapp"
            )
            return f"Reminder set for {time_match.group(1)}{time_match.group(2)}"
        return "Couldn't parse reminder time. Use format: 'remind me in 30m to...'"
    
    def send_whatsapp_message(self, to_number: str, message: str) -> bool:
        """Send a WhatsApp message"""
        try:
            if not self.client:
                return False
            
            self.client.messages.create(
                body=message,
                from_=self.whatsapp_number,
                to=to_number
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
            return False
