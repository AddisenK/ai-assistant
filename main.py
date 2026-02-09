from fastapi import FastAPI, Request
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
async def health():
    return {"status": "AI Assistant running", "version": "1.0.0"}

@app.post("/discord/interactions")
async def discord_interactions(request: Request):
    try:
        data = await request.json()
        # Handle Discord PING verification
        if data.get("type") == 1:
            return {"type": 1}  # PONG response
        # Handle other interactions
        return {"type": 4, "data": {"content": "Hello from AI Assistant! I'm now live on Vercel."}}
    except Exception as e:
        logger.error(f"Discord error: {e}")
        return {"error": str(e)}
