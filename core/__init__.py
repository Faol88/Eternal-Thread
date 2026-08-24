"""
eternal_memory_core.core
~~~~~~~~~~~~~~~~~~~~~~~~
Core package containing the 3D Weaire-Phelan memory engine, spiderweb lattice,
encryption layer, configuration manager, and multi-factor pruner.
"""

from .config import MemoryConfig
from .memory_engine import MemoryCore
from .spiderweb import SpiderwebLattice, extract_concept_keywords
from .encryption import EncryptionLayer
from .pruner import MemoryPruner
from .logging_config import setup_default_logging, logger
from .exceptions import (
    MemoryCoreError,
    StorageError,
    EncryptionError,
    LatticeError,
    ConfigurationError
)

__all__ = [
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
    "ConfigurationError"
]
