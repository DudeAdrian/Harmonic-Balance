"""
harmonic-balance/resonance/tuner.py
Acoustic and vibrational optimization.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SchumannResonance:
    fundamental: float = 7.83
    harmonics: Tuple[float, ...] = (14.3, 20.8, 27.3, 33.8, 39.0)
    
    def alignment_score(self, room_modes: List[float]) -> float:
        all_freqs = (self.fundamental,) + self.harmonics
        matches = sum(
            1 for mode in room_modes 
            if any(abs(mode - h) < 0.5 for h in all_freqs)
        )
        return matches / len(room_modes) if room_modes else 0.0


class RoomModeCalculator:
    def __init__(self, room_geometry: dict):
        self.geometry = room_geometry
        self.speed_of_sound = 343
    
    def calculate_modes(self, max_freq: float = 50.0) -> List[dict]:
        r = self.geometry.get('radius', 2.5)
        h = self.geometry.get('height', 2.8)
        modes = []
        
        for n in range(1, 10):
            freq = n * self.speed_of_sound / (2 * h)
            if freq > max_freq:
                break
            modes.append({'frequency': freq, 'type': 'axial', 'order': n})
        
        return modes


MALTA_ACOUSTICS = {
    'hagar_qim': {'resonance_hz': 80, 'reverberation_sec': 6.5}
}
