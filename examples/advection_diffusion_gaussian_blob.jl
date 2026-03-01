using Plots

# --- 1. System Parameters ---
L = 20.0         # Longer domain so the blob doesn't hit the wall
v = 2.0          # Advection velocity
D = 0.5          # Diffusion coefficient
T_end = 4.0      # Total simulation time

# Initial Blob Parameters
x0 = 4.0         # Initial starting position of the blob
sigma_0 = 0.5    # Initial width (standard deviation)

# --- 2. Grid Setup ---
nx = 200
dx = L / (nx - 1)
x = range(0, L, length=nx)

# --- 3. Stability Conditions ---
dt_advection = 0.8 * (dx / v)
dt_diffusion = 0.4 * (dx^2 / D)
dt = min(dt_advection, dt_diffusion) 
nt = Int(ceil(T_end / dt)) 

# --- 4. Initialization (The Gaussian Blob) ---
C_num = zeros(nx)
for i in 1:nx
    C_num[i] = exp(- (x[i] - x0)^2 / (2 * sigma_0^2))
end

# Store the initial state for plotting later
C_initial = copy(C_num)

# --- 5. The Advection-Diffusion Solver ---
for n in 1:nt
    C_old = copy(C_num)
    
    for i in 2:(nx-1)
        # Upwind Advection + Central Diffusion
        adv_term  = v * (dt / dx) * (C_old[i] - C_old[i-1])
        diff_term = D * (dt / dx^2) * (C_old[i+1] - 2*C_old[i] + C_old[i-1])
        
        C_num[i] = C_old[i] - adv_term + diff_term
    end
    
    # Zero-gradient boundary conditions (flat tails)
    C_num[1] = C_num[2]
    C_num[nx] = C_num[nx-1]
end

# --- 6. The Analytical Solution ---
C_analytical = zeros(nx)
# Calculate the new width and new amplitude at T_end
sigma_t = sqrt(sigma_0^2 + 2 * D * T_end)
amplitude_t = sigma_0 / sigma_t

for i in 1:nx
    C_analytical[i] = amplitude_t * exp(- (x[i] - x0 - v * T_end)^2 / (2 * sigma_t^2))
end

# --- 7. Plotting ---
plot(x, C_initial, 
    label="Initial Blob (t=0)", 
    linewidth=2, 
    color=:gray, 
    linestyle=:dot)

plot!(x, C_analytical, 
    label="Analytical (t=$T_end)", 
    linewidth=3, 
    color=:black, 
    linestyle=:dash)

plot!(x, C_num, 
    label="Numerical (t=$T_end)", 
    linewidth=2, 
    color=:red,
    fill=(0, 0.2, :red))

plot!(title="ADE: Gaussian Blob Advection & Diffusion",
      xlabel="Position (x)",
      ylabel="Concentration (C)",
      xlims=(0, L),
      ylims=(0, 1.1),
      legend=:topright,
      grid=true)