# LungoVax
This project intends to be the most complete and powerful respiratory simulator for didactic purposes. With a powerful simulation engine fueled by numpy, a wide range of testable inputs, and a user-friendly GUI, LungoVax is the ideal tool for the lung mechanics student.

![image](https://github.com/gonzagrau/LungoVax/assets/107513203/f5cccf8e-9f7f-4e46-ae7b-3a8becc706df)

# What LungoVax does

LungoVax implements the two (or three) element model for the dynamical mechanical properties of the respiratory system, described by the equation 
$P_T = RQ + \frac{V}{C_S} + PEEP$
Where $P_T$ is the transpulmonary pressure, $PEEP$ is the positive end-expiratory pressure $R$ is the lung resistance, $Q = \dot V$ is the flux, and $C_S$ is the total compliance, which can be inputted either directly or as a series connection of $C_L$ (lung compliance) and $C_T$ (rib cage compliance), using the equivalence $C_S = \frac{C_LC_T}{C_L + C_T}\$.

The user sets the constant parameters $R$ and $C$, and then chooses a variable (either flux or pressure) to clamp. The fixed variable is then defined for the entire simulation time, either as a pulse or as a sinusoid. The program then plots the resulting volume, flux, and pressure curves as a function of time, followed by the flux vs. volume loop.

# Pulse options
<ul>
  <li>Ideal pulse: a perfectly sharp pulse, defined mathematically by a rectangular function</li>
  <li>Smooth pulse: a smoothed-out version of the ideal pulse, that better reflects a continous pressure/flux wave</li>
  <li>Real pulse: a ripply version of an ideal pulse, which better represents the result of an electrically generated pulse</li>
</ul>

# Other cool features
<ul>
  <li>Light/Dark mode switch</li>
  <li>Language selector</li>
  <li>Reset-all button</li>
</ul>


