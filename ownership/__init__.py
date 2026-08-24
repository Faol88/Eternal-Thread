"""
eternal_memory_core.ownership
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Autonomous Character Agency Layer for AI Companions and Game NPCs.
"""

from .base_owner import BaseMemoryOwner
from .example_owner import AutonomousCompanion
from .affective_model import AffectiveModel, EmotionVector
from .salience_filter import SalienceFilter

__all__ = [
    "BaseMemoryOwner",
    "AutonomousCompanion",
    "AffectiveModel",
    "EmotionVector",
    "SalienceFilter",
]
