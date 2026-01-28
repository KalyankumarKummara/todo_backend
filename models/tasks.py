from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Task(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = Field(default="pending", pattern="^(pending|in progress|completed)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    due_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    reminder_time: Optional[datetime] = None
    reminder_type: str = Field(default="once", pattern="^(once|daily|weekly|monthly)$")
