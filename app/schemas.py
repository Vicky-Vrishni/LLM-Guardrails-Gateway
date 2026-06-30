from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    user_input: str


class ChatResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    blocked_reason: Optional[str] = None
    flagged_issues: Optional[list] = None