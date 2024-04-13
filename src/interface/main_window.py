import tkinter as tk
from tkinter import ttk
import random
import os

import numpy as np
from src.interface.excel_main_windows import ExcelMainWindow
from src.interface.manual_result import TurbineApp
from src.interface.switch import TwoButtonSwitch
from src.algo.both_prog import Simulations
from src.interface.puissance_total_window import RealTimePlotApp
from src.interface.puissance_all_turbine_window import RealTimePlotAppMulti

from src.interface.global_var import FILENAME, STARTING_ROW
from tkinter import filedialog


class MainApp:
    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the Main Application.

        Parameters:
            root (tk.Tk): The root Tkinter window.
        """
       

        self.root = root
        self.root.title("Outil d'optimisation de turbine")

        # self.iterations_label_text = tk.StringVar()
        # self.iterations_label_text.set("Nombre d'itérations max :")
        # self.iterations_label = ttk.Label(root, textvariable=self.iterations_label_text)
        # self.iterations_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # self.iterations_entry = ttk.Entry(root)
        # self.iterations_entry.grid(row=0, column=1, padx=5, pady=5)

        # self.run_button = ttk.Button(root, text="Run", command=self.run_simulation)
        # self.run_button.grid(row=0, column=2, padx=5, pady=5)

        # # Create a switch
        # self.switch_widget = TwoButtonSwitch(root, switch_callback=self.switch_callback)
        # self.switch_widget.grid(row=0, column=3, padx=5, pady=5)

        # self.status_label = ttk.Label(self.root, text="Statut de la simulation : Pas encore fait")
        # self.status_label.grid(row=2, columnspan=4, padx=5, pady=5)


        #  Create a canvas
        self.canvas = tk.Canvas(root, width=500, height=550)
        self.canvas.pack()

        # Draw the rectangles
        self.red_frame = tk.Frame(root)
        self.red_frame.place(x=10, y=10, width=480, height=50)  # Red rectangle at the top

        # Create the TwoButtonSwitch widget inside the red frame
        self.switch_widget = TwoButtonSwitch(self.red_frame, switch_callback=self.switch_callback)
        self.switch_widget.pack(padx=10, pady=10)

        self.blue_frame = tk.Frame(root)
        self.blue_frame.place(x=10, y=60, width=480, height=390)  # Blue rectangle in the middle (largest)

        self.green_frame = tk.Frame(root)
        self.green_frame.place(x=10, y=450, width=480, height=50)  # Green rectangle at the bottom

        self.yellow_frame = tk.Frame(root)
        self.yellow_frame.place(x=10, y=500, width=480, height=40)  # Yellow rectangle at the bottom

        # Create the "RUN" button inside the green frame
        self.run_button = tk.Button(self.green_frame, text="RUN", bg="green", fg="white", command=self.run_simulation)
        self.run_button.pack()

        # Create the status label inside the yellow frame
        self.status_label = ttk.Label(self.yellow_frame, text="Statut de la simulation : Pas encore fait")
        self.status_label.pack()

        self.create_excel_widgets()

        # Initialize switch state
        self.switch_state = True




        self.windows_fenetre_puissance_total = None
        self.windows_fenetre_puissance_turbine = None

        self.current_iteration = 0

        self.first_num_line = None
        self.num_iterations = None

        self.plot_excel_windows_total = None
        self.plot_excel_windows_turbine = None

        self.total_flow = None
        self.upstream_elevation= None
        self.turbine_states = None

        self.multi_sim = Simulations(FILENAME, ["ProgDyn","BB"])

        self.manual_windows = None

    def switch_callback(self, state):
        self.switch_state = state
        if state:  # Switch is in excel input mode
            self.create_excel_widgets()
        else:  # Switch is in manual mode
            self.create_manual_input_widgets()

    def create_manual_input_widgets(self):
        # Remove existing widgets
        for widget in self.blue_frame.winfo_children():
            widget.destroy()
        
        self.mode_label = ttk.Label(self.blue_frame, 
                                    text="Mode saisie manuelle")
        self.mode_label.configure(font = ("Century Gothic", 14, "bold"))
        self.mode_label.pack(pady=5)

        # Create entry fields for total flow and upstream elevation
        entry_frame = ttk.Frame(self.blue_frame)
        entry_frame.pack(padx=5, pady=5)

        ttk.Label(entry_frame, text="Débit total :").pack(side=tk.LEFT)
        self.total_flow_entry = ttk.Entry(entry_frame)
        self.total_flow_entry.pack(side=tk.LEFT, padx=5)

        # Create a frame for upstream elevation entry
        upstream_elevation_frame = ttk.Frame(self.blue_frame)
        upstream_elevation_frame.pack(padx=5, pady=5)

        ttk.Label(upstream_elevation_frame, text="Élévation amont :").pack(side=tk.LEFT)
        self.upstream_elevation_entry = ttk.Entry(upstream_elevation_frame)
        self.upstream_elevation_entry.pack(side=tk.LEFT, padx=5)

        self.turbine_checkboxes = []
        self.debit_max_inputs = []
        
        style = ttk.Style()
        style.configure("RoundedFrame.TFrame", borderwidth=5, relief="groove", bordercolor="black", background="#ededed")

        turbineGroup1 = tk.Frame(self.blue_frame)
        turbineGroup1.pack(padx=10, pady=10, side="top", fill="x")
        for i in range(3):
            container = ttk.Frame(turbineGroup1, style="RoundedFrame.TFrame")
            container.pack(ipadx=5, padx=10, pady=10, side="left", fill="x")  # Pack the container to the left

            label_turbine = tk.Label(container, text=f"Turbine {i+1}")
            label_turbine.pack(anchor="center", pady=5)

            checkbox_var = tk.BooleanVar(value=True)
            self.turbine_checkboxes.append(checkbox_var)
            checkbox = ttk.Checkbutton(container, text="Activé", variable=checkbox_var, command=lambda idx=i: self.print_check(idx))
            checkbox.pack(anchor="center", pady=5)

            # Label and entry on the same line
            entry_label = tk.Label(container, text="Débit max")
            entry_label.pack(side="left", pady=5, padx=5)

            entry = ttk.Entry(container, width=7)
            entry.insert(tk.END, "160")
            self.debit_max_inputs.append(entry)
            entry.pack(side="left", pady=5)
            #checkbox.bind("<Button-1>", lambda event: self.disable_entry())

        # Create the second row with 2 blocks
        turbineGroup2 = tk.Frame(self.blue_frame)
        turbineGroup2.pack(padx=10, pady=10)
        for i in range(3, 5):
            container = ttk.Frame(turbineGroup2, style="RoundedFrame.TFrame")
            container.pack(ipadx=5, padx=10, pady=10, side="left")

            label_turbine = tk.Label(container, text=f"Turbine {i+1}")
            label_turbine.pack(anchor="center", pady=5)

            checkbox_var = tk.BooleanVar(value=True)
            self.turbine_checkboxes.append(checkbox_var)
            checkbox = ttk.Checkbutton(container, text="Activé", variable=checkbox_var, command=lambda idx=i: self.print_check(idx))
            checkbox.pack(anchor="center", pady=5)

            # Label and entry on the same line
            entry_label = tk.Label(container, text="Débit max")
            entry_label.pack(side="left", padx=5, pady=5)

            entry = ttk.Entry(container, width=7)
            entry.insert(tk.END, "160")
            self.debit_max_inputs.append(entry)
            entry.pack(side="left", pady=5)
            #checkbox.bind("<Button-1>", lambda event: self.disable_entry())

    def print_check(self, idx):
        checkbox_var = self.turbine_checkboxes[idx]
        if checkbox_var.get():
            # print(f"Turbine {idx+1}: Check")
            self.debit_max_inputs[idx].delete(0, tk.END)
            self.debit_max_inputs[idx].insert(tk.END, "160")
        else:
            # print(f"Turbine {idx+1}: CheckBox is not checked.")
            self.debit_max_inputs[idx].delete(0, tk.END)
            self.debit_max_inputs[idx].insert(tk.END, "0")

    def browseFiles(self):
        filename = filedialog.askopenfilename(initialdir = ".",
                                            title = "Select a File",
                                            filetypes = (("excel files",
                                                            "*.xlsx*"),
                                                        ("all files",
                                                            "*.*")))
        
        # Change label contents
        self.excel_file_name_entry.configure(text=os.path.relpath(filename))

    def browseDirs(self):
        folder_selected = filedialog.askdirectory(initialdir=".")
        self.image_dir_path.configure(text=os.path.relpath(folder_selected))

    def create_excel_widgets(self):
        # Remove existing widgets
        for widget in self.blue_frame.winfo_children():
            widget.destroy()

        self.mode_label = ttk.Label(self.blue_frame, text="Mode données excel")
        self.mode_label.configure(font = ("Century Gothic", 14, "bold"))
        self.mode_label.pack(pady=5)

        # Create entry fields and labels for "First Num Line", "Num of Iterations", and "Excel File Name"
        entry_frame_first_num = ttk.Frame(self.blue_frame)
        entry_frame_first_num.pack(padx=5, pady=5)
        ttk.Label(entry_frame_first_num, text="Numéro de la première ligne:").pack(side=tk.LEFT)
        self.first_num_line_entry = ttk.Entry(entry_frame_first_num)
        self.first_num_line_entry.pack(side=tk.LEFT, padx=5)

        entry_frame_iterations = ttk.Frame(self.blue_frame)
        entry_frame_iterations.pack(padx=5, pady=5)
        ttk.Label(entry_frame_iterations, text="Nombre d'itérations:").pack(side=tk.LEFT)
        self.num_iterations_entry = ttk.Entry(entry_frame_iterations)
        self.num_iterations_entry.pack(side=tk.LEFT, padx=5)

        entry_frame_excel_name = ttk.Frame(self.blue_frame)
        entry_frame_excel_name.pack(padx=5, pady=5)
        ttk.Label(entry_frame_excel_name, 
                  text="Fichier de données:").pack(side=tk.LEFT)
        self.excel_file_name_entry = tk.Label(entry_frame_excel_name, 
                            text = "Aucun fichier choisi", 
                            fg = "blue")
        self.excel_file_name_entry.pack(side=tk.LEFT)
        
        filenamecontainer = ttk.Frame(self.blue_frame)
        filenamecontainer.pack(padx=5)
        button_explore = tk.Button(filenamecontainer, 
                        text = "Parcourir...",
                        command = self.browseFiles).pack(side=tk.LEFT)
        

        entry_frame_image_output = ttk.Frame(self.blue_frame)
        entry_frame_image_output.pack(padx=5, pady=5)
        ttk.Label(entry_frame_image_output, 
                  text="Dossier de sauvegarde des images:").pack(side=tk.LEFT)
        self.image_dir_path = tk.Label(entry_frame_image_output, 
                            text = "Aucun dossier choisi", 
                            fg = "blue")
        self.image_dir_path.pack(side=tk.LEFT)
        #self.image_output_folder_entry = ttk.Entry(entry_frame_image_output)
        
        #self.image_output_folder_entry.pack(side=tk.LEFT, padx=5)
        foldernamecontainer = ttk.Frame(self.blue_frame)
        foldernamecontainer.pack(padx=5)
        button_explore = tk.Button(foldernamecontainer, 
                        text = "Parcourir...",
                        command = self.browseDirs).pack(side=tk.LEFT)

    def run_simulation_excel(self) -> None:
        self.clear_and_reset()
        try:
            self.first_num_line = int(self.first_num_line_entry.get())
            self.num_iterations = int(self.num_iterations_entry.get())
            self.multi_sim.df_filename = self.excel_file_name_entry.cget("text")
        except ValueError:
            tk.messagebox.showerror("Erreur", "Veuillez entrer un nombre entier valide.")
            return
        
        if self.first_num_line < 0:
            tk.messagebox.showerror("Erreur", "first line should be sup to 0")
            return

        if self.num_iterations < 0:
            tk.messagebox.showerror("Erreur", "num_iterations should be sup to 0")
            return 
        self.current_iteration = self.first_num_line - 1

        if self.windows_fenetre_puissance_total:
            self.windows_fenetre_puissance_total.destroy()
            

        if self.windows_fenetre_puissance_turbine:
            self.windows_fenetre_puissance_turbine.destroy()

        self.windows_fenetre_puissance_total = tk.Toplevel(self.root)
        self.windows_fenetre_puissance_total.title("Real Time Plot TOTAL")
        self.plot_excel_windows_total = ExcelMainWindow(self.windows_fenetre_puissance_total ,max_iterations=self.iterations_max)
        # RealTimePlotApp(self.windows_fenetre_puissance_total, iterations_max=self.iterations_max)


        # self.windows_fenetre_puissance_turbine = tk.Toplevel(self.root)
        # self.windows_fenetre_puissance_turbine.title("Real Time Plot TURBINE")
        # self.plot_excel_windows_turbine = RealTimePlotAppMulti(self.windows_fenetre_puissance_turbine, iterations_max=self.iterations_max)

        self.animate()

    def run_simulation_manual(self) -> None:
        try:
            self.total_flow = float(self.total_flow_entry.get())
            self.upstream_elevation = float(self.upstream_elevation_entry.get())
            self.turbine_states = [var.get() for var in self.turbine_checkboxes]
            self.turbines_debit_max = [float(var.get()) for var in self.debit_max_inputs]
        except ValueError:
            tk.messagebox.showerror("Erreur", "Veuillez entrer un nombre entier valide.")
            return
        print(self.turbines_debit_max )

        
        if self.manual_windows:
            self.manual_windows.destroy()

        df_dyn_result = self.multi_sim.calcul_exemple(debit_total=self.total_flow,
                                                      niveau_amont=self.upstream_elevation,
                                                      active_turbines=self.turbine_states, 
                                                      max_debit=self.turbines_debit_max)

        dyn_puissance_total = df_dyn_result.at["Computed ProgDyn","Puissance totale"]
        dyn_puissance_turbine_1 = df_dyn_result.at["Computed ProgDyn","Puissance T1"]
        dyn_puissance_turbine_2 = df_dyn_result.at["Computed ProgDyn","Puissance T2"]
        dyn_puissance_turbine_3 = df_dyn_result.at["Computed ProgDyn","Puissance T3"]
        dyn_puissance_turbine_4 = df_dyn_result.at["Computed ProgDyn","Puissance T4"]
        dyn_puissance_turbine_5 = df_dyn_result.at["Computed ProgDyn","Puissance T5"]

        
        nomad_puissance_total = df_dyn_result.at["Computed BB","Puissance totale"]
        nomad_puissance_turbine_1 = df_dyn_result.at["Computed BB","Puissance T1"]
        nomad_puissance_turbine_2 = df_dyn_result.at["Computed BB","Puissance T2"]
        nomad_puissance_turbine_3 = df_dyn_result.at["Computed BB","Puissance T3"]
        nomad_puissance_turbine_4 = df_dyn_result.at["Computed BB","Puissance T4"]
        nomad_puissance_turbine_5 = df_dyn_result.at["Computed BB","Puissance T5"]



        dyn_debit_total = df_dyn_result.at["Computed ProgDyn","Débit disponible"]
        dyn_debit_turbine_1 = df_dyn_result.at["Computed ProgDyn","Débit T1"]
        dyn_debit_turbine_2 = df_dyn_result.at["Computed ProgDyn","Débit T2"]
        dyn_debit_turbine_3 = df_dyn_result.at["Computed ProgDyn","Débit T3"]
        dyn_debit_turbine_4 = df_dyn_result.at["Computed ProgDyn","Débit T4"]        
        dyn_debit_turbine_5 = df_dyn_result.at["Computed ProgDyn","Débit T5"]


        nomad_debit_total = df_dyn_result.at["Computed BB","Débit disponible"]
        nomad_debit_turbine_1 = df_dyn_result.at["Computed BB","Débit T1"]
        nomad_debit_turbine_2 = df_dyn_result.at["Computed BB","Débit T2"]
        nomad_debit_turbine_3 = df_dyn_result.at["Computed BB","Débit T3"]
        nomad_debit_turbine_4 = df_dyn_result.at["Computed BB","Débit T4"]        
        nomad_debit_turbine_5 = df_dyn_result.at["Computed BB","Débit T5"]

        dyn_chutte_turbine_1 = df_dyn_result.at["Computed ProgDyn","Chute Nette T1"]
        dyn_chutte_turbine_2 = df_dyn_result.at["Computed ProgDyn","Chute Nette T2"]
        dyn_chutte_turbine_3 = df_dyn_result.at["Computed ProgDyn","Chute Nette T3"]
        dyn_chutte_turbine_4 = df_dyn_result.at["Computed ProgDyn","Chute Nette T4"]        
        dyn_chutte_turbine_5 = df_dyn_result.at["Computed ProgDyn","Chute Nette T5"]


        nomad_chutte_turbine_1 = df_dyn_result.at["Computed BB","Chute Nette T1"]
        nomad_chutte_turbine_2 = df_dyn_result.at["Computed BB","Chute Nette T2"]
        nomad_chutte_turbine_3 = df_dyn_result.at["Computed BB","Chute Nette T3"]
        nomad_chutte_turbine_4 = df_dyn_result.at["Computed BB","Chute Nette T4"]        
        nomad_chutte_turbine_5 = df_dyn_result.at["Computed BB","Chute Nette T5"]

        self.manual_windows = TurbineApp(puissance_total_dyn=dyn_puissance_total,
                                         puissance_total_nomad=nomad_puissance_total,
                                         debit_total_dyn=dyn_debit_total,
                                         debit_total_nomad=nomad_debit_total,
                                         puissance_debit_chutte=[(dyn_puissance_turbine_1,nomad_puissance_turbine_1,dyn_debit_turbine_1,nomad_debit_turbine_1,dyn_chutte_turbine_1,nomad_chutte_turbine_1),
                                                                 (dyn_puissance_turbine_2,nomad_puissance_turbine_2,dyn_debit_turbine_2,nomad_debit_turbine_2,dyn_chutte_turbine_2,nomad_chutte_turbine_2),
                                                                 (dyn_puissance_turbine_3,nomad_puissance_turbine_3,dyn_debit_turbine_3,nomad_debit_turbine_3,dyn_chutte_turbine_3,nomad_chutte_turbine_3),
                                                                 (dyn_puissance_turbine_4,nomad_puissance_turbine_4,dyn_debit_turbine_4,nomad_debit_turbine_4,dyn_chutte_turbine_4,nomad_chutte_turbine_4),
                                                                 (dyn_puissance_turbine_5,nomad_puissance_turbine_5,dyn_debit_turbine_5,nomad_debit_turbine_5,dyn_chutte_turbine_5,nomad_chutte_turbine_5)])

    def run_simulation(self) -> None:
        """
        Run the simulation.

        This method fetches the maximum number of iterations and initiates the simulation.
        """
        if self.switch_state:  # If the switch is in "Excel" mode
            print("Excel Mode")
            try:
                first_num_line = int(self.first_num_line_entry.get())
                num_iterations = int(self.num_iterations_entry.get())
                excel_file_name = self.excel_file_name_entry.cget("text")
                image_output_folder = self.image_dir_path.cget("text")
                print("First Num Line:", first_num_line)
                print("Num of Iterations:", num_iterations)
                print("Excel File Name:", excel_file_name)
                print("Image Output Folder:", image_output_folder)
                # You can add the code to handle Excel mode here if needed
            except ValueError:
                tk.messagebox.showerror("Error", "Données non valides pour le mode excel. Veuillez saisir des valeurs numériques valides.")
                return
            self.run_simulation_excel()
        else:  # If the switch is in "Manual" mode
            try:
                print("Manual Mode")
                total_flow = float(self.total_flow_entry.get())
                upstream_elevation = float(self.upstream_elevation_entry.get())
                turbine_states = [var.get() for var in self.turbine_checkboxes]
                turbines_debit_max = [var.get() for var in self.debit_max_inputs]
                turbines_debit_max = []
                i = 0
                for var in self.debit_max_inputs:
                    if var.get() == "":
                        turbines_debit_max.append(None)
                    else:
                        if turbine_states[i]:
                            turbines_debit_max.append(float(var.get()))
                        else:
                            turbines_debit_max.append(float(0))
                    print("Total Flow:", total_flow)
                    print("Upstream Elevation:", upstream_elevation)
                    print("Turbine States:", turbine_states)
                    print("Turbine Max:", turbines_debit_max)

            except ValueError:
                tk.messagebox.showerror("Error", "Données non valides pour le mode excel. Veuillez saisir des valeurs numériques valides.")
                return
            self.run_simulation_manual()
            

    def animate(self) -> None:
        """
        Animate the simulation.

        This method updates the simulation state iteratively and visualizes it.
        """
        if self.plot_excel_windows_total:
            if self.current_iteration < (self.first_num_line + self.num_iterations):
                self.current_iteration += 1

                df_dyn_result = self.multi_sim.calcul_row(row_columns_index=STARTING_ROW, row_to_calculate=STARTING_ROW+self.current_iteration)

                dyn_puissance_total = df_dyn_result.at["Computed ProgDyn","Puissance totale"]
                dyn_puissance_turbine_1 = df_dyn_result.at["Computed ProgDyn","Puissance T1"]
                dyn_puissance_turbine_2 = df_dyn_result.at["Computed ProgDyn","Puissance T2"]
                dyn_puissance_turbine_3 = df_dyn_result.at["Computed ProgDyn","Puissance T3"]
                dyn_puissance_turbine_4 = df_dyn_result.at["Computed ProgDyn","Puissance T4"]
                dyn_puissance_turbine_5 = df_dyn_result.at["Computed ProgDyn","Puissance T5"]

                original_puissance_total = df_dyn_result.at["Original","Puissance totale"]
                original_puissance_turbine_1 = df_dyn_result.at["Original","Puissance T1"]
                original_puissance_turbine_2 = df_dyn_result.at["Original","Puissance T2"]
                original_puissance_turbine_3 = df_dyn_result.at["Original","Puissance T3"]
                original_puissance_turbine_4 = df_dyn_result.at["Original","Puissance T4"]
                original_puissance_turbine_5 = df_dyn_result.at["Original","Puissance T5"]

                
                nomad_puissance_total = df_dyn_result.at["Computed BB","Puissance totale"]
                nomad_puissance_turbine_1 = df_dyn_result.at["Computed BB","Puissance T1"]
                nomad_puissance_turbine_2 = df_dyn_result.at["Computed BB","Puissance T2"]
                nomad_puissance_turbine_3 = df_dyn_result.at["Computed BB","Puissance T3"]
                nomad_puissance_turbine_4 = df_dyn_result.at["Computed BB","Puissance T4"]
                nomad_puissance_turbine_5 = df_dyn_result.at["Computed BB","Puissance T5"]



                dyn_debit_total = df_dyn_result.at["Computed ProgDyn","Débit disponible"]
                dyn_debit_turbine_1 = df_dyn_result.at["Computed ProgDyn","Débit T1"]
                dyn_debit_turbine_2 = df_dyn_result.at["Computed ProgDyn","Débit T2"]
                dyn_debit_turbine_3 = df_dyn_result.at["Computed ProgDyn","Débit T3"]
                dyn_debit_turbine_4 = df_dyn_result.at["Computed ProgDyn","Débit T4"]        
                dyn_debit_turbine_5 = df_dyn_result.at["Computed ProgDyn","Débit T5"]

                original_debit_total = df_dyn_result.at["Original","Débit disponible"]
                original_debit_turbine_1 = df_dyn_result.at["Original","Débit T1"]
                original_debit_turbine_2 = df_dyn_result.at["Original","Débit T2"]
                original_debit_turbine_3 = df_dyn_result.at["Original","Débit T3"]
                original_debit_turbine_4 = df_dyn_result.at["Original","Débit T4"]        
                original_debit_turbine_5 = df_dyn_result.at["Original","Débit T5"]

                nomad_debit_total = df_dyn_result.at["Computed BB","Débit disponible"]
                nomad_debit_turbine_1 = df_dyn_result.at["Computed BB","Débit T1"]
                nomad_debit_turbine_2 = df_dyn_result.at["Computed BB","Débit T2"]
                nomad_debit_turbine_3 = df_dyn_result.at["Computed BB","Débit T3"]
                nomad_debit_turbine_4 = df_dyn_result.at["Computed BB","Débit T4"]        
                nomad_debit_turbine_5 = df_dyn_result.at["Computed BB","Débit T5"]


                self.plot_excel_windows_total.add_value(x=self.current_iteration,
                                                        y_puissance_total_dyn= dyn_puissance_total,
                                                        y_list_debit_turbine_dyn= [dyn_debit_turbine_1, dyn_debit_turbine_2, dyn_debit_turbine_3,dyn_debit_turbine_4,dyn_debit_turbine_5],
                                                        y_list_puissance_turbine_dyn=[dyn_puissance_turbine_1, dyn_puissance_turbine_2, dyn_puissance_turbine_3,dyn_puissance_turbine_4,dyn_puissance_turbine_5],
                                                        
                                                        y_puissance_total_original= original_puissance_total,
                                                        y_list_debit_turbine_original= [original_debit_turbine_1, original_debit_turbine_2, original_debit_turbine_3, original_debit_turbine_4, original_debit_turbine_5],
                                                        y_list_puissance_turbine_original=[original_puissance_turbine_1, original_puissance_turbine_2, original_puissance_turbine_3, original_puissance_turbine_4, original_puissance_turbine_5],
                                                        
                                                        y_puissance_total_nomad= nomad_puissance_total,
                                                        y_list_debit_turbine_nomad= [nomad_debit_turbine_1, nomad_debit_turbine_2, nomad_debit_turbine_3, nomad_debit_turbine_4, nomad_debit_turbine_5],
                                                        y_list_puissance_turbine_nomad=[nomad_puissance_turbine_1, nomad_puissance_turbine_2, nomad_puissance_turbine_3, nomad_puissance_turbine_4, nomad_puissance_turbine_5])
    #             self.plot_excel_windows_turbine.add_value(x=self.current_iteration, y_dyn = [dyn_puissance_turbine_1, dyn_puissance_turbine_2, dyn_puissance_turbine_3,
    #       dyn_puissance_turbine_4,
    #       dyn_puissance_turbine_5],
    # y_bb=[nomad_puissance_turbine_1,
    #       nomad_puissance_turbine_2,
    #       nomad_puissance_turbine_3,
    #                                                                                       nomad_puissance_turbine_4,
    #                                                                                       nomad_puissance_turbine_5],
    #                                                                                 y_original=[original_puissance_turbine_1,
    #                                                                                             original_puissance_turbine_2,
    #                                                                                             original_puissance_turbine_3,
    #                                                                                             original_puissance_turbine_4,
    #                                                                                             original_puissance_turbine_5])
                
                self.status_label.config(text=f"Statut de la simulation : En cours ({self.current_iteration}/{self.iterations_max})")
                self.root.after(100, self.animate)
            # else:
            #     self.status_label.config(text="Statut de la simulation : Fini")
            #     self.plot_excel_windows_total.final_plot()
            #     self.plot_excel_windows_turbine.final_plot()

    def clear_and_reset(self) -> None:
        """Clear and reset the simulation parameters."""
        self.current_iteration = 0
        self.iterations_max = None
        self.plot_excel_windows_total = None

    @staticmethod
    def y_total_value() -> int:
        """Generate random values for the simulation."""
        return random.randint(0, 100)

    def quit(self) -> None:
        """Quit the application."""
        if self.windows_fenetre_puissance_total:
            self.windows_fenetre_puissance_total.destroy()

        if self.windows_fenetre_puissance_turbine:
            self.windows_fenetre_puissance_turbine.destroy()

        if self.manual_windows:
            self.manual_windows.destroy()

        self.root.destroy()

