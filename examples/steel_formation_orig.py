import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# --- 1. System Parameters ---
L = 10.0  # Length of the domain (Angstroms)
N = 100  # Number of grid points
dx = L / N  # Space step
x = np.linspace(0, L, N, endpoint=False)  # Periodic grid

D = 1.0  # Diffusion coefficient
kB_T = 1.0  # Thermal energy (Temperature)
V_amp = 5.0  # Amplitude of Iron Grid Potential (Interaction strength)

# --- 2. Define the Potentials ---
# Iron Grid Potential: V(x) = V_amp * cos(2*pi*x / L)
# We make the period L/2 so we see two "wells" in the plot
k_vec = 2 * np.pi / L
V = V_amp * np.cos(k_vec * x)

# Pre-calculate the force (-dV/dx) acting on Carbon
# Force pushes Carbon away from peaks towards valleys
Force = -(-V_amp * k_vec * np.sin(k_vec * x))


# --- 3. The PDE (Method of Lines) ---
def dCdt(t, C):
    """
    Computes dC/dt for the Smoluchowski equation:
    dC/dt = D * d/dx ( dC/dx - Force*C/kB_T )
    Using central finite differences with periodic boundary conditions.
    """
    # 1. Calculate Flux J at staggered grid points (i+1/2)
    # J = -D * (dC/dx - Force * C / kB_T)

    # Rolling arrays handles periodic boundaries automatically
    # C_plus = C[i+1], C_minus = C[i-1]
    C_right = np.roll(C, -1)
    C_left = np.roll(C, 1)
    F_right = np.roll(Force, -1)

    # Gradient of C at i+1/2
    grad_C = (C_right - C) / dx

    # Average Force and Concentration at i+1/2 for the drift term
    avg_Force = (Force + F_right) / 2
    avg_C = (C + C_right) / 2

    # Total Flux J at i+1/2
    Flux = -D * (grad_C - (avg_Force * avg_C / kB_T))

    # 2. Conservation of Mass: dC/dt = -dJ/dx
    Flux_left = np.roll(Flux, 1)
    dC_dt = -(Flux - Flux_left) / dx

    return dC_dt


# --- 4. Initial Condition ---
# Start with random noise (Carbon atoms scattered everywhere)
np.random.seed(42)
C0 = 1.0 + 0.2 * np.random.randn(N)

# --- 5. Solve ---
t_span = (0, 0.5)  # Integrate for 0.5 time units
sol = solve_ivp(dCdt, t_span, C0, method='RK45')

# --- 6. Plotting ---
plt.figure(figsize=(10, 6))

# Plot Iron Potential (Scaled for visualization)
# We flip the sign of V for the plot so "Valleys" look like "Cups"
# that catch the Carbon.
plt.plot(x, V, 'k--', label='Iron Grid "Potential" (V)', alpha=0.5)

# Plot Initial Carbon (Noise)
# plt.plot(x, C0, 'b:', label='Carbon (Initial)', alpha=0.6)

# Plot Final Carbon (Equilibrium)
C_final = sol.y[:, -1]
plt.plot(x, C_final, 'r-', linewidth=3, label='Carbon (ODE Equilibrium)')

plt.title(f"Carbon Migration into Iron Lattice (T={kB_T})")
plt.xlabel("Position (x)")
plt.ylabel("Concentration / Potential")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()