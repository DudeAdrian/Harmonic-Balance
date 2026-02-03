"""
harmonic-balance/terracare/anchor.py
Blockchain-ready design anchoring for Harmonic Habitats.
Generates immutable design hashes and metadata for provenance tracking.
"""

import hashlib
import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid


@dataclass
class DesignAnchor:
    """
    Immutable anchor for a Harmonic Habitat design.
    Contains all parameters needed to regenerate the design.
    """
    # Identity
    anchor_id: str
    design_hash: str
    parent_anchor: Optional[str]  # For design iterations
    
    # Design parameters
    typology: str
    parameters: Dict[str, Any]
    geometry_hash: str
    
    # Harmonic signature
    target_frequency: float
    schumann_aligned: bool
    
    # Compliance
    compliance_status: Dict[str, Any]
    
    # Provenance
    timestamp: str
    version: str
    iteration: int
    
    # Creator (placeholder for wallet integration)
    creator_address: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'anchor_id': self.anchor_id,
            'design_hash': self.design_hash,
            'parent_anchor': self.parent_anchor,
            'typology': self.typology,
            'parameters': self.parameters,
            'geometry_hash': self.geometry_hash,
            'target_frequency': self.target_frequency,
            'schumann_aligned': self.schumann_aligned,
            'compliance_status': self.compliance_status,
            'timestamp': self.timestamp,
            'version': self.version,
            'iteration': self.iteration,
            'creator_address': self.creator_address
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


