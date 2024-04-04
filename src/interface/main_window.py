
import tkinter as tk
from tkinter import ttk
import random

from src.algo.test import Simulations
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

        self.iterations_label = ttk.Label(root, text="Nombre d'itérations max :")
        self.iterations_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.iterations_entry = ttk.Entry(root)
        self.iterations_entry.grid(row=0, column=1, padx=5, pady=5)

        self.run_button = ttk.Button(root, text="Run", command=self.run_simulation)
        self.run_button.grid(row=0, column=2, padx=5, pady=5)

        self.status_label = ttk.Label(self.root, text="Statut de la simulation : Pas encore fait")
        self.status_label.grid(row=2, columnspan=3, padx=5, pady=5)

        self.windows_fenetre_puissance_total = None
        self.windows_fenetre_puissance_turbine = None
        self.current_iteration = 0
        self.iterations_max = None
        self.test = None

        self.multi_sim = Simulations(FILENAME, ["ProgDyn"])



    def run_simulation(self) -> None:
        """
        Run the simulation.

        This method fetches the maximum number of iterations and initiates the simulation.
        """
        self.clear_and_reset()
        try:
            self.iterations_max = int(self.iterations_entry.get())
        except ValueError:
            tk.messagebox.showerror("Erreur", "Veuillez entrer un nombre entier valide.")
            return

        if self.windows_fenetre_puissance_total:
            self.windows_fenetre_puissance_total.destroy()

        # if self.windows_fenetre_puissance_turbine:
        #     self.windows_fenetre_puissance_total.destroy()

        self.windows_fenetre_puissance_total = tk.Toplevel(self.root)
        self.windows_fenetre_puissance_total.title("Real Time Plot TOTAL")
        self.test = RealTimePlotApp(self.windows_fenetre_puissance_total, iterations_max=self.iterations_max)

        self.animate()

    def animate(self) -> None:
        """
        Animate the simulation.

        This method updates the simulation state iteratively and visualizes it.
        """
        if self.test:
            if self.current_iteration < self.iterations_max:
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


                self.test.add_value(x=self.current_iteration, y=dyn_puissance_total, y_2=original_puissance_total)
                self.status_label.config(
                    text=f"Statut de la simulation : En cours ({self.current_iteration}/{self.iterations_max})"
                )
                self.root.after(100, self.animate)
            else:
                self.status_label.config(text="Statut de la simulation : Fini")
                self.test.final_plot()

    def clear_and_reset(self) -> None:
        """Clear and reset the simulation parameters."""
        self.current_iteration = 0
        self.iterations_max = None
        self.test = None

    @staticmethod
    def y_total_value() -> int:
        """Generate random values for the simulation."""
        return random.randint(0, 100)

    def quit(self) -> None:
        """Quit the application."""
        if self.windows_fenetre_puissance_total:
            self.windows_fenetre_puissance_total.destroy()

        self.root.destroy()

