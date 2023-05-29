import numpy as np
from matplotlib import pyplot as plt
from typing import Tuple
from ODE_solver import *
from typing import Callable

def vol_clamp_sim(T: np.ndarray, C: float, R: float, F: Callable , PEEP=0.0, *,
                  pause_lapsus=None, end_time=None) -> Tuple[np.ndarray, ...]:
    """
    T: array containing the time samples
    C: lung compliance
    R: lung flux resistance
    F: flux to be applied before the exhalation begins
    PEEP: positive end-expiratory pressure
    end_time: time when inhalation ends
    pause_lapsus: lenght of the time interval between inhalation and exhalation

    returns: volume, flux, and pressure for every instant of time
    """

    if end_time is None:
        end_time = T[len(T) // 2]

    if pause_lapsus is None:
        pause_lapsus = np.max(T)*0.1

    # first, simulate a flux pulse for inhalation
    F = np.vectorize(F)
    flux = F(T)

    # integrate flux to find volume and compute pressure
    dt = T[1] - T[0]
    volume = np.cumsum(flux)*dt
    pressure =  R * flux + volume / C + PEEP

    # after the pause lapsus, simulate exhalation
    ex_time= end_time + pause_lapsus
    pressure[T > ex_time] = PEEP
    f = lambda _, v : -(v/C)*1/R
    index = np.abs(T - ex_time).argmin()
    v_0 = volume[index]  # at this point in the simulation, volume[-1] is the maximum stored volume
    volume[T > ex_time] = single_ruku4(T[T > ex_time], f, v_0)
    flux[T > ex_time] = np.gradient(volume[T > ex_time], dt)
   
    return volume, flux, pressure


def pressure_clamp_sim(T: np.ndarray, C: float, R: float, P: Callable) -> Tuple[np.ndarray, ...]:
    """
    T: array containing the time samples
    C: lung compliance
    R: lung flux resistance
    P: function representing the pressure to be applied
    PEEP: positive end-expiratory pressure
    returns: volume, flux, and pressure for every instant of time
    """
    P = np.vectorize(P)
    pressure = P(T)
    f = lambda t, v : (P(t) - v/C)*1/R
    volume = single_ruku4(T, f, 0) # PEEP was deleted
    flux = np.gradient(volume, T)
    return volume, flux, pressure

def plot_VFP(T: np.ndarray, volume: np.ndarray, flux: np.ndarray, pressure: np.ndarray) -> None:
    """
        T: array representing time
        volume, flux, pressure: arrays representing each quantity for every instant T[i]
        plots volume, flux, and pressure against time
    """
    _, axs = plt.subplot_mosaic(
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


    axs["right column"].plot(volume, flux, alpha=0.5, color='k', linestyle='-')
    axs["right column"].set_title("Flux vs. Volume")
    axs["right column"].set_xlabel('Volume')
    axs["right column"].set_ylabel("Flux")
    axs["right column"].axhline(y=0, color='k', linestyle='--')

    plt.show()


def comparative_plot(T: np.ndarray, vol1: np.ndarray, vol2: np.ndarray, flux1: np.ndarray,
                     flux2: np.ndarray, press1: np.ndarray, press2: np.ndarray) -> None:
    """
        T: array representing time
        vol1, flux1, press1: arrays representing initial volume, flux, and pressure for every instant T[i]
        vol2, flux2, press2: arrays representing final volume, flux, and pressure for every instant T[i]
        plots initial and final volume, flux, and pressure against time, superimposed.
    """
    _, axs = plt.subplot_mosaic([['top left', 'right'],
                                    ['medium left', 'right'], 
                                    ['bottom left', 'right']])
    # Comparative values display in right and left 
    # Setting x axes as time
    axs["bottom left"].set_xlabel('T')
    axs["bottom left"].set_xlabel('T')
    
    # Plotting volumne comparison (time)
    axs["top left"].plot(T, vol1, '-b', T, vol2, '-.b')
    axs["top left"].set_ylabel('Volume [ml]')

    # Plotting flux comparison (time)
    axs["medium left"].plot(T, flux1, '-g', T, flux2, '-.g')
    axs["medium left"].set_ylabel("Flux [L/min]")
    
    # Plotting pressure comparison (time)
    axs["bottom left"].plot(T, press1, color = 'deeppink')
    axs["bottom left"].plot(T, press2, linestyle = '-.', color = 'deeppink')
    axs["bottom left"].set_ylabel("Pressure [cmH2O]")

    # plotting volume vs flux (comparative) where the flux is considered to be positive inwards
    axs["right"].plot(vol1, flux1, '-k', vol2, flux2, '-.k')
    axs["right"].set_xlabel('Volume [ml]')
    axs["right"].set_ylabel("Flux [L/min]")
    
    # Tight layout
    plt.tight_layout()
    plt.show()

def clamp_test():
    C = 100
    R = 0.01
    T = np.linspace(0, 15, 1500)


    F = lambda t: 5.0 * (T[len(T)//3] < t < T[len(T)//2])
    volume, flux, pressure = vol_clamp_sim(T, C, R, F)
    plot_VFP(T, volume, flux, pressure)

    # Test for Pressure pulse with a variable amplitude
    P = lambda t: 3.0 * (T[len(T)//3] < t < T[len(T)//2])
    volume, flux, pressure = pressure_clamp_sim(T, C, R, P)
    plot_VFP(T, volume, flux, pressure)

    # Test for a sinusoidal pressure with a variable freq and Amp 
    Amp = 3.0
    freq = 10/np.max(T)
    P = lambda t :  Amp*np.cos(2*np.pi*freq*t) + Amp
    volume, flux, pressure = pressure_clamp_sim(T, C, R, P)
    plot_VFP(T, volume, flux, pressure)

    Amp = 3.0
    freq = 10/np.max(T)
    F = lambda t :  Amp*np.cos(2*np.pi*freq*t)+Amp
    volume, flux, pressure = vol_clamp_sim(T, C, R, F)
    plot_VFP(T, volume, flux, pressure)



def comp_test():
    T = np.linspace(0, 15, 1500)
    C = 10
    R1 = 0.15
    R2 = 0.05
    clamp_val = 5.0
    v1, f1, p1 = vol_clamp_sim(T, C, R1, clamp_val)
    v2, f2, p2 = vol_clamp_sim(T, C, R2, clamp_val)
    comparative_plot(T, v1, v2, f1, f2, p1, p2)

if __name__ == '__main__':
    clamp_test()
    # comp_test()