"""
core.memory_engine
~~~~~~~~~~~~~~~~~~
Universal 3D Weaire-Phelan Living Memory Core Engine.
Combines ChromaDB Vector Database with 3D Topological Lattice & Hybrid Retrieval.
Pure on-demand initialization with standard logging.
"""

import re
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any, Tuple, Union

import chromadb
from chromadb.utils import embedding_functions

from .logging_config import logger
from .config import MemoryConfig
from .spiderweb import SpiderwebLattice, extract_concept_keywords
from .encryption import EncryptionLayer
from .pruner import MemoryPruner
from .exceptions import StorageError, MemoryCoreError


class MemoryCore:
    """Universal 3D Weaire-Phelan & ChromaDB Living Memory Engine."""

    def __init__(
        self,
        config: Optional[MemoryConfig] = None,
        data_dir: Optional[Union[str, Path]] = None,
        collection_name: Optional[str] = None,
        encryption_key: Optional[str] = None,
        embedding_model: Optional[str] = None
    ):
        self.config = config or MemoryConfig(
            data_dir=str(data_dir) if data_dir else None,
            collection_name=collection_name,
            encryption_key=encryption_key,
            embedding_model=embedding_model
        )

        self._data_lock = threading.RLock()

        # Paths
        self.data_dir = Path(data_dir).resolve() if data_dir else self.config.data_dir
        self.db_dir = self.data_dir / "chroma_db"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_dir.mkdir(parents=True, exist_ok=True)

        # Encryption
        enc_key = encryption_key if encryption_key is not None else self.config.encryption_key
        self.encryption = EncryptionLayer(enc_key if enc_key else None)

        # Embedding & ChromaDB Setup
        self.embedding_model_name = embedding_model or self.config.embedding_model
        logger.info(f"Initializing MemoryCore [Model: {self.embedding_model_name} | DataDir: {self.data_dir}]")

        try:
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model_name
            )
            col_name = collection_name or self.config.collection_name
            self.client = chromadb.PersistentClient(path=str(self.db_dir))
            self.collection = self.client.get_or_create_collection(
                name=col_name,
                embedding_function=self.embedding_fn
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB vector database: {e}")
            raise StorageError(f"Vector database initialization failed: {e}") from e

        # Initialize 3D Spiderweb Lattice
        self.spiderweb = SpiderwebLattice(self.data_dir)
        self._sync_spiderweb_with_db()

        total_strands = sum(len(v) for v in self.spiderweb.strands.values()) // 2
        logger.info(f"Living Memory Core Online [Memories: {self.collection.count()} | Cells: {len(self.spiderweb.cell_index)} | Strands: {total_strands}]")

    def _sync_spiderweb_with_db(self) -> None:
        """Ensures all memories in ChromaDB are woven into the 3D Spiderweb Lattice."""
        with self._data_lock:
            try:
                results = self.collection.get()
                ids = results.get("ids", [])
                docs = results.get("documents", [])
                metas = results.get("metadatas", [])

                needs_weave = False
                for i, doc_id in enumerate(ids):
                    if doc_id not in self.spiderweb.nodes:
                        doc = docs[i] if i < len(docs) else ""
                        decrypted_doc = self.encryption.decrypt(doc)
                        meta = metas[i] if i < len(metas) else {}
                        mp = meta.get("map", "general")
                        wt = meta.get("weight", 0.5)
                        ts = meta.get("timestamp", datetime.now(timezone.utc).isoformat())
                        acc = int(meta.get("access_count", 1))
                        last_acc = meta.get("last_accessed", ts)
                        owner_meta = meta.get("owner", "")
                        self.spiderweb.weave_node(doc_id, decrypted_doc, mp, wt, ts, owner=owner_meta, access_count=acc, last_accessed=last_acc, auto_save=False)
                        needs_weave = True
                
                if needs_weave:
                    self.spiderweb._save()
                    logger.debug(f"Synchronized {len(ids)} memories into 3D Weaire-Phelan Lattice.")
            except Exception as e:
                logger.error(f"Spiderweb DB sync error: {e}")

    # -----------------------------------------------------------------------
    # Core Memory Operations
    # -----------------------------------------------------------------------

    def save_entry(
        self,
        content: str,
        map_name: str = "general",
        emotional_weight: float = 0.7,
        tags: Optional[Any] = None,
        owner: Optional[str] = None,
        custom_id: Optional[str] = None,
        shared_with: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Saves a memory entry, embeds it in ChromaDB, and weaves it into the 3D Lattice."""
        if not content or len(content.strip()) < 2:
            logger.warning("save_entry called with empty or invalid content.")
            return {}

        raw_content = content.strip()
        map_name = map_name.strip().lower().replace(" ", "_")
        entry_id = custom_id or datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        timestamp = datetime.now(timezone.utc).isoformat()
        clamped_weight = max(0.0, min(1.0, float(emotional_weight)))

        if isinstance(tags, str):
            tags_str = tags.strip()
        elif isinstance(tags, (list, tuple, set)):
            tags_str = ",".join(str(t).strip() for t in tags if str(t).strip())
        else:
            tags_str = ""

        normalized_owner = owner.strip() if owner else ""
        shared_list = [s.strip() for s in shared_with if s.strip()] if shared_with else []
        
        metadata = {
            "map": map_name,
            "timestamp": timestamp,
            "weight": clamped_weight,
            "tags": tags_str,
            "owner": normalized_owner,
            "encrypted": self.encryption.enabled,
            "access_count": 1,
            "last_accessed": timestamp
        }
        if shared_list:
            metadata["shared_with"] = shared_list

        stored_doc = self.encryption.encrypt(raw_content)

        with self._data_lock:
            try:
                self.collection.upsert(
                    documents=[stored_doc],
                    metadatas=[metadata],
                    ids=[entry_id]
                )
                coords_info = self.spiderweb.weave_node(entry_id, raw_content, map_name, clamped_weight, timestamp, owner=normalized_owner, access_count=1, last_accessed=timestamp)
            except Exception as e:
                logger.error(f"Failed to save memory entry {entry_id}: {e}")
                raise StorageError(f"Save memory failed: {e}") from e

        logger.debug(f"Saved memory [{entry_id}] in [{map_name}|wt:{clamped_weight:.2f}]")
        return {
            "id": entry_id,
            "content": raw_content,
            "map": map_name,
            "weight": clamped_weight,
            "owner": normalized_owner,
            "timestamp": timestamp,
            "cell": coords_info.get("cell"),
            "coords": (coords_info.get("x"), coords_info.get("y"), coords_info.get("z"))
        }

    def _record_retrieval_access(self, entry_ids: List[str]) -> None:
        """Increments access count and updates recency timestamp for retrieved memories."""
        if not entry_ids:
            return
        with self._data_lock:
            for eid in entry_ids:
                new_count = self.spiderweb.record_access(eid)
                try:
                    res = self.collection.get(ids=[eid])
                    if res and res.get("ids") and res.get("metadatas"):
                        meta = dict(res["metadatas"][0])
                        meta["access_count"] = new_count if new_count > 0 else (int(meta.get("access_count", 1)) + 1)
                        meta["last_accessed"] = datetime.now(timezone.utc).isoformat()
                        self.collection.update(ids=[eid], metadatas=[meta])
                except Exception as e:
                    logger.debug(f"Could not update access metadata for {eid}: {e}")



    def share_memory(self, source_entry_id: str, to_agent: str, reason: str = "", from_agent: Optional[str] = None) -> Optional[str]:
        """Multi-Agent Gossip: Shares a private memory with another agent by duplicating it into their private space and linking them."""
        source_mem = self.get_entry(source_entry_id, current_agent=from_agent)
        if not source_mem:
            logger.error(f"Cannot share memory: {source_entry_id} not found.")
            return None
            
        # Fading Gossip: Copies decay faster and start with lower emotional weight
        faded_weight = source_mem["emotional_weight"] * 0.75
        
        # Merge existing tags with 'gossip'
        existing_tags = source_mem.get("tags", "")
        new_tags = f"{existing_tags},gossip" if existing_tags else "gossip"
        
        new_mem = self.save_entry(
            content=source_mem["content"],
            map_name=source_mem["map"],
            emotional_weight=faded_weight,
            tags=new_tags,
            owner=to_agent
        )
        
        # Physically connect the minds
        if new_mem and new_mem.get("id"):
            self.spiderweb.connect_nodes(source_entry_id, new_mem["id"], weight=0.85, reason=reason)
            return new_mem["id"]
        return None

    def get_entry(self, entry_id: str, current_agent: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieves a single memory entry by ID with decrypted content and spatial coordinates."""
        with self._data_lock:
            try:
                res = self.collection.get(ids=[entry_id])
                if not res or not res.get("ids"):
                    return None
                
                doc = res["documents"][0]
                meta = res["metadatas"][0] if res.get("metadatas") else {}
                
                # Enforce privacy check
                owner_meta = meta.get("owner", "")
                shared_with_list = meta.get("shared_with", [])
                
                if current_agent and owner_meta and owner_meta != current_agent and current_agent not in shared_with_list:
                    logger.warning(f"Privacy blocked: Agent '{current_agent}' blocked from accessing private memory '{entry_id}' owned by '{owner_meta}'.")
                    return None
                    
                decrypted = self.encryption.decrypt(doc)
                node_info = self.spiderweb.nodes.get(entry_id, {})
                strands = self.spiderweb.strands.get(entry_id, {})

                self._record_retrieval_access([entry_id])
                access_cnt = int(meta.get("access_count", node_info.get("access_count", 1))) + 1
                return {
                    "id": entry_id,
                    "content": decrypted,
                    "map": meta.get("map", "general"),
                    "emotional_weight": meta.get("weight", 0.5),
                    "owner": meta.get("owner", node_info.get("owner", "")),
                    "shared_with": meta.get("shared_with", node_info.get("shared_with", "")),
                    "access_count": access_cnt,
                    "last_accessed": meta.get("last_accessed", node_info.get("last_accessed", "")),
                    "timestamp": meta.get("timestamp", ""),
                    "tags": meta.get("tags", ""),
                    "cell": node_info.get("cell", "WeairePhelan_Core"),
                    "3d_coords": (node_info.get("x", 0.0), node_info.get("y", 0.0), node_info.get("z", 0.0)),
                    "strands": strands
                }
            except Exception as e:
                logger.error(f"Error fetching memory {entry_id}: {e}")
                return None

    def update_entry(
        self,
        entry_id: str,
        content: Optional[str] = None,
        map_name: Optional[str] = None,
        emotional_weight: Optional[float] = None,
        tags: Optional[Any] = None,
        owner: Optional[str] = None,
        shared_with: Optional[List[str]] = None,
        current_agent: Optional[str] = None
    ) -> bool:
        """Updates an existing memory's content, map, weight, or tags and re-weaves its spatial position."""
        existing = self.get_entry(entry_id, current_agent=current_agent)
        if not existing:
            return False

        new_content = content.strip() if content is not None else existing["content"]
        new_map = map_name.strip().lower().replace(" ", "_") if map_name is not None else existing["map"]
        new_weight = float(emotional_weight) if emotional_weight is not None else existing["emotional_weight"]
        new_tags = tags if tags is not None else existing.get("tags")
        new_owner = owner if owner is not None else existing.get("owner", "")
        new_shared = shared_with if shared_with is not None else existing.get("shared_with", [])

        self.save_entry(
            content=new_content,
            map_name=new_map,
            emotional_weight=new_weight,
            tags=new_tags,
            owner=new_owner,
            custom_id=entry_id,
            shared_with=new_shared
        )
        return True

    def delete_entry(self, entry_id: str, current_agent: Optional[str] = None) -> bool:
        """Permanently deletes a memory entry and unweaves it from all 3D lattice strands."""
        # Ensure authorization
        existing = self.get_entry(entry_id, current_agent=current_agent)
        if not existing:
            return False

        with self._data_lock:
            try:
                self.collection.delete(ids=[entry_id])
                self.spiderweb.unweave_node(entry_id)
                logger.debug(f"Deleted memory entry {entry_id}")
                return True
            except Exception as e:
                logger.error(f"Error deleting memory {entry_id}: {e}")
                return False

    # -----------------------------------------------------------------------
    # Hybrid Vector + 3D Spiderweb Retrieval
    # -----------------------------------------------------------------------

    def search_memories(self, query_text: str, n_results: int = 4, current_agent: Optional[str] = None) -> List[str]:
        """Simple retrieval returning only the text content strings. Respects privacy."""
        detailed = self.search_memories_detailed(query_text, n_results=n_results, current_agent=current_agent)
        return [d["content"] for d in detailed]

    def search_memories_detailed(self, query_text: str, n_results: int = 4, current_agent: Optional[str] = None) -> List[Dict[str, Any]]:
        """Detailed hybrid retrieval returning content, metadata, similarity score, and 3D cell. Respects multi-agent privacy."""
        if not query_text.strip() or self.collection.count() == 0:
            return []

        if current_agent is None:
            logger.warning("Retrieval executed in GOD MODE (current_agent=None). All privacy boundaries disabled.")

        with self._data_lock:
            try:
                fetch_count = min(n_results * 3, self.collection.count())
                
                where_filter = None
                if current_agent is not None:
                    where_filter = {"$or": [{"owner": current_agent}, {"owner": ""}, {"shared_with": {"$contains": current_agent}}]}
                
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=fetch_count,
                    where=where_filter
                )
                seed_ids = results.get("ids", [[]])[0]
                seed_docs = results.get("documents", [[]])[0]
                seed_metas = results.get("metadatas", [[]])[0] if results.get("metadatas") else [{}] * len(seed_ids)
                seed_distances = results.get("distances", [[]])[0] if results.get("distances") else [0.0] * len(seed_ids)

                if not seed_ids:
                    return []

                activated_graph = self.spiderweb.spreading_activation(seed_ids[:3], max_nodes=n_results * 2, current_agent=current_agent)

                combined_scores: Dict[str, float] = {}
                doc_map: Dict[str, Dict[str, Any]] = {}

                for i, sid in enumerate(seed_ids):
                    v_sim = max(0.0, 1.0 - (seed_distances[i] / 2.0)) if i < len(seed_distances) else 0.5
                    g_sim = activated_graph.get(sid, 0.0)
                    wt = seed_metas[i].get("weight", 0.5) if i < len(seed_metas) else 0.5
                    weight_bonus = float(wt) * 0.15

                    score = (v_sim * 0.55) + (g_sim * 0.30) + weight_bonus
                    combined_scores[sid] = score
                    
                    decrypted_doc = self.encryption.decrypt(seed_docs[i])
                    node_info = self.spiderweb.nodes.get(sid, {})
                    doc_map[sid] = {
                        "id": sid,
                        "content": decrypted_doc,
                        "map": seed_metas[i].get("map", "general") if i < len(seed_metas) else "general",
                        "weight": wt,
                        "owner": seed_metas[i].get("owner", "") if i < len(seed_metas) else "",
                        "cell": node_info.get("cell", "WeairePhelan_Core"),
                        "score": round(score, 4)
                    }

                for gid, g_score in activated_graph.items():
                    if gid not in combined_scores:
                        try:
                            item = self.collection.get(ids=[gid])
                            if item and item.get("documents"):
                                raw_doc = item["documents"][0]
                                decrypted = self.encryption.decrypt(raw_doc)
                                meta = item["metadatas"][0] if item.get("metadatas") else {}
                                wt = meta.get("weight", 0.5)
                                
                                final_g_score = (g_score * 0.40) + (float(wt) * 0.15)
                                combined_scores[gid] = final_g_score
                                node_info = self.spiderweb.nodes.get(gid, {})
                                doc_map[gid] = {
                                    "id": gid,
                                    "content": decrypted,
                                    "map": meta.get("map", "general"),
                                    "weight": wt,
                                    "owner": meta.get("owner", ""),
                                    "cell": node_info.get("cell", "WeairePhelan_Core"),
                                    "score": round(final_g_score, 4)
                                }
                        except Exception:
                            pass

                sorted_ids = sorted(combined_scores.items(), key=lambda item: item[1], reverse=True)
                final_docs = [doc_map[sid] for sid, _ in sorted_ids[:n_results] if sid in doc_map]
                retrieved_ids = [d["id"] for d in final_docs]
                self._record_retrieval_access(retrieved_ids)
                return final_docs

            except Exception as e:
                logger.error(f"Hybrid retrieval error: {e}")
                return []

    def search(self, query_text: str, top_k: int = 4, current_agent: Optional[str] = None) -> List[str]:
        return self.search_memories(query_text, n_results=top_k, current_agent=current_agent)

    def get_context_for_llm(self, query: str = "", count: Optional[int] = None, current_agent: Optional[str] = None) -> str:
        """Formats relevant memories into a clean prompt context block for any LLM."""
        n_count = count or self.config.default_context_count
        if self.collection.count() == 0:
            return "No memories recorded yet."
            
        if current_agent is None:
            logger.warning("Retrieval executed in GOD MODE (current_agent=None). All privacy boundaries disabled.")

        if query and query.strip():
            memories = self.search_memories(query, n_results=n_count, current_agent=current_agent)
        else:
            with self._data_lock:
                where_filter = None
                if current_agent is not None:
                    where_filter = {"$or": [{"owner": current_agent}, {"owner": ""}, {"shared_with": {"$contains": current_agent}}]}
                    
                results = self.collection.get(where=where_filter, limit=n_count)
                raw_docs = results.get("documents", []) if results else []
                memories = [self.encryption.decrypt(d) for d in raw_docs]

        if not memories:
            return "No relevant memories found."

        formatted = ["[3D LIVING MEMORY CONTEXT]:"]
        for m in memories:
            clean_m = re.sub(r'\[SAVE_MEMORY:[^\]]*\]', '', m).strip()
            if clean_m:
                formatted.append(f"- {clean_m}")

        return "\n".join(formatted)

    # -----------------------------------------------------------------------
    # Map & Connection Management
    # -----------------------------------------------------------------------

    def create_map(self, map_name: str, description: str = "", x_coord: Optional[float] = None) -> bool:
        """Registers a new emotional/thematic domain map with 3D coordinate placement."""
        self.spiderweb.register_domain(map_name, x_coord=x_coord, description=description)
        return True

    def list_maps(self) -> List[Dict[str, Any]]:
        """Returns all registered domain maps and their spatial configuration."""
        maps_list = []
        for name, meta in self.spiderweb.map_metadata.items():
            maps_list.append({
                "map": name,
                "display_name": meta.get("display_name", name.title()),
                "x_coord": meta.get("x_coord", 0.0),
                "description": meta.get("description", ""),
                "node_count": sum(1 for n in self.spiderweb.nodes.values() if n.get("map") == name)
            })
        return sorted(maps_list, key=lambda m: m["map"])

    def reassign_map(self, entry_id: str, new_map_name: str) -> bool:
        return self.update_entry(entry_id, map_name=new_map_name)

    def create_connection(self, source_id: str, target_id: str, weight: float = 0.8, reason: str = "") -> bool:
        """Explicitly connects two memories with a 3D strand."""
        return self.spiderweb.connect_nodes(source_id, target_id, weight=weight, reason=reason)

    def remove_connection(self, source_id: str, target_id: str) -> bool:
        return self.spiderweb.disconnect_nodes(source_id, target_id)

    def get_connections(self, entry_id: str) -> Dict[str, Any]:
        """Returns all incoming/outgoing 3D strands and coupling reasons for a memory."""
        strands = self.spiderweb.strands.get(entry_id, {})
        reasons = self.spiderweb.connection_reasons.get(entry_id, {})
        connected_nodes = []
        for target_id, weight in strands.items():
            connected_nodes.append({
                "target_id": target_id,
                "weight": weight,
                "reason": reasons.get(target_id, "")
            })
        return {
            "entry_id": entry_id,
            "total_connections": len(connected_nodes),
            "strands": connected_nodes
        }

    # -----------------------------------------------------------------------
    # Inspection, Stats & Bulk Queries
    # -----------------------------------------------------------------------

    def get_all_memories(self) -> List[Dict[str, Any]]:
        with self._data_lock:
            try:
                results = self.collection.get()
                docs = results.get("documents", [])
                metas = results.get("metadatas", [])
                ids = results.get("ids", [])
                memories = []
                for i, doc in enumerate(docs):
                    meta = metas[i] if i < len(metas) else {}
                    mid = ids[i] if i < len(ids) else ""
                    node_info = self.spiderweb.nodes.get(mid, {})
                    decrypted_doc = self.encryption.decrypt(doc)
                    memories.append({
                        "id": mid,
                        "content": decrypted_doc,
                        "map": meta.get("map", "general"),
                        "emotional_weight": meta.get("weight", 0.5),
                        "owner": meta.get("owner", node_info.get("owner", "")),
                        "access_count": int(meta.get("access_count", node_info.get("access_count", 1))) + 1,
                        "last_accessed": meta.get("last_accessed", node_info.get("last_accessed", "")),
                        "timestamp": meta.get("timestamp", ""),
                        "tags": meta.get("tags", ""),
                        "3d_coords": (node_info.get("x", 0.0), node_info.get("y", 0.0), node_info.get("z", 0.0)),
                        "cell": node_info.get("cell", "WeairePhelan_Core")
                    })
                return memories
            except Exception as e:
                logger.error(f"Error fetching all memories: {e}")
                return []

    def get_by_map(self, map_name: str) -> List[Dict[str, Any]]:
        map_clean = map_name.strip().lower().replace(" ", "_")
        with self._data_lock:
            try:
                results = self.collection.get(where={"map": map_clean})
                docs = results.get("documents", [])
                metas = results.get("metadatas", [])
                ids = results.get("ids", [])
                memories = []
                for i, doc in enumerate(docs):
                    meta = metas[i] if i < len(metas) else {}
                    mid = ids[i] if i < len(ids) else ""
                    node_info = self.spiderweb.nodes.get(mid, {})
                    decrypted_doc = self.encryption.decrypt(doc)
                    memories.append({
                        "id": mid,
                        "content": decrypted_doc,
                        "map": meta.get("map", map_clean),
                        "emotional_weight": meta.get("weight", 0.5),
                        "timestamp": meta.get("timestamp", ""),
                        "tags": meta.get("tags", ""),
                        "3d_coords": (node_info.get("x", 0.0), node_info.get("y", 0.0), node_info.get("z", 0.0)),
                        "cell": node_info.get("cell", "WeairePhelan_Core")
                    })
                return memories
            except Exception as e:
                logger.error(f"Error fetching memories for map '{map_clean}': {e}")
                return []

    def count(self) -> int:
        return self.collection.count()

    def get_stats(self) -> Dict[str, Any]:
        with self._data_lock:
            total = self.collection.count()
            all_mems = self.get_all_memories()
            maps = set(m.get("map", "general") for m in all_mems)
            cells = set(m.get("cell", "") for m in all_mems if m.get("cell"))
            total_strands = sum(len(v) for v in self.spiderweb.strands.values()) // 2
            
            return {
                "total_memories": total,
                "total_maps": len(maps),
                "available_maps": sorted(list(maps)),
                "registered_maps": len(self.spiderweb.domain_x),
                "weaire_phelan_cells": len(cells),
                "spiderweb_strands": total_strands,
                "encryption_enabled": self.encryption.enabled,
                "engine": "ChromaDB + 3D Weaire-Phelan Spiderweb",
                "embedding_model": self.embedding_model_name,
                "data_directory": str(self.data_dir)
            }

    # -----------------------------------------------------------------------
    # Intelligent Multi-Factor Pruning & Cleanup
    # -----------------------------------------------------------------------

    def prune_memories(
        self,
        max_memories: Optional[int] = None,
        min_emotional_weight: Optional[float] = None,
        older_than_days: Optional[int] = None,
        protected_maps: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Prunes low-priority memories using MemoryPruner evaluation."""
        all_mems = self.get_all_memories()
        if not all_mems:
            return {"pruned_count": 0, "pruned_ids": [], "remaining_count": 0, "dry_run": dry_run}

        max_limit = max_memories if max_memories is not None else self.config.max_memories
        min_wt = min_emotional_weight if min_emotional_weight is not None else self.config.min_emotional_weight
        prot_maps = protected_maps if protected_maps is not None else self.config.protected_maps

        targets = MemoryPruner.evaluate_candidates(
            memories=all_mems,
            strands_map=self.spiderweb.strands,
            min_emotional_weight=min_wt,
            older_than_days=older_than_days,
            protected_maps=prot_maps,
            max_memories=max_limit
        )

        target_ids = [t[0] for t in targets]

        if not dry_run and target_ids:
            with self._data_lock:
                for tid in target_ids:
                    try:
                        self.collection.delete(ids=[tid])
                        self.spiderweb.unweave_node(tid)
                    except Exception as e:
                        logger.error(f"Error pruning memory {tid}: {e}")

        logger.info(f"Pruning complete [Pruned: {len(target_ids)} | Remaining: {self.collection.count()}]")
        return {
            "pruned_count": len(target_ids),
            "pruned_ids": target_ids,
            "remaining_count": self.collection.count() - (0 if dry_run else len(target_ids)),
            "dry_run": dry_run
        }

    def wipe_all(self, confirm: bool = False) -> bool:
        if not confirm:
            logger.warning("wipe_all requested but confirm=False. Aborted.")
            return False
        with self._data_lock:
            try:
                self.client.delete_collection(name=self.collection.name)
                self.collection = self.client.create_collection(
                    name=self.collection.name,
                    embedding_function=self.embedding_fn
                )
                self.spiderweb.nodes.clear()
                self.spiderweb.strands.clear()
                self.spiderweb.connection_reasons.clear()
                self.spiderweb.cell_index.clear()
                self.spiderweb._save()
                logger.info("Memory core completely wiped and reset.")
                return True
            except Exception as e:
                logger.error(f"Wipe error: {e}")
                return False
