import numpy as np
import matplotlib.pyplot as plt
import customtkinter as ctk
import webbrowser
import assisted_respiration_simulations as lung
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
from typing import Tuple, List, Callable
import language_package_manager as lpm


# Default appearance mode
ctk.set_appearance_mode('system')
if ctk.get_appearance_mode() == 'Dark':
    plt.style.use('dark_background')
else:
    plt.style.use('default')

# IMPORTANT CONSTANTS
ICON_PATH = r'./assets/images/lung.ico'
INITIAL_RESOLUTION_POSITION = '1200x800+0+0'  # Not used
LOGO_PATH = r'./assets/images/logo.png'
REP_URL = r'https://github.com/gonzagrau/LungoVax'
TITLE = 'LungoVax'
SIM_TIME = 10.0
RIPPLE_N = 25
PULMONARY_COMPLIANCE_RANGE = [50, 200]
THORACIC_COMPLIANCE_RANGE = [200, 400]
COMBINED_COMPLIANCE_RANGE = [50*200/250, 200*400/600]
AIRWAY_RESISTANCE_RANGE = [0.5, 5.5]
COMPLIANCE_UNITS = '$\\left[\\frac{mL}{cmH_2O}\\right]$'
RESISTANCE_UNITS = '$\\left[\\frac{cmH_2O}{Ls}\\right]$'

# Shortcut for fast padding
padding = dict(padx=5, pady=5)

# Language Management settings
LANG_PACK = lpm.get_lang_package()
LANG_LIST_SF = lpm.LANG_LIST_SF
LANG_LIST = [LANG_PACK['LANGUAGE_LIST_ENGLISH'], LANG_PACK['LANGUAGE_LIST_SPANISH']]
LANG_DICTIONARY = {}
for i, value in enumerate(LANG_LIST):
    LANG_DICTIONARY[value] = LANG_LIST_SF[i]
LANG_LIST.sort()


