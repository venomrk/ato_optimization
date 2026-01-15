import numpy as np

class ATOPhysicsEngine:
    def __init__(self):
        # Constants
        self.e = 1.602e-19  # Elementary charge
        self.m_e = 9.109e-31  # Electron mass
        self.epsilon_0 = 8.854e-12  # Vacuum permittivity
        self.c = 3e8  # Speed of light
        
        # ATO Material Constants (Approximate)
        self.m_star = 0.27 * self.m_e  # Effective mass of electrons in SnO2
        self.epsilon_inf = 4.0  # High-frequency dielectric constant

    def get_carrier_concentration(self, sb_doping_percent, f_doping_percent, temperature_c):
        """
        Empirical model for AFTO Carrier Concentration (N).
        Sb substitutes Sn (donor), F substitutes O (donor).
        """
        # Base concentration
        n_base = 1e19 # cm^-3
        
        # 1. Sb Contribution (Peak efficiency ~ 4-5%)
        eff_sb = np.exp(-0.5 * ((sb_doping_percent - 5.0) / 4.0) ** 2)
        n_sb = 1.0e21 * eff_sb * (sb_doping_percent / 5.0)
        
        # 2. F Contribution (Peak efficiency ~ 10-15%)
        eff_f = np.exp(-0.5 * ((f_doping_percent - 12.0) / 6.0) ** 2)
        n_f = 1.2e21 * eff_f * (f_doping_percent / 12.0)
        
        # 3. Activation Temperature Factor
        temp_factor = np.clip((temperature_c - 200) / 300, 0, 1.0)
        
        # Combined N (Limit saturation to avoid unphysical values)
        # Interaction: High co-doping might cause clustering (negative term)
        interaction_penalty = 1.0 - 0.02 * (sb_doping_percent * f_doping_percent)
        
        n_total = n_base + (n_sb + n_f) * temp_factor * max(0.5, interaction_penalty)
        
        return min(n_total, 2.5e21) * 1e6 # Max cap at 2.5e21, convert to m^-3

    def get_mobility(self, sb_doping_percent, f_doping_percent, temperature_c):
        """
        Empirical model for Mobility (mu) with SYNERGISTIC STRAIN COMPENSATION.
        """
        mu_max = 50.0 # cm^2/V-s (Higher theoretical max for co-doped)
        mu_min = 2.0
        
        # 1. Scattering from ionized impurities (Standard)
        # More dopants = More scattering
        total_dopant = sb_doping_percent + f_doping_percent
        scattering_base = 1.0 / (1.0 + 0.2 * total_dopant)
        
        # 2. SYNERGY FACTOR (Lattice Strain)
        # Hypothesis: Sb5+ (0.60 A) shrinks, F- (1.33 A) vs O2- (1.40 A) shrinks?
        # Actually in literature: Sb expands a-axis, F expands c-axis slightly?
        # Let's assume a "Golden Ratio" exists where strain is cancelled.
        # Let's define the "Zero Strain" line as: F% = 2.5 * Sb% (Heuristic)
        # Any deviation from this line reduces mobility.
        
        target_f = 2.5 * sb_doping_percent
        deviation = abs(f_doping_percent - target_f)
        
        # If we are close to the "Golden Ratio", we get a boost!
        # This creates a "ridge" in the optimization landscape.
        strain_factor = np.exp(-0.5 * (deviation / 3.0) ** 2) # Sigma=3% tolerance
        
        # Boost mobility if strain is low
        synergy_boost = 1.0 + 2.0 * strain_factor # Up to 3x boost at perfect ratio
        
        # Crystallinity
        crystallinity = np.clip((temperature_c - 250) / 300, 0.2, 1.0)
        
        mu = (mu_min + (mu_max - mu_min) * scattering_base) * crystallinity * synergy_boost
        
        # Cap at physical limit
        return min(mu, 40.0) * 1e-4 # cm^2/Vs -> m^2/Vs

    def calculate_thermal_properties(self, N, mu, thickness_m, t_base_glass):
        """
        Calculates Solar Heat Gain Coefficient (SHGC) using AM1.5G weighted approximation.
        SHGC = T_sol + N_inward * A_sol
        For single glazing, N_inward ~ 0.27 (standard convention).
        """
        # simplified AM1.5G Spectrum Weights
        # Wavelengths (nm): [350 (UV), 450 (Blue), 550 (Green), 650 (Red), 1000 (NIR1), 1500 (NIR2), 2000 (NIR3)]
        wavelengths_nm = np.array([350, 450, 550, 650, 1000, 1500, 2000])
        weights =        np.array([0.05, 0.10, 0.15, 0.15, 0.30,  0.15,  0.10]) # Roughly sums to 1.0 representing power distribution
        
        T_sol_weighted = 0.0
        A_sol_weighted = 0.0
        
        for i, wl in enumerate(wavelengths_nm):
            wl_m = wl * 1e-9
            
            # 1. Physics at this wavelength
            # Drude Model
            omega = 2 * np.pi * self.c / wl_m
            omega_p_sq = (N * self.e**2) / (self.m_star * self.epsilon_0 * self.epsilon_inf)
            gamma = self.e / (self.m_star * mu) # Damping freq approx
            
            # Dielectric func: epsilon = epsilon_inf - omega_p^2 / (omega^2 + i*omega*gamma)
            # Simplify for transmission:
            
            # Plasma Edge:
            omega_p = np.sqrt(omega_p_sq)
            lambda_p_nm = (2 * np.pi * self.c / omega_p) * 1e9
            
            # --- Transmittance at specific wavelength ---
            # Visible region (400-700) is dominated by bandgap (UV) and scattering
            # NIR region (>700) is dominated by Plasmons (Drude)
            
            T_i = t_base_glass
            
            if wl < 400: # UV
                T_i *= 0.1 # Glass blocks UV
            
            # Scattering (Rayleigh ~ 1/lambda^4, but simpler here)
            scattering = 0.02 * (thickness_m / 500e-9)
            T_i -= scattering
            
            # Drude Absorption / Reflection (NIR)
            if wl > 700:
                # Reflection kicks in at plasma freq
                ratio = wl / lambda_p_nm
                slope = 2.0 + (mu * 1e4 / 5.0)
                rejection = 1.0 / (1.0 + (ratio * 1.2) ** slope)
                T_i *= rejection
                
                # Free carrier absorption coeff
                alpha = (N * self.e**2 * gamma) / (self.m_star * self.c * omega**2 * np.sqrt(self.epsilon_inf) * self.epsilon_0)
                T_i *= np.exp(-alpha * thickness_m)

            T_i = np.clip(T_i, 0.0, 1.0)
            R_i = max(0, t_base_glass - T_i - 0.05) # Simplified Reflectance
            A_i = 1.0 - T_i - R_i
            
            T_sol_weighted += T_i * weights[i]
            A_sol_weighted += A_i * weights[i]
            
        # SHGC Calculation
        # Heat flowing inward = Transmitted Solar + Fraction of Absorbed Heat
        # Standard fraction for convection/radiation inward ~ 0.27 to 0.3 for single pane
        shgc = T_sol_weighted + 0.27 * A_sol_weighted
        
        return float(shgc), float(T_sol_weighted)

    def simulate_measurement(self, sb_doping_percent, f_doping_percent, temperature_c, thickness_nm):
        """
        Simulates the AFTO experiment.
        """
        # 1. Get Physical Properties (N, mu)
        N = self.get_carrier_concentration(sb_doping_percent, f_doping_percent, temperature_c)
        mu = self.get_mobility(sb_doping_percent, f_doping_percent, temperature_c)
        thickness_m = thickness_nm * 1e-9
        
        # 2. Calculate Electrical Properties
        sigma = N * self.e * mu
        resistivity = 1.0 / sigma if sigma > 0 else 1e9
        sheet_resistance = resistivity / thickness_m if thickness_m > 0 else 1e9

        # 3. Optical Properties (Drude)
        omega_p_sq = (N * self.e**2) / (self.m_star * self.epsilon_0 * self.epsilon_inf)
        omega_p = np.sqrt(omega_p_sq)
        lambda_p = 2 * np.pi * self.c / omega_p
        
        # Transmittance
        t_base_glass = 0.915 # Slightly better base
        
        # Visible Loss (Bandgap + Scattering)
        scattering_loss = 0.03 * (thickness_nm / 500.0) * (1 + 0.1*sb_doping_percent)
        absorbance_vis = 0.015 * (thickness_nm / 1000.0) * max(0, (sb_doping_percent - 0.5 * f_doping_percent))
        
        T_vis = t_base_glass - scattering_loss - absorbance_vis
        
        # NIR Blocking (Plasmonic)
        lambda_nir = 1500e-9
        ratio = lambda_nir / lambda_p
        slope = 2.0 + (mu * 1e4 / 8.0) # Sharper edge with high mobility
        rejection_factor = 1.0 / (1.0 + ratio ** slope)
        
        # Free carrier absorption
        alpha_nir = 0.8e-15 * N * (lambda_nir * 1e9)**2 / (mu * 1e4)
        T_nir_absorb = np.exp(-alpha_nir * thickness_m)
        
        T_nir = t_base_glass * rejection_factor * 0.7 + T_nir_absorb * 0.3
        
        # --- THERMAL PROPERTIES ---
        shgc, t_sol = self.calculate_thermal_properties(N, mu, thickness_m, t_base_glass)
        
        # Indoor Temp Reduction Estimate (Heuristic)
        # Q_gain = 800 * SHGC. Uncoated glass SHGC ~ 0.82.
        # Delta_Q = 800 * (0.82 - SHGC)
        # dT_indoor approx Delta_Q * 0.02 (Deg C) - VERY rough room model
        dT_reduction = (0.82 - shgc) * 800 * 0.02
        
        return {
            "sheet_resistance": float(sheet_resistance),
            "T_vis": float(np.clip(T_vis, 0, 1.0)),
            "T_nir": float(np.clip(T_nir, 0, 1.0)),
            "SHGC": float(shgc),
            "T_sol": float(t_sol),
            "Indoor_Temp_Reduction_C": float(dT_reduction),
            "lambda_p_nm": float(lambda_p * 1e9),
            "carrier_conc_cm3": float(N * 1e-6),
            "mobility_cm2Vs": float(mu * 1e4)
        }

if __name__ == "__main__":
    # Test Run
    engine = ATOPhysicsEngine()
    print("Testing ATO Physics Engine...")
    
    # Heuristic optimum parameters
    result = engine.simulate_measurement(sb_doping_percent=5.0, temperature_c=450, thickness_nm=400)
    
    print(f"Inputs: Sb=5%, Temp=450C, d=400nm")
    print(f"Outputs:")
    print(f"  R_sh: {result['sheet_resistance']:.2f} ohm/sq")
    print(f"  T_vis: {result['T_vis']*100:.1f}%")
    print(f"  T_nir: {result['T_nir']*100:.1f}%")
    print(f"  Carrier Conc: {result['carrier_conc_cm3']:.2e} cm^-3")
    print(f"  Mobility: {result['mobility_cm2Vs']:.1f} cm^2/Vs")
