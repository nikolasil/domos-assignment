from pydantic import BaseModel
from typing import List, Optional


class LLMResponse(BaseModel):
    reply: str
    intent: str
    action_items: Optional[List[dict]] = None
