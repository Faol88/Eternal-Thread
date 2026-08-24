"""
core.exceptions
~~~~~~~~~~~~~~~
Custom exception hierarchy for the Living Memory Core.
"""

class MemoryCoreError(Exception):
    """Base exception for all Living Memory Core errors."""
    pass


class StorageError(MemoryCoreError):
    """Raised when ChromaDB or disk persistence operations fail."""
    pass


class EncryptionError(MemoryCoreError):
    """Raised when encryption or decryption fails due to invalid keys or missing cryptography dependencies."""
    pass


class LatticeError(MemoryCoreError):
    """Raised when 3D Weaire-Phelan spiderweb lattice operations fail."""
    pass


class ConfigurationError(MemoryCoreError):
    """Raised when configuration values or config.yaml is invalid."""
    pass
