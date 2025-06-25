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
        """True if the trade *did* have a protective stop-loss order.

        The stop-loss analyzer tags trades that **lack** a protective stop with
        the exact string "no stop-loss order". The old implementation used a
        snake-case variant ("no_stop_loss"), which never matched and therefore
        incorrectly reported every trade as having a stop order. This broke
        downstream summaries like the Stop-Loss insights section and overall
        mistake tallies. Fixing the string restores accurate reporting.
        """
        return "no stop-loss order" not in self.mistakes