# Class definitions for UI
class MainWindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title(TITLE)
        self.iconbitmap(ICON_PATH)
        self.geometry("%dx%d+0+0" %(self.winfo_screenwidth(), self.winfo_screenheight()))

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
    """
    This frame includes: the program logo, a button to access the simulator.
    a version label, a dark/light mode switch, and a GitHub link button.
    """

    def __init__(self, master: MainWindow, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master

        self.rowconfigure(0, weight=10)
        self.rowconfigure(1, weight=10)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        # Logo image
        self.logo_image = ctk.CTkImage(light_image=Image.open(LOGO_PATH),
                                       dark_image=Image.open(LOGO_PATH),
                                       size=(300, 250))
        self.logo_button = ctk.CTkButton(self,
                                         image=self.logo_image,
                                         fg_color='transparent',
                                         bg_color='transparent',
                                         text='',
                                         hover=False)
        self.logo_button.grid(row=0, column=1, columnspan=2, sticky='nsew')

        # Simulation button
        self.button_assisted_simulation = ctk.CTkButton(self, text=LANG_PACK['ASSISTED_SIMULATION_BUTTON_TEXT'],
                                                        command=self.button_assisted_simulation_action)
        self.button_assisted_simulation.grid(row=1, column=1, columnspan=2, sticky='ew')

        # Version string label
        self.version_str = ctk.CTkLabel(self, text=LANG_PACK['VER_STR'])
        self.version_str.grid(row=2, column=0, sticky='ew')

        # Switch mode button
        self.mode_switch_var = ctk.BooleanVar(self, True)
        self.mode_switch = ctk.CTkSwitch(self,
                                         variable=self.mode_switch_var,
                                         command=self.mode_switch_action,
                                         onvalue=True, offvalue=False)
        if ctk.get_appearance_mode() == 'Dark':
            self.mode_switch.deselect()
            self.mode_switch.configure(text=LANG_PACK['LIGHT_MODE_TEXT'])
        else:
            self.mode_switch.select()
            self.mode_switch.configure(text=LANG_PACK['LIGHT_MODE_TEXT'])
        self.mode_switch.grid(row=2, column=1)

        # Select Language
        self.language_menu = ctk.CTkOptionMenu(self, values=LANG_LIST, command=self.language_selection_action)
        self.language_menu.grid(row=2, column=2)

        # View repository button
        def go_to_repo():
            webbrowser.open_new(REP_URL)

        self.but_view_repo = ctk.CTkButton(self,
                                           text=LANG_PACK['REP_TEXT'],
                                           text_color=('black', 'white'),
                                           command=go_to_repo,
                                           fg_color='transparent')
        self.but_view_repo.grid(row=2, column=3)

    def button_assisted_simulation_action(self):
        self.master.current_frame = AssistedRespirationFrame(self.master)

    def mode_switch_action(self):
        light = self.mode_switch_var.get()
        if light:
            ctk.set_appearance_mode('light')
            plt.style.use('default')
            self.mode_switch.configure(text=LANG_PACK['LIGHT_MODE_TEXT'])
        else:
            ctk.set_appearance_mode("dark")
            plt.style.use('dark_background')
            self.mode_switch.configure(text=LANG_PACK['DARK_MODE_TEXT'])

    def language_selection_action(self, language_str):
        global LANG_DICTIONARY
        global LANG_PACK
        global LANG_LIST
        LANG_PACK = lpm.get_lang_package(LANG_DICTIONARY[language_str])
        LANG_LIST = [LANG_PACK['LANGUAGE_LIST_ENGLISH'], LANG_PACK['LANGUAGE_LIST_SPANISH']]
        LANG_DICTIONARY = {}
        for index, language in enumerate(LANG_LIST):
            LANG_DICTIONARY[language] = LANG_LIST_SF[index]
        LANG_LIST.sort()
        self.master.current_frame = MainFrame(self.master)


class AssistedRespirationFrame(ctk.CTkFrame):
    """
    This frame is divided into two sub-frames: the input frame, taking up
    a third of the screen, and the graphs frame, filling up the other two thirds
    """
    def __init__(self, master: MainWindow, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)

        self.sim_inputs = AssistedRespirationInputsFrame(self)
        self.sim_inputs.grid(row=0, column=0, sticky='nsew')

        self.graph_frame = AssistedRespirationGraphFrame(self)
        self.graph_frame.grid(row=0, column=1, sticky='nsew')

    def update_graph(self, fig):
        self.graph_frame.plot_simulation(fig)

    def go_back_to_main_frame(self):
        """
        This method will be accessed from within the inputs frame
        """
        self.master.current_frame = MainFrame(self.master)


class AssistedRespirationInputsFrame(ctk.CTkFrame):
    """
    This frame includes:
    -a go-back-to-mainframe button
    -a second simulation checkbox
    -the parameters controller frame
    -the stimulus controller frame
    -the clamping menu
    -the run-simulation button
    """
    def __init__(self, master: AssistedRespirationFrame, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        # Top Frame
        self.topFrame = ctk.CTkFrame(master=self, fg_color='transparent')
        self.topFrame.pack(expand=True, fill=ctk.X)
        self.topFrame.columnconfigure(0, weight=1)
        self.topFrame.columnconfigure(1, weight=9)

        # Go Back Button
        def go_back_action():
            self.master.go_back_to_main_frame()

        self.goBack = ctk.CTkButton(self.topFrame, text='<', command=go_back_action,
                                    width=15, height=15, corner_radius=15)
        self.goBack.grid(row=0, column=1, sticky='w', padx=5, pady=5)

        # Second simulation checker
        self.secondSimCheckBox = ctk.CTkCheckBox(self.topFrame,
                                                 text=LANG_PACK['SECOND_SIM_TEXT'],
                                                 command=self.toggle_second_sim)
        self.secondSimCheckBox.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

        # Simulation Parameters Controller
        self.params_controller = SimulationParametersControllerTabview(self)
        self.params_controller.pack(expand=True, fill=ctk.BOTH)

        # Clamping Menu
        self.clamp_mode = ctk.StringVar(value=LANG_PACK['PRESSURE_MODE_SIM_TEXT'])

        def set_clamping_variables(mode):
            if mode == LANG_PACK['PRESSURE_MODE_SIM_TEXT']:
                pass
            elif mode == LANG_PACK['VOLUME_MODE_SIM_TEXT']:
                pass

        self.clamp_menu = ctk.CTkOptionMenu(self,
                                            values=[LANG_PACK['PRESSURE_MODE_SIM_TEXT'],
                                                    LANG_PACK['VOLUME_MODE_SIM_TEXT']],
                                            variable=self.clamp_mode,
                                            command=set_clamping_variables)
        self.clamp_menu.pack(expand=True, fill=ctk.X)
        # Run Button
        self.runButton = ctk.CTkButton(master=self,
                                       text=LANG_PACK['RUN_SIM_BUT_TEXT'],
                                       command=self.run_sim,
                                       corner_radius=15,
                                       font=("Roboto", 20))
        self.runButton.pack(expand=True, fill=ctk.X)

    def toggle_second_sim(self):
        self.params_controller.toggle_tab("Sim. 2", self.secondSimCheckBox.get())

    def get_params(self) -> Tuple[list[float], list[float]]:
        capacitances_list = []
        resistances_list = []
        for tab_name in self.params_controller.tab_list:
            capacitance, resistance = self.params_controller.get_system_parameters(tab_name)
            capacitances_list.append(capacitance)
            resistances_list.append(resistance)
        return capacitances_list, resistances_list

    def get_clamping_funcs(self) -> Tuple[List[Callable], List[float], List[float]]:
        func_list = []
        end_times = []
        pauses = []
        for tab_name in self.params_controller.tab_list:
            values = self.params_controller.get_stimulus_parameters(tab_name)
            choice = self.params_controller.get_clamping_option(tab_name)
            end_time = None
            pause_lapsus = None
            # Adjusting amplitude
            if self.clamp_mode.get() == LANG_PACK['PRESSURE_MODE_SIM_TEXT']:
                multiplier = 1/10
            elif self.clamp_mode.get() == LANG_PACK['VOLUME_MODE_SIM_TEXT']:
                multiplier = 4
            else:
                raise ValueError(f'Invalid clamping mode: {self.clamp_mode.get()}')

            if choice == LANG_PACK["IDEAL_PULSE_TEXT"]:
                start, end, amplitude = values
                amplitude *= multiplier
                func = lung.ideal_pulse_func(start, end, amplitude)
                end_time = end
            elif choice == LANG_PACK["SMOOTH_PULSE_TEXT"]:
                start, end, amplitude = values
                amplitude *= multiplier
                func = lung.smooth_pulse_func(start, end, amplitude)
                pause_lapsus = 0
                end_time = end + 0.1 * SIM_TIME
            elif choice == LANG_PACK["REAL_PULSE_TEXT"]:
                start, end, amplitude = values
                amplitude *= multiplier
                func = lung.ripply_pulse_func(start, end, amplitude, iterations=RIPPLE_N, length=SIM_TIME)
                pause_lapsus = 0
                end_time = end + 0.1 * SIM_TIME
            elif choice == LANG_PACK["SINUSOIDAL_TEXT"]:
                amplitude, phase, period = values
                amplitude *= multiplier * 30
                freq = 1/period
                # convert phase to radians
                phase = phase*np.pi/180.0
                func = lung.sinusoidal_func(amplitude/100*2, phase, freq)
            else:
                raise ValueError("Invalid function choice")
            func_list.append(func)
            end_times.append(end_time)
            pauses.append(pause_lapsus)
        return func_list, end_times, pauses

    def run_sim(self):
        time_vector = np.linspace(0, SIM_TIME, 1500)
        capacitances, resistances = self.get_params()
        resistances = np.array(resistances)/1000.  # Converting between cmH20/(Ls) to cmH20/(mLs)
        clamping_functions, end_times, pauses = self.get_clamping_funcs()
        if self.clamp_mode.get() == LANG_PACK['PRESSURE_MODE_SIM_TEXT']:
            sim_func = lung.pressure_clamp_sim
        elif self.clamp_mode.get() == LANG_PACK['VOLUME_MODE_SIM_TEXT']:
            sim_func = lung.vol_clamp_sim
        else:
            raise ValueError(f'Invalid clamping mode: {self.clamp_mode.get()}')

        if len(capacitances) == 1:
            volume, flux, pressure = sim_func(time_vector,
                                              capacitances[0],
                                              resistances[0],
                                              clamping_functions[0],
                                              end_time=end_times[0],
                                              pause_lapsus=pauses[0])
            flux *= 60 / 1000  # Converting from mL/s to L/min
            fig = lung.plot_vfp(time_vector, volume, flux, pressure, False, LANG_PACK)
        else:
            volume1, flux1, pressure1 = sim_func(time_vector, capacitances[0], resistances[0], clamping_functions[0],
                                                 end_time=end_times[0], pause_lapsus=pauses[0])
            flux1 *= 60 / 1000  # Converting from mL/s to L/min
            volume2, flux2, pressure2 = sim_func(time_vector, capacitances[1], resistances[1], clamping_functions[1],
                                                 end_time=end_times[1], pause_lapsus=pauses[1])
            flux2 *= 60 / 1000  # Converting from mL/s to L/min
            fig = lung.comparative_plot(time_vector, volume1, volume2, flux1, flux2, pressure1, pressure2, False)
        self.master.update_graph(fig)


class ToggleableTabview(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.tab_list = ['Sim. 1']
        self.add("Sim. 1")
        self.configure_tab("Sim. 1")

    def configure_tab(self, tab_name):
        pass

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
        plt.close()
        fig, ax = plt.subplots(figsize=(1, 1))
        try:
            tone = int(self.master['background'][-2:])
        except ValueError:
            tone = 0
        hex_color = '#%02x%02x%02x' % (int(256 * tone/100), int(256 * tone/100), int(256 * tone/100))
        fig.set_facecolor(hex_color)
        ax.axis(False)
        ax.text(.5, .5, title_text, ha='center', va='center', fontsize=10)
        graphs = FigureCanvasTkAgg(fig, self)
        graphs.get_tk_widget().grid(row=0, column=0)

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

    def set(self, val):
        self.slider.set(val)


class PulseParameters(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color='transparent', **kwargs)
        self.start = ParameterSlider(self, LANG_PACK['PULSE_START_TEXT'], 0, SIM_TIME)
        self.start.set(0.2*SIM_TIME)
        self.start.pack(expand=True, fill=ctk.X)
        self.end = ParameterSlider(self, LANG_PACK['PULSE_END_TEXT'], 0, SIM_TIME)
        self.end.set(0.5*SIM_TIME)
        self.end.pack(expand=True, fill=ctk.X)
        self.amplitude = ParameterSlider(self, LANG_PACK['PULSE_AMPLITUDE_TEXT'], 10, 100)
        self.amplitude.pack(expand=True, fill=ctk.X)

    def get_parameters(self) -> Tuple[float, float, float]:
        return self.start.get(), self.end.get(), self.amplitude.get()


class SinusoidalParameters(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color='transparent', **kwargs)
        self.amplitude = ParameterSlider(self, LANG_PACK['SINUSOIDAL_AMPLITUDE_TEXT'], 10, 100)
        self.amplitude.pack(expand=True, fill=ctk.X)
        self.phase = ParameterSlider(self, LANG_PACK['SINUSOIDAL_PHASE_TEXT'], 0, 90)
        self.phase.pack(expand=True, fill=ctk.X)
        self.period = ParameterSlider(self, LANG_PACK['SINUSOIDAL_PERIOD_TEXT'], 1, 4)
        self.period.pack(expand=True, fill=ctk.X)

    def get_parameters(self) -> Tuple[float, float, float]:
        return self.amplitude.get(), self.phase.get(), self.period.get()


class SimulationParametersControllerTabview(ToggleableTabview):
    def __init__(self, master: AssistedRespirationInputsFrame, **kwargs):
        super().__init__(master, **kwargs)

    def configure_tab(self, tab_name):
        """
        In this method, we set the layout for getting parameters
        This is automatically called whenever a new tab is created
        """
        tab = self.tab(tab_name)

        tab.model_parameters_title = ctk.CTkLabel(tab, text=LANG_PACK['MODEL_PARAMETERS_TITLE'])
        tab.model_parameters_title.pack(expand=True, fill=ctk.BOTH)

        # Model Toggler
        tab.switch_var = ctk.BooleanVar(value=True)

        def toggle_cap2():
            enabled = tab.switch_var.get()
            if enabled:
                tab.slider_cap2.slider.configure(state='normal', button_color=("#3a7ebf", "#1f538d"))
                tab.slider_cap1.destroy()
                tab.slider_cap1 = ParameterSlider(tab, f"{LANG_PACK['PULMONARY_COMPLIANCE_TEXT']} {COMPLIANCE_UNITS}",
                                                  *PULMONARY_COMPLIANCE_RANGE)
                tab.slider_cap1.pack(before=tab.slider_cap2, expand=True, fill=ctk.BOTH)
            else:
                tab.slider_cap2.slider.configure(state='disabled', button_color='gray')
                tab.slider_cap1.destroy()
                tab.slider_cap1 = ParameterSlider(tab, f"{LANG_PACK['COMBINED_COMPLIANCE_TEXT']} {COMPLIANCE_UNITS}",
                                                  *COMBINED_COMPLIANCE_RANGE)
                tab.slider_cap1.pack(before=tab.slider_cap2, expand=True, fill=ctk.BOTH)

        tab.switch_cap2 = ctk.CTkSwitch(master=tab, text=LANG_PACK['MODEL_SWITCH_THIRD_ELEMENT_TEXT'],
                                        variable=tab.switch_var, command=toggle_cap2, onvalue=True, offvalue=False)
        tab.switch_cap2.pack(expand=True, fill=ctk.BOTH)

        # C1 slider
        tab.slider_cap1 = ParameterSlider(tab, f"{LANG_PACK['PULMONARY_COMPLIANCE_TEXT']} {COMPLIANCE_UNITS}",
                                          *PULMONARY_COMPLIANCE_RANGE)
        tab.slider_cap1.pack(expand=True, fill=ctk.BOTH)

        # C2 Slider
        tab.slider_cap2 = ParameterSlider(tab, f"{LANG_PACK['THORACIC_COMPLIANCE_TEXT']} {COMPLIANCE_UNITS}",
                                          *THORACIC_COMPLIANCE_RANGE)
        tab.slider_cap2.pack(expand=True, fill=ctk.BOTH)

        # Resistance
        tab.slider_resistance = ParameterSlider(tab, f"{LANG_PACK['AIRWAY_RESISTANCE_TEXT']} {RESISTANCE_UNITS}",
                                                *AIRWAY_RESISTANCE_RANGE)
        tab.slider_resistance.pack(expand=True, fill=ctk.BOTH)

        # Stimulus Options Section Title
        tab.stimulus_options_title = ctk.CTkLabel(tab, text=LANG_PACK['STIMULUS_OPTIONS_TITLE'])
        tab.stimulus_options_title.pack(expand=True, fill=ctk.BOTH)

        # Stimulus Options
        tab.stimulus_selection_frame = StimulusOptions(tab)
        tab.stimulus_selection_frame.pack(expand=True, fill=ctk.BOTH)

        # Stimulus Parameters
        tab.stimulus_parameters_frame = self.set_stimulus_parameters_frame(tab_name)
        tab.stimulus_parameters_frame.pack(expand=True, fill=ctk.BOTH)

        def changer():
            tab.stimulus_parameters_frame.destroy()
            tab.stimulus_parameters_frame = self.set_stimulus_parameters_frame(tab_name)
            tab.stimulus_parameters_frame.pack(expand=True, fill=ctk.BOTH)

        tab.changer = changer

    def get_system_parameters(self, tab_name) -> Tuple[float, float]:
        capacitance_1 = getattr(self.tab(tab_name), 'slider_cap1').get()
        capacitance_2 = getattr(self.tab(tab_name), 'slider_cap2').get()
        resistance = getattr(self.tab(tab_name), 'slider_resistance').get()
        third_element = getattr(self.tab(tab_name), 'switch_var').get()
        if third_element:
            capacitance = capacitance_1*capacitance_2 / (capacitance_1 + capacitance_2)
        else:
            capacitance = capacitance_1
        return capacitance, resistance

    def set_stimulus_parameters_frame(self, tab_name: str) -> PulseParameters | SinusoidalParameters:
        tab = self.tab(tab_name)
        stimulus_type = tab.stimulus_selection_frame.get_option()
        if stimulus_type in (LANG_PACK['IDEAL_PULSE_TEXT'],
                             LANG_PACK['SMOOTH_PULSE_TEXT'],
                             LANG_PACK['REAL_PULSE_TEXT']):
            return PulseParameters(tab)
        elif stimulus_type == LANG_PACK['SINUSOIDAL_TEXT']:
            return SinusoidalParameters(tab)
        else:
            raise NotImplementedError('Invalid Stimulus Type.')

    def get_stimulus_parameters(self, tab_name: str) -> Tuple[float, float, float]:
        tab = self.tab(tab_name)
        return tab.stimulus_parameters_frame.get_parameters()

    def get_clamping_option(self, tab_name: str) -> str:
        tab = self.tab(tab_name)
        return tab.stimulus_selection_frame.get_option()


class StimulusOptions(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color='transparent', **kwargs)
        self.master = master

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.choice = ctk.StringVar(value=LANG_PACK['IDEAL_PULSE_TEXT'])

        def update_parameters():
            master.changer()

        self.option_1 = ctk.CTkRadioButton(master=self, text=LANG_PACK['IDEAL_PULSE_TEXT'],
                                           variable=self.choice, value=LANG_PACK['IDEAL_PULSE_TEXT'],
                                           command=update_parameters)
        self.option_1.grid(row=0, column=0, **padding)
        self.option_2 = ctk.CTkRadioButton(master=self, text=LANG_PACK['SMOOTH_PULSE_TEXT'],
                                           variable=self.choice, value=LANG_PACK['SMOOTH_PULSE_TEXT'],
                                           command=update_parameters)
        self.option_2.grid(row=0, column=1, **padding)
        self.option_3 = ctk.CTkRadioButton(master=self, text=LANG_PACK['REAL_PULSE_TEXT'],
                                           variable=self.choice, value=LANG_PACK['REAL_PULSE_TEXT'],
                                           command=update_parameters)
        self.option_3.grid(row=1, column=0, **padding)
        self.option_4 = ctk.CTkRadioButton(master=self, text=LANG_PACK['SINUSOIDAL_TEXT'],
                                           variable=self.choice, value=LANG_PACK['SINUSOIDAL_TEXT'],
                                           command=update_parameters)
        self.option_4.grid(row=1, column=1, **padding)

    def get_option(self) -> str:
        return self.choice.get()


class AssistedRespirationGraphFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # The following label is here just to show the other developers my layout ideas
        # The only widget in this frame should be the matplotlib figure
        self.set_initial_graph()

    def set_initial_graph(self):
        # Generate empty axes graph
        empty_T = np.linspace(0, 5, 10)
        v, f, p = lung.pressure_clamp_sim(time_array=np.linspace(0, 5, 10), compliance=1, resistance=1,
                                          pressure_function=lambda t: 0)
        empty_graphs_fig = lung.comparative_plot(empty_T, v, v, f, f, p, p, False, LANG_PACK)
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
