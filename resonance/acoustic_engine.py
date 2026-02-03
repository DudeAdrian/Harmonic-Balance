"""
harmonic-balance/resonance/acoustic_engine.py
Advanced acoustic analysis for Harmonic Habitats.
Room modes, Schumann coupling, and Malta oracle acoustics.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from enum import Enum


SCHUMANN_FREQUENCIES = [7.83, 14.3, 20.8, 27.3, 33.8, 39.0, 45.0]

MALTA_ORACLE_ACOUSTICS = {
    'target_resonance_hz': 80.0,
    'reverberation_sec': 6.5,
    'quality_factor': 15.0
}


@dataclass
class RoomMode:
    """A single room mode with frequency and type."""
    frequency_hz: float
    mode_type: str  # 'axial', 'tangential', 'oblique'
    order: Tuple[int, int, int]  # (length, width, height mode numbers)
    amplitude: float = 1.0


@dataclass
class AcousticProfile:
    """Complete acoustic profile for a space."""
    fundamental_hz: float
    modes: List[RoomMode]
    schumann_aligned: bool
    schumann_coupling_strength: float
    rt60_sec: float
    volume_cubic_m: float
    surface_area_sqm: float


class CircularPodAcoustics:
    """
    Acoustic analysis for circular pods (SinglePod typology).
    
    6.5m diameter = 52.8Hz fundamental axial mode
    Height adjustment needed for 7.83Hz coupling
    """
    
    SPEED_OF_SOUND = 343.0  # m/s at 20°C
    
    def __init__(self, diameter: float = 6.5, height: float = 3.2,
                 wall_thickness: float = 0.30):
        self.diameter = diameter
        self.radius = diameter / 2
        self.height = height
        self.wall_thickness = wall_thickness
        self.volume = math.pi * self.radius ** 2 * height
        self.floor_area = math.pi * self.radius ** 2
        self.surface_area = (2 * self.floor_area + math.pi * diameter * height)
    
    def calculate_axial_modes(self, max_order: int = 5) -> List[RoomMode]:
        """Calculate axial modes for circular cylinder."""
        modes = []
        
        # Height modes (axial along cylinder axis)
        for n in range(1, max_order + 1):
            freq = n * self.SPEED_OF_SOUND / (2 * self.height)
            modes.append(RoomMode(
                frequency_hz=round(freq, 2),
                mode_type='axial',
                order=(0, 0, n)
            ))
        
        # Radial modes (across diameter)
        # First zero of J0 Bessel function ≈ 2.405
        for n in range(1, max_order + 1):
            freq = n * 2.405 * self.SPEED_OF_SOUND / (2 * math.pi * self.radius)
            modes.append(RoomMode(
                frequency_hz=round(freq, 2),
                mode_type='radial',
                order=(n, 0, 0)
            ))
        
        # Circumferential modes
        for n in range(1, max_order + 1):
            freq = n * self.SPEED_OF_SOUND / (math.pi * self.diameter)
            modes.append(RoomMode(
                frequency_hz=round(freq, 2),
                mode_type='tangential',
                order=(0, n, 0)
            ))
        
        return sorted(modes, key=lambda m: m.frequency_hz)
    
    def find_schumann_coupling(self, tolerance_hz: float = 0.5) -> Dict:
        """Find how well room modes align with Schumann resonances."""
        modes = self.calculate_axial_modes(max_order=10)
        couplings = []
        
        for schumann_freq in SCHUMANN_FREQUENCIES:
            for mode in modes:
                delta = abs(mode.frequency_hz - schumann_freq)
                if delta < tolerance_hz:
                    couplings.append({
                        'schumann_freq': schumann_freq,
                        'room_mode': mode.frequency_hz,
                        'delta_hz': round(delta, 3),
                        'mode_type': mode.mode_type,
                        'coupling_strength': round(1 - (delta / tolerance_hz), 3)
                    })
        
        return {
            'couplings_found': len(couplings),
            'couplings': couplings,
            'best_coupling': max(couplings, key=lambda x: x['coupling_strength']) if couplings else None
        }
    
    def optimal_height_for_schumann(self, target_hz: float = 7.83) -> float:
        """Calculate optimal height for Schumann coupling."""
        # h = n * c / (2 * f)
        optimal_h = self.SPEED_OF_SOUND / (2 * target_hz)
        return round(optimal_h, 3)
    
    def honeycomb_diffuser_effect(self, cavity_depth: float = 0.15) -> Dict:
        """
        Calculate acoustic diffusion from honeycomb wall cavities.
        Surface geometry acts as acoustic diffuser.
        """
        # Schroeder frequency for diffuser effectiveness
        # f = c / (2 * cavity_depth)
        effective_freq = self.SPEED_OF_SOUND / (2 * cavity_depth)
        
        # Diffusion coefficient estimate
        diffusion = 0.7 + 0.2 * math.sin(2 * math.pi * cavity_depth / 0.3)
        
        return {
            'cavity_depth_m': cavity_depth,
            'effective_frequency_hz': round(effective_freq, 1),
            'diffusion_coefficient': round(diffusion, 2),
            'scattering_pattern': 'wide_angle',
            'applicable_modes': [m for m in self.calculate_axial_modes() 
                                if m.frequency_hz > effective_freq * 0.5]
        }


class MultiPodClusterAcoustics:
    """
    Acoustic analysis for 4-pod cluster arrangement.
    Central gathering space + pod-to-pod isolation.
    """
    
    SPEED_OF_SOUND = 343.0
    
    def __init__(self, pod_diameter: float = 6.0, arrangement_radius: float = 12.0,
                 central_space_diameter: float = 8.0, pod_count: int = 4):
        self.pod_diameter = pod_diameter
        self.arrangement_radius = arrangement_radius
        self.central_space_diameter = central_space_diameter
        self.pod_count = pod_count
        self.central_radius = central_space_diameter / 2
        self.central_volume = math.pi * self.central_radius ** 2 * 3.5
        self.central_area = math.pi * self.central_radius ** 2
    
    def central_gathering_modes(self) -> List[RoomMode]:
        """Calculate modes for central gathering space."""
        modes = []
        height = 3.5  # Open to sky/partial roof
        
        # Axial modes
        for n in range(1, 6):
            freq = n * self.SPEED_OF_SOUND / (2 * height)
            modes.append(RoomMode(
                frequency_hz=round(freq, 2),
                mode_type='axial',
                order=(0, 0, n)
            ))
        
        # Radial modes of circular space
        for n in range(1, 5):
            freq = n * 2.405 * self.SPEED_OF_SOUND / (2 * math.pi * self.central_radius)
            modes.append(RoomMode(
                frequency_hz=round(freq, 2),
                mode_type='radial',
                order=(n, 0, 0)
            ))
        
        return sorted(modes, key=lambda m: m.frequency_hz)
    
    def pod_to_pod_isolation(self, wall_transmission_loss_db: float = 45) -> Dict:
        """Calculate acoustic isolation between adjacent pods."""
        # Distance between pod centers
        pod_separation = 2 * self.arrangement_radius * math.sin(math.pi / self.pod_count)
        
        # Spherical spreading loss
        distance_loss_db = 20 * math.log10(pod_separation / self.pod_diameter)
        
        # Total isolation
        total_isolation = wall_transmission_loss_db + distance_loss_db
        
        return {
            'pod_separation_m': round(pod_separation, 2),
            'distance_loss_db': round(distance_loss_db, 1),
            'wall_transmission_loss_db': wall_transmission_loss_db,
            'total_isolation_db': round(total_isolation, 1),
            'privacy_rating': 'excellent' if total_isolation > 55 else 'good' if total_isolation > 45 else 'fair'
        }
    
    def cluster_resonance(self) -> Dict:
        """Calculate overall cluster resonance characteristics."""
        central_modes = self.central_gathering_modes()
        
        # Check for Schumann alignment in central space
        schumann_aligned = any(
            any(abs(m.frequency_hz - s) < 0.5 for s in SCHUMANN_FREQUENCIES)
            for m in central_modes
        )
        
        return {
            'central_space_modes': central_modes,
            'schumann_aligned': schumann_aligned,
            'coupling_to_pods': 'acoustic_short_circuit_via_openings',
            'recommended_central_height': round(self.SPEED_OF_SOUND / (2 * 7.83 * 2), 2)
        }


class OrganicFamilyAcoustics:
    """
    Acoustic analysis for OrganicFamily typology.
    Spiral staircase as helical waveguide.
    Multi-level mode distribution.
    """
    
    SPEED_OF_SOUND = 343.0
    
    def __init__(self, length: float = 15.0, width: float = 5.6,
                 height_per_level: float = 2.8, levels: int = 2):
        self.length = length
        self.width = width
        self.height_per_level = height_per_level
        self.levels = levels
        self.total_height = height_per_level * levels
        self.floor_area = length * width
        self.total_volume = self.floor_area * self.total_height
    
    def spiral_stair_waveguide(self, stair_diameter: float = 1.2,
                               riser_height: float = 0.18) -> Dict:
        """
        Model spiral staircase as helical acoustic waveguide.
        """
        # Helical path length
        rotations = self.total_height / riser_height / 12  # ~12 steps per rotation
        helix_radius = stair_diameter / 2
        helix_length = math.sqrt((2 * math.pi * helix_radius * rotations) ** 2 + self.total_height ** 2)
        
        # Cutoff frequency for waveguide (simplified)
        # f_c = c / (2 * diameter) for circular duct
        cutoff_freq = self.SPEED_OF_SOUND / (2 * stair_diameter)
        
        # Helical resonances
        resonances = []
        for n in range(1, 6):
            freq = n * self.SPEED_OF_SOUND / (2 * helix_length)
            resonances.append(round(freq, 2))
        
        return {
            'helix_length_m': round(helix_length, 2),
            'rotations': round(rotations, 1),
            'waveguide_diameter_m': stair_diameter,
            'cutoff_frequency_hz': round(cutoff_freq, 1),
            'passband': f"0 - {round(cutoff_freq, 1)} Hz",
            'helical_resonances_hz': resonances,
            'mode_coupling': 'vertical_transmission_between_levels'
        }
    
    def multi_level_modes(self) -> Dict:
        """Calculate mode distribution across multiple levels."""
        all_modes = []
        
        for level in range(1, self.levels + 1):
            level_height = level * self.height_per_level
            level_volume = self.floor_area * self.height_per_level
            
            # Axial modes for this level's ceiling height
            level_modes = []
            for n in range(1, 6):
                freq = n * self.SPEED_OF_SOUND / (2 * self.height_per_level)
                level_modes.append(RoomMode(
                    frequency_hz=round(freq, 2),
                    mode_type='axial_vertical',
                    order=(0, 0, n),
                    amplitude=1.0 / level  # Attenuation with height
                ))
            
            # Length and width modes
            for n in range(1, 4):
                freq_l = n * self.SPEED_OF_SOUND / (2 * self.length)
                freq_w = n * self.SPEED_OF_SOUND / (2 * self.width)
                level_modes.append(RoomMode(
                    frequency_hz=round(freq_l, 2),
                    mode_type='axial_length',
                    order=(n, 0, 0)
                ))
                level_modes.append(RoomMode(
                    frequency_hz=round(freq_w, 2),
                    mode_type='axial_width',
                    order=(0, n, 0)
                ))
            
            all_modes.append({
                'level': level,
                'ceiling_height': self.height_per_level,
                'modes': sorted(level_modes, key=lambda m: m.frequency_hz)
            })
        
        return {
            'level_modes': all_modes,
            'inter_level_coupling': 'through_stairwell_opening',
            'vertical_mode_beating': 'between_level_fundamentals'
        }
    
    def flowing_form_diffusion(self, curvature_radius: float = 8.0) -> Dict:
        """
        Calculate acoustic effects of curved flowing walls.
        """
        # Curved surfaces provide diffusion
        diffusion_coeff = 0.6 + 0.3 * (1 - math.exp(-self.length / curvature_radius))
        
        # Focusing effect at specific distances
        focal_distance = curvature_radius / 2
        
        return {
            'wall_curvature_radius_m': curvature_radius,
            'diffusion_coefficient': round(diffusion_coeff, 2),
            'focal_distance_m': round(focal_distance, 2),
            'sound_focus_locations': [
                (self.length / 2, self.width / 2, focal_distance)
            ],
            'recommendation': 'avoid_seating_at_focal_points_for_uniformity'
        }


class MaltaOracleSimulator:
    """
    Simulate Malta oracle room acoustic characteristics.
    Target: 80Hz resonance, 6.5s reverb time.
    """
    
    def __init__(self, room_dims: Tuple[float, float, float] = (4.5, 3.2, 2.8)):
        self.length, self.width, self.height = room_dims
        self.volume = room_dims[0] * room_dims[1] * room_dims[2]
        self.target_resonance = MALTA_ORACLE_ACOUSTICS['target_resonance_hz']
        self.target_rt60 = MALTA_ORACLE_ACOUSTICS['reverberation_sec']
    
    def calculate_rt60_sabine(self, absorption_coeff: float = 0.05) -> float:
        """Calculate RT60 using Sabine equation."""
        surface_area = 2 * (self.length * self.width + 
                           self.length * self.height + 
                           self.width * self.height)
        
        # Sabine: RT60 = 0.161 * V / (A * S)
        rt60 = 0.161 * self.volume / (absorption_coeff * surface_area)
        return rt60
    
    def target_absorption_for_rt60(self) -> float:
        """Calculate required absorption to achieve 6.5s RT60."""
        surface_area = 2 * (self.length * self.width + 
                           self.length * self.height + 
                           self.width * self.height)
        
        # Rearranged Sabine: A = 0.161 * V / (RT60 * S)
        absorption = 0.161 * self.volume / (self.target_rt60 * surface_area)
        return absorption
    
    def resonance_analysis(self) -> Dict:
        """Analyze room to achieve 80Hz target resonance."""
        c = 343.0
        
        # Find mode closest to 80Hz
        modes = []
        for nx in range(4):
            for ny in range(4):
                for nz in range(4):
                    if nx == 0 and ny == 0 and nz == 0:
                        continue
                    freq = c / 2 * math.sqrt((nx/self.length)**2 + 
                                             (ny/self.width)**2 + 
                                             (nz/self.height)**2)
                    modes.append((freq, (nx, ny, nz)))
        
        modes.sort()
        
        # Find closest to 80Hz
        closest = min(modes, key=lambda m: abs(m[0] - self.target_resonance))
        
        return {
            'target_resonance_hz': self.target_resonance,
            'closest_mode': {
                'frequency_hz': round(closest[0], 2),
                'order': closest[1],
                'delta_hz': round(abs(closest[0] - self.target_resonance), 2)
            },
            'target_rt60_sec': self.target_rt60,
            'required_absorption': round(self.target_absorption_for_rt60(), 3),
            'all_modes_below_150hz': [(round(m[0], 1), m[1]) for m in modes if m[0] < 150]
        }


def full_acoustic_analysis(typology: str, **params) -> Dict:
    """
    Perform complete acoustic analysis for any typology.
    
    Args:
        typology: 'single_pod', 'multi_pod_cluster', 'organic_family', 'malta_oracle'
        **params: Typology-specific parameters
    
    Returns:
        Complete acoustic profile
    """
    if typology == 'single_pod':
        analyzer = CircularPodAcoustics(
            diameter=params.get('diameter', 6.5),
            height=params.get('height', 3.2)
        )
        return {
            'typology': 'single_pod',
            'axial_modes': analyzer.calculate_axial_modes(),
            'schumann_coupling': analyzer.find_schumann_coupling(),
            'optimal_height_for_7.83hz': analyzer.optimal_height_for_schumann(),
            'honeycomb_diffusion': analyzer.honeycomb_diffuser_effect()
        }
    
    elif typology == 'multi_pod_cluster':
        analyzer = MultiPodClusterAcoustics(
            pod_diameter=params.get('pod_diameter', 6.0),
            arrangement_radius=params.get('arrangement_radius', 12.0),
            central_space_diameter=params.get('central_space_diameter', 8.0)
        )
        return {
            'typology': 'multi_pod_cluster',
            'central_gathering_modes': analyzer.central_gathering_modes(),
            'pod_isolation': analyzer.pod_to_pod_isolation(),
            'cluster_resonance': analyzer.cluster_resonance()
        }
    
    elif typology == 'organic_family':
        analyzer = OrganicFamilyAcoustics(
            length=params.get('length', 15.0),
            width=params.get('width', 5.6),
            levels=params.get('levels', 2)
        )
        return {
            'typology': 'organic_family',
            'spiral_stair_waveguide': analyzer.spiral_stair_waveguide(),
            'multi_level_modes': analyzer.multi_level_modes(),
            'flowing_form_diffusion': analyzer.flowing_form_diffusion()
        }
    
    elif typology == 'malta_oracle':
        simulator = MaltaOracleSimulator(
            room_dims=params.get('dims', (4.5, 3.2, 2.8))
        )
        return {
            'typology': 'malta_oracle',
            'resonance_analysis': simulator.resonance_analysis()
        }
    
    else:
        raise ValueError(f"Unknown typology: {typology}")


if __name__ == "__main__":
    print("=== SinglePod Acoustic Analysis ===")
    analysis = full_acoustic_analysis('single_pod', diameter=6.5, height=3.2)
    print(f"Optimal height for 7.83Hz: {analysis['optimal_height_for_7.83hz']}m")
    print(f"Schumann couplings found: {analysis['schumann_coupling']['couplings_found']}")
    
    print("\n=== MultiPodCluster Acoustic Analysis ===")
    analysis = full_acoustic_analysis('multi_pod_cluster')
    print(f"Pod isolation: {analysis['pod_isolation']['total_isolation_db']}dB")
    print(f"Privacy rating: {analysis['pod_isolation']['privacy_rating']}")
    
    print("\n=== OrganicFamily Acoustic Analysis ===")
    analysis = full_acoustic_analysis('organic_family')
    waveguide = analysis['spiral_stair_waveguide']
    print(f"Stair waveguide length: {waveguide['helix_length_m']}m")
    print(f"Waveguide cutoff: {waveguide['cutoff_frequency_hz']}Hz")
    
    print("\n=== Malta Oracle Room Simulation ===")
    analysis = full_acoustic_analysis('malta_oracle')
    res = analysis['resonance_analysis']
    print(f"Target resonance: {res['target_resonance_hz']}Hz")
    print(f"Closest mode: {res['closest_mode']['frequency_hz']}Hz ({res['closest_mode']['order']})")
    print(f"Required absorption for {res['target_rt60_sec']}s RT60: {res['required_absorption']}")
