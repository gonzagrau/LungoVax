import numpy as np
import matplotlib.pyplot as plt
# from ODE_solver import *
import customtkinter as ctk
import webbrowser
import lungovax_main as lung
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Default appearence mode
ctk.set_appearance_mode('system')
if ctk.get_appearance_mode() == 'Dark':
    plt.style.use('dark_background')
else:
    plt.style.use('default')

# CONSTANTS
# WORDS: Remember the intention is to work later with .xml file with translations, so we can change between EN/ES
ASSISTED_SIMULATION_BUTTON_TEXT_ES = 'Simulación de\nRespiración Asistida'
ASSISTED_SIMULATION_PARAMETERS_FRAME_TEXT_ES = 'PARÁMETROS'
REP_TEXT_ES = 'Ver en GitHub'
VER_STR = 'Version 1.0'
REP_URL = r'https://github.com/gonzagrau/LungoVax'
TITLE = 'LungoVax'
DARK_MODE_TEXT_ES = 'Modo oscuro'
LIGHT_MODE_TEXT_ES = 'Modo claro'

# Language: for now just manually set parameters
ASSISTED_SIMULATION_BUTTON_TEXT = ASSISTED_SIMULATION_BUTTON_TEXT_ES
REP_TEXT = REP_TEXT_ES
ASSISTED_SIMULATION_PARAMETERS_FRAME_TEXT = ASSISTED_SIMULATION_PARAMETERS_FRAME_TEXT_ES
DARK_MODE_TEXT = DARK_MODE_TEXT_ES
LIGHT_MODE_TEXT = LIGHT_MODE_TEXT_ES

# Class definitions for UI
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

class MainFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master

        self.rowconfigure(0, weight=20)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)


        self.button_assisted_simulation = ctk.CTkButton(self, text=ASSISTED_SIMULATION_BUTTON_TEXT,
                                                        command=self.button_assisted_simulation_action)
        self.button_assisted_simulation.grid(row=0, column=1, sticky='ew')

        self.version_str = ctk.CTkLabel(self, text=VER_STR)
        self.version_str.grid(row=2, column=0, sticky='ew')

        self.mode_switch_var = ctk.BooleanVar(self, True)
        self.mode_switch = ctk.CTkSwitch(self,
                                         variable=self.mode_switch_var,
                                         command=self.mode_switch_action,
                                         onvalue=True, offvalue=False)
        if ctk.get_appearance_mode() == 'Dark':
            self.mode_switch.deselect()
            self.mode_switch.configure(text=DARK_MODE_TEXT)
        else:
            self.mode_switch.select()
            self.mode_switch.configure(text=LIGHT_MODE_TEXT)
        self.mode_switch.grid(row=2, column=1)

        self.but_view_repo = ctk.CTkButton(self,
                                           text=REP_TEXT,
                                           text_color=('black', 'white'),
                                           command=lambda: webbrowser.open_new(REP_URL),
                                           fg_color='transparent')
        self.but_view_repo.grid(row=2, column=2)

    def button_assisted_simulation_action(self):
        self.master.current_frame = AssistedRespirationFrame(self.master)

    def mode_switch_action(self):
        light = self.mode_switch_var.get()
        if light:
            ctk.set_appearance_mode('light')
            plt.style.use('default')
            self.mode_switch.configure(text=LIGHT_MODE_TEXT)
        else:
            ctk.set_appearance_mode("dark")
            plt.style.use('dark_background')
            self.mode_switch.configure(text=DARK_MODE_TEXT)



class AssistedRespirationFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)

        self.sim_params = AssistedRespirationInputsFrame(self)
        self.sim_params.grid(row=0, column=0, sticky='nsew')

        self.graph_frame = AssistedRespirationGraphFrame(self)
        self.graph_frame.grid(row=0, column=1, sticky='nsew')

    def update_graph(self, fig):
        self.graph_frame.plot_simulation(fig)

    def go_back_to_main_frame(self):
        self.master.current_frame = MainFrame(self.master)


class AssistedRespirationInputsFrame(ctk.CTkFrame):
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
                                       corner_radius=15,
                                       font=("Roboto", 20))
        self.runButton.pack(expand=True, fill=ctk.X)

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
        P_func = lambda t: 20.0 * (time_vector[2*len(time_vector)//7] < t < time_vector[4*len(time_vector)//7])
        if len(capacitances) == 1:
            volume, flux, pressure = lung.pressure_clamp_sim(time_vector, capacitances[0], resistances[0], P_func)
            fig = lung.plot_VFP(time_vector, volume, flux, pressure, False)
        else:
            volume1, flux1, pressure1 = lung.pressure_clamp_sim(time_vector, capacitances[0], resistances[0], P_func)
            volume2, flux2, pressure2 = lung.pressure_clamp_sim(time_vector, capacitances[1], resistances[1], P_func)
            fig = lung.comparative_plot(time_vector, volume1, volume2, flux1, flux2, pressure1, pressure2, False)
        self.master.update_graph(fig)


class ParametersControllerTabview(ctk.CTkTabview):
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

        # Model Toggler
        tab.switch_var = ctk.BooleanVar(value=True)

        def toggle_cap2():
            enabled = tab.switch_var.get()
            if enabled:
                tab.slider_cap2.slider.configure(state='normal')
                tab.slider_cap2.slider.configure(button_color=("#3a7ebf", "#1f538d"))
            else:
                tab.slider_cap2.slider.configure(state='disabled')
                tab.slider_cap2.slider.configure(button_color='gray')

        tab.switch_cap2 = ctk.CTkSwitch(master=tab, text="Añadir tercer elemento",
                                         variable=tab.switch_var, command=toggle_cap2,
                                         onvalue=True, offvalue=False)
        tab.switch_cap2.pack(expand=True, fill=ctk.BOTH)

        # C1 slider
        tab.slider_cap1 = ParameterSlider(tab, 'C1', 20, 50)
        tab.slider_cap1.pack(expand=True, fill=ctk.BOTH)

        # C2 Slider
        tab.slider_cap2 = ParameterSlider(tab, 'C2', 20, 50)
        tab.slider_cap2.pack(expand=True, fill=ctk.BOTH)

        # Resistance
        tab.slider_resistance = ParameterSlider(tab, 'R', 0.01, 0.1)
        tab.slider_resistance.pack(expand=True, fill=ctk.BOTH)


    def get_all_values(self, tab_name):
        capacitance_1 = getattr(self.tab(tab_name), 'slider_cap1').get()
        capacitance_2 = getattr(self.tab(tab_name), 'slider_cap2').get()
        resistance = getattr(self.tab(tab_name), 'slider_resistance').get()

        third_element = getattr(self.tab(tab_name), 'switch_var').get()
        if third_element:
            capacitance = capacitance_1*capacitance_2 / (capacitance_1 + capacitance_2)
        else:
            capacitance = capacitance_1

        return capacitance, resistance


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
        self.value.configure(text=f'{self.slider.get():.2f}')

    def get(self):
        return self.slider.get()


class AssistedRespirationGraphFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # The following label is here just to show the other developers my layout ideas
        # The only widget in this frame should be the matplotlib figure
        self.set_intial_graph()

    def set_intial_graph(self):
        # Generate empty axes graph
        empty_T = np.linspace(0, 5, 10)
        v, f, p = lung.pressure_clamp_sim(T=np.linspace(0, 5, 10), C=1, R=1, P=lambda t: 0)
        empty_graphs_fig = lung.comparative_plot(empty_T, v, v, f, f, p, p, show=False)
        empty_graphs = FigureCanvasTkAgg(empty_graphs_fig, self)
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
