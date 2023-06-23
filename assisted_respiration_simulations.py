from typing import Tuple
from ODE_solver import *
from typing import Callable
from language_package_manager import LANG_PACK

UNITS = {'Volume': '$[ml]$',
         'Pressure': '$[cmH_2O]$',
         'Flux': '$\\left[\\frac{L}{min}\\right]$',
         'Time': '$[s]$'}


def vol_clamp_sim(time_vector: np.ndarray, capacitance: float, resistance: float, flux: Callable, peep=0.0, *,
                  pause_lapsus=None, end_time=None, **kwargs) -> Tuple[np.ndarray, ...]:
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


def pressure_clamp_sim(time_array: np.ndarray, compliance: float, resistance: float, pressure_function: Callable,
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


def plot_vfp(time_array: np.ndarray, volume: np.ndarray, flux: np.ndarray, pressure: np.ndarray,
             show=True, lang_pack=LANG_PACK) -> None:
    """
        T: array representing time
        volume, flux, pressure: arrays representing each quantity for every instant T[i]
        plots volume, flux, and pressure against time
    """
    plt.close()
    fig, axs = plt.subplot_mosaic(
        [["top left", "right column"],
         ["middle left", "right column"],
         ["bottom left", "right column"]]
    )

    axs["top left"].plot(time_array, volume, color='blue')
    axs["top left"].set_ylabel(f"${lang_pack['VOLUME_LABEL']}$ {UNITS['Volume']}")

    axs["middle left"].plot(time_array, flux, color='green')
    axs["middle left"].set_ylabel(f"${lang_pack['FLUX_LABEL']}$ {UNITS['Flux']}")

    axs["bottom left"].plot(time_array, pressure, color='deeppink')
    axs["bottom left"].set_ylabel(f"${lang_pack['PRESSURE_LABEL']}$ {UNITS['Pressure']}")
    axs["bottom left"].set_xlabel(f"${lang_pack['TIME_LABEL']}$ {UNITS['Time']}")

    axs["right column"].plot(volume, flux, color='r', linestyle='-')
    axs["right column"].set_xlabel(f"${lang_pack['VOLUME_LABEL']}$ {UNITS['Volume']}")
    axs["right column"].set_ylabel(f"${lang_pack['FLUX_LABEL']}$ {UNITS['Flux']}")
    axs["right column"].axhline(y=0, color='y', linestyle='-')

    # Tight layout
    plt.tight_layout()

    if show:
        plt.show()
    return fig


def comparative_plot(time_vector: np.ndarray, vol1: np.ndarray, vol2: np.ndarray, flux1: np.ndarray,
                     flux2: np.ndarray, press1: np.ndarray, press2: np.ndarray, show=True, lang_pack=LANG_PACK) -> None:
    """
        T: array representing time
        vol1, flux1, press1: arrays representing initial volume, flux, and pressure for every instant T[i]
        vol2, flux2, press2: arrays representing final volume, flux, and pressure for every instant T[i]
        plots initial and final volume, flux, and pressure against time, superimposed.
    """
    plt.close()
    fig, axs = plt.subplot_mosaic([['top left', 'right'],
                                   ['medium left', 'right'],
                                   ['bottom left', 'right']])
    # Comparative values display in right and left 
    # Setting x axes as time
    axs["bottom left"].set_xlabel(f"${lang_pack['TIME_LABEL']}$ {UNITS['Time']}")
    
    # Plotting volume comparison (time)
    axs["top left"].plot(time_vector, vol1, '-b', time_vector, vol2, '-.b')
    axs["top left"].set_ylabel(f"${lang_pack['VOLUME_LABEL']}$ {UNITS['Volume']}")

    # Plotting flux comparison (time)
    axs["medium left"].plot(time_vector, flux1, '-g', time_vector, flux2, '-.g')
    axs["medium left"].set_ylabel(f"${lang_pack['FLUX_LABEL']}$ {UNITS['Flux']}")
    
    # Plotting pressure comparison (time)
    axs["bottom left"].plot(time_vector, press1, color='deeppink')
    axs["bottom left"].plot(time_vector, press2, linestyle='-.', color='deeppink')
    axs["bottom left"].set_ylabel(f"${lang_pack['PRESSURE_LABEL']}$ {UNITS['Pressure']}")

    # plotting volume vs flux (comparative) where the flux is considered to be positive inwards
    axs["right"].plot(vol1, flux1, '-r', vol2, flux2, '-.r')
    axs["right"].set_xlabel(f"${lang_pack['VOLUME_LABEL']}$ {UNITS['Volume']}")
    axs["right"].set_ylabel(f"${lang_pack['FLUX_LABEL']}$ {UNITS['Flux']}")
    axs["right"].axhline(y=0, color='y', linestyle='-')
    
    # Tight layout
    plt.tight_layout()

    if show:
        plt.show()
    return fig


def ideal_pulse_func(start: float, end: float, amplitude: float) -> Callable:
    """
    start: t_0 - d/2
    end: t_0 + d/2
    A: amplitude

    returns a function that represents the pulse function A*Pi( (t-t_0)/d ) evaluated at time=t
    """
    t_0 = (start + end)/2
    d = end - start
    return lambda t: amplitude * int(np.abs((t - t_0) / d) < 1 / 2)


def smooth_pulse_func(start: float, end: float, amplitude: float) -> Callable:
    """
    start: t_0 - d/2
    end: t_0 + d/2
    A: amplitude

    returns a function that represents a smoothed out version of the pulse function A*Pi((t-t_0)/d) evaluated at time=t
    """
    t_0 = (start + end)/2
    d = end - start
    return lambda t: amplitude / np.sqrt(1 + ((t - t_0) / (d / 2)) ** 18)


def ripply_pulse_func(start: float, end: float, amplitude: float, iterations: int, length: float) -> Callable:
    """
    start: t_0 - d/2
    end: t_0 + d/2
    A: amplitude
    N: number of iterations for the approximation
    length: maximum window of time to be considered

    returns a function that represents a rippled version of the pulse function A*Pi( (t-t_0)/d ) evaluated at time=t
    """
    t_0 = (start + end)/2
    d = end - start
    f_0 = 1 / length

    def fourier_pulse(t):
        result = 0
        w_0 = 2 * np.pi * f_0
        for n in range(-iterations, iterations + 1):
            x_n = amplitude * d * f_0 * np.sinc(np.array(n * f_0 * d)) * np.exp(-1j * n * w_0 * t_0)
            result += np.real(x_n * np.exp(1j * n * w_0 * t))
        return result

    return fourier_pulse


def sinusoidal_func(amplitude: float, phase: float, freq: float) -> Callable:
    """
    Generates a sinusoidal function with the specified parameters
    """
    return lambda t: amplitude*np.sin(2*np.pi*freq*t + phase) + amplitude


def clamp_test():
    def run_both_tests(t_test, c_test, r_test, func, end_time=None, pause_lapsus=None):
        volume, flux, pressure = pressure_clamp_sim(t_test, c_test, r_test, func)
        plot_vfp(time_array, volume, flux, pressure)

        volume, flux, pressure = vol_clamp_sim(t_test, c_test, r_test, func,
                                               end_time=end_time,
                                               pause_lapsus=pause_lapsus)
        plot_vfp(time_array, volume, flux, pressure)

    time_array = np.linspace(0, 15, 1500)
    compliance = 100
    resistance = 0.01

    start = time_array[len(time_array)//3]
    end = time_array[len(time_array)//2]
    amplitude = 5.0

    # Test for hard pulse with a variable amplitude
    clamp_func = ideal_pulse_func(start, end, amplitude)
    run_both_tests(time_array, compliance, resistance, clamp_func)

    # Test for a sinusoidal pressure with a variable freq and Amp
    amplitude = 3.0
    freq = 10/np.max(time_array)
    clamp_func = sinusoidal_func(amplitude, 0, freq)
    run_both_tests(time_array, compliance, resistance, clamp_func)

    # Test for a smooth pulse
    clamp_func = smooth_pulse_func(start, end, amplitude)
    pause = 2.0
    end_time = end + pause
    run_both_tests(time_array, compliance, resistance, clamp_func, end_time=end_time, pause_lapsus=pause)

    # Test for a hard pulse
    n_iter = 20
    length = time_array[-1]
    clamp_func = ripply_pulse_func(start, end, amplitude, n_iter, length)
    pause = 2.0
    end_time = end + pause
    run_both_tests(time_array, compliance, resistance, clamp_func, end_time=end_time, pause_lapsus=pause)


def comp_test():
    compliance = 10
    resistance = 0.1
    time_array = np.linspace(0, 15, 1500)

    start = time_array[len(time_array)//3]
    end = time_array[len(time_array)//2]
    amplitude = 5.0

    flux_ideal = ideal_pulse_func(start, end, amplitude)
    flux_soft = smooth_pulse_func(start, end, amplitude)
    v1, f1, p1 = pressure_clamp_sim(time_array, compliance, resistance, flux_ideal)
    v2, f2, p2 = pressure_clamp_sim(time_array, compliance, resistance, flux_soft)
    comparative_plot(time_array, v1, v2, f1, f2, p1, p2)


if __name__ == '__main__':
    clamp_test()
    # comp_test()
