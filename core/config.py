"""
core.config
~~~~~~~~~~~
Centralized configuration manager for the Living Memory Core.
Supports explicit parameter injection, config.yaml parsing, and environment variable overrides.
Does NOT instantiate global objects on import.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from .logging_config import logger


class MemoryConfig:
    """Configuration container with priority: Explicit Args > Env Vars > YAML > Defaults."""

    DEFAULT_DATA_DIR = "./data"
    DEFAULT_COLLECTION = "living_memory_core"
    DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    DEFAULT_MAX_MEMORIES = 50000
    DEFAULT_MIN_WEIGHT = 0.15
    DEFAULT_PROTECTED_MAPS = ["identity", "facts", "preferences"]
    DEFAULT_LLM_URL = "http://localhost:11434/api/generate"
    DEFAULT_LLM_MODEL = "llama3:latest"
    DEFAULT_CONTEXT_COUNT = 4

    def __init__(
        self,
        config_path: Optional[str] = None,
        data_dir: Optional[str] = None,
        collection_name: Optional[str] = None,
        embedding_model: Optional[str] = None,
        encryption_key: Optional[str] = None,
        max_memories: Optional[int] = None,
        min_emotional_weight: Optional[float] = None,
        protected_maps: Optional[List[str]] = None,
        llm_api_url: Optional[str] = None,
        llm_model: Optional[str] = None,
        default_context_count: Optional[int] = None
    ):
        self.config_path = self._resolve_config_path(config_path)
        self.raw_config: Dict[str, Any] = {}
        if self.config_path:
            self._load_yaml()

        storage_cfg = self.raw_config.get("storage", {})
        emb_cfg = self.raw_config.get("embedding", {})
        sec_cfg = self.raw_config.get("security", {})
        mm_cfg = self.raw_config.get("memory_management", {})
        llm_cfg = self.raw_config.get("llm_bridge", {})

        # 1. Storage
        resolved_dir = data_dir or os.getenv("MEMORY_DATA_DIR") or storage_cfg.get("data_dir", self.DEFAULT_DATA_DIR)
        self.data_dir = Path(resolved_dir).resolve()
        self.collection_name = collection_name or os.getenv("MEMORY_COLLECTION") or storage_cfg.get("collection_name", self.DEFAULT_COLLECTION)

        # 2. Embedding Model
        self.embedding_model = embedding_model or os.getenv("MEMORY_EMBEDDING_MODEL") or emb_cfg.get("model_name", self.DEFAULT_EMBEDDING_MODEL)

        # 3. Security
        self.encryption_key = encryption_key or os.getenv("MEMORY_ENCRYPTION_KEY") or sec_cfg.get("encryption_key", "")

        # 4. Memory Management & Pruning
        max_m = max_memories or (int(os.getenv("MEMORY_MAX_COUNT")) if os.getenv("MEMORY_MAX_COUNT") else None) or mm_cfg.get("max_memories", self.DEFAULT_MAX_MEMORIES)
        self.max_memories = int(max_m)
        min_w = min_emotional_weight or (float(os.getenv("MEMORY_MIN_WEIGHT")) if os.getenv("MEMORY_MIN_WEIGHT") else None) or mm_cfg.get("min_emotional_weight", self.DEFAULT_MIN_WEIGHT)
        self.min_emotional_weight = float(min_w)
        self.protected_maps = protected_maps or mm_cfg.get("protected_maps", list(self.DEFAULT_PROTECTED_MAPS))

        # 5. LLM Bridge Defaults
        self.llm_api_url = llm_api_url or os.getenv("MEMORY_LLM_URL") or llm_cfg.get("api_url", self.DEFAULT_LLM_URL)
        self.llm_model = llm_model or os.getenv("MEMORY_LLM_MODEL") or llm_cfg.get("model_name", self.DEFAULT_LLM_MODEL)
        ctx_c = default_context_count or (int(os.getenv("MEMORY_CONTEXT_COUNT")) if os.getenv("MEMORY_CONTEXT_COUNT") else None) or llm_cfg.get("default_context_count", self.DEFAULT_CONTEXT_COUNT)
        self.default_context_count = int(ctx_c)

    def _resolve_config_path(self, custom_path: Optional[str]) -> Optional[Path]:
        if custom_path:
            p = Path(custom_path)
            if p.exists():
                return p.resolve()
        
        candidates = [
            Path("config.yaml"),
            Path(__file__).resolve().parent.parent / "config.yaml",
            Path.cwd() / "config.yaml"
        ]
        for c in candidates:
            if c.exists():
                return c.resolve()
        return None

    def _load_yaml(self) -> None:
        if self.config_path and self.config_path.exists() and HAS_YAML:
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.raw_config = yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"Failed to parse configuration file {self.config_path}: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Returns active configuration as a dictionary."""
        return {
            "data_dir": str(self.data_dir),
            "collection_name": self.collection_name,
            "embedding_model": self.embedding_model,
            "encryption_enabled": bool(self.encryption_key),
            "max_memories": self.max_memories,
            "min_emotional_weight": self.min_emotional_weight,
            "protected_maps": self.protected_maps,
            "llm_api_url": self.llm_api_url,
            "llm_model": self.llm_model,
            "default_context_count": self.default_context_count
        }

    @classmethod
    def from_yaml(cls, path: str) -> "MemoryConfig":
        """Factory method to load configuration from a specific YAML file."""
        return cls(config_path=path)
