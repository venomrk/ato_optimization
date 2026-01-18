"""
Interactive Chemistry Engine
Simulates chemical reactions, atomic structures, and reaction parameters in real-time.
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime
import json


class ChemicalState(str, Enum):
    SOLID = "solid"
    LIQUID = "liquid"
    GAS = "gas"
    PLASMA = "plasma"
    AQUEOUS = "aqueous"


class BondType(str, Enum):
    COVALENT = "covalent"
    IONIC = "ionic"
    METALLIC = "metallic"
    HYDROGEN = "hydrogen"
    VAN_DER_WAALS = "van_der_waals"


@dataclass
class Atom:
    """Represents an individual atom with quantum properties."""
    symbol: str
    atomic_number: int
    mass: float
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    charge: float = 0.0
    electron_configuration: str = ""
    valence_electrons: int = 0
    electronegativity: float = 0.0
    
    def __post_init__(self):
        if not self.electron_configuration:
            self.electron_configuration = self._get_electron_config()
        if not self.valence_electrons:
            self.valence_electrons = self._calculate_valence()
    
    def _get_electron_config(self) -> str:
        """Get electron configuration for the atom."""
        configs = {
            1: "1s¹", 6: "1s² 2s² 2p²", 7: "1s² 2s² 2p³", 8: "1s² 2s² 2p⁴",
            11: "1s² 2s² 2p⁶ 3s¹", 12: "1s² 2s² 2p⁶ 3s²",
            17: "1s² 2s² 2p⁶ 3s² 3p⁵", 19: "[Ar] 4s¹", 20: "[Ar] 4s²"
        }
        return configs.get(self.atomic_number, f"[Complex: Z={self.atomic_number}]")
    
    def _calculate_valence(self) -> int:
        """Calculate valence electrons."""
        valence_map = {1: 1, 6: 4, 7: 5, 8: 6, 11: 1, 12: 2, 17: 7, 19: 1, 20: 2}
        return valence_map.get(self.atomic_number, 0)


@dataclass
class Bond:
    """Represents a chemical bond between atoms."""
    atom1_id: str
    atom2_id: str
    bond_type: BondType
    bond_order: int = 1
    bond_length: float = 0.0
    bond_energy: float = 0.0
    polarity: float = 0.0
    
    def calculate_bond_energy(self, atom1: Atom, atom2: Atom) -> float:
        """Calculate bond dissociation energy."""
        base_energies = {
            BondType.COVALENT: 350.0,
            BondType.IONIC: 500.0,
            BondType.HYDROGEN: 20.0,
            BondType.METALLIC: 200.0,
            BondType.VAN_DER_WAALS: 5.0
        }
        return base_energies.get(self.bond_type, 100.0) * self.bond_order


@dataclass
class Molecule:
    """Represents a molecule with atoms and bonds."""
    name: str
    formula: str
    atoms: List[Atom] = field(default_factory=list)
    bonds: List[Bond] = field(default_factory=list)
    state: ChemicalState = ChemicalState.SOLID
    temperature: float = 298.15  # Kelvin
    pressure: float = 101325.0  # Pascal
    pH: Optional[float] = None
    color: str = "#FFFFFF"
    molecular_weight: float = 0.0
    
    def __post_init__(self):
        if not self.molecular_weight:
            self.molecular_weight = sum(atom.mass for atom in self.atoms)
    
    def get_3d_structure(self) -> Dict[str, Any]:
        """Generate 3D molecular structure for visualization."""
        return {
            "atoms": [
                {
                    "symbol": atom.symbol,
                    "position": atom.position,
                    "charge": atom.charge,
                    "color": self._get_atom_color(atom.symbol)
                }
                for atom in self.atoms
            ],
            "bonds": [
                {
                    "atom1": bond.atom1_id,
                    "atom2": bond.atom2_id,
                    "type": bond.bond_type.value,
                    "order": bond.bond_order
                }
                for bond in self.bonds
            ]
        }
    
    def _get_atom_color(self, symbol: str) -> str:
        """CPK coloring scheme for atoms."""
        colors = {
            "H": "#FFFFFF", "C": "#909090", "N": "#3050F8", "O": "#FF0D0D",
            "F": "#90E050", "Cl": "#1FF01F", "Br": "#A62929", "I": "#940094",
            "S": "#FFFF30", "P": "#FF8000", "Na": "#AB5CF2", "Mg": "#8AFF00",
            "Ca": "#3DFF00", "Fe": "#E06633", "Cu": "#C88033", "Zn": "#7D80B0"
        }
        return colors.get(symbol, "#FF1493")


@dataclass
class Reaction:
    """Represents a chemical reaction."""
    reactants: List[Molecule]
    products: List[Molecule]
    reaction_type: str
    activation_energy: float
    enthalpy_change: float
    entropy_change: float
    rate_constant: float
    equilibrium_constant: Optional[float] = None
    mechanism: List[str] = field(default_factory=list)
    
    def calculate_gibbs_free_energy(self, temperature: float = 298.15) -> float:
        """Calculate ΔG = ΔH - TΔS"""
        return self.enthalpy_change - (temperature * self.entropy_change)
    
    def is_spontaneous(self, temperature: float = 298.15) -> bool:
        """Check if reaction is spontaneous (ΔG < 0)."""
        return self.calculate_gibbs_free_energy(temperature) < 0
    
    def get_reaction_equation(self) -> str:
        """Generate balanced chemical equation."""
        reactant_str = " + ".join([m.formula for m in self.reactants])
        product_str = " + ".join([m.formula for m in self.products])
        arrow = "⇌" if self.equilibrium_constant else "→"
        return f"{reactant_str} {arrow} {product_str}"


class ChemistryEngine:
    """Main chemistry simulation engine."""
    
    def __init__(self):
        self.molecules: Dict[str, Molecule] = {}
        self.reactions: List[Reaction] = []
        self.temperature = 298.15
        self.pressure = 101325.0
        self.time_step = 0.001  # seconds
        
    def add_molecule(self, molecule: Molecule) -> str:
        """Add a molecule to the simulation."""
        mol_id = f"{molecule.name}_{len(self.molecules)}"
        self.molecules[mol_id] = molecule
        return mol_id
    
    def create_water_molecule(self) -> Molecule:
        """Create H2O molecule with proper structure."""
        h1 = Atom("H", 1, 1.008, position=(-0.757, 0.586, 0.0))
        h2 = Atom("H", 1, 1.008, position=(0.757, 0.586, 0.0))
        o = Atom("O", 8, 15.999, position=(0.0, 0.0, 0.0))
        
        bond1 = Bond("H1", "O", BondType.COVALENT, bond_order=1, bond_length=0.958)
        bond2 = Bond("H2", "O", BondType.COVALENT, bond_order=1, bond_length=0.958)
        
        return Molecule(
            name="Water",
            formula="H₂O",
            atoms=[h1, o, h2],
            bonds=[bond1, bond2],
            state=ChemicalState.LIQUID,
            color="#ADD8E6",
            pH=7.0
        )
    
    def create_sodium_chloride(self) -> Molecule:
        """Create NaCl ionic compound."""
        na = Atom("Na", 11, 22.990, charge=1.0, position=(-1.0, 0.0, 0.0))
        cl = Atom("Cl", 17, 35.453, charge=-1.0, position=(1.0, 0.0, 0.0))
        
        bond = Bond("Na", "Cl", BondType.IONIC, bond_order=1, bond_length=2.36)
        
        return Molecule(
            name="Sodium Chloride",
            formula="NaCl",
            atoms=[na, cl],
            bonds=[bond],
            state=ChemicalState.SOLID,
            color="#F0F0F0"
        )
    
    def simulate_reaction(
        self, 
        reactant_ids: List[str], 
        temperature: float = 298.15
    ) -> Dict[str, Any]:
        """
        Simulate a chemical reaction and return detailed results.
        
        Returns WHY, WHAT, and HOW the reaction occurs.
        """
        reactants = [self.molecules[rid] for rid in reactant_ids if rid in self.molecules]
        
        if not reactants:
            return {"error": "No valid reactants found"}
        
        # Analyze reaction
        reaction_analysis = self._analyze_reaction(reactants, temperature)
        
        # Simulate molecular dynamics
        dynamics = self._simulate_molecular_dynamics(reactants, steps=100)
        
        # Calculate energy changes
        energy_profile = self._calculate_energy_profile(reactants, temperature)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "reactants": [r.formula for r in reactants],
            "analysis": reaction_analysis,
            "dynamics": dynamics,
            "energy_profile": energy_profile,
            "visualization_data": self._get_visualization_data(reactants, dynamics)
        }
    
    def _analyze_reaction(self, reactants: List[Molecule], temperature: float) -> Dict[str, Any]:
        """
        Detailed analysis explaining WHY and HOW the reaction occurs.
        """
        analysis = {
            "what_happens": [],
            "why_it_happens": [],
            "how_it_happens": [],
            "atomic_interactions": [],
            "energy_considerations": {}
        }
        
        # WHAT happens
        for mol in reactants:
            analysis["what_happens"].append({
                "molecule": mol.formula,
                "state": mol.state.value,
                "atoms": len(mol.atoms),
                "bonds": len(mol.bonds),
                "molecular_weight": mol.molecular_weight
            })
        
        # WHY it happens (thermodynamics)
        analysis["why_it_happens"] = [
            "Molecules collide due to thermal motion at given temperature",
            f"Temperature {temperature}K provides kinetic energy for bond breaking",
            "Electronegativity differences drive electron transfer",
            "System moves toward lower Gibbs free energy state",
            "Entropy change favors product formation"
        ]
        
        # HOW it happens (mechanism)
        analysis["how_it_happens"] = [
            "Step 1: Molecules approach through diffusion",
            "Step 2: Collision orientation must be favorable",
            "Step 3: Activation energy barrier must be overcome",
            "Step 4: Bonds break in reactants (endothermic)",
            "Step 5: New bonds form in products (exothermic)",
            "Step 6: Products separate and stabilize"
        ]
        
        # Atomic-level interactions
        for mol in reactants:
            for atom in mol.atoms:
                analysis["atomic_interactions"].append({
                    "atom": atom.symbol,
                    "electrons": atom.electron_configuration,
                    "valence": atom.valence_electrons,
                    "electronegativity": atom.electronegativity,
                    "bonding_capacity": atom.valence_electrons,
                    "charge": atom.charge
                })
        
        return analysis
    
    def _simulate_molecular_dynamics(
        self, 
        molecules: List[Molecule], 
        steps: int = 100
    ) -> Dict[str, Any]:
        """Simulate molecular motion and interactions."""
        trajectory = []
        
        for step in range(steps):
            positions = {}
            for mol in molecules:
                for i, atom in enumerate(mol.atoms):
                    # Simple Brownian motion
                    dx = np.random.normal(0, 0.1)
                    dy = np.random.normal(0, 0.1)
                    dz = np.random.normal(0, 0.1)
                    
                    new_pos = (
                        atom.position[0] + dx,
                        atom.position[1] + dy,
                        atom.position[2] + dz
                    )
                    
                    positions[f"{mol.name}_{i}"] = new_pos
            
            trajectory.append({
                "step": step,
                "time": step * self.time_step,
                "positions": positions
            })
        
        return {
            "total_steps": steps,
            "timestep": self.time_step,
            "trajectory": trajectory[::10],  # Sample every 10th frame
            "motion_type": "Brownian motion with thermal fluctuations"
        }
    
    def _calculate_energy_profile(
        self, 
        molecules: List[Molecule], 
        temperature: float
    ) -> Dict[str, Any]:
        """Calculate reaction energy profile."""
        
        # Calculate total bond energies
        reactant_energy = sum(
            sum(bond.calculate_bond_energy(mol.atoms[0], mol.atoms[1]) 
                for bond in mol.bonds)
            for mol in molecules
        )
        
        # Estimate activation energy (simplified)
        activation_energy = reactant_energy * 0.3
        
        # Estimate product energy (assume exothermic)
        product_energy = reactant_energy * 0.85
        
        return {
            "reactant_energy_kJ": reactant_energy,
            "activation_energy_kJ": activation_energy,
            "product_energy_kJ": product_energy,
            "enthalpy_change_kJ": product_energy - reactant_energy,
            "is_exothermic": product_energy < reactant_energy,
            "thermal_energy_kJ": 8.314 * temperature / 1000,  # RT
            "profile_points": [
                {"x": 0, "y": reactant_energy, "label": "Reactants"},
                {"x": 0.5, "y": activation_energy, "label": "Transition State"},
                {"x": 1.0, "y": product_energy, "label": "Products"}
            ]
        }
    
    def _get_visualization_data(
        self, 
        molecules: List[Molecule], 
        dynamics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate data for 3D visualization."""
        return {
            "molecules": [mol.get_3d_structure() for mol in molecules],
            "animation_frames": dynamics["trajectory"],
            "camera_position": {"x": 0, "y": 0, "z": 10},
            "lighting": {
                "ambient": 0.4,
                "directional": 0.6,
                "specular": 0.8
            }
        }
    
    def explain_reaction(
        self, 
        reactant_formulas: List[str], 
        product_formulas: List[str]
    ) -> str:
        """
        Generate detailed natural language explanation of reaction.
        """
        explanation = f"""
🧪 CHEMICAL REACTION EXPLANATION

REACTANTS: {' + '.join(reactant_formulas)}
PRODUCTS: {' + '.join(product_formulas)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 WHAT HAPPENS:
The reactant molecules interact and transform into product molecules through
breaking and forming of chemical bonds. Atoms are rearranged but conserved
(Law of Conservation of Mass).

🔬 WHY IT HAPPENS:
1. THERMODYNAMIC DRIVING FORCE:
   - The reaction proceeds because the products have lower Gibbs free energy
   - ΔG = ΔH - TΔS must be negative for spontaneity
   - Entropy increases as molecules become more disordered

2. ELECTRONIC FACTORS:
   - Atoms seek stable electron configurations (octet rule)
   - Electronegativity differences drive electron transfer
   - Bond formation releases energy (exothermic)

3. KINETIC FEASIBILITY:
   - Molecules have sufficient thermal energy to overcome activation barrier
   - Proper collision orientation allows bond breaking/forming
   - Catalysts can lower activation energy

⚡ HOW IT HAPPENS (MECHANISM):

Step 1: MOLECULAR COLLISION
   - Reactant molecules diffuse through solution/gas
   - Random thermal motion brings molecules together
   - Only effective collisions lead to reaction

Step 2: ACTIVATION COMPLEX FORMATION
   - Molecules reach transition state (highest energy)
   - Partial bonds form while old bonds weaken
   - Electrons begin to redistribute

Step 3: BOND BREAKING & FORMING
   - Old bonds break (requires energy input)
   - New bonds form (releases energy)
   - Net energy change = ΔH (enthalpy of reaction)

Step 4: PRODUCT FORMATION
   - New molecules stabilize in lower energy state
   - Excess energy released as heat/light
   - Products separate and diffuse away

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 ATOMIC-LEVEL DETAILS:
Each atom contributes valence electrons to bonding. The reaction involves
electron transfer (ionic) or sharing (covalent) to achieve stable configurations.

📈 ENERGY PROFILE:
The reaction pathway shows energy changes from reactants → transition state → products.
Activation energy must be overcome for reaction to proceed.

🌡️ CONDITIONS:
Temperature, pressure, and concentration affect reaction rate and equilibrium position.
        """
        return explanation.strip()


# Predefined common molecules
COMMON_MOLECULES = {
    "water": lambda: ChemistryEngine().create_water_molecule(),
    "salt": lambda: ChemistryEngine().create_sodium_chloride(),
}
