import numpy as np
from matplotlib import pyplot as plt
from typing import Tuple
from ODE_solver import *

def vol_clamp_sim(T: np.ndarray, C: float, R: float, F: float, PEEP=0.0, *, start_time=5.0,
                  pause_lapsus=2.0, end_time=15.0) -> Tuple[np.ndarray, ...]:
    """
    T: array containing the time samples
    C: lung compliance
    R: lung flux resistance
    F: prefixed constant flux to be applied
    start_time: time when inhalation begins
    end_time: time when inhalation ends
    pause_lapsus: lenght of the time interval between inhalation and exhalation

    returns: volume, flux, and pressure as a function of time
    """

    inhale = lambda x: F * (x - start_time)
    V_c = F * (end_time - start_time)
    tau = 1 / (R * C)
    ex_time = end_time + pause_lapsus
    exhale = lambda x: V_c * np.exp(-tau * (x - ex_time))
    v_vol = np.vectorize(
        lambda x: inhale(x) * (start_time < x < end_time) + V_c * (end_time <= x < ex_time) + exhale(x) * (
                    x >= ex_time))

    volume = v_vol(T)
    flux = np.gradient(volume, T)
    pressure = R * flux + volume / C + PEEP
    return volume, flux, pressure


def pressure_clamp_sim(T: np.ndarray, C: float, R: float, P: float, PEEP = 0.0, *, start_time = 5.0,
                       end_time = 15.0) -> Tuple[np.ndarray, ...]:
    """
    T: array containing the time samples
    C: lung compliance
    R: lung flux resistance
    P: prefixed constant pressute to be applied
    start_time: time when pressure pulse begins
    end_time: time when pressure pulse ends
    pause_lapsus: lenght of the time interval between inhalation and exhalation

    returns: volume, flux, and pressure as a function of time
    """
    h = T[1] - T[0]
    p_func = np.vectorize( lambda t : P*(start_time <= t < end_time) )
    pressure = p_func(T)

    f = lambda t, v : (p_func(t) - PEEP - v/C)*1/R
    v_0 = 0
    volume = single_ruku4(T, f, v_0)
    '''
    inhale = lambda t : (C*(P-PEEP))*(1 - np.exp(-(t-start_time)/(R*C)))
    exhale = lambda t : (C*(P-PEEP))*(np.exp(-(t-end_time)/(R*C)))
    vol_func = np.vectorize( lambda t : inhale(t)*(start_time < t < end_time) + exhale(t)*(t > end_time) )
    volume = vol_func(T)
    '''
    flux = np.gradient(volume, T)
    flux[abs(T - end_time) < h] = 0  # fixing a discontinuity overshoot at t ~ end_time
    return volume, flux, pressure


def plot_VFP(t: np.ndarray, volume: np.ndarray, flux: np.ndarray, pressure: np.ndarray):
    fig, axs = plt.subplots(3, 1)
    for ax in axs:
        ax.set_xlabel('T')
    axs[0].plot(t, volume, color='blue')
    axs[0].set_ylabel('Volumen [ml]')
    axs[1].plot(t, flux, color='green')
    axs[1].set_ylabel("Flujo [L/min]")
    axs[2].plot(t, pressure, color='#FF3366')
    axs[2].set_ylabel("Presión [cmH2O]")

    plt.show()


def main():
    C = 40
    R = 0.1
    P = 20

    T = np.linspace(0, 30, 1000)
    volume, flux, pressure = pressure_clamp_sim(T, C, R, P, end_time=13.33)
    plot_VFP(T, volume, flux, pressure)

    F = 5
    volume, flux, pressure = vol_clamp_sim(T, C, R, F, end_time=13.33)
    plot_VFP(T, volume, flux, pressure)

if __name__ == '__main__':
    main()