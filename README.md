# LungoVax
This project intends to be the most complete and powerful respiratory simulator for didactic purposes. With a powerful simulation engine fueled by NumPy, a wide range of testable inputs, and a user-friendly GUI, LungoVax is the ideal tool for the lung mechanics student.

![image](https://github.com/gonzagrau/LungoVax/assets/107513203/f5cccf8e-9f7f-4e46-ae7b-3a8becc706df)

## What LungoVax does

LungoVax implements the two (or three) element model for the dynamical mechanical properties of the respiratory system, described by the equation $$P_T 
= RQ + \frac{V}{C_S} + PEEP$$
where $P_T$ is the transpulmonary pressure, $PEEP$ is the positive end-expiratory pressure (a constant), $R$ is the lung resistance, $Q = \dot V$ is the flux, and $C_S$ is the total compliance, which can be inputted either directly or as a series connection of $C_L$ (lung compliance) and $C_T$ (thoraric compliance), using the equivalence $C_S = \frac{C_LC_T}{C_L + C_T}\$.

The user sets the constant parameters $R$ and $C$, and then chooses a variable (either flux or pressure) to clamp. The fixed variable is then defined for the entire simulation time, either as a pulse or as a sinusoid. As an output, the program plots the resulting volume, flux, and pressure curves as a function of time, followed by the flux vs. volume loop.

## Input options
The values for both resistance and compliance are set by the user within an acceptable range, determined by sliders. Once the clamped variable is chosen, the function that represents its dependance on time is set to be either a sinusoid (with a chosen amplitude, frequency and phase) or a pulse (with a specified height, start time, and endtime). In order to better represent realistic scenarios, there is a series of possible pulse functions to choose from:
<ul>
  <li>Ideal pulse: a perfectly sharp pulse, defined mathematically by a rectangular function</li>
  <li>Smooth pulse: a smoothed-out version of the ideal pulse, that better reflects a continuous pressure/flux wave</li>
  <li>Real pulse: a ripply version of an ideal pulse, which better represents the result of an electrically generated pulse</li>
</ul>

## Comparative plotting
The user can choose to run either one or two simulations simultanously. If the "second simulation" checkbox is ticked, inputs for both simulations will be requiered, and both sets of graphs will be plotted in the same set of axis. To differentiate the results from each simulation, the original one is plotted with a solid line, and the second one with a dotted line.


## Other cool features
<ul>
  <li>User-friendly GUI, built with CustomTKinter</li>
  <li>Light/dark mode switch</li>
  <li>Language selector (current available languages: english and spanish)</li>
  <li>Reset-all button</li>
</ul>

## Some code snippets
### ODE_solver.py
This module was developed to solve ordinary differential equations (ODEs) by applying the Runge-Kutta 4 method. To do so in a vectorized way, NumPy was the obvious choice. In addition, a new class was defined to emulate a MATLAB-like behaviour for an array of vector functions:

```python
class FunctionArray(object):
    def __init__(self, functions: list = None) -> None:
        if functions is None:
            functions = []
        self.functions = functions

    def append(self, func: Callable) -> None:
        self.functions.append(func)

    def __call__(self, *args, **kwargs) -> np.ndarray:
        return np.array([f(*args, **kwargs) for f in self.functions])

    def __len__(self) -> int:
        return len(self.functions)
```

The core function of this module, and the engine that fuels the entire simulation, is the following:

```python
def ruku4(T: np.ndarray, F: FunctionArray, X_0: np.ndarray) -> np.ndarray:
    """
    :param np.ndarray T: time array of len N, defined as the range a:h:b
    :param np.ndarray F: array of functions of len M
    :param np.ndarray X_0: array of initial conditions at T[0]

    Uses the Runge-Kutta 4 method to solve the following system of differential equations:
    dX/dt = F(T, X(T))
    where X and F are vectors of functions of time, and T is a scalar. This translates to:
    { dX[0](T)/dt = F[0](T, X(T))
    { dX[1](T)/dt = F[1](T, X(T))
                 ...
    { dX[M](T)/dt = F[M](T, X(T))

    :return np.ndarray: X, an array of dimensions M x N with the values of each X[i] at T[j]
    """
    h = T[1] - T[0]
    N = len(T)
    M = len(F)
    X = np.zeros((N, M))
    X[0, :] = X_0

    for j in range(N - 1):
        X_j = X[j, :]
        k1 = F(T[j], X_j)
        k2 = F(T[j] + h / 2, X_j + (h / 2) * k1)
        k3 = F(T[j] + h / 2, X_j + (h / 2) * k2)
        k4 = F(T[j] + h, X_j + h * k3)
        X[j + 1, :] = X_j + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6

    return X
```
It is using this function that a method to solve a single ordinary differential equation can be defined, which is exactly what single_ruku4 does:

```python
def single_ruku4(T: np.ndarray, f: Callable, x0 : float|int) -> np.ndarray:
    """
    :param np.ndarray T: time array of len N, defined as the range a:h:b
    :param Callable f: function of time and x, f(t, x)
    :param float|int x0: initial condition, x(t=T[0])

    Applies the Runge-Kutta 4 method (readily implemented in ruku4) to a single ODE of the form:
    dx(T)/dt = f(T, x(T))

    :return np.ndarray: x, a 1-dimensional numpy array of len N with the values of x at every instant T[j]
    """
    F = FunctionArray([f])
    X_0 = np.array([x0])
    x = ruku4(T, F, X_0)[:, 0]
    return x
```

There is also a third function we developed in order to solve higher-order linear ODEs, by transforming it into an equivalent system of first-order ODEs using state variables

```python
def higher_order_ODE(T: np.ndarray, f: Callable, X_0: np.ndarray, v: np.ndarray) -> np.ndarray:
    """
    :param np.ndarray: time array of len N, defined as the range a:h:b
    :param f: function of time and x, f(t, x)
    :param np.ndarray: initial conditions for x (x(T[0]), x'(T[0]), ... x**(M-1)(T[0]))
    :param np.ndarray: vector containing of len M + 1 containing the coefficients a_0, a_1, ..., a_M

    Applies the Runge-Kutta 4 method (readily implemented in ruku4()) to a single M-order ODE of the form:
    a_M*x**(M) + a_(M-1)*x**(M-1) + ... + a_1*x' + a_0*x = f(t, x)
    using state variables, by calling x = X[0] and building the system
    {   X[0]' = X[1]
    {        ...
    { X[M-2]' = X[M-1]
    { X[M-1]' = (f(t, X[0]) - <v[:-1], X>)/v[-1]
    where <.,.> indicates the dot product.

    :return np.ndarray: x, a 1-dimensional numpy array of len N with the values of x at every instant T[j]
    """
    M = len(X_0)
    if M + 1 != len(v):
        raise ValueError("The dimensions of the coefficients and the initial conditions do not match")
    F = FunctionArray()
    for i in range(M - 1):
        F.append(lambda t, X : X[i+1])
    F.append(lambda t, X : ( f(t, X[0]) - np.dot(v[:-1], X)) / v[-1])
    x = ruku4(T, F, X_0)[:, 0]
    return x
```

### assisted_respiration_simulation.py
This module implements the base equation for the model, and runs the simulations for any given input. There are two types of simulations: volume clamp and presure clamp. The difference between the two is which variable (either flux or pressure) is set as an input. Thus, the following two functions are defined:
```python
def vol_clamp_sim(time_vector: np.ndarray,
                  capacitance: float, resistance: float,
                  flux: Callable,
                  peep=0.0, *,
                  pause_lapsus=None,
                  end_time=None, **kwargs) -> Tuple[np.ndarray, ...]:
    """
    Time: array containing the time samples
    capacitance: lung compliance
    resistance: lung flux resistance
    flux: flux to be applied before the exhalation begins
    peep: positive end-expiratory pressure
    end_time: time when inhalation ends
    pause_lapsus: length of the time interval between inhalation and exhalation

    returns: volume, flux, and pressure for every instant of time
    """

    if end_time is None:
        end_time = time_vector[int(0.6*len(time_vector))]

    if pause_lapsus is None:
        pause_lapsus = np.max(time_vector) * 0.1

    # first, simulate inhalation
    flux = np.vectorize(flux)
    flux = flux(time_vector)
    flux[time_vector > end_time] = 0.0

    # integrate flux to find volume and compute pressure
    dt = time_vector[1] - time_vector[0]
    volume = np.cumsum(flux)*dt
    pressure = resistance * flux + volume / capacitance + peep

    # after the pause lapsus, simulate exhalation
    ex_time = end_time + pause_lapsus
    pressure[time_vector > ex_time] = peep
    index = np.abs(time_vector - ex_time).argmin()
    v_0 = volume[index]
    volume[time_vector > ex_time] = single_ruku4(time_vector[time_vector > ex_time],
                                                 lambda _, v: -(v / capacitance) * 1 / resistance, v_0)
    flux[time_vector > ex_time] = np.gradient(volume[time_vector > ex_time], dt)
   
    return volume, flux, pressure
```

```python
def pressure_clamp_sim(time_array: np.ndarray,
                        compliance: float, resistance: float,
                        pressure_function: Callable,
                        peep=0.0, **kwargs) -> Tuple[np.ndarray, ...]:
    """
    T: array containing the time samples
    C: lung compliance
    R: lung flux resistance
    P: function representing the pressure to be applied
    PEEP: positive end-expiratory pressure
    returns: volume, flux, and pressure for every instant of time
    """
    pressure_function = np.vectorize(pressure_function)
    pressure = pressure_function(time_array)

    def p_func(t):
        return pressure[np.abs(time_array - t).argmin()]

    def flux(t, v):
        return (p_func(t) - v / compliance - peep) * 1 / resistance

    volume = single_ruku4(time_array, flux, 0)
    flux = np.gradient(volume, time_array)
    return volume, flux, pressure
```


