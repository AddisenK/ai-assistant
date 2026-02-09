import os
import logging
from typing import Optional
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

class DiscordService:
    """Discord bot service"""
    
    def __init__(self, ai_service, email_service, calendar_service, reminder_service):
        self.ai_service = ai_service
        self.email_service = email_service
        self.calendar_service = calendar_service
        self.reminder_service = reminder_service
        self.token = os.getenv("DISCORD_TOKEN")
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.bot = commands.Bot(command_prefix="!", intents=self.intents)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup event handlers"""
        @self.bot.event
        async def on_ready():
            logger.info(f"Discord bot logged in as {self.bot.user}")
        
        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return
            await self._handle_message(message)
        
        @self.bot.command(name="ask")
        async def ask_command(ctx, *, question):
            async with ctx.typing():
                response = await self.ai_service.ask(question)
                await ctx.send(response[:2000])  # Discord message limit
        
        @self.bot.command(name="emails")
        async def emails_command(ctx, count: int = 5):
            async with ctx.typing():
                emails = self.email_service.get_recent_emails(count)
                response = "\n".join([f"- {e}" for e in emails[:5]])
                await ctx.send(response or "No emails found")
        
        @self.bot.command(name="calendar")
        async def calendar_command(ctx, days: int = 7):
            async with ctx.typing():
                events = self.calendar_service.get_upcoming_events(days)
                response = "\n".join([f"- {e}" for e in events[:5]])
                await ctx.send(response or "No events found")
        
        @self.bot.command(name="remind")
        async def remind_command(ctx, time_str: str, *, message: str):
            self.reminder_service.schedule_reminder(time_str, message, "discord", ctx.author.id)
            await ctx.send(f"Reminder set for {time_str}")
    
    async def _handle_message(self, message):
        """Handle direct messages"""
        if isinstance(message.channel, discord.DMChannel):
            response = await self.ai_service.ask(message.content)
            await message.reply(response[:2000])
        else:
            await self.bot.process_commands(message)
    
    async def handle_interaction(self, data: dict):
        # Handle Discord's PING verification
                if data.get("type") == 1:
                                return {"type": 1}  # PONG response
                            
                # Handle other interaction types here
            return {"type": 4, "data": {"content": "Interaction received"}}
    
    def is_running(self) -> bool:
        """Check if bot is running"""
        return self.bot and self.bot.latency >= 0 if hasattr(self.bot, 'latency') else False
    
    def start(self):
        """Start the Discord bot"""
        if self.token:
            self.bot.run(self.token)
        else:
            logger.error("Discord token not configured")
