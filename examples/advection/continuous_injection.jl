

# You may need to run `using Pkg; Pkg.add("Plots")` first if you don't have it installed.
using Plots

# --- 1. System Parameters ---
L = 10.0         # Length of the domain
v = 1.0          # Advection velocity
T_end = 5.0      # Total simulation time
C_0 = 1.0        # Injection concentration at x=0

# --- 2. Grid Setup ---
nx = 200                 # Number of spatial points
dx = L / (nx - 1)        # Spatial step size
x = range(0, L, length=nx)

# CFL Condition: For stability in explicit advection, v * dt/dx must be <= 1
CFL = 0.8                # Courant number
dt = CFL * dx / v        # Time step size
nt = Int(ceil(T_end / dt)) # Number of time steps

# --- 3. Initialization ---
# Initialize numerical array (starts completely empty, C=0)
C_num = zeros(nx)
C_num[1] = C_0 # Apply boundary condition at x=0

# --- 4. The Upwind Solver ---
# dC/dt = -v * dC/dx -> C_new[i] = C[i] - v*(dt/dx)*(C[i] - C[i-1])
for n in 1:nt
    C_old = copy(C_num)
    # Start at i=2 because i=1 is our fixed boundary condition
    for i in 2:nx
        C_num[i] = C_old[i] - v * (dt / dx) * (C_old[i] - C_old[i-1])
    end
end

# --- 5. The Analytical Solution ---
# Using the Heaviside step function logic: C = C_0 if x <= v*t, else 0
C_analytical = [xi <= v * T_end ? C_0 : 0.0 for xi in x]

# --- 6. Plotting ---
plot(x, C_analytical, 
    label="Analytical (Perfect Step)", 
    linewidth=3, 
    color=:black, 
    linestyle=:dash)

plot!(x, C_num, 
    label="Numerical (Upwind Scheme)", 
    linewidth=2, 
    color=:blue,
    fill=(0, 0.2, :blue)) # Fills the area under the curve

plot!(title="1D Advection: Continuous Injection at t=$(round(T_end, digits=1))",
      xlabel="Position (x)",
      ylabel="Concentration (C)",
      xlims=(0, L),
      ylims=(-0.1, 1.2),
      legend=:topright,
      grid=true)