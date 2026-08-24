"""
core.pruner
~~~~~~~~~~~
Intelligent Multi-Factor Decay & Pruning for the Living Memory Core.
Calculates retention scores based on emotional weight, connection density,
access reinforcement, and temporal recency.
"""

from datetime import datetime, timezone
from typing import List, Dict, Optional, Any, Tuple


class MemoryPruner:
    """Intelligently cleans up and decays low-resonance memories."""

    @staticmethod
    def calculate_retention_score(
        emotional_weight: float,
        strands_count: int,
        days_old: float,
        access_count: int = 1
    ) -> float:
        """
        Calculates multi-factor retention priority score:
        Score = (emotional_weight * 0.40) + (connection_density * 0.25) + (access_reinforcement * 0.20) + (recency * 0.15)
        """
        weight_factor = max(0.0, min(1.0, float(emotional_weight)))
        connection_factor = min(1.0, strands_count / 5.0)
        access_factor = min(1.0, access_count / 4.0)
        recency_factor = max(0.0, 1.0 - (days_old / 60.0))

        score = (weight_factor * 0.40) + (connection_factor * 0.25) + (access_factor * 0.20) + (recency_factor * 0.15)
        return round(score, 4)

    @classmethod
    def evaluate_candidates(
        cls,
        memories: List[Dict[str, Any]],
        strands_map: Dict[str, Dict[str, float]],
        min_emotional_weight: float = 0.15,
        older_than_days: Optional[int] = None,
        protected_maps: Optional[List[str]] = None,
        max_memories: Optional[int] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Evaluates memories and identifies candidates for pruning."""
        protected = set(m.strip().lower().replace(" ", "_") for m in (protected_maps or ["identity", "facts"]))
        now = datetime.now(timezone.utc)
        scored: List[Tuple[str, float, Dict[str, Any]]] = []

        for mem in memories:
            mid = mem["id"]
            m_map = mem.get("map", "general")
            m_weight = float(mem.get("emotional_weight", 0.5))
            m_access = int(mem.get("access_count", 1))

            if m_map in protected:
                continue

            ts_str = mem.get("timestamp", "")
            days_old = 0.0
            try:
                dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if not dt.tzinfo:
                    dt = dt.replace(tzinfo=timezone.utc)
                days_old = max(0.0, (now - dt).total_seconds() / 86400.0)
            except Exception:
                pass

            if older_than_days is not None and days_old < older_than_days and m_weight >= min_emotional_weight:
                continue

            strands_count = len(strands_map.get(mid, {}))
            score = cls.calculate_retention_score(m_weight, strands_count, days_old, m_access)
            scored.append((mid, score, mem))

        scored.sort(key=lambda x: x[1])

        if max_memories is not None and len(memories) > max_memories:
            excess = len(memories) - max_memories
            return scored[:excess]
        else:
            threshold = min_emotional_weight * 1.5
            return [c for c in scored if c[1] < threshold]
