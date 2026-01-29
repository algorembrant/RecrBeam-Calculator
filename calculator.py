import math

class RectangularBeam:
    def __init__(self, width: float, effective_depth: float, f_c: float, f_y: float, rebar_area: float):
        """
        Initialize the Rectangular Beam.
        
        Args:
            width (float): Beam width (t), inches.
            effective_depth (float): Effective depth (d), inches.
            f_c (float): Specified compressive strength of concrete, psi.
            f_y (float): Specified yield strength of reinforcement, psi.
            rebar_area (float): Area of tension reinforcement (As), sq in.
        """
        self.b = width
        self.d = effective_depth
        self.fc = f_c
        self.fy = f_y
        self.As = rebar_area
        self.beta1 = self._calculate_beta1()

    def _calculate_beta1(self):
        """Calculates beta1 based on f_c (psi)."""
        if self.fc <= 4000:
            return 0.85
        elif self.fc >= 8000:
            return 0.65
        else:
            return 0.85 - 0.05 * (self.fc - 4000) / 1000

    def calculate_mn(self):
        """
        Calculates Nominal Moment Capacity (Mn).
        
        Returns:
            dict: Contains 'a' (depth of equivalent rectangular stress block),
                  'c' (neutral axis depth),
                  'Mn_kft' (Nominal Moment in k-ft),
                  'Mn_kin' (Nominal Moment in k-in),
                  'phi' (strength reduction factor - simplified/assumed flexure controlled usually 0.9 for now, but calculated properly)
        """
        # 1. Compute 'a'
        # a = (As * fy) / (0.85 * fc * b)
        a = (self.As * self.fy) / (0.85 * self.fc * self.b)
        
        # 2. Compute Nominal Moment Mn
        # Mn = As * fy * (d - a/2)
        Mn_force = self.As * self.fy 
        arm = self.d - (a / 2)
        Mn_kin = Mn_force * arm # lb-in
        
        # Convert to k-ft
        Mn_kft = Mn_kin / 12000.0 # lb-in / 12 / 1000
        
        # Check strain for ductile failure (phi factor)
        c = a / self.beta1
        epsilon_t = 0.003 * (self.d - c) / c
        
        # ACI-318 phi logic
        if epsilon_t >= 0.005:
            phi = 0.9
        elif epsilon_t <= 0.002:
            phi = 0.65
        else:
            phi = 0.65 + 0.25 * (epsilon_t - 0.002) / 0.003
            
        Mu_kft = phi * Mn_kft
        
        return {
            'a': a,
            'c': c,
            'epsilon_t': epsilon_t,
            'Mn_kin': Mn_kin / 1000.0, # k-in
            'Mn_kft': Mn_kft,
            'phi': phi,
            'Mu_kft': Mu_kft
        }
