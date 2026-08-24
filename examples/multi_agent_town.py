import sys
from pathlib import Path

# Ensure we can import the core module
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.memory_engine import MemoryCore

def run_multi_agent_simulation():
    # 1. Initialize a single shared MemoryCore (The Town's Database)
    # Using a temporary memory location for the example
    print("Initializing Multi-Agent Town MemoryCore...")
    shared_core = MemoryCore(data_dir=Path("./data/town_simulation"))
    
    # 2. Save a PUBLIC FACT (No owner, meaning everyone in town knows it)
    print("\n--- The Public Event ---")
    public_event = shared_core.save_entry(
        content="A massive red dragon was seen flying over the eastern mountains this morning.",
        map_name="facts",
        emotional_weight=0.9
    )
    print(f"[PUBLIC] Saved event: A massive red dragon was seen...")

    # 3. Define our Agents and their private thoughts
    print("\n--- Saving Private Agent Personalities ---")
    shared_core.save_entry(
        content="I am a brave Guard. My duty is to protect the townsfolk from monsters at all costs.",
        map_name="identity",
        owner="Guard",
        emotional_weight=1.0
    )
    shared_core.save_entry(
        content="I am a wealthy Bartender. I care most about my gold and keeping my tavern safe.",
        map_name="identity",
        owner="Bartender",
        emotional_weight=0.8
    )
    shared_core.save_entry(
        content="I am a traveling Merchant. I trade secrets and rare goods.",
        map_name="identity",
        owner="Merchant",
        emotional_weight=0.6
    )
    
    # 4. Spreading Activation (Different Reactions to the same Public Fact)
    print("\n--- Agents Reacting to the Word 'dragon' ---")
    
    # The Guard's Context
    guard_context = shared_core.get_context_for_llm("dragon", current_agent="Guard")
    print("\n[GUARD'S LLM CONTEXT]:")
    print(guard_context)
    
    # The Bartender's Context
    bartender_context = shared_core.get_context_for_llm("dragon", current_agent="Bartender")
    print("\n[BARTENDER'S LLM CONTEXT]:")
    print(bartender_context)
    
    # 5. Gossip (Transferring Memories via share_memory)
    print("\n--- The Gossip Mechanic ---")
    secret_mem = shared_core.save_entry(
        content="The King is secretly hoarding magical artifacts in the royal vault.",
        map_name="social",
        owner="Merchant",
        emotional_weight=0.95
    )
    print(f"Merchant learns a secret. Does the Bartender know about the King?")
    
    # Check Bartender's knowledge
    b_knows = shared_core.search("King magical artifacts", current_agent="Bartender")
    print(f"Bartender searches for King: {len(b_knows)} results found.")
    
    print("\nMerchant whispers the secret to the Bartender...")
    shared_core.share_memory(
        source_entry_id=secret_mem["id"],
        to_agent="Bartender",
        reason="Gossip passed at the tavern at midnight"
    )
    
    # Check Bartender's knowledge again
    b_knows_now = shared_core.search("King magical artifacts", current_agent="Bartender")
    print(f"Bartender searches for King again: {len(b_knows_now)} results found.")
    print(f"Retrieved: '{b_knows_now[0]}'")
    
    print("\n--- Simulation Complete ---")
    print(f"Total connections across the multi-agent spiderweb: {len(shared_core.spiderweb.strands)}")

if __name__ == "__main__":
    run_multi_agent_simulation()
