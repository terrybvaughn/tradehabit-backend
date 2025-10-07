"""
MentorDataService - Provides data access for Mentor blueprint endpoints.

Phase 1: Fixture-only mode - reads from JSON files in data/static/
Phase 2: Will support live mode using analytics and trade_objs
"""

import os
import json
from typing import Any, Dict, Tuple


class MentorDataService:
    """
    Data service for Mentor blueprint endpoints.

    Phase 1: Reads fixture data from data/static/ directory
    Phase 2: Will support live computation from trade_objs and analytics
    """

    def __init__(self, fixtures_path: str = None):
        """
        Initialize the data service.

        Args:
            fixtures_path: Path to fixture directory. Defaults to data/static/
        """
        if fixtures_path is None:
            # Default to data/static relative to project root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            fixtures_path = os.path.join(base_dir, "data", "static")

        self.fixtures_path = fixtures_path
        self.cache: Dict[str, Any] = {}

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
        return self.load_json("summary.json")

    def get_trades(self) -> Tuple[Dict[str, Any], int]:
        """
        Get trades data.

        Returns:
            Tuple of (trades_dict, status_code)
        """
        return self.load_json("trades.json")

    def get_losses(self) -> Tuple[Dict[str, Any], int]:
        """
        Get losses data.

        Returns:
            Tuple of (losses_dict, status_code)
        """
        return self.load_json("losses.json")

    def get_endpoint(self, endpoint_name: str) -> Tuple[Dict[str, Any], int]:
        """
        Get data for a specific analytics endpoint.

        Args:
            endpoint_name: Name of endpoint (e.g., "revenge", "excessive-risk")

        Returns:
            Tuple of (data_dict, status_code)
        """
        filename = f"{endpoint_name}.json"
        return self.load_json(filename)

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
