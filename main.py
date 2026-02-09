from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import os
import logging
from dotenv import load_dotenv
# from services.discord_service import DiscordService
from services.whatsapp_service import WhatsAppService
from services.imessage_service import iMessageService
from services.ai_service import AIService
from services.email_service import EmailService
from services.calendar_service import CalendarService
from services.reminder_service import ReminderService

load_dotenv()

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
ai_service = AIService()
email_service = EmailService()
calendar_service = CalendarService()
reminder_service = ReminderService()

# Platform services
# discord_service = DiscordService(ai_service, email_service, calendar_service, reminder_service)
whatsapp_service = WhatsAppService(ai_service, email_service, calendar_service, reminder_service)
imessage_service = iMessageService(ai_service, email_service, calendar_service, reminder_service)

# @app.get("/")
async def health():
    return {"status": "AI Assistant running", "version": "1.0.0"}

# WhatsApp Webhook
@app.get("/whatsapp/webhook")
async def whatsapp_verify(request: Request):
    verify_token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    expected_token = os.getenv("TWILIO_VERIFY_TOKEN", "test_token")
    
    if verify_token == expected_token:
        return PlainTextResponse(challenge)
    return HTTPException(status_code=403)

@app.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    try:
        data = await request.json()
        await whatsapp_service.handle_message(data)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"WhatsApp error: {e}")
        return {"error": str(e)}

# Discord webhook
@app.post("/discord/interactions")

    data = await request.json()
    # Handle Discord PING verification
    if data.get("type") == 1:
                return {"type": 1}  # PONG response
            return {"type": 4, "data": {"content": "Hello from AI Assistant!"}}
    
