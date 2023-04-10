import numpy as np
from matplotlib import pyplot as plt
from typing import Callable, Tuple
from volume_clamp import plot_VFP
from ODE_solver import *



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
    p_func = np.vectorize( lambda t : P*(start_time <= t < end_time) )
    pressure = p_func(T)

    f = lambda t, v : (p_func(t) - PEEP - v/C)*1/R
    v_0 = 0
    volume = single_ruku4(T, f, v_0)
    '''
    vol_func = np.vectorize( lambda t : 0*(t < start_time) \
                                        + (C*(P-PEEP))*(1 - np.exp(-(t-start_time)/(R*C)))*(start_time <= t < end_time) \
                                        + (C*(P-PEEP))*(np.exp(-(t-end_time)/(R*C)))*(t > end_time))
    volume = vol_func(T)
    '''
    flux = np.gradient(volume, T)
    return volume, flux, pressure


def main():
    C = 40
    R = 0.05
    P = 20

    T = np.linspace(0, 30, 1000)
    volume, flux, pressure = pressure_clamp_sim(T, C, R, P, end_time=13.33)
    plot_VFP(T, volume, flux, pressure)

if __name__ == "__main__":
    main()