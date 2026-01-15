import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel
from scipy.stats import norm
from physics_engine import ATOPhysicsEngine
import warnings

# Suppress sklearn warnings
warnings.filterwarnings("ignore")

class AFTOOptimizer:
    def __init__(self):
        self.engine = ATOPhysicsEngine()
        self.X_data = [] # [Sb%, F%, Temp, Thickness] (4D)
        self.y_data = [] 
        
        # Kernel: 4D anisotropic Matern to handle different scales
        self.kernel = ConstantKernel(1.0) * Matern(length_scale=[1.0, 1.0, 50.0, 50.0], nu=2.5) + WhiteKernel(noise_level=0.1)
        self.model = GaussianProcessRegressor(kernel=self.kernel, n_restarts_optimizer=5)
        
        # Bounds: Sb(0-10), F(0-25), Temp(300-550), Thick(100-1000)
        self.bounds = np.array([
            [0.0, 10.0],  # Sb
            [0.0, 25.0],  # F (Usually needs higher doping)
            [300.0, 550.0],
            [100.0, 1000.0]
        ])

    def objective_function(self, r_sh, t_vis, t_nir, shgc):
        """
        Thermal Targets: 
        SHGC < 0.5 (Critical)
        Tvis > 0.85
        Rsh < 10
        """
        score = 0
        
        # 1. Sheet Resistance (Target < 10)
        if r_sh < 10:
            score += 100 + (10 - r_sh) * 10
        else:
            score -= (r_sh - 10) * 10
            
        # 2. Visible Transmittance (Target > 0.85)
        if t_vis > 0.85:
            score += 50 + (t_vis - 0.85) * 500
        else:
            score -= (0.85 - t_vis) * 300 # Heavy penalty, must see through window
            
        # 3. THERMAL: SHGC (Lower is better)
        # Target < 0.50 (High performance glazing)
        # Uncoated is 0.82
        if shgc < 0.50:
            score += 100 + (0.50 - shgc) * 1000 # Massive bonus for heat rejection
        else:
            score -= (shgc - 0.50) * 200
            
        return score

    def acquisition_function(self, X_candidates):
        mu, sigma = self.model.predict(X_candidates, return_std=True)
        if len(self.y_data) == 0: return mu
        mu_sample_opt = np.max(self.y_data)
        with np.errstate(divide='warn'):
            imp = mu - mu_sample_opt
            Z = imp / sigma
            ei = imp * norm.cdf(Z) + sigma * norm.pdf(Z)
            ei[sigma == 0.0] = 0.0
        return ei

    def run_optimization(self, iterations=50, initial_samples=10):
        print(f"--- Starting AFTO Optimization (Co-Doping Search) ---")
        
        # Initial Sampling
        for i in range(initial_samples):
            params = np.random.uniform(self.bounds[:, 0], self.bounds[:, 1])
            self._evaluate(params)
            
        # Optimization Loop
        for i in range(iterations):
            self.model.fit(np.array(self.X_data), np.array(self.y_data))
            
            candidates = np.random.uniform(self.bounds[:, 0], self.bounds[:, 1], size=(5000, 4))
            ei_scores = self.acquisition_function(candidates)
            
            best_idx = np.argmax(ei_scores)
            next_params = candidates[best_idx]
            
            self._evaluate(next_params)
            
            best_so_far_idx = np.argmax(self.y_data)
            print(f"Iter {i+1}/{iterations} | Best: {self.y_data[best_so_far_idx]:.1f} | Params: {np.round(self.X_data[best_so_far_idx], 2)}")

        best_idx = np.argmax(self.y_data)
        return self.X_data[best_idx], self.engine.simulate_measurement(*self.X_data[best_idx])

    def _evaluate(self, p):
        res = self.engine.simulate_measurement(p[0], p[1], p[2], p[3])
        score = self.objective_function(res['sheet_resistance'], res['T_vis'], res['T_nir'], res['SHGC'])
        self.X_data.append(p)
        self.y_data.append(score)

if __name__ == "__main__":
    opt = AFTOOptimizer()
    best_p, best_m = opt.run_optimization()
    
    print("\n=== THERMAL COMFORT AFTO OPTIMUM ===")
    print(f"  Sb: {best_p[0]:.2f} %")
    print(f"  F:  {best_p[1]:.2f} %")
    print(f"  Temp: {best_p[2]:.1f} C")
    print(f"  Thick: {best_p[3]:.1f} nm")
    print(f"Performance:")
    print(f"  Rsh: {best_m['sheet_resistance']:.2f} ohm/sq")
    print(f"  Tvis: {best_m['T_vis']*100:.1f} %")
    print(f"  SHGC: {best_m['SHGC']:.3f} (Standard: 0.82)")
    print(f"  Temp Reduction: -{best_m['Indoor_Temp_Reduction_C']:.1f} °C (Est. at Peak Sun)")

