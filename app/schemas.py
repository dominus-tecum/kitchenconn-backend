from typing import List, Optional
from pydantic import BaseModel

class MenuItem(BaseModel):
    id: int
    name: str

class OrderCreate(BaseModel):
    waiter: str
    items: List[int]

class OrderResponse(BaseModel):
    id: int
    items: List[int]
    item_names: List[str]
    waiter: str
    timestamp: str
    status: str
    confirmed_at: Optional[str] = None
    ready_at: Optional[str] = None
    served_at: Optional[str] = None

class OrderStatsResponse(BaseModel):
    total: int
    pending: int
    confirmed: int
    ready: int
    served: int
    popularItems: List[dict]