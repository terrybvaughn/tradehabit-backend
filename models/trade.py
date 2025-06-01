from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

@dataclass
class Trade:
    # Fields without default values first
    symbol: str
    entry_time: datetime
    entry_price: float
    entry_qty: int
    exit_time: datetime
    exit_price: float
    exit_qty: int
    side: str  # 'Buy' or 'Sell'
    
    # Fields with default values last
    id: int = None
    exit_order_id: Optional[str] = None
    pnl: Optional[float] = None
    mistakes: List[str] = field(default_factory=list)
