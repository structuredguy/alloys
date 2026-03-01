# You will need to run: using Pkg; Pkg.add(["Plots", "SpecialFunctions"])
using Plots
using SpecialFunctions # Required for the analytical erfc() function

# --- 1. System Parameters ---
L = 10.0         # Length of the domain
v = 1.0          # Advection velocity
D = 0.1          # Diffusion coefficient (Try changing this!)
T_end = 5.0      # Total simulation time
C_0 = 1.0        # Injection concentration at x=0

# --- 2. Grid Setup ---
nx = 200                 # Number of spatial points
dx = L / (nx - 1)        # Spatial step size
x = range(0, L, length=nx)

# --- 3. Stability Conditions (The tricky part!) ---
# dt must be small enough to satisfy BOTH advection and diffusion limits
dt_advection = 0.8 * (dx / v)
dt_diffusion = 0.4 * (dx^2 / D)
dt = min(dt_advection, dt_diffusion) 
nt = Int(ceil(T_end / dt)) 

# --- 4. Initialization ---
C_num = zeros(nx)
C_num[1] = C_0 

# --- 5. The Advection-Diffusion Solver ---
for n in 1:nt
    C_old = copy(C_num)
    
    # Update interior points
    for i in 2:(nx-1)
        # Upwind for Advection
        advection_term = v * (dt / dx) * (C_old[i] - C_old[i-1])
        
        # Central Difference for Diffusion
        diffusion_term = D * (dt / dx^2) * (C_old[i+1] - 2*C_old[i] + C_old[i-1])
        
        # Combine them!
        C_num[i] = C_old[i] - advection_term + diffusion_term
    end
    
    # Right boundary condition (Zero gradient / outflow)
    C_num[nx] = C_num[nx-1]
end

# --- 6. The Analytical Solution ---
# For a continuous injection, the solution involves the error function (erfc)
# We use the dominant term which is highly accurate for these parameters
C_analytical = zeros(nx)
for i in 1:nx
    if T_end > 0
        # The physical "blurring" of the step function
        argument = (x[i] - v * T_end) / (2 * sqrt(D * T_end))
        C_analytical[i] = 0.5 * C_0 * erfc(argument)
    end
end
C_analytical[1] = C_0

# --- 7. Plotting ---
plot(x, C_analytical, 
    label="Analytical (erfc)", 
    linewidth=3, 
    color=:black, 
    linestyle=:dash)

plot!(x, C_num, 
    label="Numerical (Upwind + Central)", 
    linewidth=2, 
    color=:purple,
    fill=(0, 0.2, :purple))

plot!(title="1D Advection-Diffusion at t=$(round(T_end, digits=1))\n(v=$v, D=$D)",
      xlabel="Position (x)",
      ylabel="Concentration (C)",
      xlims=(0, L),
      ylims=(-0.1, 1.2),
      legend=:topright,
      grid=true)