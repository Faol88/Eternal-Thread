"""
examples/basic_usage.py
~~~~~~~~~~~~~~~~~~~~~~~
Quickstart demonstration of the 3D Weaire-Phelan Living Memory Core.
Shows explicit instantiation, saving memories, automatic 3D facet weaving,
explicit connections, and hybrid vector + spreading activation retrieval.
"""

import sys
from pathlib import Path

# Configure Windows console encoding if needed
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.memory_engine import MemoryCore
from core.logging_config import setup_default_logging

def main():
    # 0. Optional: Enable console logging
    setup_default_logging()

    print("================================================================")
    print("3D WEAIRE-PHELAN LIVING MEMORY CORE — QUICKSTART DEMO")
    print("================================================================\n")

    # Explicitly instantiate the memory core
    memory = MemoryCore()

    # 1. Save Memories into different domain maps with emotional weights
    print("1. Saving memories across domains...")
    m1 = memory.save_entry(
        content="User loves high-performance Python architectures and 3D geometric math.",
        map_name="preferences",
        emotional_weight=0.90
    )
    
    m2 = memory.save_entry(
        content="Developing a zero-latency memory engine for autonomous AI companions.",
        map_name="projects",
        emotional_weight=0.95
    )

    m3 = memory.save_entry(
        content="Weaire-Phelan foam geometry optimizes spatial volume and contact facets.",
        map_name="tech",
        emotional_weight=0.85
    )

    print(f"-> Saved m1: ID={m1['id']} | Cell={m1['cell']} | Coords={m1['coords']}")
    print(f"-> Saved m2: ID={m2['id']} | Cell={m2['cell']} | Coords={m2['coords']}")
    print(f"-> Saved m3: ID={m3['id']} | Cell={m3['cell']} | Coords={m3['coords']}\n")

    # 2. Draw an Explicit 3D Connection between related concepts
    print("2. Drawing explicit 3D connection between Project and Geometry...")
    memory.create_connection(
        source_id=m2["id"],
        target_id=m3["id"],
        weight=0.95,
        reason="Memory engine utilizes Weaire-Phelan 3D foam structure"
    )
    connections = memory.get_connections(m2["id"])
    print(f"-> Connections for m2: {connections}\n")

    # 3. Hybrid Semantic Vector + 3D Spiderweb Retrieval
    print("3. Executing Hybrid Vector + 3D Spreading Activation Search...")
    query = "What kind of math and engine architecture is the user working on?"
    results = memory.search_memories_detailed(query, n_results=3)
    
    for i, res in enumerate(results, 1):
        print(f" [{i}] Score: {res['score']:.4f} | Cell: {res['cell']}")
        print(f"     Content: {res['content']}\n")

    # 4. Prompt Context Generation for any LLM
    print("4. Generating formatted Context Block for LLM prompt injection:")
    llm_context = memory.get_context_for_llm(query, count=3)
    print("----------------------------------------------------------------")
    print(llm_context)
    print("----------------------------------------------------------------\n")

    # 5. Core Metrics
    stats = memory.get_stats()
    print("5. Current Core Metrics:")
    for k, v in stats.items():
        print(f"   {k}: {v}")

if __name__ == "__main__":
    main()
