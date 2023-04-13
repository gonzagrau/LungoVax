import numpy as np
from matplotlib import pyplot as plt
from typing import Callable


class FunctionArray(object):
    def __init__(self, functions=None):
        if functions is None:
            functions = []
        self.functions = functions

    def append(self, func: Callable):
        self.functions.append(func)

    def __call__(self, *args, **kwargs):
        return np.array([f(*args, **kwargs) for f in self.functions])

    def __len__(self):
        return len(self.functions)


def ruku4(T: np.ndarray, F: FunctionArray, X_0: np.ndarray) -> np.ndarray:
    """
    T: time array of len N, defined as the range a:h:b
    F: array of functions of len M
    X_0: array of initial conditions at T[0]

    Uses the Runge-Kutta 4 method to solve the following system of differential equations:
    dX/dt = F(T, X(T))
    where X and F are vectors of functions of time, and T is a scalar. This translates to:
    { dX[0]/dt = F[0](T, X[T])
    { dX[1]/dt = F[1](T, X[T])
    ...
    { dX[M]/dt = F[M](T, X[T])

    Returns: X, an array of dimensions M x N with the values of each X[i] at T[j]
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


def single_ruku4(T: np.ndarray, f: Callable, x0 : float) -> np.ndarray:
    """
    @param T: time array of len N, defined as the range a:h:b
    @param f: function of time and x, f(t, x)
    @param x0: initial condition, x(t=T[0])

    Applies the Runge-Kutta 4 method (readily implemented in ruku4() ) to a single ODE of the form:
    dx/dt = f(t, x)
    where x = x(t)

    @return: x, a 1-dimensional numpy array of len N with the values of x at every instant T[j]
    """
    F = FunctionArray()
    F.append(f)
    X_0 = np.array([x0])
    x = ruku4(T, F, X_0)[:, 0]
    return x


def higher_order_ODE(T: np.ndarray, f: Callable, X_0: np.ndarray, v: np.ndarray) -> np.ndarray:
    """
    @param T: time array of len N, defined as the range a:h:b
    @param f: function of time and x, f(t, x)
    @param X_0: initial conditions for x(T[0]), x'(T[0]), ... x**(M-1)(T[0])
    @param v: vector containing of len M+1 containing the coefficients a_0, a_1, ..., a_M

    Applies the Runge-Kutta 4 method (readily implemented in ruku4() ) to a single M-order ODE of the form:
    a_M*x**(M) + a_(M-1)*x**(M-1) + ... + a_1*x' + a_0*x = f(t, x)
    using state variables, by calling x = X[0] and building the system
    {X[0]' = X[1]
    {...
    {X[M-2]' = X[M-1]
    {X[M-1]' = ( f(t, X[0]) - <v[:-1], X> )/v[-1]
    where <.,.> indicates the dot product.

    @return: x, a 1-dimensional numpy array of len N with the values of x at every instant T[j]
    """
    M = len(X_0)
    if M+1 != len(v):
        raise ValueError("The dimensions of the coefficients and the initial conditions do not match")
    F = FunctionArray()
    for i in range(M-1):
        F.append(lambda t, X : X[i+1])
    F.append(lambda t, X : ( f(t, X[0]) - np.dot(v[:-1], X)) / v[-1] )
    x = ruku4(T, F, X_0)[:, 0]
    return x


def test_ruku4():
    """
    solves the system
    {dx/dt = x + 2*y
    {dy/dt = 3x + 2*y

    (x(0), y(0)) = (6, 4)
    in the time interval [0,5]. The numerical solution is plotted superimposed with the analytical solution.
    """
    T = np.linspace(0, 5, 200)
    F = FunctionArray()
    F.append(lambda t, X: X[0] + 2 * X[1])
    F.append(lambda t, X: 3 * X[0] + 2 * X[1])
    X_0 = np.array([6, 4])
    X = ruku4(T, F, X_0)

    fig, axs = plt.subplots(2, 1)
    axs[0].plot(T, X[:, 0], 'r-')
    axs[0].plot(T, 4 * np.exp(4 * T) + 2 * np.exp(-T), 'b--')
    axs[1].plot(T, X[:, 1])
    axs[1].plot(T, 6 * np.exp(4 * T) - 2 * np.exp(-T), 'b--')

    plt.show()


def test_single_ruku4():
    """
    solves the ODE
    dX/dt = t*x
    and plots it compared to the analytical solution
    """
    T = np.linspace(0, 5, 200)
    f = lambda t, x : -t*x
    x_0 = 1
    x = single_ruku4(T, f, x_0)

    plt.plot(T, x, 'r-')
    plt.plot(T, np.exp(-(T**2)/2), 'b--')

    plt.show()


def test_higher_order_ODE():
    """
    solves the order 2 ODE
    x'' − 10*x' + 9*x = 5*t, x(0)=−1, x'(0)=2
    and plots it compared to the analytical solution
    """
    T = np.linspace(0, 0.5, 200)
    coefficients = np.array([9,-10,1])
    X_0 = np.array([-1, 2])
    f = lambda t, x : 5*t
    x = higher_order_ODE(T, f, X_0, coefficients)

    plt.plot(T, x, 'r-')
    plt.plot(T, 50/81 + 5*T/9 - 2*np.exp(T) + (31/81)*np.exp(9*T), 'b--')

    plt.show()



if __name__ == '__main__':
    test_ruku4()
    test_single_ruku4()
    test_higher_order_ODE()