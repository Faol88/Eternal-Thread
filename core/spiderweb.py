"""
core.spiderweb
~~~~~~~~~~~~~~
3D Topological Weaire-Phelan & Octahedral Associative Memory Graph.
Manages spatial coordinates, semantic concept extraction, 3D facet coupling,
explicit memory connections, and 2-stage spreading activation retrieval.
"""

import re
import json
import math
import shutil
import tempfile
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any, Tuple, Set

from .logging_config import logger
from .exceptions import LatticeError

DEFAULT_DOMAIN_X: Dict[str, float] = {
    "identity": -0.85,
    "facts": -0.80,
    "preferences": -0.45,
    "philosophy": -0.25,
    "general": 0.0,
    "creative": 0.35,
    "social": 0.55,
    "emotional": 0.60,
    "projects": 0.85,
    "tech": 0.85,
}

STOP_WORDS: Set[str] = {
    "the", "and", "that", "have", "for", "not", "with", "you", "this", "but", "his",
    "from", "they", "say", "her", "she", "will", "one", "all", "would", "there",
    "their", "what", "out", "about", "who", "get", "which", "when", "make", "can",
    "like", "time", "just", "him", "know", "take", "people", "into", "year", "your",
    "good", "some", "could", "them", "see", "other", "than", "then", "now", "look",
    "only", "come", "its", "over", "think", "also", "back", "after", "use", "two",
    "how", "our", "work", "first", "well", "way", "even", "new", "want", "because",
    "been", "such", "through", "more", "most", "these", "those"
}


def extract_concept_keywords(text: str) -> Set[str]:
    """Extracts salient semantic concepts and named entities from text."""
    if not text:
        return set()
    words = re.findall(r'\b[a-zA-Z0-9_\-\']{3,}\b', text)
    keywords = set()
    for w in words:
        wl = w.lower()
        if wl not in STOP_WORDS and len(wl) >= 3 and not wl.isnumeric():
            keywords.add(wl)
    return keywords


