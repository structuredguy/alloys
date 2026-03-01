Adding physical diffusion to our advection model is exactly the right next step. Now we are no longer just pushing a mathematically perfect block of carbon down a pipe; we are watching it physically spread out and blur into the surrounding material as it travels.

### 1. The Governing Equation

The 1D **Advection-Diffusion Equation (ADE)** combines both transport mechanisms into a single PDE:

$$\frac{\partial C}{\partial t} + v \frac{\partial C}{\partial x} = D \frac{\partial^2 C}{\partial x^2}$$

* **Left Side (Advection):** The bulk movement of the fluid carrying the carbon at velocity $v$.
* **Right Side (Diffusion):** The random spreading of the carbon atoms driven by the concentration gradient, scaled by the diffusion coefficient $D$.

### 2. The Numerical Strategy

To solve this numerically, we combine the two techniques we have discussed:

1. **For Advection ($v \frac{\partial C}{\partial x}$):** We keep the **Upwind Scheme** (looking backward to $i-1$) because information flows from left to right.
2. **For Diffusion ($D \frac{\partial^2 C}{\partial x^2}$):** We use the **Central Difference Scheme** (looking at $i-1$, $i$, and $i+1$) because diffusion spreads in both directions simultaneously.

A critical detail: adding diffusion makes the simulation much more sensitive to blowing up. We must restrict our time step (`dt`) to satisfy **both** the advection stability limit (Courant number) and the diffusion stability limit.

### 3. The Julia Solution

Here is the complete Julia code. It plots the numerical solution alongside the analytical solution (which, for a continuous step injection, uses the complementary error function `erfc`).

### What happens in this plot?

When you run this, you will see the wave has still traveled exactly to $x = 5.0$ (because $v = 1.0$ and $T_{end} = 5.0$).

However, instead of the sharp, vertical cliff we saw in pure advection, the front of the wave now has a smooth, S-shaped curve. This S-curve is dictated exactly by the complementary error function (`erfc`).

* **Advection** determines *where* the center of the curve is.
* **Diffusion** determines *how wide* and slanted the curve is.

If you change `D = 0.1` to `D = 0.5` in the code, you will see the curve blur out much further ahead of and behind the $x = 5.0$ mark.

**Would you like me to show you how to wrap this solver in an animation loop so you can watch the carbon dynamically flow and spread down the pipe from $t=0$ to $t=5$?**