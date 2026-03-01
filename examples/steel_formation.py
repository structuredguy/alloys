# This script solves the full time-dependent Partial Differential Equation (PDE) using the "Method of Lines." It
# shows how an initially random distribution of Carbon eventually "finds" the holes in the Iron grid.

#%% setup
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.special import i0 # Import Bessel function for analytical solution

# %% --- 1. System Parameters ---
L = 10.0  # Length of the domain (Angstroms)
N = 100  # Number of grid points
dx = L / N  # Space step
x = np.linspace(0, L, N, endpoint=False)  # Periodic grid

D = 1.0  # Diffusion coefficient
kB_T_initial = 1.0  # Thermal energy (Temperature) for time evolution
V_amp = 5.0  # Amplitude of Iron Grid Potential (Interaction strength)

# %% --- 2. Define the Potentials ---
# Iron Grid Potential: V(x) = V_amp * cos(2*pi*x / L)
# We make the period L/2 so we see two "wells" in the plot
k_vec = 2 * np.pi / L 
V = V_amp * np.cos(k_vec * x)

# Pre-calculate the force (-dV/dx) acting on Carbon
# Force pushes Carbon away from peaks towards valleys
Force = -(-V_amp * k_vec * np.sin(k_vec * x))

# %% --- 3. The PDE (Method of Lines) ---
def dCdt(t, C, D_val, kB_T_val, Force_val):
    """
    Computes dC/dt for the Smoluchowski equation:
    dC/dt = D * d/dx ( dC/dx - Force*C/kB_T )
    Using central finite differences with periodic boundary conditions.
    """
    # 1. Calculate Flux J at staggered grid points (i+1/2)
    # J = -D * (dC/dx - Force * C / kB_T)

    # Rolling arrays handles periodic boundaries automatically
    # C_right = C[i+1], C_minus = C[i-1]
    C_right = np.roll(C, -1)
    # C_left = np.roll(C, 1) # Not directly used in this flux calculation
    F_right = np.roll(Force_val, -1)

    # Gradient of C at i+1/2
    grad_C = (C_right - C) / dx

    # Average Force and Concentration at i+1/2 for the drift term
    avg_Force = (Force_val + F_right) / 2
    avg_C = (C + C_right) / 2

    # Total Flux J at i+1/2
    Flux = -D_val * (grad_C - (avg_Force * avg_C / kB_T_val))

    # 2. Conservation of Mass: dC/dt = -dJ/dx
    Flux_left = np.roll(Flux, 1)
    dC_dt = -(Flux - Flux_left) / dx

    return dC_dt

# %% --- 4. Initial Condition ---
# Start with random noise (Carbon atoms scattered everywhere)
np.random.seed(42)
C0 = 1.0 + 0.2 * np.random.randn(N)

# %% --- 5. Solve Time Evolution ---
t_span = (0, 0.5)  # Integrate for 0.5 time units
sol = solve_ivp(dCdt, t_span, C0, args=(D, kB_T_initial, Force), method='RK45')

# %% --- 6. Plotting Time Evolution and Analytical Solution ---
plt.figure(figsize=(12, 7))

# Plot Iron Potential (Scaled for visualization)
# We flip the sign of V for the plot so "Valleys" look like "Cups"
# that catch the Carbon.
plt.plot(x, -V/V_amp, 'k--', label='Iron Grid "Wells" (-V)', alpha=0.5)

# Plot Initial Carbon (Noise)
plt.plot(x, C0, 'b:', label='Carbon (Initial)', alpha=0.6)

# Plot Final Carbon (Equilibrium from simulation)
C_final_sim = sol.y[:, -1]
plt.plot(x, C_final_sim, 'g-', linewidth=2, label=f'Carbon (Simulated Equilibrium, T={kB_T_initial})')

# Plot Analytical Boltzmann Distribution for the same temperature
beta_analytical = V_amp / kB_T_initial
C_analytical = np.exp(-V / kB_T_initial) # C(x) ~ exp(-V(x)/kT)
# Normalize to have the same total mass as C0
C_analytical = C_analytical * (np.sum(C0) / np.sum(C_analytical))
plt.plot(x, C_analytical, 'r--', linewidth=2, label=f'Carbon (Analytical Boltzmann, T={kB_T_initial})')


plt.title(f"Carbon Migration into Iron Lattice (Time Evolution & Analytical)")
plt.xlabel("Position (x)")
plt.ylabel("Concentration / Potential")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('../img/time_evolution.png', dpi=300)
plt.show()

# %% --- 7. Plotting Dirac Delta Limit ---
plt.figure(figsize=(12, 7))

# Define a wider range for plotting to show more periods for the Dirac Delta
L_plot = 2.0 * L
x_plot = np.linspace(-L_plot/2, L_plot/2, N*2) # Plot 2 periods centered at 0
V_plot = V_amp * np.cos(k_vec * x_plot) # Potential for the wider range

# Plot the Potential (background)
# We plot -V_plot because atoms fall into the minima
plt.plot(x_plot, -V_plot, 'k--', label='Iron Lattice Potential V(x)', alpha=0.3)

temperatures = [5.0, 1.0, 0.5, 0.1] # High to very low temperatures
colors = ['green', 'orange', 'red', 'purple']

for i, T in enumerate(temperatures):
    beta = V_amp / T

    # Calculate the Analytical Boltzmann Distribution
    # C(x) ~ exp(-V/kT) = exp( beta * cos(k_vec * x_plot) )
    C_dist = np.exp(beta * np.cos(k_vec * x_plot))

    # Normalize by I0(beta) for proper probability density, and then scale for visualization
    # We normalize to have a peak value of 1 for easier comparison of shapes
    C_dist_normalized = C_dist / np.max(C_dist)

    label = f'T={T} (beta={beta:.1f})'
    linewidth = 1.5 if T > 0.1 else 2.5 # Make the limit case thicker

    plt.plot(x_plot, C_dist_normalized, color=colors[i], linewidth=linewidth, label=label)

# Annotations
plt.title(f"Approaching the Dirac Delta Limit (T -> 0)")
plt.xlabel("Position (x)")
plt.ylabel("Normalized Carbon Probability Density")
plt.xlim(-L/2, L/2) # Focus on one period for clarity
plt.legend()
plt.grid(True, alpha=0.3)

# Add text arrow to show the sharpening
plt.annotate('As $T \\to 0$, Width $\\to 0$',
             xy=(0, 0.8), xytext=(L/4, 0.9),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8),
             horizontalalignment='center', verticalalignment='bottom',
             fontsize=10)

plt.tight_layout()
plt.savefig('../img/dirac_delta_limit.png', dpi=300)
plt.show()