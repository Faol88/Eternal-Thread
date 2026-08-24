# 📖 Eternal Living Memory Core — Architectural & Developer Guide

**Author**: Faol88 (K.N.A.M) | Kevin Nuydens  
**Version**: 1.0.0 (Commercial itch.io & Open Source Edition)  
**License**: MIT License  

---

## 🧭 Table of Contents
1. [Core Philosophy & Architecture](#1-core-philosophy--architecture)
2. [The 3D Continuous Coordinate Lattice](#2-the-3d-continuous-coordinate-lattice)
3. [Domain Maps & Spatial Anchors](#3-domain-maps--spatial-anchors)
4. [2-Stage Spreading Activation Retrieval](#4-2-stage-spreading-activation-retrieval)
5. [Retrieval Reinforcement & Spaced Repetition](#5-retrieval-reinforcement--spaced-repetition)
6. [The Character Agency / Ownership Layer](#6-the-character-agency--ownership-layer)
   - [Valence–Arousal–Dominance (VAD) Affective Model](#valencearousaldominance-vad-affective-model)
   - [Conversational Salience Filter](#conversational-salience-filter)
   - [Autonomous Reflection & Associative Consolidation](#autonomous-reflection--associative-consolidation)
7. [Zero-Knowledge Encryption & Multi-Factor Pruning](#7-zero-knowledge-encryption--multi-factor-pruning)
8. [Integration Blueprints (Ollama, LM Studio, FastAPI, Discord)](#8-integration-blueprints)
9. [Configuration & Performance Tuning](#9-configuration--performance-tuning)

---

## 1. Core Philosophy & Architecture

Traditional AI memory architectures suffer from **flat indexing**: past conversations are stored as disconnected database rows. Flat RAG systems search exclusively using vector cosine similarity, missing associative relationships, thematic depth, and emotional significance.

The **3D Living Memory Core** introduces **Topological Associative Memory**:
* Thoughts occupy continuous 3D physical coordinates $(X, Y, Z) \in [-1.0, 1.0]^3$.
* Memories form **spatial clusters** inside 3D Weaire–Phelan foam octants.
* Explicit and semantic connections create an **associative spiderweb graph**.
* Retrieval blends **vector cosine similarity** with **graph energy diffusion (spreading activation)**.
* Memories gain **spaced-repetition reinforcement** every time they are retrieved.

---

## 2. The 3D Continuous Coordinate Lattice

Every memory is computed into 3 continuous spatial coordinates $(X, Y, Z)$:
$$X = 	ext{Domain Anchor} + \Delta_{	ext{content hash}}$$
$$Y = (2 	imes 	ext{Emotional Weight}) - 1.0$$
$$Z = 1.0 - \left(rac{	ext{Days Elapsed}}{30.0}ight)$$

### The Three Axes:
1. **$X$-Axis (Cognitive Domain Map)**: Thematic category from left to right.
2. **$Y$-Axis (Emotional Resonance)**: Trivial notes sink toward `-1.0`; deeply cherished memories rise toward `+1.0`.
3. **$Z$-Axis (Temporal Depth)**: Fresh impressions linger near `+1.0`; memories older than 60 days sink to `-1.0`.

### Weaire–Phelan Spatial Octant Cells
Memories automatically sort into cells like:
* `WeairePhelan_East_High_Recent`: High-importance, recent technical or project memory.
* `WeairePhelan_West_High_Deep`: Deeply cherished foundational identity memory.
* `WeairePhelan_Core_Low_Recent`: Fleeting everyday conversational remark.

---

## 3. Domain Maps & Spatial Anchors

Domain maps allow categorizing thoughts without rigid database schemas.

### Default Built-in Maps:
| Map Name | $X$-Coordinate | Description |
|:---|:---:|:---|
| `identity` | `-0.85` | Core facts about the user and AI persona |
| `facts` | `-0.80` | Verified background knowledge & rules |
| `preferences` | `-0.45` | Likes, dislikes, preferred aesthetics |
| `philosophy` | `-0.25` | Worldview, ethics, deep musings |
| `general` | `0.00` | Conversational everyday thoughts |
| `creative` | `+0.35` | Brainstorming, stories, creative ideas |
| `social` | `+0.55` | Bonds, interpersonal milestones |
| `emotional` | `+0.60` | Direct feelings & expressions |
| `projects` | `+0.85` | Active tasks, roadmaps, code repos |
| `tech` | `+0.85` | Architecture, code snippets, hardware |

### Registering Custom Maps:
```python
memory.create_map("gaming", description="Game development & strategy", x_coord=0.40)
```

---

## 4. 2-Stage Spreading Activation Retrieval

When searching for memories:
1. **Vector Seed Lookup**: ChromaDB embeds the query via `all-MiniLM-L6-v2` and selects the top $N$ seed nodes.
2. **Graph Spreading Activation**: Energy radiates outward from seed nodes along 3D facet strands. Neighboring nodes connected by concept keywords or spatial proximity receive decayed activation scores:
   $$	ext{Score}_{	ext{neighbor}} = 	ext{Score}_{	ext{seed}} 	imes 	ext{Coupling}_{	ext{strand}} 	imes 0.82$$
3. **Hybrid Re-ranking**: Final ranking combines vector distance ($55\%$), graph traversal energy ($30\%$), and emotional resonance ($15\%$).

---

## 5. Retrieval Reinforcement & Spaced Repetition

Every memory possesses an internal `access_count` integer and a `last_accessed` timestamp:
* When a memory is created via `save_entry()`, it starts with `access_count = 1`.
* Each time that memory is returned by `search_memories_detailed()`, `get_entry()`, or `get_context_for_llm()`, its `access_count` increments automatically and persists to disk.
* Frequently retrieved memories earn **spaced-repetition retention bonuses**, shielding them from pruning.

---

## 6. The Character Agency / Ownership Layer

Located in `ownership/`, this subsystem gives AI companions and game NPCs genuine cognitive agency.

### Valence–Arousal–Dominance (VAD) Affective Model
Replaces brittle keyword matching with continuous 3-axis emotional state tracking:
* **Valence** $\in [-1.0, 1.0]$: Negative (unpleasant) to Positive (pleasant).
* **Arousal** $\in [0.0, 1.0]$: Calm/passive to Excited/intense.
* **Dominance** $\in [0.0, 1.0]$: Overwhelmed to Confident/in-control.
* **Mood Inertia**: Mood transitions smoothly across conversational turns ($65\%$ retention).

### Conversational Salience Filter
* Assesses entity density, cognitive markers (`"I prefer"`, `"I am"`, `"designing"`), and sentence length.
* Automatically discards conversational filler (`"hi"`, `"ok cool"`, `"thanks"`) while preserving meaningful thoughts.

### Autonomous Reflection & Associative Consolidation
The `reflect_on_memories()` routine:
1. Wanders the memory space and retrieves candidate memories on a topic.
2. Evaluates cross-memory pairwise semantic similarity and shared domain context.
3. Automatically connects related thoughts with new 3D associative graph strands.

```python
from core.memory_engine import MemoryCore
from ownership.example_owner import AutonomousCompanion

memory = MemoryCore()
companion = AutonomousCompanion(character_name="Aria", memory_core=memory)

# Perceive interaction
result = companion.perceive("We solved the physics engine bug! It runs at 120 FPS now!")
print(f"Emotion: {result['emotion']['primary_label']} | Map: {result['map']}")

# Consolidate memories during reflection
reflection = companion.reflect_on_memories(topic="physics and engine performance")
print(f"Consolidated links: {len(reflection['consolidated_links'])}")
```

---

## 7. Zero-Knowledge Encryption & Multi-Factor Pruning

### Encryption (Fernet AES-128-CBC + HMAC-SHA256)
```python
memory = MemoryCore(encryption_key="my-secret-passphrase")
```
Documents and metadata are encrypted before writing to disk and decrypted on-the-fly during search.

### Multi-Factor Pruning Formula:
$$	ext{Retention} = (	ext{Weight} 	imes 0.40) + (	ext{Strand Density} 	imes 0.25) + (	ext{Access Count} 	imes 0.20) + (	ext{Recency} 	imes 0.15)$$

```python
# Purge decayed memories
report = memory.prune_memories(min_emotional_weight=0.15, max_memories=50000)
print(f"Pruned: {report['pruned_count']} | Remaining: {report['remaining_count']}")
```

---

## 8. Integration Blueprints

### Ollama Integration
```python
import requests
from core.memory_engine import MemoryCore

memory = MemoryCore()

def chat_with_ollama(user_msg: str) -> str:
    ctx = memory.get_context_for_llm(user_msg, count=3)
    prompt = f"{ctx}\n\nUser: {user_msg}\nAI:"
    
    res = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3:latest",
        "prompt": prompt,
        "stream": False
    }).json()
    
    answer = res["response"]
    memory.save_entry(f"User: '{user_msg}' | AI: '{answer}'", map_name="general", emotional_weight=0.6)
    return answer
```

---

## 9. Configuration & Performance Tuning

```yaml
storage:
  data_dir: "./data"
  collection_name: "living_memory_core"

embedding:
  model_name: "all-MiniLM-L6-v2"

memory_management:
  max_memories: 50000
  min_emotional_weight: 0.15
  protected_maps:
    - "identity"
    - "facts"
    - "preferences"
```
