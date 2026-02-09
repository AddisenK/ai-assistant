import os
import httpx
import json
from typing import Optional

class AIService:
    """Handles AI responses using ChatGPT web (via Mac bridge) or API"""
    
    def __init__(self):
        self.mode = os.getenv("AI_MODE", "bridge")  # 'bridge' or 'api'
        self.mac_bridge_url = os.getenv("MAC_BRIDGE_URL")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
    async def ask(self, question: str, context: Optional[str] = None) -> str:
        """Get AI response to a question"""
        try:
            if self.mode == "bridge":
                return await self._ask_via_mac_bridge(question, context)
            else:
                return await self._ask_via_openai(question, context)
        except Exception as e:
            return f"Error getting AI response: {str(e)}"
    
    async def _ask_via_mac_bridge(self, question: str, context: Optional[str] = None) -> str:
        """Use Mac bridge to talk to ChatGPT web"""
        if not self.mac_bridge_url:
            return "Mac bridge URL not configured"
        
        payload = {
            "message": question,
            "context": context or ""
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mac_bridge_url}/chat",
                    json=payload,
                    timeout=30.0
                )
                data = response.json()
                return data.get("response", "No response received")
        except Exception as e:
            return f"Failed to connect to Mac bridge: {str(e)}"
    
    async def _ask_via_openai(self, question: str, context: Optional[str] = None) -> str:
        """Use OpenAI API (requires API key)"""
        if not self.openai_api_key:
            return "OpenAI API key not configured"
        
        # Placeholder - implement based on your needs
        return "OpenAI integration not yet implemented"
    
    def is_available(self) -> bool:
        """Check if AI service is properly configured"""
        if self.mode == "bridge":
            return bool(self.mac_bridge_url)
        return bool(self.openai_api_key)
