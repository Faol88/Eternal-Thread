# 📚 Eternal Living Memory Core — API Reference Manual (v1.0.0)

Complete, type-annotated API specifications for the `eternal_memory_core` library.

---

## 1. `core.memory_engine.MemoryCore`
`from core.memory_engine import MemoryCore` (or `from eternal_memory_core import MemoryCore`)

### Constructor:
```python
MemoryCore(
    config: Optional[MemoryConfig] = None,
    data_dir: Optional[Union[str, Path]] = None,
    collection_name: Optional[str] = None,
    encryption_key: Optional[str] = None,
    embedding_model: Optional[str] = None
)
```
Initializes the ChromaDB vector collection, SentenceTransformer embeddings, and the 3D Spiderweb Lattice on-demand.

---

### Core CRUD Operations

#### `save_entry(content: str, map_name: str = "general", emotional_weight: float = 0.7, tags: Optional[Any] = None, custom_id: Optional[str] = None) -> Dict[str, Any]`
Saves a memory document, embeds it in ChromaDB, anchors continuous 3D coordinates, and weaves facet strands.
* **`content`**: Plaintext memory string.
* **`map_name`**: Cognitive domain map (e.g. `"preferences"`, `"projects"`, `"tech"`).
* **`emotional_weight`**: Normalized resonance between `0.0` and `1.0`.
* **`tags`**: Optional list or comma-separated string of tags.
* **`custom_id`**: Optional explicit memory ID.
* **Returns**: Dictionary containing `id`, `content`, `map`, `weight`, `timestamp`, `cell`, `coords`.

#### `get_entry(entry_id: str) -> Optional[Dict[str, Any]]`
Retrieves a memory entry by ID. Increments its `access_count` and returns decrypted content, 3D coordinates, access metrics, and active strands.

#### `update_entry(entry_id: str, content: Optional[str] = None, map_name: Optional[str] = None, emotional_weight: Optional[float] = None, tags: Optional[Any] = None) -> bool`
Updates existing memory fields and recomputes 3D coordinates.

#### `delete_entry(entry_id: str) -> bool`
Permanently deletes a memory from ChromaDB and unweaves all associated 3D lattice strands.

---

### Retrieval Operations

#### `search_memories(query_text: str, n_results: int = 4) -> List[str]`
Hybrid retrieval returning a list of decrypted content strings. Automatically increments `access_count` on returned memories.

#### `search_memories_detailed(query_text: str, n_results: int = 4) -> List[Dict[str, Any]]`
Hybrid retrieval returning rich metadata including similarity score, 3D cell, map, emotional weight, and access count.

#### `get_context_for_llm(query: str = "", count: Optional[int] = None) -> str`
Formats retrieved memories into a clean prompt context block for injection into any LLM.

---

### Connection & Map Operations

#### `create_connection(source_id: str, target_id: str, weight: float = 0.8, reason: str = "") -> bool`
Explicitly connects two memories with a 3D strand and contextual attribution reason.

#### `remove_connection(source_id: str, target_id: str) -> bool`
Removes a strand connection between two memory nodes.

#### `get_connections(entry_id: str) -> Dict[str, Any]`
Returns all incoming/outgoing strands, edge weights, and association reasons for a memory node.

#### `create_map(map_name: str, description: str = "", x_coord: Optional[float] = None) -> bool`
Registers a new cognitive domain map with custom spatial placement.

#### `list_maps() -> List[Dict[str, Any]]`
Returns all registered domain maps, coordinates, and memory counts.

---

### Maintenance & Metrics

#### `prune_memories(max_memories: Optional[int] = None, min_emotional_weight: Optional[float] = None, older_than_days: Optional[int] = None, protected_maps: Optional[List[str]] = None, dry_run: bool = False) -> Dict[str, Any]`
Executes multi-factor retention evaluation taking emotional weight, connection density, access count, and recency into account.

#### `get_stats() -> Dict[str, Any]`
Returns architectural metrics: total memories, active cells, total strands, registered maps, encryption status, and embedding model.

---

## 2. `ownership.base_owner.BaseMemoryOwner`
`from ownership.base_owner import BaseMemoryOwner`

Abstract base class for character agency and memory ownership.

### Methods:
* `perceive(text: str, emotional_override: Optional[str] = None, force_store: bool = False) -> Dict[str, Any]`: Evaluates VAD emotion and salience, storing memory if meaningful.
* `claim_memory(content: str, map_name: str, importance: float, tags: Optional[List[str]]) -> Dict[str, Any]`: Claims an attributed memory.
* `associate_memories(source_id: str, target_id: str, reason: str, strength: float) -> bool`: Explicitly draws an associative connection.
* `reflect_on_memories(topic: Optional[str] = None, limit: int = 6, similarity_threshold: float = 0.60) -> Dict[str, Any]`: Wanders memory space and consolidates new 3D graph strands.
* `get_prompt_context(current_topic: str = "", limit: int = 4) -> str`: Returns memory context augmented with character's live emotional mood state.

---

## 3. `ownership.affective_model.AffectiveModel`
`from ownership.affective_model import AffectiveModel, EmotionVector`

### Methods:
* `evaluate_text(text: str, explicit_override: Optional[str] = None) -> EmotionVector`: Computes continuous `valence`, `arousal`, `dominance`, `primary_label`, and `intensity`.

---

## 4. `ownership.salience_filter.SalienceFilter`
`from ownership.salience_filter import SalienceFilter`

### Methods:
* `evaluate(text: str, threshold: float = 0.35) -> Tuple[bool, float, str, Dict[str, Any]]`: Returns `(should_store, salience_score, suggested_map, metrics)`.
