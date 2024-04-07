
import tkinter as tk
from tkinter import ttk
import random

from src.interface.manual_result import TurbineApp
from src.interface.switch import TwoButtonSwitch
from src.algo.both_prog import Simulations
from src.interface.puissance_total_window import RealTimePlotApp
from src.interface.puissance_all_turbine_window import RealTimePlotAppMulti

from src.interface.global_var import FILENAME, STARTING_ROW



class MainApp:
    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the Main Application.

        Parameters:
            root (tk.Tk): The root Tkinter window.
        """
       

        self.root = root
        self.root.title("Real Time Plot")

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
        self.canvas = tk.Canvas(root, width=500, height=450)
        self.canvas.pack()

        # Draw the rectangles
        self.red_frame = tk.Frame(root, bg="red")
        self.red_frame.place(x=10, y=10, width=480, height=50)  # Red rectangle at the top

        # Create the TwoButtonSwitch widget inside the red frame
        self.switch_widget = TwoButtonSwitch(self.red_frame, switch_callback=self.switch_callback)
        self.switch_widget.pack(padx=10, pady=10)

        self.blue_frame = tk.Frame(root, bg="blue")
        self.blue_frame.place(x=10, y=60, width=480, height=290)  # Blue rectangle in the middle (largest)

        self.green_frame = tk.Frame(root, bg="green")
        self.green_frame.place(x=10, y=350, width=480, height=50)  # Green rectangle at the bottom

        self.yellow_frame = tk.Frame(root, bg="yellow")
        self.yellow_frame.place(x=10, y=400, width=480, height=40)  # Yellow rectangle at the bottom

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

        self.mode_label = ttk.Label(self.blue_frame, text="MANUAL", background="blue", foreground="white")
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

        # Create 5 check boxes for turbines
        self.turbine_checkboxes = []
        for i in range(5):
            checkbox_var = tk.BooleanVar(value=True)
            checkbox = ttk.Checkbutton(self.blue_frame, text=f"Turbine {i+1}", variable=checkbox_var)
            checkbox.pack(padx=5, pady=5)
            self.turbine_checkboxes.append(checkbox_var)

    def create_excel_widgets(self):
        # Remove existing widgets
        for widget in self.blue_frame.winfo_children():
            widget.destroy()

        self.mode_label = ttk.Label(self.blue_frame, text="EXCEL", background="blue", foreground="white")
        self.mode_label.pack(pady=5)

        # Create entry fields and labels for "First Num Line", "Num of Iterations", and "Excel File Name"
        entry_frame_first_num = ttk.Frame(self.blue_frame)
        entry_frame_first_num.pack(padx=5, pady=5)
        ttk.Label(entry_frame_first_num, text="First Num Line:").pack(side=tk.LEFT)
        self.first_num_line_entry = ttk.Entry(entry_frame_first_num)
        self.first_num_line_entry.pack(side=tk.LEFT, padx=5)

        entry_frame_iterations = ttk.Frame(self.blue_frame)
        entry_frame_iterations.pack(padx=5, pady=5)
        ttk.Label(entry_frame_iterations, text="Num of Iterations:").pack(side=tk.LEFT)
        self.num_iterations_entry = ttk.Entry(entry_frame_iterations)
        self.num_iterations_entry.pack(side=tk.LEFT, padx=5)

        entry_frame_excel_name = ttk.Frame(self.blue_frame)
        entry_frame_excel_name.pack(padx=5, pady=5)
        ttk.Label(entry_frame_excel_name, text="Excel File Name (default):").pack(side=tk.LEFT)
        self.excel_file_name_entry = ttk.Entry(entry_frame_excel_name)
        self.excel_file_name_entry.insert(tk.END, "data/DataProjet2024.xlsx")  # Default value
        self.excel_file_name_entry.pack(side=tk.LEFT, padx=5)

        entry_frame_image_output = ttk.Frame(self.blue_frame)
        entry_frame_image_output.pack(padx=5, pady=5)
        ttk.Label(entry_frame_image_output, text="Image Output Folder:").pack(side=tk.LEFT)
        self.image_output_folder_entry = ttk.Entry(entry_frame_image_output)
        self.image_output_folder_entry.insert(tk.END, "data/capture/")  # Default value
        self.image_output_folder_entry.pack(side=tk.LEFT, padx=5)

    def run_simulation_excel(self) -> None:
        self.clear_and_reset()
        try:
            self.first_num_line = int(self.first_num_line_entry.get())
            self.num_iterations = int(self.num_iterations_entry.get())
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
        self.plot_excel_windows_total = RealTimePlotApp(self.windows_fenetre_puissance_total, iterations_max=self.iterations_max)


        self.windows_fenetre_puissance_turbine = tk.Toplevel(self.root)
        self.windows_fenetre_puissance_turbine.title("Real Time Plot TURBINE")
        self.plot_excel_windows_turbine = RealTimePlotAppMulti(self.windows_fenetre_puissance_turbine, iterations_max=self.iterations_max)

        

        self.animate()

    def run_simulation_manual(self) -> None:
        try:
            self.total_flow = float(self.total_flow_entry.get())
            self.upstream_elevation = float(self.upstream_elevation_entry.get())
            self.turbine_states = [var.get() for var in self.turbine_checkboxes]
        except ValueError:
            tk.messagebox.showerror("Erreur", "Veuillez entrer un nombre entier valide.")
            return
        
        if self.manual_windows:
            self.manual_windows.destroy()
        

        df_dyn_result = self.multi_sim.calcul_exemple(debit_total=self.total_flow,niveau_amont=self.upstream_elevation,active_turbines=self.turbine_states)

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
        # print("   PUISSANCE TOTAL   ")
        # print(f"NOMAD : {nomad_puissance_total}")
        # print(f"DYNAM : {dyn_puissance_total}")

        # print("   PUISSANCE TURBINE 1   ")
        # print(f"NOMAD : {nomad_puissance_turbine_1}")
        # print(f"DYNAM : {dyn_puissance_turbine_1}")

        self.manual_windows = TurbineApp(puissance_total_dyn=dyn_puissance_total,
                                         puissance_total_nomad=nomad_puissance_total,
                                         debit_total_dyn=dyn_debit_total,
                                         debit_total_nomad=nomad_debit_total,
                                         puissance_debit=[(dyn_puissance_turbine_1,nomad_puissance_turbine_1,dyn_debit_turbine_1,nomad_debit_turbine_1),
                                                          (dyn_puissance_turbine_2,nomad_puissance_turbine_2,dyn_debit_turbine_2,nomad_debit_turbine_2),
                                                          (dyn_puissance_turbine_3,nomad_puissance_turbine_3,dyn_debit_turbine_3,nomad_debit_turbine_3),
                                                          (dyn_puissance_turbine_4,nomad_puissance_turbine_4,dyn_debit_turbine_4,nomad_debit_turbine_4),
                                                          (dyn_puissance_turbine_5,nomad_puissance_turbine_5,dyn_debit_turbine_5,nomad_debit_turbine_5)])

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
                excel_file_name = self.excel_file_name_entry.get()
                image_output_folder = self.image_output_folder_entry.get()
                print("First Num Line:", first_num_line)
                print("Num of Iterations:", num_iterations)
                print("Excel File Name:", excel_file_name)
                print("Image Output Folder:", image_output_folder)
                # You can add the code to handle Excel mode here if needed
            except ValueError:
                tk.messagebox.showerror("Error", "Invalid input for Excel mode. Please enter valid numeric values.")
                return
            self.run_simulation_excel()
        else:  # If the switch is in "Manual" mode
            try:
                print("Manual Mode")
                total_flow = float(self.total_flow_entry.get())
                upstream_elevation = float(self.upstream_elevation_entry.get())
                turbine_states = [var.get() for var in self.turbine_checkboxes]
                print("Total Flow:", total_flow)
                print("Upstream Elevation:", upstream_elevation)
                print("Turbine States:", turbine_states)
            except ValueError:
                tk.messagebox.showerror("Error", "Invalid input. Please enter valid numeric values.")
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


                self.plot_excel_windows_total.add_value(x=self.current_iteration, y_dyn=dyn_puissance_total, y_original=original_puissance_total, y_bb=nomad_puissance_total)
                self.plot_excel_windows_turbine.add_value(x=self.current_iteration,y_dyn=[dyn_puissance_turbine_1,
                                                                                          dyn_puissance_turbine_2,
                                                                                          dyn_puissance_turbine_3,
                                                                                          dyn_puissance_turbine_4,
                                                                                          dyn_puissance_turbine_5],
                                                                                    y_bb=[nomad_puissance_turbine_1,
                                                                                          nomad_puissance_turbine_2,
                                                                                          nomad_puissance_turbine_3,
                                                                                          nomad_puissance_turbine_4,
                                                                                          nomad_puissance_turbine_5],
                                                                                    y_original=[original_puissance_turbine_1,
                                                                                                original_puissance_turbine_2,
                                                                                                original_puissance_turbine_3,
                                                                                                original_puissance_turbine_4,
                                                                                                original_puissance_turbine_5])
                
                self.status_label.config(text=f"Statut de la simulation : En cours ({self.current_iteration}/{self.iterations_max})")
                self.root.after(100, self.animate)
            else:
                self.status_label.config(text="Statut de la simulation : Fini")
                self.plot_excel_windows_total.final_plot()
                self.plot_excel_windows_turbine.final_plot()

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

