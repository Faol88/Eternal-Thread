"""
ownership.affective_model
~~~~~~~~~~~~~~~~~~~~~~~~~
Multi-Axis Affective Appraisal System (Valence, Arousal, Dominance).
Provides realistic emotional state tracking and mood persistence for AI agents.
"""

import math
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class EmotionVector:
    """Represents a continuous emotional state in VAD space."""
    valence: float     # [-1.0 (negative) to 1.0 (positive)]
    arousal: float     # [0.0 (calm/passive) to 1.0 (excited/intense)]
    dominance: float   # [0.0 (submissive/overwhelmed) to 1.0 (in-control/confident)]
    primary_label: str
    intensity: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valence": round(self.valence, 3),
            "arousal": round(self.arousal, 3),
            "dominance": round(self.dominance, 3),
            "primary_label": self.primary_label,
            "intensity": round(self.intensity, 3)
        }


class AffectiveModel:
    """
    Computes continuous emotional appraisal vectors from dialogue context,
    tracking emotional inertia, mood decay, and personality biases.
    """

    # Lexical affective cues mapped to (Valence, Arousal, Dominance)
    AFFECTIVE_LEXICON = {
        # Positive High Arousal
        "excited": (0.85, 0.90, 0.75, "Excited"),
        "thrilled": (0.90, 0.95, 0.80, "Thrilled"),
        "amazing": (0.80, 0.85, 0.70, "Inspired"),
        "breakthrough": (0.85, 0.85, 0.90, "Triumphant"),
        "victory": (0.80, 0.80, 0.85, "Triumphant"),
        "love": (0.90, 0.75, 0.70, "Affectionate"),
        "awesome": (0.75, 0.80, 0.70, "Inspired"),
        
        # Positive Low Arousal
        "calm": (0.60, 0.15, 0.65, "Serene"),
        "peaceful": (0.70, 0.10, 0.60, "Serene"),
        "grateful": (0.75, 0.35, 0.55, "Grateful"),
        "content": (0.65, 0.20, 0.60, "Content"),
        "relaxed": (0.60, 0.15, 0.55, "Serene"),
        
        # Curious / Cognitive
        "curious": (0.45, 0.60, 0.60, "Curious"),
        "interesting": (0.50, 0.55, 0.55, "Curious"),
        "fascinating": (0.70, 0.70, 0.65, "Wonder"),
        "wonder": (0.65, 0.65, 0.50, "Wonder"),
        "code": (0.30, 0.50, 0.70, "Analytical"),
        "engine": (0.35, 0.55, 0.75, "Analytical"),
        "algorithm": (0.30, 0.50, 0.70, "Analytical"),
        "physics": (0.40, 0.60, 0.75, "Analytical"),
        
        # Negative High Arousal
        "angry": (-0.80, 0.85, 0.75, "Frustrated"),
        "frustrated": (-0.65, 0.75, 0.50, "Frustrated"),
        "difficult": (-0.40, 0.60, 0.45, "Challenged"),
        "bug": (-0.45, 0.65, 0.50, "Challenged"),
        "error": (-0.40, 0.60, 0.45, "Challenged"),
        "crisis": (-0.85, 0.90, 0.30, "Apprehensive"),
        
        # Negative Low Arousal
        "sad": (-0.75, 0.25, 0.25, "Melancholy"),
        "tired": (-0.40, 0.15, 0.30, "Exhausted"),
        "exhausted": (-0.50, 0.10, 0.25, "Exhausted"),
        "disappointed": (-0.60, 0.35, 0.35, "Disappointed"),
        "lonely": (-0.70, 0.30, 0.25, "Melancholy"),
        "confused": (-0.25, 0.50, 0.35, "Confused"),
    }

    INTENSIFIERS = {"very": 1.3, "extremely": 1.5, "really": 1.25, "super": 1.35, "so": 1.2}
    NEGATORS = {"not", "never", "no", "without", "hardly", "barely"}

    def __init__(self, baseline_valence: float = 0.1, baseline_arousal: float = 0.3, baseline_dominance: float = 0.5):
        self.current_v = baseline_valence
        self.current_a = baseline_arousal
        self.current_d = baseline_dominance
        self.mood_inertia = 0.65  # 65% retained mood across conversational turns

    def evaluate_text(self, text: str, explicit_override: Optional[str] = None) -> EmotionVector:
        """Evaluates text to produce a new continuous emotional state vector."""
        if explicit_override:
            return self._from_label(explicit_override)

        tokens = text.lower().split()
        matched_cues = []
        multiplier = 1.0
        negate_next = False

        for i, word in enumerate(tokens):
            clean_w = word.strip(".,!?;:\"'/()[]{}")
            
            if clean_w in self.NEGATORS:
                negate_next = True
                continue

            if clean_w in self.INTENSIFIERS:
                multiplier = self.INTENSIFIERS[clean_w]
                continue

            if clean_w in self.AFFECTIVE_LEXICON:
                v, a, d, label = self.AFFECTIVE_LEXICON[clean_w]
                if negate_next:
                    v = -v * 0.75
                    d = d * 0.8
                    negate_next = False

                matched_cues.append((v * multiplier, a * multiplier, d, label))
                multiplier = 1.0
            else:
                negate_next = False

        if not matched_cues:
            # Decay towards neutral baseline
            self.current_v = (self.current_v * self.mood_inertia) + (0.05 * (1 - self.mood_inertia))
            self.current_a = (self.current_a * self.mood_inertia) + (0.25 * (1 - self.mood_inertia))
            self.current_d = (self.current_d * self.mood_inertia) + (0.50 * (1 - self.mood_inertia))
            label = self._classify_vad(self.current_v, self.current_a, self.current_d)
            return EmotionVector(self.current_v, self.current_a, self.current_d, label, intensity=self.current_a)

        # Average matches
        avg_v = sum(c[0] for c in matched_cues) / len(matched_cues)
        avg_a = sum(c[1] for c in matched_cues) / len(matched_cues)
        avg_d = sum(c[2] for c in matched_cues) / len(matched_cues)

        # Apply emotional inertia
        self.current_v = max(-1.0, min(1.0, (self.current_v * self.mood_inertia) + (avg_v * (1 - self.mood_inertia))))
        self.current_a = max(0.05, min(1.0, (self.current_a * self.mood_inertia) + (avg_a * (1 - self.mood_inertia))))
        self.current_d = max(0.05, min(1.0, (self.current_d * self.mood_inertia) + (avg_d * (1 - self.mood_inertia))))

        dominant_label = matched_cues[-1][3] if matched_cues else self._classify_vad(self.current_v, self.current_a, self.current_d)
        intensity = round(math.sqrt(self.current_v**2 + self.current_a**2) / 1.414, 3)

        return EmotionVector(
            valence=round(self.current_v, 3),
            arousal=round(self.current_a, 3),
            dominance=round(self.current_d, 3),
            primary_label=dominant_label,
            intensity=min(1.0, intensity)
        )

    def _classify_vad(self, v: float, a: float, d: float) -> str:
        if v >= 0.3:
            return "Inspired" if a >= 0.5 else "Content"
        elif v <= -0.3:
            return "Frustrated" if a >= 0.5 else "Reflective"
        else:
            return "Curious" if a >= 0.4 else "Neutral"

    def _from_label(self, label: str) -> EmotionVector:
        for cue, (v, a, d, lbl) in self.AFFECTIVE_LEXICON.items():
            if lbl.lower() == label.lower():
                self.current_v, self.current_a, self.current_d = v, a, d
                return EmotionVector(v, a, d, lbl, intensity=a)
        return EmotionVector(0.0, 0.3, 0.5, label.title(), 0.3)
