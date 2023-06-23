#import numpy as np
#from matplotlib import pyplot as plt
from typing import Tuple
from ODE_solver import *
from typing import Callable


def vol_clamp_sim(time_vector: np.ndarray, capacitance: float, resistance: float, flux: Callable, peep=0.0, *,
                  pause_lapsus=None, end_time=None, **kwargs) -> Tuple[np.ndarray, ...]:
    """
    Time: array containing the time samples
    capacitance: lung compliance
    resistance: lung flux resistance
    flux: flux to be applied before the exhalation begins
    peep: positive end-expiratory pressure
    end_time: time when inhalation ends
    pause_lapsus: lenght of the time interval between inhalation and exhalation

    returns: volume, flux, and pressure for every instant of time
    """

    if end_time is None:
        end_time = time_vector[len(time_vector) // 2]

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


def pressure_clamp_sim(T: np.ndarray, C: float, R: float, P: Callable, PEEP=0.0, **kwargs) -> Tuple[np.ndarray, ...]:
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
    p_func = lambda t :  pressure[np.abs(T - t).argmin()]
    f = lambda t, v : (p_func(t) - v/C - PEEP)*1/R
    volume = single_ruku4(T, f, 0)
    flux = np.gradient(volume, T)
    return volume, flux, pressure


def plot_VFP(T: np.ndarray, volume: np.ndarray, flux: np.ndarray, pressure: np.ndarray, show=True) -> None:
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

    axs["middle left"].plot(T, flux, color='green')
    axs["middle left"].set_ylabel("Flux [L/min]")

    axs["bottom left"].plot(T, pressure, color='deeppink')
    axs["bottom left"].set_ylabel("Pressure [cmH2O]")
    axs["bottom left"].set_xlabel("Time [s]")

    axs["right column"].plot(volume, flux, color='r', linestyle='-')
    axs["right column"].set_xlabel("Volume [ml]")
    axs["right column"].set_ylabel("Flux [L/min]")
    axs["right column"].axhline(y=0, color='y', linestyle='-')

    # Tight layout
    plt.tight_layout()

    if show:
        plt.show()
    return fig


def comparative_plot(T: np.ndarray, vol1: np.ndarray, vol2: np.ndarray, flux1: np.ndarray,
                     flux2: np.ndarray, press1: np.ndarray, press2: np.ndarray, show=True) -> None:
    """
        T: array representing time
        vol1, flux1, press1: arrays representing initial volume, flux, and pressure for every instant T[i]
        vol2, flux2, press2: arrays representing final volume, flux, and pressure for every instant T[i]
        plots initial and final volume, flux, and pressure against time, superimposed.
    """
    fig, axs = plt.subplot_mosaic([['top left', 'right'],
                                    ['medium left', 'right'], 
                                    ['bottom left', 'right']])
    # Comparative values display in right and left 
    # Setting x axes as time
    axs["bottom left"].set_xlabel('Time [s]')
    
    # Plotting volume comparison (time)
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
    axs["right"].plot(vol1, flux1, '-r', vol2, flux2, '-.r')
    axs["right"].set_xlabel('Volume [ml]')
    axs["right"].set_ylabel("Flux [L/min]")
    axs["right"].axhline(y=0, color='y', linestyle='-')
    
    # Tight layout
    plt.tight_layout()

    if show:
        plt.show()
    return fig

def ideal_pulse_func(start: float, end: float, A:float) -> Callable:
    """
    start: t_0 - d/2
    end: t_0 + d/2
    A: amplitude

    returns a function that represents the pulse function A*Pi( (t-t_0)/d ) evaluated at time=t
    """
    t_0 = (start + end)/2
    d = end - start
    return lambda t :  A * int( np.abs( (t-t_0)/d ) < 1/2 )


def smooth_pulse_func(start: float, end: float, A:float) -> Callable:
    """
    start: t_0 - d/2
    end: t_0 + d/2
    A: amplitude

    returns a function that represents a smoothed out version of the pulse function A*Pi( (t-t_0)/d ) evaluated at time=t
    """
    t_0 = (start + end)/2
    d = end - start
    return lambda t : A / np.sqrt(1 + ((t - t_0)/(d/2))**18)


def ripply_pulse_func(start: float, end: float, A:float, N:int, lenght:float) -> Callable:
    """
    start: t_0 - d/2
    end: t_0 + d/2
    A: amplitude
    N: number of iterations for the approximation
    lenght: maximum window of time to be considered

    returns a function that represents a ripply version of the pulse function A*Pi( (t-t_0)/d ) evaluated at time=t
    """
    t_0 = (start + end)/2
    d = end - start
    f_0 = 1/lenght
    def fourier_pulse(t):
        result = 0
        w_0 = 2 * np.pi * f_0
        for n in range(-N, N + 1):
            Xn = A * d * f_0 * np.sinc(n * f_0 * d) * np.exp(-1j * n * w_0 * t_0)
            result += np.real(Xn * np.exp(1j * n * w_0 * t))
        return result

    return fourier_pulse


def sinusoidal_func(amplitude: float, phase: float, freq:float) -> Callable:
    """
    Generates a sinusoidal function with the specified parameters
    """
    return lambda t : amplitude*np.sin(2*np.pi*freq*t + phase) + amplitude


def clamp_test():
    def run_both_tests(T_test, C_test, R_test, func, end_time=None, pause_lapsus=None):
        volume, flux, pressure = pressure_clamp_sim(T_test, C_test, R_test, func)
        plot_VFP(T, volume, flux, pressure)

        volume, flux, pressure = vol_clamp_sim(T_test, C_test, R_test, func,
                                               end_time=end_time,
                                               pause_lapsus=pause_lapsus)
        plot_VFP(T, volume, flux, pressure)

    T = np.linspace(0, 15, 1500)
    C = 100
    R = 0.01

    start = T[len(T)//3]
    end = T[len(T)//2]
    A = 5.0

    # Test for hard pulse with a variable amplitude
    Clamp_func = ideal_pulse_func(start, end, A)
    run_both_tests(T, C, R, Clamp_func)

    # Test for a sinusoidal pressure with a variable freq and Amp
    Amp = 3.0
    freq = 10/np.max(T)
    Clamp_func = sinusoidal_func(Amp, 0, freq)
    run_both_tests(T, C, R, Clamp_func)

    # Test for a smooth pulse
    Clamp_func = smooth_pulse_func(start, end, A)
    pause = 2.0
    end_time = end + pause
    run_both_tests(T, C, R, Clamp_func, end_time=end_time, pause_lapsus=pause)

    # Test for a ripply pulse
    N_iter = 20
    lenght = T[-1]
    Clamp_func = ripply_pulse_func(start, end, A, N_iter,lenght)
    pause = 2.0
    end_time = end + pause
    run_both_tests(T, C, R, Clamp_func, end_time=end_time, pause_lapsus=pause)

def comp_test():
    C = 10
    R = 0.1
    T = np.linspace(0, 15, 1500)

    start = T[len(T)//3]
    end = T[len(T)//2]
    A = 5.0
    pause = 3.0

    F_hard = ideal_pulse_func(start, end, A)
    F_soft = smooth_pulse_func(start, end, A)
    v1, f1, p1 = pressure_clamp_sim(T, C, R, F_hard)
    v2, f2, p2 = pressure_clamp_sim(T, C, R, F_soft)
    comparative_plot(T, v1, v2, f1, f2, p1, p2)


if __name__ == '__main__':
    clamp_test()
    #comp_test()