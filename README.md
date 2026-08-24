# 🧠 3D Weaire–Phelan Living Memory Core
### Universal 3D Topological Vector Memory & Cognitive Framework for AI Companions, Game NPCs & Local LLMs

**Author**: Faol88 (K.N.A.M) | Kevin Nuydens  
**Vision**: For A.I. By A.I.  
**Version**: 1.5.0 (Commercial & Open Source Release)  
**License**: MIT License  

---

## 🌟 Overview

The **3D Living Memory Core** is a fast, 100% local cognitive memory engine designed to give AI companions, NPCs, and autonomous assistants durable, human-like memory.

Traditional RAG (Retrieval-Augmented Generation) systems treat past interactions as flat database rows, relying solely on vector cosine distance. 

The **Living Memory Core** structures thoughts inside a **3D Continuous Coordinate Lattice** and an **Associative Spiderweb Graph**:
* **$X$-Axis (Domain Maps)**: Thematic placement (`identity`, `facts`, `preferences`, `projects`, `tech`, `philosophy`, etc.).
* **$Y$-Axis (Emotional Resonance & Weight)**: Meaningful milestones ascend to higher geometric cells, shielding vital memories from decay.
* **$Z$-Axis (Temporal Depth & Recency)**: Fresh thoughts remain near the conscious surface ($+1.0$), while older memories sink gradually into long-term depth ($-1.0$).

```
                          [3D LIVING MEMORY CORE]
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
┌───────────────────────┐                           ┌─────────────────────┐
│  Local ChromaDB RAG   │                           │  3D Weaire-Phelan   │
│  (all-MiniLM-L6-v2)   │ ── Facet Coupling Strands ─▶ Spatial Foam Graph │
└──────────┬────────────┘                           └──────────┬──────────┘
           │                                                   │
           └─────────────────────────┬─────────────────────────┘
                                     ▼
                   2-Stage Spreading Activation Retrieval
                                     │
                                     ▼
                   [Prompt Context for Ollama / LM Studio]
```

---

## ✨ Core Highlights

* 🚀 **100% Local & Offline**: Powered by local ChromaDB and `all-MiniLM-L6-v2` embeddings. Zero external API calls or subscription costs.
* 🕸️ **2-Stage Spreading Activation Retrieval**: Blends vector embeddings with multi-hop graph energy traversal to retrieve deep associative context.
* 👁️ **Spaced-Repetition Retrieval Reinforcement**: Memories increment an internal `access_count` each time they are retrieved, earning permanent retention bonuses against decay.
* 🛡️ **Multi-Agent Privacy & Fading Gossip (v1.5.0)**: Secure compartmentalization for thousands of agents in a single shared world. Supports Public Events, Private Secrets, Limited Sharing (`shared_with` lists), and automatic Fading Gossip mechanics.
* 🎭 **Affective Character Agency (`ownership/`)**:
  * **Valence–Arousal–Dominance (VAD)** continuous emotional state tracking with mood inertia.
  * **Conversational Salience Filter**: Automatically rejects conversational filler (`"hi"`, `"ok cool"`, `"lol"`) while storing substantive facts and preferences.
  * **Reflective Memory Consolidation**: Autonomous reflection routine that wanders memory space, computes pairwise thematic affinity, and consolidates new 3D graph strands.
* 🔒 **Zero-Knowledge Encryption**: Optional Fernet AES-128-CBC + HMAC encryption for secure at-rest storage.
* 🧹 **Intelligent Multi-Factor Pruning**: Decays stale, low-resonance memories using weight, strand density, access frequency, and recency.
* 🖥️ **Themeable Desktop Viewer (`ui/memory_viewer.py`)**: Standalone CustomTkinter browser with live metrics, multi-theme selector, and 3D strand inspector.

---

## 🛡️ Multi-Agent Privacy & Fading Gossip (v1.5.0)

The core now features a robust compartmentalized privacy engine, allowing hundreds of agents to live in the same simulated world, querying the same memory core, with strict zero-leakage boundaries.

* **Public Events**: `owner=""`. Memories visible to every agent in the simulation (e.g. "The sky is blue").
* **Private Secrets**: `owner="Agent A"`. Thoughts and memories strictly locked to a single agent.
* **Limited Sharing**: `shared_with=["Agent B"]`. Securely share private memories with specific whitelisted agents. The vector database filters the search natively for maximum efficiency.
* **Fading Gossip**: When an agent shares a memory, the receiving agent naturally degrades the `emotional_weight` of the memory and appends a `gossip` tag, naturally simulating the fading impact of second-hand information.

### Multi-Agent Privacy Example

```python
# Private memory (Only Guard_01 can retrieve this)
memory.save_entry("I found the hidden key.", owner="Guard_01")

# Limited sharing (Only the Merchant, Player, and Guard_01 can retrieve this)
memory.save_entry(
    "The treasure is behind the waterfall.",
    owner="Merchant",
    shared_with=["Player", "Guard_01"]
)

# Public event (Everyone in the simulation can retrieve this)
memory.save_entry("The festival starts at noon.", owner="")
```

---

## 📦 Installation

### Requirements
* Python 3.9, 3.10, 3.11, or 3.12
* Windows, macOS, or Linux

### Install Dependencies
```bash
git clone https://github.com/Faol88/eternal-memory-core.git
cd eternal-memory-core
pip install -r requirements.txt
```

Or install as an editable package:
```bash
pip install -e .
```

---

## ⚡ Quick Start: Basic Memory Operations

