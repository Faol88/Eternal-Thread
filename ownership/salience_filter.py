"""
ownership.salience_filter
~~~~~~~~~~~~~~~~~~~~~~~~~
Evaluates dialogue turns for informational salience, entity density,
and personal significance before committing memories to long-term storage.
"""

import re
from typing import Tuple, Dict, Any

TRIVIAL_PATTERNS = [
    r'^(hi|hello|hey|greetings|yo|sup)[.!]?$',
    r'^(ok|okay|k|cool|nice|neat|sure|yep|yes|no|nope)[.!]?$',
    r'^(thanks|thank you|thx|cheers)[.!]?$',
    r'^(lol|haha|lmao|hehe)[.!]?$',
    r'^(bye|goodbye|cya|see ya|later)[.!]?$'
]


class SalienceFilter:
    """
    Assesses whether a conversational turn contains durable facts, preferences,
    or emotional milestones worthy of being stored in the Living Memory Core.
    """

    @classmethod
    def evaluate(cls, text: str, threshold: float = 0.35) -> Tuple[bool, float, str, Dict[str, Any]]:
        """
        Evaluates input text.
        Returns: (should_store, salience_score, suggested_map, metrics)
        """
        raw = text.strip()
        if len(raw) < 5:
            return False, 0.0, "general", {"reason": "Too short"}

        raw_lower = raw.lower()
        for pat in TRIVIAL_PATTERNS:
            if re.match(pat, raw_lower):
                return False, 0.1, "general", {"reason": "Conversational filler"}

        # 1. Entity & Keyword Density
        words = re.findall(r'\b[a-zA-Z0-9_\-\']{3,}\b', raw)
        word_count = len(words)
        if word_count == 0:
            return False, 0.0, "general", {"reason": "No lexical tokens"}

        # Check for named entities (capitalized words in middle of sentence)
        named_entities = [w for i, w in enumerate(raw.split()) if i > 0 and w and w[0].isupper() and w.isalpha()]
        entity_score = min(0.35, len(named_entities) * 0.10)

        # 2. Key Cognitive Markers
        marker_score = 0.0
        suggested_map = "general"

        if any(k in raw_lower for k in ["i like", "i prefer", "i love", "my favorite", "i hate", "i dislike"]):
            marker_score += 0.40
            suggested_map = "preferences"
        elif any(k in raw_lower for k in ["i am", "my name is", "i work as", "i live in", "my goal is"]):
            marker_score += 0.45
            suggested_map = "identity"
        elif any(k in raw_lower for k in ["building", "designing", "developing", "project", "code", "engine", "repo", "architecture"]):
            marker_score += 0.35
            suggested_map = "projects"
        elif any(k in raw_lower for k in ["physics", "math", "algorithm", "weaire", "phelan", "vector", "gpu", "shader"]):
            marker_score += 0.35
            suggested_map = "tech"
        elif any(k in raw_lower for k in ["why", "meaning", "consciousness", "belief", "ethics", "life"]):
            marker_score += 0.30
            suggested_map = "philosophy"

        # 3. Information Length & Complexity Factor
        length_score = min(0.30, word_count / 30.0)

        # Total Salience
        total_salience = round(min(1.0, entity_score + marker_score + length_score + 0.15), 3)
        should_store = total_salience >= threshold

        metrics = {
            "word_count": word_count,
            "named_entities": len(named_entities),
            "entity_score": round(entity_score, 3),
            "marker_score": round(marker_score, 3),
            "length_score": round(length_score, 3),
            "salience": total_salience
        }

        return should_store, total_salience, suggested_map, metrics
