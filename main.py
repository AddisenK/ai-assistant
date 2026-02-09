from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import os
import logging
from dotenv import load_dotenv
from services.discord_service import DiscordService
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
discord_service = DiscordService(ai_service, email_service, calendar_service, reminder_service)
whatsapp_service = WhatsAppService(ai_service, email_service, calendar_service, reminder_service)
imessage_service = iMessageService(ai_service, email_service, calendar_service, reminder_service)

@app.get("/")
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
async def discord_interactions(request: Request):
    try:
        data = await request.json()
        return await discord_service.handle_interaction(data)
    except Exception as e:
        logger.error(f"Discord error: {e}")
        return {"error": str(e)}

# iMessage webhook
@app.post("/imessage/message")
async def imessage_webhook(request: Request):
    try:
        data = await request.json()
        await imessage_service.handle_message(data)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"iMessage error: {e}")
        return {"error": str(e)}

# Reminder endpoint
@app.post("/reminders/check")
async def check_reminders():
    try:
        await reminder_service.check_and_send_reminders()
        return {"status": "reminders checked"}
    except Exception as e:
        logger.error(f"Reminder error: {e}")
        return {"error": str(e)}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "discord": discord_service.is_running(),
        "whatsapp": "connected",
        "imessage": "ready"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