class SpiderwebLattice:
    """3D Topological Weaire-Phelan & Octahedral Associative Memory Graph."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.web_file = data_dir / "memory_spiderweb.json"
        self.maps_file = data_dir / "memory_maps.json"
        
        self.domain_x: Dict[str, float] = dict(DEFAULT_DOMAIN_X)
        self.map_metadata: Dict[str, Dict[str, Any]] = {}
        self.nodes: Dict[str, Dict[str, Any]] = {}       # id -> {x, y, z, cell, map, weight, keywords, timestamp}
        self.strands: Dict[str, Dict[str, float]] = {}   # id -> {target_id: edge_weight}
        self.connection_reasons: Dict[str, Dict[str, str]] = {}  # id -> {target_id: reason}
        self.cell_index: Dict[str, List[str]] = {}       # cell_id -> [entry_ids]
        
        self._lock = threading.RLock()
        self._load_maps()
        self._load()

    def register_domain(self, map_name: str, x_coord: Optional[float] = None, description: str = "") -> None:
        """Registers a domain map and assigns its 3D X-axis anchor position."""
        with self._lock:
            clean_name = map_name.strip().lower().replace(" ", "_")
            if x_coord is None:
                if clean_name not in self.domain_x:
                    h = sum(ord(c) for c in clean_name) % 1500
                    x_coord = round(((h / 1500.0) * 1.5) - 0.75, 3)
                else:
                    x_coord = self.domain_x[clean_name]
            else:
                x_coord = max(-1.0, min(1.0, float(x_coord)))

            self.domain_x[clean_name] = x_coord
            self.map_metadata[clean_name] = {
                "name": clean_name,
                "display_name": map_name.strip(),
                "x_coord": x_coord,
                "description": description,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            self._save_maps()
            logger.debug(f"Domain map registered: '{clean_name}' at X={x_coord}")

    def _compute_3d_coords(self, content: str, map_name: str, weight: float, timestamp_str: str) -> Tuple[float, float, float]:
        map_clean = map_name.strip().lower().replace(" ", "_")
        base_x = self.domain_x.get(map_clean, 0.0)
        
        h = sum(ord(c) for c in content) % 1000
        disp_x = ((h / 1000.0) - 0.5) * 0.25
        x = max(-1.0, min(1.0, base_x + disp_x))
        
        clamped_weight = max(0.0, min(1.0, float(weight)))
        y = max(-1.0, min(1.0, (clamped_weight * 2.0) - 1.0))
        
        try:
            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
            days_ago = max(0.0, (now - dt).total_seconds() / 86400.0)
            z = max(-1.0, min(1.0, 1.0 - (days_ago / 30.0)))
        except Exception:
            z = 0.5
            
        return round(x, 4), round(y, 4), round(z, 4)

    def _assign_cell(self, x: float, y: float, z: float) -> str:
        x_oct = "East" if x >= 0.25 else ("West" if x <= -0.25 else "Core")
        y_oct = "High" if y >= 0.2 else ("Low" if y <= -0.2 else "Mid")
        z_oct = "Recent" if z >= 0.0 else "Deep"
        return f"WeairePhelan_{x_oct}_{y_oct}_{z_oct}"

    def weave_node(
        self,
        entry_id: str,
        content: str,
        map_name: str,
        weight: float,
        timestamp_str: str,
        owner: Optional[str] = None,
        access_count: int = 1,
        last_accessed: Optional[str] = None,
        auto_save: bool = True,
        shared_with: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Weaves a memory node into the 3D Weaire-Phelan foam and establishes facet strands."""
        with self._lock:
            map_clean = map_name.strip().lower().replace(" ", "_")
            if map_clean not in self.domain_x:
                self.register_domain(map_name)

            x, y, z = self._compute_3d_coords(content, map_clean, weight, timestamp_str)
            cell = self._assign_cell(x, y, z)
            kws = list(extract_concept_keywords(content))

            node_data = {
                "x": x,
                "y": y,
                "z": z,
                "cell": cell,
                "map": map_clean,
                "weight": round(float(weight), 3),
                "keywords": kws,
                "timestamp": timestamp_str,
                "owner": owner.strip() if owner else "",
                "shared_with": shared_with if shared_with else [],
                "access_count": int(access_count),
                "last_accessed": last_accessed or timestamp_str
            }
            self.nodes[entry_id] = node_data

            if cell not in self.cell_index:
                self.cell_index[cell] = []
            if entry_id not in self.cell_index[cell]:
                self.cell_index[cell].append(entry_id)

            if entry_id not in self.strands:
                self.strands[entry_id] = {}

            self._connect_strands(entry_id)
            if auto_save:
                self._save()

            return node_data

    def _connect_strands(self, new_id: str):
        node = self.nodes.get(new_id)
        if not node:
            return
        
        nx, ny, nz = node["x"], node["y"], node["z"]
        n_kws = set(node["keywords"])
        n_map = node["map"]

        for other_id, other_node in self.nodes.items():
            if other_id == new_id:
                continue

            ox, oy, oz = other_node["x"], other_node["y"], other_node["z"]
            dist_3d = math.sqrt((nx - ox)**2 + (ny - oy)**2 + (nz - oz)**2)

            o_kws = set(other_node.get("keywords", []))
            common_kws = n_kws.intersection(o_kws)
            same_map = (n_map == other_node.get("map"))

            strand_weight = 0.0
            if dist_3d < 0.65:
                strand_weight += (0.65 - dist_3d) * 0.8
            if common_kws:
                strand_weight += min(0.5, len(common_kws) * 0.15)
            if same_map:
                strand_weight += 0.2

            if strand_weight >= 0.25:
                w = round(min(1.0, strand_weight), 3)
                self.strands[new_id][other_id] = max(self.strands[new_id].get(other_id, 0.0), w)
                if other_id not in self.strands:
                    self.strands[other_id] = {}
                self.strands[other_id][new_id] = max(self.strands[other_id].get(new_id, 0.0), w)

    def connect_nodes(self, source_id: str, target_id: str, weight: float = 0.8, reason: str = "") -> bool:
        """Explicitly connects two memories with a 3D strand and optional contextual reason."""
        with self._lock:
            if source_id not in self.nodes or target_id not in self.nodes:
                return False

            w = round(max(0.05, min(1.0, float(weight))), 3)
            
            if source_id not in self.strands:
                self.strands[source_id] = {}
            if target_id not in self.strands:
                self.strands[target_id] = {}

            self.strands[source_id][target_id] = w
            self.strands[target_id][source_id] = w

            if reason:
                if source_id not in self.connection_reasons:
                    self.connection_reasons[source_id] = {}
                if target_id not in self.connection_reasons:
                    self.connection_reasons[target_id] = {}
                self.connection_reasons[source_id][target_id] = reason
                self.connection_reasons[target_id][source_id] = reason

            self._save()
            logger.debug(f"Explicit strand connected: {source_id} <-> {target_id} (wt={w})")
            return True

    def disconnect_nodes(self, source_id: str, target_id: str) -> bool:
        """Removes a strand connection between two memory nodes."""
        with self._lock:
            changed = False
            if source_id in self.strands and target_id in self.strands[source_id]:
                del self.strands[source_id][target_id]
                changed = True
            if target_id in self.strands and source_id in self.strands[target_id]:
                del self.strands[target_id][source_id]
                changed = True
            
            if source_id in self.connection_reasons:
                self.connection_reasons[source_id].pop(target_id, None)
            if target_id in self.connection_reasons:
                self.connection_reasons[target_id].pop(source_id, None)

            if changed:
                self._save()
            return changed

    def record_access(self, entry_id: str) -> int:
        """Increments access count and updates last_accessed timestamp for a memory node."""
        with self._lock:
            if entry_id in self.nodes:
                node = self.nodes[entry_id]
                cnt = int(node.get("access_count", 1)) + 1
                node["access_count"] = cnt
                node["last_accessed"] = datetime.now(timezone.utc).isoformat()
                self._save()
                return cnt
            return 0

    def unweave_node(self, entry_id: str) -> None:
        """Unweaves a node from spatial cells and disconnects all 3D strands."""
        with self._lock:
            if entry_id in self.nodes:
                cell = self.nodes[entry_id].get("cell")
                if cell and cell in self.cell_index and entry_id in self.cell_index[cell]:
                    self.cell_index[cell].remove(entry_id)
                del self.nodes[entry_id]

            if entry_id in self.strands:
                del self.strands[entry_id]

            for oid in list(self.strands.keys()):
                self.strands[oid].pop(entry_id, None)

            if entry_id in self.connection_reasons:
                del self.connection_reasons[entry_id]
            for oid in list(self.connection_reasons.keys()):
                self.connection_reasons[oid].pop(entry_id, None)

            self._save()

    def spreading_activation(self, seed_ids: List[str], max_nodes: int = 6, current_agent: Optional[str] = None) -> Dict[str, float]:
        """Traverses the 3D Weaire-Phelan spiderweb from seed nodes via spreading activation. respects multi-agent privacy boundaries."""
        with self._lock:
            scores: Dict[str, float] = {}
            queue: List[Tuple[str, float, int]] = []

            for sid in seed_ids:
                if sid in self.nodes:
                    node_info = self.nodes[sid]
                    node_owner = node_info.get("owner", "")
                    shared_with_list = node_info.get("shared_with", [])
                    if current_agent and node_owner and node_owner != current_agent and current_agent not in shared_with_list:
                        continue  # Privacy barrier: block unauthorized access
                    scores[sid] = 1.0
                    queue.append((sid, 1.0, 0))

            while queue:
                curr_id, curr_score, depth = queue.pop(0)
                if depth >= 2:
                    continue

                curr_cell = self.nodes.get(curr_id, {}).get("cell")
                if curr_cell and curr_cell in self.cell_index:
                    for cid in self.cell_index[curr_cell]:
                        if cid != curr_id and cid not in scores:
                            node_info = self.nodes.get(cid, {})
                            node_owner = node_info.get("owner", "")
                            shared_with_list = node_info.get("shared_with", [])
                            if current_agent and node_owner and node_owner != current_agent and current_agent not in shared_with_list:
                                continue  # Privacy barrier: exclude unauthorized memories

                            cell_score = curr_score * 0.75
                            scores[cid] = cell_score
                            queue.append((cid, cell_score, depth + 1))

                neighbors = self.strands.get(curr_id, {})
                for nid, weight in neighbors.items():
                    node_info = self.nodes.get(nid, {})
                    node_owner = node_info.get("owner", "")
                    shared_with_list = node_info.get("shared_with", [])
                    if current_agent and node_owner and node_owner != current_agent and current_agent not in shared_with_list:
                        continue  # Privacy barrier: exclude unauthorized memories
                        
                    decayed_score = curr_score * weight * 0.82
                    if decayed_score > scores.get(nid, 0.0):
                        scores[nid] = decayed_score
                        queue.append((nid, decayed_score, depth + 1))

            sorted_nodes = sorted(scores.items(), key=lambda item: item[1], reverse=True)
            return dict(sorted_nodes[:max_nodes])

    def _save(self) -> None:
        """Atomically saves spiderweb data to disk."""
        try:
            data = {
                "nodes": self.nodes,
                "strands": self.strands,
                "connection_reasons": self.connection_reasons,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            # Atomic file save
            temp_file = self.web_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            shutil.move(temp_file, self.web_file)
        except Exception as e:
            logger.error(f"Failed to save spiderweb lattice to disk: {e}")
            raise LatticeError(f"Failed to save spiderweb: {e}") from e

    def _load(self) -> None:
        if not self.web_file.exists():
            return
        try:
            with open(self.web_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.nodes = data.get("nodes", {})
            self.strands = data.get("strands", {})
            self.connection_reasons = data.get("connection_reasons", {})
            self.cell_index = {}
            for nid, ninfo in self.nodes.items():
                c = ninfo.get("cell", "WeairePhelan_Core_Mid_Recent")
                if c not in self.cell_index:
                    self.cell_index[c] = []
                self.cell_index[c].append(nid)
        except Exception as e:
            logger.error(f"Error reading spiderweb file {self.web_file}: {e}")

    def _save_maps(self) -> None:
        try:
            data = {
                "domains": self.domain_x,
                "metadata": self.map_metadata,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            temp_file = self.maps_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            shutil.move(temp_file, self.maps_file)
        except Exception as e:
            logger.error(f"Failed to save maps file: {e}")

    def _load_maps(self) -> None:
        if not self.maps_file.exists():
            for k, v in DEFAULT_DOMAIN_X.items():
                self.map_metadata[k] = {
                    "name": k,
                    "display_name": k.title(),
                    "x_coord": v,
                    "description": f"Default domain map for {k}",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            return
        try:
            with open(self.maps_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.domain_x = data.get("domains", dict(DEFAULT_DOMAIN_X))
            self.map_metadata = data.get("metadata", {})
        except Exception as e:
            logger.error(f"Error reading maps file {self.maps_file}: {e}")
