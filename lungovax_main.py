#import numpy as np
#from matplotlib import pyplot as plt
from typing import Tuple
from ODE_solver import *

def vol_clamp_sim(T: np.ndarray, C: float, R: float, F: float, PEEP=0.0, *, start_time=0.5,
                  pause_lapsus=0.2, end_time=1.5) -> Tuple[np.ndarray, ...]:
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
    pressure[T > ex_time] = PEEP
    f = lambda t, v : -(v/C)*1/R
    v_0 = volume[-1]
    volume[T > ex_time] = single_ruku4(T[T > ex_time], f, v_0)
    flux[T > ex_time] = np.gradient(volume[T > ex_time], dt)
   
    return volume, flux, pressure


def pressure_clamp_sim(T: np.ndarray, C: float, R: float, P: float, *, PEEP = 0.0, start_time = 0.5,
                       end_time = 1.5) -> Tuple[np.ndarray, ...]:
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
    fig, axs = plt.subplot_mosaic(
        [["top left", "right column"],
         ["middle left", "right column"],
         ["bottom left", "right column"]]
    )

    axs["top left"].plot(T, volume, color='blue')
    axs["top left"].set_ylabel('Volume [ml]')
    axs["top left"].set_title("V, F, P vs. T")

    axs["middle left"].plot(T, flux, color='green')
    axs["middle left"].set_ylabel("Flux [L/min]")

    axs["bottom left"].plot(T, pressure, color='deeppink')
    axs["bottom left"].set_ylabel("Pressure [cmH2O]")
    axs["bottom left"].set_xlabel("Time [s]")

    axs["right column"].plot(volume, flux)
    axs["right column"].set_title("Flux vs. Volume")
    axs["right column"].set_xlabel('Volume')
    axs["right column"].set_ylabel("Flux")
    axs["right column"].axhline(y=0, color='k', linestyle='--')
    plt.show()


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
    C = 100
    R = 0.01
    T = np.linspace(0, 5, 1500)

    P = 3.0
    volume, flux, pressure = pressure_clamp_sim(T, C, R, P, end_time=2.5)
    plot_VFP(T, volume, flux, pressure)

    F = 5.0
    volume, flux, pressure = vol_clamp_sim(T, C, R, F, end_time=2.5)
    plot_VFP(T, volume, flux, pressure)

    Amp = 3.0
    freq = 5/np.max(T)
    volume, flux, pressure = sin_pressure_sim(T, C, R, freq, Amp)
    plot_VFP(T, volume, flux, pressure)


def comp_test():
    T = np.linspace(0, 3, 1500)
    C = 15
    R1 = 0.15
    R2 = 0.05
    clamp_val = 5.0
    v1, f1, p1 = vol_clamp_sim(T, C, R1, clamp_val)
    v2, f2, p2 = vol_clamp_sim(T, C, R2, clamp_val)
    comparative_plot(T, v1, v2, f1, f2, p1, p2)

if __name__ == '__main__':
    clamp_test()
    #comp_test()