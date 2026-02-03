"""
Rectangular Beam Nominal Moment Strength Calculator
Based on ACI 318 Provisions (Example 4-1 and 4-1M)

Variables:
    fc' - Concrete compressive strength
    fy  - Steel yield strength
    Es  - Modulus of elasticity of steel
    b   - Beam width
    h   - Total beam depth
    d   - Effective depth (to centroid of tension steel)
    As  - Total area of tension steel
    beta1 - Stress block factor
    epsilon_cu - Ultimate concrete strain (0.003)

Calculated:
    T       - Tension force in steel
    a       - Depth of equivalent stress block
    c       - Neutral axis depth
    epsilon_y - Yield strain of steel
    epsilon_s - Strain in steel at ultimate
    Mn      - Nominal moment strength
    As_min  - Minimum steel area per ACI
"""

import math


class RectangularBeam:
    def __init__(
        self,
        b: float,
        h: float,
        d: float,
        fc: float,
        fy: float,
        n_bars: int,
        bar_area: float,
        Es: float = None,
        beta1: float = None,
        epsilon_cu: float = 0.003,
        unit_system: str = "imperial"
    ):
        """
        Initialize the Rectangular Beam.
        
        Args:
            b: Beam width (in or mm)
            h: Total beam depth (in or mm)
            d: Effective depth (in or mm)
            fc: Concrete compressive strength (psi or MPa)
            fy: Steel yield strength (psi or MPa)
            n_bars: Number of reinforcement bars
            bar_area: Area of each bar (in2 or mm2)
            Es: Modulus of elasticity of steel (psi or MPa). Default based on unit system.
            beta1: Stress block factor. Default calculated from fc.
            epsilon_cu: Ultimate concrete strain. Default 0.003.
            unit_system: 'imperial' (psi, in) or 'si' (MPa, mm)
        """
        self.b = b
        self.h = h
        self.d = d
        self.fc = fc
        self.fy = fy
        self.n_bars = n_bars
        self.bar_area = bar_area
        self.As = n_bars * bar_area
        self.epsilon_cu = epsilon_cu
        self.unit_system = unit_system.lower()
        
        # Set Es default based on unit system
        if Es is None:
            self.Es = 29000000 if self.unit_system == "imperial" else 200000
        else:
            self.Es = Es
        
        # Set beta1 - calculate if not provided
        if beta1 is None:
            self.beta1 = self._calculate_beta1()
        else:
            self.beta1 = beta1

    def _calculate_beta1(self) -> float:
        """Calculates beta1 based on fc per ACI 318."""
        if self.unit_system == "imperial":
            # fc in psi
            if self.fc <= 4000:
                return 0.85
            elif self.fc >= 8000:
                return 0.65
            else:
                return 0.85 - 0.05 * (self.fc - 4000) / 1000
        else:
            # fc in MPa
            if self.fc <= 28:
                return 0.85
            elif self.fc >= 55:
                return 0.65
            else:
                return 0.85 - 0.05 * (self.fc - 28) / 7

    def calculate_as_min(self) -> float:
        """
        Calculate minimum steel area per ACI 318.
        
        Imperial: As_min = max(3*sqrt(fc)/fy * b*d, 200/fy * b*d)
        SI: As_min = max(0.25*sqrt(fc)/fy * b*d, 1.4/fy * b*d)
        """
        if self.unit_system == "imperial":
            term1 = (3 * math.sqrt(self.fc) / self.fy) * self.b * self.d
            term2 = (200 / self.fy) * self.b * self.d
        else:
            term1 = (0.25 * math.sqrt(self.fc) / self.fy) * self.b * self.d
            term2 = (1.4 / self.fy) * self.b * self.d
        return max(term1, term2)

    def calculate_mn(self) -> dict:
        """
        Calculates Nominal Moment Capacity (Mn) and related values.
        
        Returns:
            dict with all calculated values including:
            - T: Tension force
            - a: Depth of stress block
            - c: Neutral axis depth
            - epsilon_y: Yield strain
            - epsilon_s: Steel strain at ultimate
            - yield_check: Whether steel yields
            - fs: Steel stress
            - Mn: Nominal moment
            - Mn_display: Moment in display units (k-ft or kN-m)
            - As_min: Minimum steel area
            - as_check: Whether As >= As_min
            - phi: Strength reduction factor
            - Mu: Design moment capacity
        """
        # Tension force
        T = self.As * self.fy
        
        # Stress block depth
        a = (self.As * self.fy) / (0.85 * self.fc * self.b)
        
        # Neutral axis depth
        c = a / self.beta1
        
        # Strains
        epsilon_y = self.fy / self.Es
        epsilon_s = self.epsilon_cu * (self.d - c) / c
        
        # Check if steel yields
        yield_check = epsilon_s >= epsilon_y
        fs = self.fy if yield_check else epsilon_s * self.Es
        
        # Nominal moment
        Mn = self.As * fs * (self.d - a / 2)
        
        # Convert to display units
        if self.unit_system == "imperial":
            Mn_display = Mn / 12000  # lb-in to k-ft
            T_display = T / 1000  # lb to kips
            Mn_k = Mn / 1000  # lb-in to k-in
        else:
            Mn_display = Mn / 1e6  # N-mm to kN-m
            T_display = T / 1000  # N to kN
            Mn_k = Mn  # N-mm
        
        # Minimum steel check
        As_min = self.calculate_as_min()
        as_check = self.As >= As_min
        
        # Phi factor (ACI 318)
        epsilon_t = epsilon_s  # For tension-controlled check
        if epsilon_t >= 0.005:
            phi = 0.9
        elif epsilon_t <= 0.002:
            phi = 0.65
        else:
            phi = 0.65 + 0.25 * (epsilon_t - 0.002) / 0.003
        
        Mu = phi * Mn
        if self.unit_system == "imperial":
            Mu_display = Mu / 12000
        else:
            Mu_display = Mu / 1e6
        
        return {
            "T": T,
            "T_display": T_display,
            "a": a,
            "c": c,
            "epsilon_y": epsilon_y,
            "epsilon_s": epsilon_s,
            "yield_check": yield_check,
            "fs": fs,
            "Mn": Mn,
            "Mn_k": Mn_k,
            "Mn_display": Mn_display,
            "As": self.As,
            "As_min": As_min,
            "as_check": as_check,
            "epsilon_t": epsilon_t,
            "phi": phi,
            "Mu": Mu,
            "Mu_display": Mu_display,
            # Legacy compatibility
            "Mn_kft": Mn_display if self.unit_system == "imperial" else None,
            "Mn_kin": Mn_k / 1000 if self.unit_system == "imperial" else None,
            "Mu_kft": Mu_display if self.unit_system == "imperial" else None,
        }

    def get_units(self) -> dict:
        """Get unit labels based on current unit system."""
        if self.unit_system == "imperial":
            return {
                "length": "in",
                "area": "in^2",
                "force": "lb",
                "force_k": "kips",
                "stress": "psi",
                "moment": "lb-in",
                "moment_k": "k-in",
                "moment_display": "k-ft",
            }
        else:
            return {
                "length": "mm",
                "area": "mm^2",
                "force": "N",
                "force_k": "kN",
                "stress": "MPa",
                "moment": "N-mm",
                "moment_k": "N-mm",
                "moment_display": "kN-m",
            }
