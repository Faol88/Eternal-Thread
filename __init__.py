"""
Eternal Living Memory Core
~~~~~~~~~~~~~~~~~~~~~~~~~~
Universal 3D Weaire-Phelan Topological & Vector Memory Architecture for AI.
Author: Faol88
Version: 1.5.0
"""

__version__ = "1.5.0"
__author__ = "Faol88"

from core.memory_engine import MemoryCore
from core.config import MemoryConfig
from core.spiderweb import SpiderwebLattice, extract_concept_keywords
from core.encryption import EncryptionLayer
from core.pruner import MemoryPruner
from core.logging_config import setup_default_logging, logger
from core.exceptions import (
    MemoryCoreError,
    StorageError,
    EncryptionError,
    LatticeError,
    ConfigurationError
)
from ownership.base_owner import BaseMemoryOwner
from ownership.example_owner import AutonomousCompanion

__all__ = [
    "__version__",
    "__author__",
    "MemoryCore",
    "MemoryConfig",
    "SpiderwebLattice",
    "extract_concept_keywords",
    "EncryptionLayer",
    "MemoryPruner",
    "setup_default_logging",
    "logger",
    "MemoryCoreError",
    "StorageError",
    "EncryptionError",
    "LatticeError",
    "ConfigurationError",
    "BaseMemoryOwner",
    "AutonomousCompanion",
]
