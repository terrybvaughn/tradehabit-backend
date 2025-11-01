"""
MentorDataService - Provides data access for Mentor blueprint endpoints.

Phase 1: Fixture-only mode - reads from JSON files in data/static/
Phase 2: Live mode - computes analytics from trade_objs and order_df
"""

import os
import json
import statistics
from typing import Any, Dict, Tuple, List, Optional


class MentorDataService:
    """
    Data service for Mentor blueprint endpoints.

    Supports two modes:
    - fixtures: Reads pre-generated JSON files from data/static/
    - api: Computes analytics in real-time from app.trade_objs and app.order_df
    """

    def __init__(self, mode: str = "fixtures", fixtures_path: str = None, trade_objs_ref=None, order_df_ref=None):
        """
        Initialize the data service.

        Args:
            mode: "fixtures" (default) or "api"
            fixtures_path: Path to fixture directory. Defaults to data/static/
            trade_objs_ref: Callable that returns trade_objs list (for api mode)
            order_df_ref: Callable that returns order_df (for api mode)
        """
        self.mode = mode
        self._trade_objs_ref = trade_objs_ref
        self._order_df_ref = order_df_ref
        
        if fixtures_path is None:
            # Default to data/static relative to project root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            fixtures_path = os.path.join(base_dir, "data", "static")

        self.fixtures_path = fixtures_path
        self.cache: Dict[str, Any] = {}

    def _get_trade_objs(self) -> List[Any]:
        """
        Access global trade_objs from app.py.
        
        Returns:
            List of Trade objects
        """
        if self._trade_objs_ref:
            return self._trade_objs_ref()
        return []

    def _get_order_df(self) -> Optional[Any]:
        """
        Access global order_df from app.py.
        
        Returns:
            Pandas DataFrame or None
        """
        if self._order_df_ref:
            return self._order_df_ref()
        return None

    def load_json(self, filename: str) -> Tuple[Dict[str, Any], int]:
        """
        Load a JSON fixture file with caching.

        Args:
            filename: Name of the JSON file (e.g., "summary.json")

        Returns:
            Tuple of (data_dict, status_code)
        """
        # Check cache first
        if filename in self.cache:
            return self.cache[filename], 200

        path = os.path.join(self.fixtures_path, filename)
        if not os.path.exists(path):
            return {"status": "ERROR", "message": f"{filename} not found"}, 404

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.cache[filename] = data
            return data, 200
        except json.JSONDecodeError:
            return {"status": "ERROR", "message": f"Invalid JSON format in {filename}"}, 400
        except Exception as e:
            return {"status": "ERROR", "message": f"Unexpected error: {str(e)}"}, 500

    def get_summary(self) -> Tuple[Dict[str, Any], int]:
        """
        Get portfolio summary data.

        Returns:
            Tuple of (summary_dict, status_code)
        """
        if self.mode == "api":
            return self._compute_api_summary()
        return self.load_json("summary.json")

    def _compute_api_summary(self) -> Tuple[Dict[str, Any], int]:
        """
        Compute summary from api trade_objs (matches /api/summary logic).
        
        Returns:
            Tuple of (summary_dict, status_code)
        """
        trade_objs = self._get_trade_objs()
        
        if not trade_objs:
            return {
                "status": "ERROR",
                "message": "No trades have been analyzed yet"
            }, 400
        
        total_trades = len(trade_objs)
        
        # 1) Mistake tallies
        mistake_counts: Dict[str, int] = {}
        for t in trade_objs:
            for m in t.mistakes:
                mistake_counts[m] = mistake_counts.get(m, 0) + 1
        total_mistakes = sum(mistake_counts.values())
        flagged_trades = sum(1 for t in trade_objs if t.mistakes)
        
        # 2) Success metrics
        clean_trade_rate = round((total_trades - flagged_trades) / total_trades, 2)
        
        # Streaks (import from analytics)
        from analytics.goal_tracker import get_clean_streak_stats
        current_streak, best_streak = get_clean_streak_stats(trade_objs)
        
        # 3) Payoff & win-rate stats
        wins = [t.pnl for t in trade_objs if t.pnl and t.pnl > 0]
        losses = [abs(t.pnl) for t in trade_objs if t.pnl and t.pnl < 0]
        win_count = len(wins)
        loss_count = len(losses)
        
        win_rate = round(len(wins) / total_trades, 2) if total_trades else 0.0
        avg_win = round(sum(wins) / len(wins), 2) if wins else 0.0
        avg_loss = round(sum(losses) / len(losses), 2) if losses else 0.0
        payoff_ratio = round(avg_win / avg_loss, 2) if avg_loss else None
        required_wr_raw = 1 / (1 + (payoff_ratio or 0)) if payoff_ratio else None
        required_wr_adj = round(required_wr_raw * 1.01, 2) if required_wr_raw else None
        
        # 4) Headline diagnostic
        from insights.summary_insight import generate_summary_insight
        
        # Build stats dict for summary insight
        summary_stats = {
            "total_trades": total_trades,
            "mistake_counts": mistake_counts,
            "trades_with_mistakes": flagged_trades,
            "clean_trades": total_trades - flagged_trades,
            "required_wr": required_wr_adj,
            "win_rate": win_rate,
            "risk_sizing_stats": {"is_consistent": True}  # Not calculated in live mode yet
        }
        summary_insight = generate_summary_insight(summary_stats)
        summary_text = summary_insight.get("diagnostic", "")
        
        # 5) Return same structure as /api/summary
        return {
            "total_trades": total_trades,
            "win_count": win_count,
            "loss_count": loss_count,
            "total_mistakes": total_mistakes,
            "flagged_trades": flagged_trades,
            "clean_trade_rate": clean_trade_rate,
            "streak_current": current_streak,
            "streak_record": best_streak,
            "mistake_counts": mistake_counts,
            "win_rate": win_rate,
            "average_win": avg_win,
            "average_loss": avg_loss,
            "payoff_ratio": payoff_ratio,
            "required_wr_adj": required_wr_adj,
            "diagnostic_text": summary_text,
        }, 200

    def get_trades(self) -> Tuple[Dict[str, Any], int]:
        """
        Get trades data.

        Returns:
            Tuple of (trades_dict, status_code)
        """
        if self.mode == "api":
            return self._compute_api_trades()
        return self.load_json("trades.json")

    def _compute_api_trades(self) -> Tuple[Dict[str, Any], int]:
        """
        Convert trade_objs to fixture-like structure via API (matches /api/trades logic).
        
        Returns:
            Tuple of (trades_dict, status_code)
        """
        trade_objs = self._get_trade_objs()
        
        if not trade_objs:
            return {
                "status": "ERROR",
                "message": "No trades have been analyzed yet"
            }, 400
        
        # Convert to dict format (Trade.to_dict() handles camelCase)
        trades_list = [t.to_dict() for t in trade_objs]
        
        # Compute date range
        if trades_list:
            entry_times = [t["entryTime"] for t in trades_list if t.get("entryTime")]
            exit_times = [t["exitTime"] for t in trades_list if t.get("exitTime")]
            start = min(entry_times) if entry_times else None
            end = max(exit_times) if exit_times else None
        else:
            start = end = None
        
        return {
            "trades": trades_list,
            "date_range": {
                "start": start,
                "end": end
            }
        }, 200

    def get_losses(self) -> Tuple[Dict[str, Any], int]:
        """
        Get losses data.

        Returns:
            Tuple of (losses_dict, status_code)
        """
        if self.mode == "api":
            return self._compute_api_losses()
        return self.load_json("losses.json")

    def _compute_api_losses(self, sigma: float = 1.0, symbol: Optional[str] = None) -> Tuple[Dict[str, Any], int]:
        """
        Compute losses from api trade_objs (matches /api/losses logic).
        
        Args:
            sigma: Sigma multiplier for outsized loss threshold
            symbol: Optional symbol filter
        
        Returns:
            Tuple of (losses_dict, status_code)
        """
        trade_objs = self._get_trade_objs()
        
        if not trade_objs:
            return {
                "status": "ERROR",
                "message": "No trades have been analyzed yet"
            }, 400
        
        # 1) Filter to actual losing trades
        filtered = [
            t for t in trade_objs
            if t.pnl < 0 and (symbol is None or t.symbol == symbol)
        ]
        
        # 2) Compute stats
        losses = [t.points_lost for t in filtered]
        mean_pts = statistics.mean(losses) if losses else 0.0
        std_pts = statistics.pstdev(losses) if len(losses) > 1 else 0.0
        threshold = mean_pts + sigma * std_pts
        
        # 3) Identify outsized losses
        outsized = [t for t in filtered if t.points_lost > threshold]
        
        # 4) Build the series
        loss_list = []
        for idx, t in enumerate(filtered, start=1):
            loss_list.append({
                "lossIndex": idx,
                "tradeId": t.id,
                "pointsLost": t.points_lost,
                "hasMistake": t.points_lost > threshold,
                "side": t.side,
                "exitQty": t.exit_qty,
                "symbol": t.symbol,
                "entryTime": t.entry_time.isoformat() if t.entry_time else None,
                "exitOrderId": t.exit_order_id,
            })
        
        # 5) Diagnostic - Calculate full stats and generate insight
        from analytics.outsized_loss_analyzer import calculate_outsized_loss_stats
        from insights.outsized_loss_insight import generate_outsized_loss_insight
        
        stats = calculate_outsized_loss_stats(trade_objs, sigma)
        insight = generate_outsized_loss_insight(stats)
        
        # 6) Return same structure as /api/losses
        return {
            "losses": loss_list,
            "meanPointsLost": round(mean_pts, 2),
            "stdDevPointsLost": round(std_pts, 2),
            "thresholdPointsLost": round(threshold, 2),
            "sigmaUsed": sigma,
            "symbolFiltered": symbol,
            "diagnostic": insight.get('diagnostic', ''),
            "count": stats.get('outsized_loss_count', 0),
            "percentage": stats.get('outsized_percent', 0.0),
            "excessLossPoints": stats.get('excess_loss_points', 0.0)
        }, 200

    def get_endpoint(self, endpoint_name: str) -> Tuple[Dict[str, Any], int]:
        """
        Get data for a specific analytics endpoint.

        Args:
            endpoint_name: Name of endpoint (e.g., "revenge", "excessive-risk")

        Returns:
            Tuple of (data_dict, status_code)
        """
        if self.mode == "api":
            return self._compute_api_endpoint(endpoint_name)
        filename = f"{endpoint_name}.json"
        return self.load_json(filename)

    def _compute_api_endpoint(self, endpoint_name: str) -> Tuple[Dict[str, Any], int]:
        """
        Compute analytics endpoint data from api trade_objs.
        
        Args:
            endpoint_name: Name of endpoint (revenge, excessive-risk, etc.)
        
        Returns:
            Tuple of (data_dict, status_code)
        """
        trade_objs = self._get_trade_objs()
        order_df = self._get_order_df()
        
        if not trade_objs:
            return {
                "status": "ERROR",
                "message": "No trades have been analyzed yet"
            }, 400
        
        # Map endpoint names to their computation functions
        try:
            if endpoint_name == "revenge":
                return self._compute_revenge_endpoint(trade_objs)
            elif endpoint_name == "excessive-risk":
                return self._compute_excessive_risk_endpoint(trade_objs)
            elif endpoint_name == "risk-sizing":
                return self._compute_risk_sizing_endpoint(trade_objs)
            elif endpoint_name == "stop-loss":
                return self._compute_stop_loss_endpoint(trade_objs)
            elif endpoint_name == "winrate-payoff":
                return self._compute_winrate_payoff_endpoint(trade_objs)
            elif endpoint_name == "insights":
                if order_df is None:
                    return {
                        "status": "ERROR",
                        "message": "Order data is missing or has not been processed yet"
                    }, 400
                return self._compute_insights_endpoint(trade_objs, order_df)
            elif endpoint_name == "trades":
                return self._compute_api_trades()
            else:
                return {
                    "status": "ERROR",
                    "message": f"Unknown endpoint: {endpoint_name}"
                }, 400
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Error computing {endpoint_name}: {str(e)}"
            }, 500

    def _compute_revenge_endpoint(self, trade_objs: List[Any], k: float = 1.0) -> Tuple[Dict[str, Any], int]:
        """Compute revenge trading analysis."""
        from copy import deepcopy
        from analytics.revenge_analyzer import analyze_trades_for_revenge, calculate_revenge_stats
        from insights.revenge_insight import generate_revenge_insight
        
        # Tag revenge trades
        trades = deepcopy(trade_objs)
        analyze_trades_for_revenge(trades, k)
        
        # Calculate statistics
        stats = calculate_revenge_stats(trades)
        
        # Generate insight narrative
        insight = generate_revenge_insight(stats)
        
        return {
            "revenge_multiplier": k,
            "total_revenge_trades": stats["revenge_count"],
            "revenge_win_rate": stats["win_rate_revenge"],
            "average_win_revenge": stats["avg_win_revenge"],
            "average_loss_revenge": stats["avg_loss_revenge"],
            "payoff_ratio_revenge": stats["payoff_ratio_revenge"],
            "net_pnl_revenge": stats["net_pnl_revenge"],
            "net_pnl_per_trade_revenge": stats["net_pnl_per_revenge"],
            "overall_win_rate": stats["win_rate_overall"],
            "overall_payoff_ratio": stats["payoff_ratio_overall"],
            "diagnostic": insight["diagnostic"]
        }, 200

    def _compute_excessive_risk_endpoint(self, trade_objs: List[Any], sigma: float = 1.5) -> Tuple[Dict[str, Any], int]:
        """Compute excessive risk analysis."""
        from analytics.excessive_risk_analyzer import calculate_excessive_risk_stats
        from insights.excessive_risk_insight import generate_excessive_risk_insight
        
        # Calculate statistics
        stats = calculate_excessive_risk_stats(trade_objs, sigma)
        
        # Generate insight narrative
        insight = generate_excessive_risk_insight(stats)
        
        return {
            "totalTradesWithStops": stats.get("total_trades_with_risk", 0),
            "meanRiskPoints": stats.get("mean_risk", 0.0),
            "stdDevRiskPoints": stats.get("std_dev_risk", 0.0),
            "excessiveRiskThreshold": stats.get("threshold", 0.0),
            "excessiveRiskCount": stats.get("excessive_risk_count", 0),
            "excessiveRiskPercent": stats.get("excessive_percent", 0.0),
            "averageRiskAmongExcessive": stats.get("avg_excessive_risk", 0.0),
            "sigmaUsed": sigma,
            "diagnostic": insight.get("diagnostic", "")
        }, 200

    def _compute_risk_sizing_endpoint(self, trade_objs: List[Any], vr: float = 0.35) -> Tuple[Dict[str, Any], int]:
        """Compute risk sizing consistency analysis."""
        from analytics.risk_sizing_analyzer import calculate_risk_sizing_consistency_stats
        from insights.risk_sizing_insight import generate_risk_sizing_insight
        
        # Calculate stats once
        stats = calculate_risk_sizing_consistency_stats(trade_objs, vr)
        
        # Generate insight from stats
        insight = generate_risk_sizing_insight(stats)
        
        return {
            "count": stats["trades_with_risk_data"],
            "minRiskPoints": stats["min_risk"],
            "maxRiskPoints": stats["max_risk"],
            "meanRiskPoints": stats["mean_risk"],
            "stdDevRiskPoints": stats["std_dev_risk"],
            "variationRatio": stats["risk_variation_ratio"],
            "variationThreshold": vr,
            "diagnostic": insight["diagnostic"]
        }, 200

    def _compute_stop_loss_endpoint(self, trade_objs: List[Any]) -> Tuple[Dict[str, Any], int]:
        """Compute stop loss behavior analysis."""
        from analytics.stop_loss_analyzer import calculate_stop_loss_stats
        from insights.stop_loss_insight import generate_stop_loss_insight
        
        # Calculate statistics
        stats = calculate_stop_loss_stats(trade_objs)
        
        # Generate insight narrative
        insight = generate_stop_loss_insight(stats)
        
        return {
            "totalTrades": stats["total_trades"],
            "tradesWithStops": stats["trades_with_stops"],
            "tradesWithoutStops": stats["trades_without_stops"],
            "averageLossWithStop": stats["avg_loss_with_stops"],
            "averageLossWithoutStop": stats["avg_loss_without_stops"],
            "maxLossWithoutStop": stats["max_loss_without_stops"],
            "diagnostic": insight["diagnostic"]
        }, 200

    def _compute_winrate_payoff_endpoint(self, trade_objs: List[Any]) -> Tuple[Dict[str, Any], int]:
        """Compute win rate and payoff ratio analysis."""
        from analytics.breakeven_analyzer import calculate_breakeven_stats
        from insights.breakeven_insight import generate_breakeven_insight
        
        # Calculate stats using the refactored function
        stats = calculate_breakeven_stats(trade_objs)
        
        # Generate insight from stats
        insight = generate_breakeven_insight(stats)
        
        return {
            "winRate": stats["win_rate"],
            "averageWin": stats["avg_win"],
            "averageLoss": stats["avg_loss"],
            "payoffRatio": stats["payoff_ratio"],
            "expectancy": stats["expectancy"],
            "breakevenWinRate": stats["breakeven_win_rate"],
            "delta": stats["delta"],
            "performanceCategory": stats["performance_category"],
            "diagnostic": insight["diagnostic"]
        }, 200

    def _compute_insights_endpoint(self, trade_objs: List[Any], order_df: Any) -> Tuple[Dict[str, Any], int]:
        """Compute full insights report."""
        from insights.insights_report import generate_insights_report

        insights = generate_insights_report(trade_objs, order_df)

        # Convert new insights format to old API format for backward compatibility
        insights_with_priority = []
        for idx, insight in enumerate(insights):
            insights_with_priority.append({
                "title": insight["title"],
                "diagnostic": insight["diagnostic"],
                "priority": idx
            })

        return insights_with_priority, 200

    def list_available_endpoints(self) -> list:
        """
        List all available JSON fixtures.

        Returns:
            List of available endpoint keys (without .json extension)
        """
        if not os.path.isdir(self.fixtures_path):
            return []

        endpoints = []
        for fname in os.listdir(self.fixtures_path):
            if fname.lower().endswith(".json"):
                stem = os.path.splitext(fname)[0]
                endpoints.append(stem)

        return sorted(endpoints)

    def refresh_cache(self) -> None:
        """Clear the in-memory cache."""
        self.cache.clear()
