"""
ownership.base_owner
~~~~~~~~~~~~~~~~~~~~
Autonomous Character Agency Layer for the 3D Living Memory Core.
Provides affective state modeling, salience-filtered perception,
thematic domain routing, and associative memory consolidation during reflection.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from core.memory_engine import MemoryCore
from .affective_model import AffectiveModel, EmotionVector
from .salience_filter import SalienceFilter


class BaseMemoryOwner(ABC):
    """
    Abstract base class for AI agents, NPCs, and companions that possess
    autonomous memory ownership, multi-axis affective states, and reflection capabilities.
    """

    def __init__(
        self,
        character_name: str,
        memory_core: MemoryCore,
        salience_threshold: float = 0.30
    ):
        if memory_core is None:
            raise ValueError(
                f"BaseMemoryOwner for '{character_name}' requires an explicit MemoryCore instance. "
                "Example: memory = MemoryCore(); owner = AutonomousCompanion(character_name='...', memory_core=memory)"
            )
        self.character_name = character_name
        self.memory = memory_core
        self.affective_model = AffectiveModel()
        self.salience_threshold = salience_threshold
        self.current_emotion = EmotionVector(0.1, 0.3, 0.5, "Neutral", 0.3)
        self.recent_perceptions: List[str] = []

    def perceive(
        self,
        text: str,
        emotional_override: Optional[str] = None,
        force_store: bool = False
    ) -> Dict[str, Any]:
        """
        Perceives a dialogue turn, assesses affective resonance (VAD),
        filters for information salience, and claims the memory if meaningful.
        """
        # 1. Affective Appraisal (Valence, Arousal, Dominance)
        self.current_emotion = self.affective_model.evaluate_text(text, explicit_override=emotional_override)

        # 2. Salience Evaluation
        should_store, salience_score, suggested_map, salience_metrics = SalienceFilter.evaluate(
            text,
            threshold=self.salience_threshold
        )

        saved_info = None
        if should_store or force_store:
            # Map emotional intensity to memory importance
            calculated_importance = min(1.0, max(0.2, (salience_score * 0.6) + (self.current_emotion.intensity * 0.4)))
            
            saved_info = self.claim_memory(
                content=text,
                map_name=suggested_map,
                importance=calculated_importance,
                tags=[self.current_emotion.primary_label.lower()]
            )
            
            # Form associative strand with recent perception if thematic affinity exists
            new_id = saved_info.get("id")
            if new_id and self.recent_perceptions:
                prev_id = self.recent_perceptions[-1]
                self.associate_memories(
                    source_id=new_id,
                    target_id=prev_id,
                    reason=f"Conversational continuity during mood [{self.current_emotion.primary_label}]",
                    strength=0.75
                )

            if new_id:
                self.recent_perceptions.append(new_id)
                if len(self.recent_perceptions) > 10:
                    self.recent_perceptions.pop(0)

        return {
            "character": self.character_name,
            "stored": should_store or force_store,
            "memory_id": saved_info.get("id") if saved_info else None,
            "map": suggested_map,
            "emotion": self.current_emotion.to_dict(),
            "salience": salience_score,
            "salience_metrics": salience_metrics
        }

    def claim_memory(
        self,
        content: str,
        map_name: str = "general",
        importance: float = 0.7,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Stores a memory entry explicitly attributed to this character via metadata,
        keeping the raw content unmutated and semantically clean.
        """
        return self.memory.save_entry(
            content=content.strip(),
            map_name=map_name,
            emotional_weight=importance,
            tags=tags,
            owner=self.character_name
        )

    def associate_memories(
        self,
        source_id: str,
        target_id: str,
        reason: str = "",
        strength: float = 0.85
    ) -> bool:
        """Draws an explicit 3D associative strand connection between two memories."""
        attributed_reason = f"[{self.character_name}] {reason}" if reason else f"Associated by {self.character_name}"
        return self.memory.create_connection(
            source_id=source_id,
            target_id=target_id,
            weight=strength,
            reason=attributed_reason
        )

    def create_personal_map(self, map_name: str, description: str = "", x_coord: Optional[float] = None) -> bool:
        """Registers a personal domain map specifically for this character's thematic reflections."""
        desc = f"Personal domain map for {self.character_name}: {description}" if description else f"Owned by {self.character_name}"
        return self.memory.create_map(
            map_name=map_name,
            description=desc,
            x_coord=x_coord
        )

    def recall(self, query: str, limit: int = 4) -> List[str]:
        """Recalls relevant memories using hybrid vector similarity + 3D spreading activation."""
        return self.memory.search_memories(query, n_results=limit)

    def get_prompt_context(self, current_topic: str = "", limit: int = 4) -> str:
        """Builds a formatted memory prompt context block enriched with current emotional state."""
        raw_context = self.memory.get_context_for_llm(query=current_topic, count=limit)
        mood_str = f"[CURRENT MOOD: {self.current_emotion.primary_label} (Valence: {self.current_emotion.valence:+.2f}, Intensity: {self.current_emotion.intensity:.2f})]"
        return f"{mood_str}\n{raw_context}"

    def reflect_on_memories(
        self,
        topic: Optional[str] = None,
        limit: int = 6,
        similarity_threshold: float = 0.60
    ) -> Dict[str, Any]:
        """
        Autonomous Cognitive Reflection:
        1. Retrieves candidate memories on a topic or general experience.
        2. Discovers non-obvious cross-domain associations.
        3. Strengthens 3D spiderweb strands between related insights.
        """
        query = topic or "important concepts, projects, and experiences"
        candidates = self.memory.search_memories_detailed(query, n_results=limit)
        
        established_links = []
        if len(candidates) >= 2:
            for i in range(len(candidates)):
                for j in range(i + 1, len(candidates)):
                    m1 = candidates[i]
                    m2 = candidates[j]
                    
                    # Compute cross-memory affinity based on score proximity and shared domain
                    score_diff = abs(m1.get("score", 0.0) - m2.get("score", 0.0))
                    same_map = (m1.get("map") == m2.get("map"))
                    
                    if score_diff < 0.20 or same_map:
                        coupling = round(0.70 + (0.20 if same_map else 0.0) - (score_diff * 0.5), 3)
                        reason = f"Reflective consolidation: related thematic focus ({m1.get('map')} & {m2.get('map')})"
                        
                        self.associate_memories(
                            source_id=m1["id"],
                            target_id=m2["id"],
                            reason=reason,
                            strength=coupling
                        )
                        established_links.append((m1["id"], m2["id"], coupling))

        return {
            "topic": query,
            "candidates_reviewed": len(candidates),
            "consolidated_links": established_links,
            "current_feeling": self.current_emotion.primary_label
        }
