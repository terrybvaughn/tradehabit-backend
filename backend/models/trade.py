from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

def _fmt_time(value):
    return value.isoformat() if isinstance(value, datetime) else str(value)

@dataclass
class Trade:
    id: str = field(default_factory=lambda: str(uuid4()))
    symbol: str = ""
    entry_time: datetime = None
    entry_price: float = 0.0
    entry_qty: int = 0
    exit_time: datetime = None
    exit_price: float = 0.0
    exit_qty: int = 0
    side: str = ""
    exit_order_id: Optional[int] = None
    pnl: Optional[float] = None
    mistakes: List[str] = field(default_factory=list)
    risk_points: Optional[float] = None

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side,
            "entryTime": _fmt_time(self.entry_time),
            "entryPrice": self.entry_price,
            "entryQty": self.entry_qty,
            "exitTime": _fmt_time(self.exit_time),
            "exitPrice": self.exit_price,
            "exitQty": self.exit_qty,
            "exitOrderId": self.exit_order_id,
            "pnl": self.pnl,
            "pointsLost": getattr(self, "points_lost", None),
            "riskPoints": getattr(self, "risk_points", None),
            "mistakes": self.mistakes,
        }

    @property
    def has_stop_order(self) -> bool:
        """Returns True if the trade is not flagged as missing a stop-loss."""
        return "no_stop_loss" not in self.mistakes
