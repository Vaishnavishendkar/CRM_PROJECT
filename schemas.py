from datetime import datetime

from pydantic import BaseModel, field_validator
from typing import Optional



class Register(BaseModel):
    username: str
    email: str
    password: str
    role: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class Login(BaseModel):
    email: str
    password: str

        # ==================== TICKET ====================
class Ticket(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    assigned_to: Optional[int] = None
    category_id: Optional[int] = None
    priority: str = "medium"
    status: str = "open"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str):
        allowed = {'low', 'medium', 'high', 'urgent'}
        if v not in allowed:
            raise ValueError(f'priority must be one of {allowed}')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str):
        allowed = {'open', 'in_progress', 'resolved', 'closed'}
        if v not in allowed:
            raise ValueError(f'status must be one of {allowed}')
        return v
    
# ==================== TICKET STATUS HISTORY ====================
class TicketStatusHistory(BaseModel):
    id: Optional[int] = None
    ticket_id: int
    old_status: Optional[str] = None
    new_status: str
    changed_by_id: int
    changed_at: Optional[datetime] = None
    note: Optional[str] = None

    class Config:
        from_attributes = True

# ==================== TICKET COMMENT ====================
class TicketComment(BaseModel):
    id: Optional[int] = None
    ticket_id: int
    author_id: int
    body: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
