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
TEM_BUT_TEXT_ES = 'Modelo de Tres elementos'
REP_TEXT_ES = 'Ver en GitHub'
VER_STR = '1.0'
REP_URL = r'https://github.com/gonzagrau/LungoVax'
TITLE = 'LungoVax'

# Language: for now just manually set parameters
TEM_BUT_TEXT = TEM_BUT_TEXT_ES
REP_TEXT = REP_TEXT_ES

# Generate empty axes graph
empty_T = np.linspace(0, 5, 10)
v, f, p = pressure_clamp_sim(T=np.linspace(0, 5, 10), C=1, R=1, P= lambda t : 0)
EMPTY_GRAPHS_FIG = comparative_plot(empty_T, v, v, f, f, p, p, show=False)

# Class definitions for UI

class MainFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master

        self.rowconfigure(0, weight=19)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.but_3EM = ctk.CTkButton(self, text=TEM_BUT_TEXT, command=self.button_3EM)
        self.but_3EM.grid(row=0, column=0, columnspan=2)

        self.version_str = ctk.CTkLabel(self, text=VER_STR)
        self.version_str.grid(row=1, column=0)

        self.but_view_repo = ctk.CTkButton(self, text=REP_TEXT, command=lambda: webbrowser.open_new(REP_URL),
                                           fg_color='transparent')
        self.but_view_repo.grid(row=1, column=1)

    def button_3EM(self):
        self.master.current_frame = TEMFrame(self.master)


class TEMFrame(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)

        self.sim_params = SimParamsFrame(self)
        self.sim_params.grid(row=0, column=0, sticky='nsew')

        self.graph_frame = GraphFrame(self)
        self.graph_frame.grid(row=0, column=1, sticky='nsew')


class SimParamsFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=8)
        self.rowconfigure(2, weight=2)
        self.columnconfigure(0, weight=1)

        # The following label, alongside with the first row of the grid,
        # are here just to show the other developers my layout ideas
        self.lbl = ctk.CTkLabel(self, text='PARAMS FRAME')
        self.lbl.grid(row=0, column=0)

        self.tabs = ParamsTabView(self)
        self.tabs.fill_tab("linestyle=-")
        self.tabs.fill_tab("linestyle=-.")
        self.tabs.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        self.run_button = ctk.CTkButton(master=self,
                                        text='Run simulation',
                                        command=self.run_sim,
                                        corner_radius=15)
        self.run_button.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)

    def get_params(self):
        pass

    def run_sim(self):
        pass


class ParamsTabView(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.add("linestyle=-")
        self.add("linestyle=-.")

    def fill_tab(self, tabname):
        self.tab_lbl = ctk.CTkLabel(master=self.tab(tabname), text=f"tab to set params. for simulation with {tabname}")
        self.tab_lbl.grid(row=0, column=0, padx=20, pady=10)


class GraphFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # The following label is here just to show the other developers my layout ideas
        # The only widget in this frame should be the matplotlib figure
        self.lbl = ctk.CTkLabel(self, text='GRAPH FRAME')
        self.lbl.pack()
        empty_graphs = FigureCanvasTkAgg(EMPTY_GRAPHS_FIG, self)
        empty_graphs.get_tk_widget().pack(expand=True, fill=ctk.BOTH)



class MainWindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title(TITLE)
        self.iconbitmap("lung.ico")
        self.state('zoomed')
        #self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Setting properties
        self.current_frame = MainFrame(self)

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

    '''
    root = ctk.CTk()
    frm_params = ctk.CTkFrame(master=root,
                               width=200,
                               height=200,
                               corner_radius=10)
    frm_params.pack()

    ents = []
    lbls = ['t', 'C1', 'C2', 'R1', 'R2']
    for i in range(5):
        lbl = ctk.CTkLabel(master=frm_params, text=lbls[i])
        lbl.place(x=0, y=25*i)
        ent = ctk.CTkEntry(master=frm_params,
                             width=120,
                             height=25,
                             corner_radius=10)
        ent.place(x=25, y=25*i)
        ents.append(ent)


    frm_graphs = ctk.CTkFrame(master=root,
                              width=200,
                              height=200,
                              corner_radius=10)
    frm_graphs.pack()
    def run_sim():
        t_f = float(ents[0].get())
        C1 = float(ents[1].get())
        C2 = float(ents[2].get())
        R1 = float(ents[3].get())
        R2 = float(ents[4].get())

        T = np.linspace(0, t_f, 1500)
        t_mid = T[len(T) // 4]
        d = T[len(T) // 8]
        P = lambda t: 3.0 / (1 + ((t - t_mid) / d) ** 18)

        v1, f1, p1 = pressure_clamp_sim(T, C1, R1, P)
        v2, f2, p2 = pressure_clamp_sim(T, C2, R2, P)
        fig = comparative_plot(T, v1, v2, f1, f2, p1, p2, show=False)

        for widget in frm_graphs.winfo_children():
            widget.destroy()

        graphs = FigureCanvasTkAgg(fig, frm_graphs)
        graphs.get_tk_widget().pack(expand=True, fill=ctk.BOTH)



    btn_simulation = ctk.CTkButton(root, text='Run simulation', corner_radius=10, command=run_sim)
    btn_simulation.pack()
    '''

    root.mainloop()


if __name__ == '__main__':
    main()