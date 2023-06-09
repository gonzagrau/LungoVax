# import numpy as np
# import matplotlib.pyplot as plt
# from ODE_solver import *
import customtkinter as ctk
import webbrowser
import numpy as np
from lungovax_main import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Config statements
plt.style.use('dark_background')
ctk.set_appearance_mode("dark")

# CONSTANTS
# WORDS: Remember the intention is to work later with .xml file with translations, so we can change between EN/ES
ASSISTED_SIMULATION_BUTTON_TEXT_ES = 'Simulación de Respiración Asistida'
ASSISTED_SIMULATION_GRAPH_FRAME_TEXT_ES = 'GRÁFICO'
ASSISTED_SIMULATION_PARAMETERS_FRAME_TEXT_ES = 'PARÁMETROS'
REP_TEXT_ES = 'Ver en GitHub'
VER_STR = '1.0'
REP_URL = r'https://github.com/gonzagrau/LungoVax'
TITLE = 'LungoVax'

# Language: for now just manually set parameters
ASSISTED_SIMULATION_BUTTON_TEXT = ASSISTED_SIMULATION_BUTTON_TEXT_ES
REP_TEXT = REP_TEXT_ES
ASSISTED_SIMULATION_GRAPH_FRAME_TEXT = ASSISTED_SIMULATION_GRAPH_FRAME_TEXT_ES
ASSISTED_SIMULATION_PARAMETERS_FRAME_TEXT = ASSISTED_SIMULATION_PARAMETERS_FRAME_TEXT_ES

# Generate empty axes graph
empty_T = np.linspace(0, 5, 10)
v, f, p = pressure_clamp_sim(T=np.linspace(0, 5, 10), C=1, R=1, P=lambda t: 0)
EMPTY_GRAPHS_FIG = comparative_plot(empty_T, v, v, f, f, p, p, show=False)


# Class definitions for UI

class MainFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master

        self.rowconfigure(0, weight=20)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)


        self.button_assisted_simulation = ctk.CTkButton(self, text=ASSISTED_SIMULATION_BUTTON_TEXT,
                                                        command=self.button_assisted_simulation_action)
        self.button_assisted_simulation.grid(row=0, column=0, columnspan=2)

        self.version_str = ctk.CTkLabel(self, text=VER_STR)
        self.version_str.grid(row=2, column=0)

        self.but_view_repo = ctk.CTkButton(self, text=REP_TEXT, command=lambda: webbrowser.open_new(REP_URL),
                                           fg_color='transparent')
        self.but_view_repo.grid(row=2, column=1)

    def button_assisted_simulation_action(self):
        self.master.current_frame = AssistedRespirationFrame(self.master)



class AssistedRespirationFrame(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)

        self.sim_params = AssistedRespirationParametersFrame(self)
        self.sim_params.grid(row=0, column=0, sticky='nsew')

        self.graph_frame = AssistedRespirationGraphFrame(self)
        self.graph_frame.grid(row=0, column=1, sticky='nsew')


class AssistedRespirationParametersFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=8)
        self.rowconfigure(2, weight=2)
        self.columnconfigure(0, weight=1)

        # The following label, alongside with the first row of the grid,
        # are here just to show the other developers my layout ideas
        self.lbl = ctk.CTkLabel(self, text=ASSISTED_SIMULATION_PARAMETERS_FRAME_TEXT)
        self.lbl.grid(row=0, column=0)

        self.controller = AssistedSimulationParametersControllerFrame(self)
        self.controller.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        self.run_button = ctk.CTkButton(master=self,
                                        text='Run simulation',
                                        command=self.run_sim,
                                        corner_radius=15)
        self.run_button.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)

    def get_params(self):
        pass

    def run_sim(self):
        pass


class AssistedSimulationParametersControllerFrame(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=5)
        self.columnconfigure(0, weight=1)




class TwoElementModelParameterSelector(ctk.CTkFrame):
    pass


class ThreeElementModelParameterSelector(ctk.CTkFrame):
    pass


class AssistedRespirationGraphFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # The following label is here just to show the other developers my layout ideas
        # The only widget in this frame should be the matplotlib figure
        self.lbl = ctk.CTkLabel(self, text=ASSISTED_SIMULATION_GRAPH_FRAME_TEXT)
        self.lbl.pack()
        empty_graphs = FigureCanvasTkAgg(EMPTY_GRAPHS_FIG, self)
        empty_graphs.get_tk_widget().pack(expand=True, fill=ctk.BOTH)


class MainWindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title(TITLE)
        self.iconbitmap("lung.ico")
        self.geometry('900x600')

        # self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Setting properties
        self.current_frame = MainFrame(self)
        # self.state('zoomed') # This is not working

    @property
    def current_frame(self):
        return self._current_frame

    @current_frame.setter
    def current_frame(self, frame):
        try:
            self._current_frame.destroy()
        except AttributeError:
            pass
        self._current_frame = frame
        self._current_frame.grid(row=0, column=0, sticky="nsew")

    @current_frame.getter
    def current_frame(self):
        return self._current_frame


def main():
    root = MainWindow()
    root.mainloop()

if __name__ == '__main__':
    main()
