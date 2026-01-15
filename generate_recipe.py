import sys

def generate_recipe(sb_doping_percent, f_doping_percent, temperature_c, thickness_nm):
    """
    Generates a Holmarc Spray Pyrolysis Recipe for AFTO (Sb + F co-doped).
    """
    # Constants
    M_SnCl4_5H2O = 350.58 # g/mol
    M_SbCl3 = 228.11 # g/mol
    M_NH4F = 37.04 # g/mol (Ammonium Fluoride)
    
    # Process Settings
    total_volume_ml = 50.0 # Standard batch size
    molarity = 0.4 # Standard molarity
    
    # Molar Calculations
    # Total Sn moles is the base. Dopants are usually added relative to Sn.
    # N_dopant = N_Sn * (Atomic%). 
    # Note: Sometimes literature defines Atomic% as Dopant / (Sn + Dopant).
    # Here, we assume "Added At%" -> Moles_Dopant = Moles_Sn * (Percent/100)
    
    moles_sn = molarity * (total_volume_ml / 1000.0)
    moles_sb = moles_sn * (sb_doping_percent / 100.0)
    moles_f  = moles_sn * (f_doping_percent / 100.0)
    
    mass_sn_precursor = moles_sn * M_SnCl4_5H2O
    mass_sb_precursor = moles_sb * M_SbCl3
    mass_f_precursor  = moles_f  * M_NH4F
    
    # Spray Parameters (Holmarc HO-TH-04 specific heuristics)
    # Deposition rate ~ 5-10 nm/min depending on flow rate
    # Target thickness -> Total Time
    deposition_rate_approx = 7.0 # nm/min
    spray_time_min = thickness_nm / deposition_rate_approx
    
    print(f"\n=======================================================")
    print(f"   NOVEL AFTO SMART GLASS RECIPE (Holmarc HO-TH-04)")
    print(f"=======================================================")
    print(f"Target Properties:")
    print(f"  - Sb Doping: {sb_doping_percent:.2f} at%")
    print(f"  - F Doping:  {f_doping_percent:.2f} at%")
    print(f"  - Substrate Temp: {temperature_c:.0f} C")
    print(f"  - Film Thickness: {thickness_nm:.0f} nm")
    print(f"-------------------------------------------------------")
    print(f"Chemical Precursors (for {total_volume_ml} mL solution):")
    print(f"  1. Tin Precursor: SnCl4·5H2O")
    print(f"     -> Quantity: {mass_sn_precursor:.4f} g")
    print(f"  2. Sb Dopant: SbCl3")
    print(f"     -> Quantity: {mass_sb_precursor:.4f} g")
    print(f"  3. F Dopant: NH4F (Ammonium Fluoride)")
    print(f"     -> Quantity: {mass_f_precursor:.4f} g")
    print(f"     -> PRE-DISSOLVE NH4F in minimal water before adding!")
    print(f"  4. Solvent: Ethanol : Deionized Water (1:1 vol/vol)")
    print(f"     -> Quantity: {total_volume_ml} mL")
    print(f"     -> Add 1-2 mL HCl (conc) to stabilize clear solution.")
    print(f"-------------------------------------------------------")
    print(f"Machine Parameters (HO-TH-04):")
    print(f"  - Nozzle Pressure: 2.2 bar (Air/N2)")
    print(f"  - Flow Rate: 4 - 5 mL/min")
    print(f"  - Spray Distance: 28 cm")
    print(f"  - Substrate Temp: {temperature_c:.0f} C (Heater Set -> {temperature_c + 50:.0f} C)")
    print(f"  - Est. Spray Duration: {spray_time_min:.1f} minutes")
    print(f"  - Intermittent Spray: 5s ON / 10s OFF")
    print(f"=======================================================\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sb = float(sys.argv[1])
        f  = float(sys.argv[2])
        temp = float(sys.argv[3])
        d = float(sys.argv[4])
        generate_recipe(sb, f, temp, d)
    else:
        print("Usage: python generate_recipe.py <Sb%> <F%> <Temp> <Thickness>")
