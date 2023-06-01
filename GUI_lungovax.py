#import numpy as np
#import matplotlib.pyplot as plt
import tkinter as tk
from ODE_solver import *
from lungovax_main import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def main():
    # set parameters
    C = 100
    R = 0.01
    T = np.linspace(0, 15, 1500)
    t_mid = T[len(T)//2]
    d = T[len(T)//8]
    P1 = lambda t: 3.0 / (1 + ((t - t_mid)/d)**18)
    P2 = lambda t: 3.0 * (T[3*len(T)//8] < t < T[5*len(T)//8])

    # run simulations and get graphs
    v1, f1, p1 = pressure_clamp_sim(T, C, R, P1)
    v2, f2, p2 = pressure_clamp_sim(T, C, R, P2)
    fig = comparative_plot(T, v1, v2, f1, f2, p1, p2, show=False)

    # set GUI
    root = tk.Tk()
    lbl = tk.Label(master=root, text='This is a TKinter window')
    lbl.pack()
    graphs = FigureCanvasTkAgg(fig, root)
    graphs.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    root.mainloop()

if __name__ == '__main__':
    main()
