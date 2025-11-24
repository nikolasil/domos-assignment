from pydantic import BaseModel
from typing import List, Optional
from core.models.intent import Intent


class LLMResponse(BaseModel):
    reply: str
    intent: Intent
    action_items: Optional[List[dict]] = None
