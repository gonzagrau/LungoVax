import numpy as np
import matplotlib.pyplot as plt
# from ODE_solver import *
import customtkinter as ctk
import webbrowser
import lungovax_main as lung
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Config statements
plt.style.use('dark_background')
ctk.set_appearance_mode("dark")

# CONSTANTS
# WORDS: Remember the intention is to work later with .xml file with translations, so we can change between EN/ES
ASSISTED_SIMULATION_BUTTON_TEXT_ES = 'Simulación de Respiración Asistida'
ASSISTED_SIMULATION_PARAMETERS_FRAME_TEXT_ES = 'PARÁMETROS'
REP_TEXT_ES = 'Ver en GitHub'
VER_STR = '1.0'
REP_URL = r'https://github.com/gonzagrau/LungoVax'
TITLE = 'LungoVax'

# Language: for now just manually set parameters
ASSISTED_SIMULATION_BUTTON_TEXT = ASSISTED_SIMULATION_BUTTON_TEXT_ES
REP_TEXT = REP_TEXT_ES
ASSISTED_SIMULATION_PARAMETERS_FRAME_TEXT = ASSISTED_SIMULATION_PARAMETERS_FRAME_TEXT_ES

# Generate empty axes graph
empty_T = np.linspace(0, 5, 10)
v, f, p = lung.pressure_clamp_sim(T=np.linspace(0, 5, 10), C=1, R=1, P=lambda t: 0)
EMPTY_GRAPHS_FIG = lung.comparative_plot(empty_T, v, v, f, f, p, p, show=False)


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
        self.master = master

        # Top Frame
        self.topFrame = ctk.CTkFrame(master=self, fg_color='transparent')
        self.topFrame.pack(expand=True, side=ctk.TOP)
        self.topFrame.columnconfigure(0, weight=1)
        self.topFrame.columnconfigure(1, weight=5)

        # Go Back Button
        def go_back_action():
            self.master.go_back_to_main_frame()

        self.goBack = ctk.CTkButton(self.topFrame, text='<', command=go_back_action,
                                    width=15, height=15, corner_radius=15)
        self.goBack.grid(row=0, column=1, sticky='w', padx=5, pady=5)

        # Second simulation checker
        self.secondSimCheckBox = ctk.CTkCheckBox(self.topFrame,
                                                 text="Segunda simulacion",
                                                 command=self.toggle_second_sim)
        self.secondSimCheckBox.grid(row=0, column=2, padx=5, pady=5)


        # Simulation Controller
        self.controller = ParametersControllerTabview(self)
        self.controller.pack(expand=True, fill=ctk.BOTH)

        # Clamping Menu
        self.clamp_mode = ctk.StringVar(value='Pressure')

        def set_clamping_variables(mode):
            if mode == 'Pressure':
                pass
            elif mode == 'Volume':
                pass

        self.clamp_menu = ctk.CTkOptionMenu(self,
                                            values=['Pressure', 'Volume'],
                                            variable=self.clamp_mode,
                                            command=set_clamping_variables)
        self.clamp_menu.pack(expand=True, fill=ctk.X)
        # Run Button
        self.runButton = ctk.CTkButton(master=self,
                                        text="Simular",
                                        command=self.run_sim,
                                        corner_radius=15)


        self.runButton.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)

    def toggle_second_sim(self):
        self.controller.toggle_tab("Sim. 2", self.secondSimCheckBox.get())

    def get_params(self):
        capacitances_list = []
        resistances_list = []
        for tab_name in self.controller.tab_list:
            capacitance, resistance = self.controller.get_all_values(tab_name)
            capacitances_list.append(capacitance)
            resistances_list.append(resistance)
        return capacitances_list, resistances_list

    def run_sim(self):
        capacitances, resistances = self.get_params()
        time_vector = np.linspace(0, 15, 1500)
        P_func = lambda t: 3.0 * (time_vector[len(time_vector)//3] < t < time_vector[len(time_vector)//2])
        if len(capacitances) == 1:
            volume, flux, pressure = lung.pressure_clamp_sim(time_vector, capacitances[0], resistances[0], P_func)
            fig = lung.plot_VFP(time_vector, volume, flux, pressure, False)
        else:
            volume1, flux1, pressure1 = lung.pressure_clamp_sim(time_vector, capacitances[0], resistances[0], P_func)
            volume2, flux2, pressure2 = lung.pressure_clamp_sim(time_vector, capacitances[1], resistances[1], P_func)
            fig = lung.comparative_plot(time_vector, volume1, volume2, flux1, flux2, pressure1, pressure2, False)
        self.master.update_graph(fig)


class AssistedSimulationParametersControllerTabview(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.tab_list = ['Sim. 1']
        self.add("Sim. 1")
        self.configure_tab("Sim. 1")

    def configure_tab(self, tab_name):
        """
        In this method, we set the layout for getting parameters
        This is automatically called whenever a new tab is created
        """
        tab = self.tab(tab_name)
        lbl = ctk.CTkLabel(master=tab, text=f"This is a tab named {tab_name}")
        lbl.pack()

    def toggle_tab(self, tab_name, enabled):
        try:
            if enabled:
                self.add(tab_name)
                self.configure_tab(tab_name)
                self.tab_list.append(tab_name)
            else:
                self.delete(tab_name)
                self.tab_list.remove(tab_name)
        except ValueError:
            # either tried creating an already existing tab or deleting
            # non-existing one. Either way, everything should stay as is
            pass



class ParameterSlider(ctk.CTkFrame):
    """
    This class is used to create the parameters sliders for each tab view in the assisted
    respiration simulation frame
    """
    def __init__(self, master, title_text, from_value, to_value, **kwargs):
        super().__init__(master, fg_color='transparent', **kwargs)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=4)
        self.columnconfigure(2, weight=1)

        # Title
        self.title = ctk.CTkLabel(master=self, text=title_text)
        self.title.grid(row=0, column=0)

        # Value Displayer
        self.value = ctk.CTkLabel(master=self)
        self.value.grid(row=0, column=2, padx=5, pady=5)

        # Slider
        self.slider = ctk.CTkSlider(master=self, from_=from_value, to=to_value,
                                    command=lambda val: self.value.configure(text=f'{val:.2f}'))
        self.slider.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Initial display
        self.value.configure(text=f'{self.slider.get()}')

    def get(self):
        return self.slider.get()


class AssistedRespirationGraphFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # The following label is here just to show the other developers my layout ideas
        # The only widget in this frame should be the matplotlib figure
        empty_graphs = FigureCanvasTkAgg(EMPTY_GRAPHS_FIG, self)
        empty_graphs.get_tk_widget().pack(expand=True, fill=ctk.BOTH)

    def plot_simulation(self, updated_figure):
        for widget in self.winfo_children():
            widget.destroy()
        graphs = FigureCanvasTkAgg(updated_figure, self)
        graphs.get_tk_widget().pack(expand=True, fill=ctk.BOTH)



def main():
    root = MainWindow()
    root.mainloop()

if __name__ == '__main__':
    main()
