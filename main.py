import tkinter as tk
from tkinter import ttk
import random

from puissance_total_window import RealTimePlotApp
from puissance_all_turbine_window import RealTimePlotAppMulti


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
                self.test.add_value(x=self.current_iteration, y=self.y_total_value())
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


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()