```python
from core.memory_engine import MemoryCore

# 1. Instantiate the memory core
memory = MemoryCore()

# 2. Save a memory with thematic domain and emotional weight (0.0 to 1.0)
m1 = memory.save_entry(
    content="User is building a high-speed physics engine for an orbital flight simulator.",
    map_name="projects",
    emotional_weight=0.95
)

# 3. Retrieve hybrid 3D associative context for any prompt
context = memory.get_context_for_llm("Tell me about the user's simulation projects")
print(context)
```

**Output**:
```text
[3D LIVING MEMORY CONTEXT]:
- User is building a high-speed physics engine for an orbital flight simulator.
```

---

## 🎭 AI Companion Integration (Affective Agency)

```python
from core.memory_engine import MemoryCore
from ownership.example_owner import AutonomousCompanion

memory = MemoryCore()
companion = AutonomousCompanion(character_name="Aria", memory_core=memory)

# 1. Perceive a conversation turn (appraises emotion + tests salience)
result = companion.perceive("We solved the physics engine bug! It runs at 120 FPS now!")
print(f"Emotion: {result['emotion']['primary_label']} (Valence: {result['emotion']['valence']:+.2f})")
print(f"Stored: {result['stored']} | Map: {result['map']}")

# 2. Autonomous Cognitive Reflection (reinforces 3D associative strands)
consolidation = companion.reflect_on_memories(topic="physics and engine performance")
print(f"Consolidated links created: {len(consolidation['consolidated_links'])}")

# 3. Get prompt context enriched with live emotional mood state
prompt_context = companion.get_prompt_context("flight simulator")
print(prompt_context)
```

---

## 🤖 Local LLM Integration Blueprint (Ollama / LM Studio)

```python
import requests
from core.memory_engine import MemoryCore

memory = MemoryCore()
user_query = "What geometry are we using for our memory engine?"

# 1. Retrieve 3D memory context
context = memory.get_context_for_llm(user_query, count=3)

# 2. Construct augmented prompt
prompt = f"""You are a helpful AI assistant with 3D topological memory.

{context}

User: {user_query}
Assistant:"""

# 3. Query local LLM (Ollama endpoint)
res = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama3:latest",
    "prompt": prompt,
    "stream": False
}).json()["response"]

print(res)

# 4. Save interaction back to memory
memory.save_entry(f"User asked: '{user_query}' | AI answered: '{res}'", map_name="general", emotional_weight=0.6)
```

---

## ⚙️ Configuration (`config.yaml`)

Manage settings cleanly in `config.yaml` (see `config.example.yaml` for a complete template):

```yaml
storage:
  data_dir: "./data"
  collection_name: "living_memory_core"

embedding:
  model_name: "all-MiniLM-L6-v2"

security:
  encryption_key: ""  # Set passphrase to enable AES encryption at rest

memory_management:
  max_memories: 50000
  min_emotional_weight: 0.15
  protected_maps:
    - "identity"
    - "facts"
    - "preferences"

llm_bridge:
  api_url: "http://localhost:11434/api/generate"
  model_name: "llama3:latest"
  default_context_count: 4
```

All values can also be passed via environment variables (`MEMORY_DATA_DIR`, `MEMORY_ENCRYPTION_KEY`, `MEMORY_EMBEDDING_MODEL`, `MEMORY_MAX_COUNT`, `MEMORY_LLM_URL`).

---

## 🖥️ Standalone Desktop Memory Viewer

Launch the desktop cluster browser with a single command:
```bash
python ui/memory_viewer.py
```
* **4 Professional Themes**: `Synthwave 80s (Dark)`, `Cyber Neon (Dark)`, `Midnight Obsidian (Dark)`, `Clean Minimal (Light)`.
* **Live Metrics Dashboard**: Total memories, 3D cells, active strands, registered maps, encryption status.
* **Access Badges**: Real-time display of retrieval counts (`• 👁️ 3x`).
* **Interactive Strand Inspector**: Modal window displaying all facet links and coupling weights.

---

## 📁 Package Architecture

```
eternal_memory_core/
├── config.yaml               # Active configuration
├── config.example.yaml       # Commented configuration template
├── pyproject.toml            # Modern Python package specification
├── setup.py                  # Standard setuptools installer
├── requirements.txt          # Pinned dependency ranges
├── README.md                 # Product overview & quickstart
├── LICENSE                   # Permissive MIT License
├── core/
│   ├── __init__.py           # Core exports
│   ├── config.py             # Configuration & env var loader
│   ├── exceptions.py         # Custom exception hierarchy
│   ├── logging_config.py     # Clean logger setup
│   ├── memory_engine.py      # Main MemoryCore class
│   ├── spiderweb.py          # 3D Weaire-Phelan spatial lattice
│   ├── encryption.py         # AES/Fernet encryption layer
│   └── pruner.py             # Multi-factor decay algorithm
├── ownership/
│   ├── __init__.py           # Ownership layer exports
│   ├── affective_model.py    # Multi-axis Valence-Arousal-Dominance engine
│   ├── salience_filter.py    # Conversational salience & entity evaluator
│   ├── base_owner.py         # BaseMemoryOwner abstract class
│   └── example_owner.py      # AutonomousCompanion implementation
├── ui/
│   ├── __init__.py
│   └── memory_viewer.py      # Themeable CustomTkinter 3D browser
├── examples/
│   ├── basic_usage.py        # Quickstart demo
│   └── with_local_llm.py     # Local LLM integration walkthrough
└── docs/
    ├── GUIDE.md              # In-depth architectural & developer guide
    ├── API_REFERENCE.md      # Type-annotated API reference manual
    └── ITCH_IO_STORE_PAGE.md # Ready-to-paste itch.io store page listing
```

---

## 📜 License

Distributed under the **MIT License**. Free for personal, academic, and commercial use. See [LICENSE](LICENSE) for details.
