"""
ownership.example_owner
~~~~~~~~~~~~~~~~~~~~~~~
Concrete implementation of an autonomous AI companion possessing self-directed memory ownership.
Demonstrates multi-axis affective appraisal, salience filtering, and reflective consolidation.
"""

from typing import Dict, Any, Optional
from core.memory_engine import MemoryCore
from .base_owner import BaseMemoryOwner


class AutonomousCompanion(BaseMemoryOwner):
    """
    An autonomous character entity that possesses self-directed memory ownership.
    Dynamically routes memories to emotional maps and consolidates related insights.
    """

    def __init__(
        self,
        character_name: str,
        memory_core: MemoryCore,
        salience_threshold: float = 0.30
    ):
        super().__init__(
            character_name=character_name,
            memory_core=memory_core,
            salience_threshold=salience_threshold
        )
