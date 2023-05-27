#import numpy as np
#import matplotlib.pyplot as plt
import matplotlib.pyplot as plt

from ODE_solver import *
from lungovax_main import pressure_clamp_sim, plot_VFP

def main():
    T = np.linspace(0, 30, 500)
    h = T[1] - T[0]
    end_time = 15.0
    C = 25
    R = 0.1
    P = 3.0
    volume, flux, pressure = pressure_clamp_sim(T, C, R, P, end_time=end_time)
    volume = np.max(volume) - volume[T > end_time - 2*h]
    flux = np.abs(flux[T > end_time - 2*h])
    plt.plot(volume, flux, 'r-')
    plt.title("flux vs. volume spirometry")
    plt.xlabel('Volume')
    plt.ylabel("Flux")
    plt.axhline(y=0, color='k', linestyle='--')
    plt.show()

if __name__ == '__main__':
    main()
