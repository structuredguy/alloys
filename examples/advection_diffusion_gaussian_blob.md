This is a fantastic transition. Moving from the "Step Function" to the "Gaussian Blob" perfectly isolates the two physical behaviors: you will literally see the advection *translating* the center of mass, while the diffusion simultaneously *deflates and widens* the blob.

### 1. The Physics and The Math

When you inject a finite "blob" of carbon into a long rod (or a pipe), you no longer have an infinite supply pushing from the left. You have a fixed number of atoms.

Mathematically, our Initial Condition at $t=0$ is a Gaussian bell curve centered at $x_0$ with an initial variance $\sigma_0^2$:


$$C(x, 0) = \exp\left( -\frac{(x - x_0)^2}{2\sigma_0^2} \right)$$

As time moves forward, two things happen simultaneously in the **Analytical Solution**:

1. **Advection (Translation):** The center of the peak moves to the right. The new center becomes $x_c = x_0 + vt$.
2. **Diffusion (Spreading):** The variance (width) of the curve grows linearly with time: $\sigma^2(t) = \sigma_0^2 + 2Dt$.
3. **Conservation of Mass:** Because the blob gets wider, it *must* get shorter so the total area under the curve remains constant.

The exact analytical solution combines all three effects:


$$C(x,t) = \frac{\sigma_0}{\sqrt{\sigma_0^2 + 2Dt}} \exp\left( -\frac{(x - (x_0 + vt))^2}{2(\sigma_0^2 + 2Dt)} \right)$$

---

### 2. The Julia Code (The Gaussian Blob)

We can adapt our previous script. We will make the domain longer (`L = 20.0`), start the blob at `x = 4.0`, and let it travel.

Notice that we changed the boundary conditions. Since the blob is in the middle of the rod, we just let the edges of the simulation remain flat (zero-gradient).
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

```

### 3. The "Secret" of Numerical Solvers

When you run this code, look very closely at the red numerical curve compared to the black dashed analytical curve. You will likely notice that the red curve is slightly **shorter and wider** than the perfect mathematical solution.

This is not a bug in your code! This exposes a famous flaw in the **Upwind Scheme**. The simple act of checking the grid point to the left ($i-1$) inherently acts like a tiny bit of extra, artificial diffusion. In computational physics, this is called **Numerical Diffusion**.

Your numerical solver is actually simulating a system with an effective diffusion of $D_{total} = D_{physical} + D_{numerical}$.

**Would you like me to show you how to swap the Upwind scheme for the "Lax-Wendroff" scheme, which mathematically eliminates this artificial numerical diffusion to make your solver much more accurate?**