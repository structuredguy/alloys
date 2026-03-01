Pumping carbon into a clean pipe (or molten metal flow) starting at $t=0$.

To solve this, we will use the **Method of Characteristics** for the analytical part, and an **Upwind Finite Difference Scheme** for the numerical part in Julia.

Here is how the physics and the code come together.

---

### 1. The Analytical Solution (Method of Characteristics)

We are solving the 1D pure advection equation. Let's use $v$ for velocity (instead of $D$, so we don't confuse it with diffusion):

$$\frac{\partial C}{\partial t} + v \frac{\partial C}{\partial x} = 0$$

**The Physical Setup:**

* **Initial Condition (The empty rod):** At $t=0$, there is no carbon in the rod. $C(x, 0) = 0$ for $x > 0$.
* **Boundary Condition (The continuous injection):** At $x=0$, we maintain a constant concentration $C_0$ starting at $t=0$. $C(0, t) = C_0$ for $t \ge 0$.

**The Solution:**
The advection equation states that concentration is strictly conserved along lines of constant speed (called "characteristics"). Mathematically, the solution must take the form of a traveling wave: $C(x,t) = f(x - vt)$.

Because information only travels forward at speed $v$, we can break the rod into two distinct zones:

1. **Downstream ($x > vt$):** The fluid here was already in the pipe at $t=0$. The injected carbon hasn't reached this point yet. So, $C(x,t) = 0$.
2. **Upstream ($x \le vt$):** The fluid here entered the pipe *after* $t=0$ from the boundary $x=0$. It carries the injected concentration. So, $C(x,t) = C_0$.

We can write this elegantly using the **Heaviside step function** ($H$):

$$C(x,t) = C_0 \cdot H(vt - x)$$

This mathematically perfectly describes a solid "wall" or "step" of carbon moving to the right at a constant speed $v$.

---

### 2. The Julia Solution (Upwind Scheme)

When solving advection numerically, you cannot use the standard central difference method we used for diffusion—it causes the wave to wildly oscillate and blow up (a phenomenon known as numerical instability).

Because physics tells us information only flows from left to right, our numerical solver must only look backwards to the left. This is called the **Upwind Scheme**.

Here is the complete Julia code to solve this and plot the analytical vs. numerical results side-by-side.

```julia
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

```

### What to Look For in the Plot

When you run this in Julia, you will see a graph at $t = 5.0$. Because the velocity is $v = 1.0$, the wave should be exactly halfway down the length 10 rod.

You will notice a fascinating discrepancy between the two lines:

1. **The Analytical Line (Black dashed):** This is a perfectly sharp 90-degree cliff face exactly at $x = 5.0$.
2. **The Numerical Line (Blue solid):** The wave is in the correct location ($x = 5.0$), but the "cliff" is slightly rounded or smeared out.

**Why does the numerical version smear?**
This is known as **Numerical Diffusion**. Because computers use discrete grids ($\Delta x$) rather than continuous space, the process of averaging the values from one grid cell to the next accidentally acts exactly like Fick's Law of Diffusion. The code inherently "blurs" the sharpness of the advection over time, even though we didn't program any diffusion into the math!

**Would you like me to show you how to add actual, physical diffusion into this Julia script so you can solve the full Advection-Diffusion equation?**