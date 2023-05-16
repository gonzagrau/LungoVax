#import numpy as np
#from matplotlib import pyplot as plt
from typing import Tuple
from ODE_solver import *

def vol_clamp_sim(T: np.ndarray, C: float, R: float, F: float, PEEP=0.0, *, start_time=5.0,
                  pause_lapsus=2.0, end_time=15.0) -> Tuple[np.ndarray, ...]:
    """
    T: array containing the time samples
    C: lung compliance
    R: lung flux resistance
    F: prefixed constant flux to be applied
    PEEP: positive end-expiratory pressure
    start_time: time when inhalation begins
    end_time: time when inhalation ends
    pause_lapsus: lenght of the time interval between inhalation and exhalation

    returns: volume, flux, and pressure for every instant of time
    """
    # first, simulate a flux pulse for inhalation
    flux_pulse = np.vectorize ( lambda t : F*( start_time < t < end_time) )
    flux = flux_pulse(T)
    # integrate flux to find volume
    dt = T[1] - T[0]
    volume = np.cumsum(flux)*dt
    pressure =  R * flux + volume / C + PEEP

    # after the pause lapsus, simulate exhalation
    ex_time = end_time + pause_lapsus
    pressure[T > ex_time] = 0
    f = lambda t, v : -(PEEP + v/C)*1/R
    v_0 = volume[-1]
    volume[T > ex_time] = single_ruku4(T[T > ex_time], f, v_0)
    flux[T > ex_time] = np.gradient(volume[T > ex_time], T[T > ex_time])
   
    return volume, flux, pressure


def pressure_clamp_sim(T: np.ndarray, C: float, R: float, P: float, *, PEEP = 0.0, start_time = 5.0,
                       end_time = 15.0) -> Tuple[np.ndarray, ...]:
    """
    T: array containing the time samples
    C: lung compliance
    R: lung flux resistance
    P: prefixed constant pressure to be applied
    PEEP: positive end-expiratory pressure
    start_time: time when pressure pulse begins
    end_time: time when pressure pulse ends
    pause_lapsus: lenght of the time interval between inhalation and exhalation

    returns: volume, flux, and pressure for every instant of time
    """
    p_func = np.vectorize( lambda t : P*(start_time <= t < end_time) )
    pressure = p_func(T)
    f = lambda t, v : (p_func(t) - PEEP - v/C)*1/R
    volume = single_ruku4(T, f, 0)
    flux = np.gradient(volume, T)
    return volume, flux, pressure


def sin_pressure_sim(T: np.ndarray, C: float, R: float, freq: float, Amp: float, PEEP = 0.0) -> Tuple[np.ndarray, ...]:
    """
        T: array containing the time samples
        C: lung compliance
        R: lung flux resistance
        freq: respiratory frequency
        Amp: sinusoidal amplitude
        PEEP: positive end-expiratory pressure

        returns: volume, flux, and pressure for every instant of time
    """
    p_func = np.vectorize( lambda t :  Amp*np.cos(2*np.pi*freq*t) + Amp )
    pressure = p_func(T)

    f = lambda t, v : (p_func(t) - PEEP - v/C)*1/R
    volume = single_ruku4(T, f, 0)
    flux = np.gradient(volume, T)
    return volume, flux, pressure


def plot_VFP(T: np.ndarray, volume: np.ndarray, flux: np.ndarray, pressure: np.ndarray) -> None:
    """
        T: array representing time
        volume, flux, pressure: arrays representing each quantity for every instant T[i]
        plots volume, flux, and pressure against time
    """
    fig, axs = plt.subplots(3, 1)
    for ax in axs:
        ax.set_xlabel('T')
    axs[0].plot(T, volume, color='blue')
    axs[0].set_ylabel('Volume [ml]')
    axs[1].plot(T, flux, color='green')
    axs[1].set_ylabel("Flux [L/min]")
    axs[2].plot(T, pressure, color='deeppink')
    axs[2].set_ylabel("Pressure [cmH2O]")

    plt.show()


def comparative_plot(T: np.ndarray, vol1: np.ndarray, vol2: np.ndarray, flux1: np.ndarray,
                     flux2: np.ndarray, press1: np.ndarray, press2: np.ndarray) -> None:
    """
        T: array representing time
        vol1, flux1, press1: arrays representing initial volume, flux, and pressure for every instant T[i]
        vol2, flux2, press2: arrays representing final volume, flux, and pressure for every instant T[i]
        plots initial and final volume, flux, and pressure against time, superimposed.
    """
    fig, axs = plt.subplots(3, 1)
    axs[2].set_xlabel('T')
    axs[0].plot(T, vol1, '-b', T, vol2, '-.b')
    axs[0].set_ylabel('Volume [ml]')
    axs[1].plot(T, flux1, '-g', T, flux2, '-.g')
    axs[1].set_ylabel("Flux [L/min]")
    axs[2].plot(T, press1, color = 'deeppink')
    axs[2].plot(T, press2, linestyle = '-.', color = 'deeppink')
    axs[2].set_ylabel("Pressure [cmH2O]")

    plt.show()

def clamp_test():
    C = 25
    R = 0.1
    T = np.linspace(0, 30, 1000)

    P = 3.0
    volume, flux, pressure = pressure_clamp_sim(T, C, R, P, end_time=13.33)
    plot_VFP(T, volume, flux, pressure)

    F = 5.0
    volume, flux, pressure = vol_clamp_sim(T, C, R, F, end_time=13.33)
    plot_VFP(T, volume, flux, pressure)

    Amp = 3.0
    freq = 5/np.max(T)
    volume, flux, pressure = sin_pressure_sim(T, C, R, freq, Amp)
    plot_VFP(T, volume, flux, pressure)


def comp_test():
    T = np.linspace(0, 30, 1000)
    C1 = 25
    C2 = 15
    R = 0.05
    F = 5.0
    v1, f1, p1 = vol_clamp_sim(T, C1, R, F)
    v2, f2, p2 = vol_clamp_sim(T, C2, R, F)
    comparative_plot(T , v1, v2, f1, f2, p1, p2)

if __name__ == '__main__':
    comp_test()