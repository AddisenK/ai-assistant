# AI Assistant Bot

Your personal AI assistant that connects to Discord, WhatsApp, and iMessage (Mac), with access to your Gmail, Apple Calendar, and reminders. Uses ChatGPT web (via Mac bridge) so you don't need API keys.

## Features

- **Discord Bot**: Full bot with slash commands and DMs
- **WhatsApp**: Twilio integration for messaging
- **iMessage**: Mac-only automation
- **ChatGPT Web**: Uses your existing ChatGPT account via Mac bridge
- **Email**: Gmail/Outlook integration
- **Calendar**: Apple Calendar + Google Calendar
- **Reminders**: Schedule notifications to any platform

## Quick Start

### 1. Fork & Clone

```bash
git clone https://github.com/YOUR_USERNAME/ai-assistant.git
cd ai-assistant
```

### 2. Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

Or use the Vercel GitHub integration - just import your repo.

### 3. Set Environment Variables

In Vercel Dashboard → Settings → Environment Variables, add:

| Variable | Value | Required For |
|----------|-------|--------------|
| `AI_MODE` | `bridge` | Using ChatGPT web |
| `MAC_BRIDGE_URL` | Your ngrok URL | ChatGPT bridge |
| `DISCORD_TOKEN` | From Discord Dev Portal | Discord bot |
| `TWILIO_SID` | From Twilio | WhatsApp |

### 4. Set Up Mac Bridge (ChatGPT Web)

This runs **on your Mac** and connects ChatGPT web to your Vercel backend.

```bash
# On your Mac, go to mac-bridge folder
cd mac-bridge

# Run setup
chmod +x setup.sh
./setup.sh

# Create .env with your ngrok token
echo "NGROK_AUTH_TOKEN=your_token_here" > .env

# Run the bridge
python mac_bridge.py
```

Copy the ngrok URL (e.g., `https://abc123.ngrok.io`) to your Vercel `MAC_BRIDGE_URL` environment variable.

## How It Works

```
You (Discord/WhatsApp)
         │
         ▼
    ┌─────────┐
    │ Vercel  │  ← Your deployed FastAPI app
    └────┬────┘
         │ (ngrok tunnel)
         ▼
    ┌─────────┐
    │  Mac    │  ← Your local machine
    │ Browser │     opens ChatGPT.com
    └────┬────┘
         │
         ▼
    ChatGPT Web
```

## Platform Setup

### Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. New Application → Bot → Enable **"Message Content Intent"**
3. OAuth2 → URL Generator:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: Send Messages, Read Message History
4. Copy URL, add bot to your server
5. Copy Bot Token to Vercel `DISCORD_TOKEN`

### WhatsApp (Twilio)

1. Sign up at [Twilio](https://www.twilio.com)
2. Get a WhatsApp number
3. Join sandbox by texting the join code to the number
4. Configure webhook: `https://your-app.vercel.app/whatsapp/webhook`
5. Add Twilio credentials to Vercel

### Gmail

1. [Google Cloud Console](https://console.cloud.google.com) → Enable Gmail API
2. Create OAuth 2.0 credentials (Desktop app)
3. Download `credentials.json`
4. Run auth locally once (see `services/email_service.py`)

### Apple Calendar

1. Generate app-specific password at [appleid.apple.com](https://appleid.apple.com)
2. Add `APPLE_ID` and `APPLE_APP_PASSWORD` to Vercel

## Commands

### Discord

| Command | Description |
|---------|-------------|
| `!remind 30m Submit assignment` | Set a reminder |
| `!emails 5` | Show recent Gmail messages |
| `!calendar 7` | Show upcoming events |
| `!ask What is AI?` | Ask the AI anything |
| `@mention` bot | Chat in channel |
| **DM the bot** | Private conversation |

### WhatsApp

- `Remind me in 30m to call mom` - Set reminder
- `What emails do I have?` - Check Gmail
- `What's on my calendar tomorrow?` - Check schedule
- Anything else - Chat with AI

## Project Structure

```
ai-assistant/
├── main.py              # FastAPI entry point
├── requirements.txt     # Dependencies
├── vercel.json          # Vercel config
├── .env.example         # Environment template
├── bot/
│   ├── discord_bot.py   # Discord bot
│   ├── whatsapp_handler.py  # WhatsApp webhook
│   └── imessage_handler.py  # iMessage (Mac only)
├── services/
│   ├── ai_service.py    # AI routing (API vs Bridge)
│   ├── email_service.py # Gmail/Outlook
│   ├── calendar_service.py  # Calendar access
│   └── reminder_service.py  # Notifications
└── mac-bridge/          # LOCAL MAC ONLY ⬇️
    ├── mac_bridge.py    # ChatGPT browser automation
    ├── requirements.txt
    └── setup.sh
```

## Mac Bridge Details

The Mac bridge uses **Playwright** to control a browser:

1. Opens ChatGPT.com in Chromium
2. Maintains your login session
3. Creates a **new chat** for every message
4. Types your message, waits for response
5. Sends response back to Vercel via ngrok tunnel

**Requirements:**
- macOS (for Messages integration)
- Chrome/Chromium
- Python 3.9+
- Your Mac must stay on

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Mac bridge won't start | Run `playwright install chromium` |
| ngrok URL not working | Restart ngrok, update Vercel env var |
| ChatGPT not responding | Check you're logged in; browser must be visible |
| Discord bot offline | Check token; enable Message Content Intent |
| WhatsApp not working | Check webhook URL in Twilio console |

## Security

- **Never commit `.env` or credentials**
- Use app-specific passwords for Apple
- The Mac bridge uses your browser cookies
- Consider using a separate browser profile

## License

MIT
