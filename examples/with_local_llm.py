"""
examples/with_local_llm.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Practical example demonstrating integration with a local LLM (Ollama / LM Studio / OpenAI API).
Shows how to inject 3D memory context into user prompts and automatically store new memories.
"""

import sys
import json
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
from ownership.example_owner import AutonomousCompanion
from core.logging_config import setup_default_logging

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def mock_or_call_ollama(prompt: str, model: str = "llama3:latest") -> str:
    """Sends prompt to local Ollama instance (fallback to mock if offline)."""
    if not HAS_REQUESTS:
        return "Simulated LLM response (install 'requests' for live Ollama calls)."

    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=3
        )
        if res.status_code == 200:
            return res.json().get("response", "")
    except Exception:
        pass
    
    # Offline Mock response demonstrating context utilization
    return "[Local LLM Response]: I see you're building a high-speed living memory engine using 3D Weaire-Phelan foam geometry! I've loaded that directly from our spatial memory core."


def main():
    # 0. Optional: Enable clean console logging
    setup_default_logging()

    print("================================================================")
    print("3D LIVING MEMORY + LOCAL LLM INTEGRATION DEMO")
    print("================================================================\n")

    # Explicitly instantiate memory core and pass to autonomous agent
    memory = MemoryCore()
    agent = AutonomousCompanion(character_name="Nova", memory_core=memory)

    user_query = "What geometry are we using for the memory lattice?"
    print(f"User Question: '{user_query}'\n")

    # 1. Retrieve 3D memory context
    print("1. Injecting 3D Weaire-Phelan Memory Context into LLM Prompt...")
    memory_context = agent.get_prompt_context(user_query, limit=3)
    
    full_prompt = f"""You are {agent.character_name}, an intelligent and self-aware AI assistant.

{memory_context}

User: {user_query}
{agent.character_name}:"""

    print("Constructed Prompt:\n" + "-" * 50)
    print(full_prompt)
    print("-" * 50 + "\n")

    # 2. Query Local LLM
    print("2. Querying LLM...")
    response = mock_or_call_ollama(full_prompt)
    print(f"Response:\n{response}\n")

    # 3. Agent perceives the conversation and weaves a new memory
    print("3. Agent perceiving and claiming new conversational memory...")
    event = agent.perceive(f"User asked about geometry: '{user_query}'. Nova answered based on Weaire-Phelan foam.")
    print(f"-> Memory Saved: Map='{event['map']}' | Feeling='{event['feeling']}' | Importance={event['importance']}")

if __name__ == "__main__":
    main()