class DesignHasher:
    """Generate cryptographic hashes of design data."""
    
    @staticmethod
    def hash_geometry(geometry_data: Dict) -> str:
        """
        Generate SHA-256 hash of geometry data.
        Creates deterministic hash for geometry verification.
        """
        # Normalize geometry data for consistent hashing
        normalized = json.dumps(geometry_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_parameters(parameters: Dict) -> str:
        """Generate hash of design parameters."""
        normalized = json.dumps(parameters, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_design_hash(typology: str, parameters: Dict, 
                            geometry_data: Dict) -> str:
        """
        Generate composite design hash.
        Combines typology, parameters, and geometry.
        """
        param_hash = DesignHasher.hash_parameters(parameters)
        geom_hash = DesignHasher.hash_geometry(geometry_data)
        
        composite = f"{typology}:{param_hash}:{geom_hash}"
        return hashlib.sha256(composite.encode('utf-8')).hexdigest()


class AnchorRegistry:
    """
    Registry for design anchors.
    Manages design iterations and prepares for blockchain submission.
    """
    
    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or Path("terracare/anchors")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._anchors: Dict[str, DesignAnchor] = {}
        self._load_existing()
    
    def _load_existing(self):
        """Load existing anchors from storage."""
        if not self.storage_path.exists():
            return
        
        for anchor_file in self.storage_path.glob("*.json"):
            try:
                with open(anchor_file, 'r') as f:
                    data = json.load(f)
                    anchor = DesignAnchor(**data)
                    self._anchors[anchor.anchor_id] = anchor
            except Exception as e:
                print(f"Warning: Could not load anchor {anchor_file}: {e}")
    
    def create_anchor(self, typology: str, parameters: Dict,
                     geometry_data: Dict, compliance_status: Dict,
                     target_frequency: float = 7.83,
                     parent_anchor: Optional[str] = None,
                     creator_address: Optional[str] = None) -> DesignAnchor:
        """
        Create a new design anchor.
        
        Args:
            typology: Design typology name
            parameters: Design parameters dictionary
            geometry_data: Generated geometry data
            compliance_status: Compliance check results
            target_frequency: Target Schumann frequency
            parent_anchor: Previous version anchor ID (for iterations)
            creator_address: Blockchain wallet address (optional)
        
        Returns:
            New DesignAnchor instance
        """
        # Generate IDs and hashes
        anchor_id = str(uuid.uuid4())
        geometry_hash = DesignHasher.hash_geometry(geometry_data)
        design_hash = DesignHasher.generate_design_hash(
            typology, parameters, geometry_data
        )
        
        # Calculate iteration number
        iteration = 1
        if parent_anchor and parent_anchor in self._anchors:
            iteration = self._anchors[parent_anchor].iteration + 1
        
        # Check Schumann alignment
        schumann_aligned = compliance_status.get('schumann_aligned', False)
        
        # Create anchor
        anchor = DesignAnchor(
            anchor_id=anchor_id,
            design_hash=design_hash,
            parent_anchor=parent_anchor,
            typology=typology,
            parameters=parameters,
            geometry_hash=geometry_hash,
            target_frequency=target_frequency,
            schumann_aligned=schumann_aligned,
            compliance_status=compliance_status,
            timestamp=datetime.now(timezone.utc).isoformat(),
            version=f"1.0.{iteration}",
            iteration=iteration,
            creator_address=creator_address
        )
        
        # Store and save
        self._anchors[anchor_id] = anchor
        self._save_anchor(anchor)
        
        return anchor
    
    def _save_anchor(self, anchor: DesignAnchor):
        """Save anchor to file."""
        filepath = self.storage_path / f"{anchor.anchor_id}.json"
        with open(filepath, 'w') as f:
            f.write(anchor.to_json())
    
    def get_anchor(self, anchor_id: str) -> Optional[DesignAnchor]:
        """Retrieve anchor by ID."""
        return self._anchors.get(anchor_id)
    
    def get_design_lineage(self, anchor_id: str) -> List[DesignAnchor]:
        """Get full lineage of a design (all iterations)."""
        lineage = []
        current = self._anchors.get(anchor_id)
        
        while current:
            lineage.append(current)
            if current.parent_anchor:
                current = self._anchors.get(current.parent_anchor)
            else:
                break
        
        return list(reversed(lineage))
    
    def list_anchors(self, typology: str = None) -> List[DesignAnchor]:
        """List all anchors, optionally filtered by typology."""
        anchors = list(self._anchors.values())
        if typology:
            anchors = [a for a in anchors if a.typology == typology]
        return sorted(anchors, key=lambda a: a.timestamp, reverse=True)


class MockLedgerClient:
    """
    Mock blockchain ledger client.
    Prepares and simulates ledger submissions.
    """
    
    def __init__(self, network: str = "mock_harmonic_chain"):
        self.network = network
        self.submissions: List[Dict] = []
    
    def prepare_submission(self, anchor: DesignAnchor) -> Dict:
        """
        Prepare anchor for ledger submission.
        Formats data for blockchain transaction.
        """
        return {
            'network': self.network,
            'transaction_type': 'DESIGN_ANCHOR',
            'payload': {
                'design_hash': anchor.design_hash,
                'geometry_hash': anchor.geometry_hash,
                'typology': anchor.typology,
                'timestamp': anchor.timestamp,
                'creator': anchor.creator_address or 'anonymous',
                'metadata_uri': f"ipfs://{anchor.anchor_id}"  # Placeholder for IPFS
            },
            'estimated_gas': 150000,
            'priority': 'medium'
        }
    
    def submit_to_ledger(self, anchor: DesignAnchor) -> Dict:
        """
        Mock submission to blockchain ledger.
        Returns transaction receipt simulation.
        """
        submission = self.prepare_submission(anchor)
        
        # Simulate transaction
        tx_hash = hashlib.sha256(
            f"{anchor.design_hash}:{time.time()}".encode()
        ).hexdigest()
        
        receipt = {
            'transaction_hash': tx_hash,
            'block_number': 18472931,  # Mock block
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'confirmed',
            'gas_used': 142350,
            'anchor_id': anchor.anchor_id,
            'design_hash': anchor.design_hash
        }
        
        self.submissions.append(receipt)
        return receipt
    
    def verify_on_ledger(self, design_hash: str) -> Optional[Dict]:
        """Verify a design hash exists on the ledger."""
        for submission in self.submissions:
            if submission['design_hash'] == design_hash:
                return {
                    'verified': True,
                    'transaction_hash': submission['transaction_hash'],
                    'block_number': submission['block_number'],
                    'timestamp': submission['timestamp']
                }
        return None


class TerraCareAnchor:
    """
    Main interface for Terracare anchoring system.
    Combines hashing, registry, and ledger preparation.
    """
    
    def __init__(self, storage_path: Path = None):
        self.registry = AnchorRegistry(storage_path)
        self.ledger = MockLedgerClient()
        self.hasher = DesignHasher()
    
    def anchor_design(self, typology: str, parameters: Dict,
                     geometry_data: Dict, compliance_report: Dict,
                     target_frequency: float = 7.83,
                     submit_to_ledger: bool = False) -> Dict:
        """
        Complete anchoring workflow.
        
        Args:
            typology: Design typology
            parameters: Design parameters
            geometry_data: Generated geometry
            compliance_report: Compliance check results
            target_frequency: Target frequency
            submit_to_ledger: Whether to submit to blockchain
        
        Returns:
            Complete anchoring result with IDs and hashes
        """
        # Create anchor
        anchor = self.registry.create_anchor(
            typology=typology,
            parameters=parameters,
            geometry_data=geometry_data,
            compliance_status=compliance_report,
            target_frequency=target_frequency
        )
        
        result = {
            'anchor_id': anchor.anchor_id,
            'design_hash': anchor.design_hash,
            'geometry_hash': anchor.geometry_hash,
            'timestamp': anchor.timestamp,
            'version': anchor.version,
            'stored_locally': True,
            'ledger_submission': None
        }
        
        # Optional ledger submission
        if submit_to_ledger:
            receipt = self.ledger.submit_to_ledger(anchor)
            result['ledger_submission'] = receipt
        
        return result
    
    def verify_design(self, anchor_id: str, current_geometry: Dict) -> Dict:
        """
        Verify design integrity against anchored hash.
        
        Args:
            anchor_id: Anchor to verify against
            current_geometry: Current geometry data to check
        
        Returns:
            Verification result
        """
        anchor = self.registry.get_anchor(anchor_id)
        if not anchor:
            return {'valid': False, 'error': 'Anchor not found'}
        
        current_hash = self.hasher.hash_geometry(current_geometry)
        
        return {
            'valid': current_hash == anchor.geometry_hash,
            'anchor_id': anchor_id,
            'stored_hash': anchor.geometry_hash,
            'current_hash': current_hash,
            'design_hash': anchor.design_hash,
            'timestamp_verified': datetime.now(timezone.utc).isoformat()
        }
    
    def get_design_history(self, anchor_id: str) -> List[Dict]:
        """Get full design history/lineage."""
        lineage = self.registry.get_design_lineage(anchor_id)
        return [anchor.to_dict() for anchor in lineage]


# Convenience functions
def anchor_single_pod(diameter: float = 6.5, height: float = 3.2,
                     geometry_data: Dict = None, compliance: Dict = None) -> Dict:
    """Quick anchor for SinglePod."""
    terracare = TerraCareAnchor()
    
    params = {'diameter': diameter, 'height': height}
    geom = geometry_data or {'type': 'single_pod', 'diameter': diameter, 'height': height}
    comp = compliance or {'schumann_aligned': True, 'compliant': True}
    
    return terracare.anchor_design('single_pod', params, geom, comp)


def anchor_multi_pod_cluster(pod_count: int = 4, arrangement_radius: float = 12.0,
                            geometry_data: Dict = None, compliance: Dict = None) -> Dict:
    """Quick anchor for MultiPodCluster."""
    terracare = TerraCareAnchor()
    
    params = {'pod_count': pod_count, 'arrangement_radius': arrangement_radius}
    geom = geometry_data or {
        'type': 'multi_pod_cluster',
        'pod_count': pod_count,
        'arrangement_radius': arrangement_radius
    }
    comp = compliance or {'schumann_aligned': True, 'compliant': True}
    
    return terracare.anchor_design('multi_pod_cluster', params, geom, comp)


def anchor_organic_family(length: float = 15.0, width: float = 5.6, levels: int = 2,
                         geometry_data: Dict = None, compliance: Dict = None) -> Dict:
    """Quick anchor for OrganicFamily."""
    terracare = TerraCareAnchor()
    
    params = {'length': length, 'width': width, 'levels': levels}
    geom = geometry_data or {
        'type': 'organic_family',
        'length': length,
        'width': width,
        'levels': levels
    }
    comp = compliance or {'schumann_aligned': True, 'compliant': True}
    
    return terracare.anchor_design('organic_family', params, geom, comp)


if __name__ == "__main__":
    print("=== TerraCare Anchoring Demo ===")
    
    # Create anchoring system
    terracare = TerraCareAnchor()
    
    # Anchor a SinglePod design
    print("\n--- Anchoring SinglePod ---")
    result = anchor_single_pod(
        diameter=6.5,
        height=3.2,
        geometry_data={'cells': 24, 'area_sqm': 52.8}
    )
    print(f"Anchor ID: {result['anchor_id']}")
    print(f"Design Hash: {result['design_hash'][:16]}...")
    print(f"Version: {result['version']}")
    
    # Anchor with ledger submission
    print("\n--- Submitting to Ledger ---")
    result = terracare.anchor_design(
        typology='organic_family',
        parameters={'length': 15.0, 'width': 5.6, 'levels': 2},
        geometry_data={'footprint': 84.0, 'volume': 470.4},
        compliance_report={'schumann_aligned': True, 'ntc2018': 'compliant'},
        submit_to_ledger=True
    )
    print(f"Transaction Hash: {result['ledger_submission']['transaction_hash'][:16]}...")
    print(f"Block: {result['ledger_submission']['block_number']}")
    
    # Verify design
    print("\n--- Verification ---")
    verify = terracare.verify_design(
        result['anchor_id'],
        {'footprint': 84.0, 'volume': 470.4}
    )
    print(f"Valid: {verify['valid']}")
    
    # List all anchors
    print("\n--- Registry Contents ---")
    anchors = terracare.registry.list_anchors()
    for anchor in anchors:
        print(f"  {anchor.typology}: {anchor.anchor_id[:8]}... (v{anchor.iteration})")
