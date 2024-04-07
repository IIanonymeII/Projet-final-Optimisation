import tkinter as tk
from tkinter import ttk
import random
from typing import List
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class RealTimePlotAppMulti:
    def __init__(self, root: tk.Tk, iterations_max: int = 20) -> None:
        """
        Initialize the Real Time Plot Application.

        Parameters:
            root (tk.Tk): The root Tkinter window.
            iterations_max (int): Maximum number of iterations.
        """
        self.root = root
        self.root.title("Real Time Plot")

        self.fig, self.axs = plt.subplots(5, 1, figsize=(8, 10))
        self.lines = [[], [], [], [], []]
        self.x_data = [[] for _ in range(5)]
        self.y_data = [[] for _ in range(5)]
        self.y_data_2 = [[] for _ in range(5)]
        self.y_data_3 = [[] for _ in range(5)]
        for i in range(5):
            self.lines[i].append(self.axs[i].plot([], [], 'b-', label='prog dynamique')[0])
            self.lines[i].append(self.axs[i].plot([], [], 'r-', label='valeur original')[0])  # Second line in red
            self.lines[i].append(self.axs[i].plot([], [], 'g-', label='valeur nomad')[0])  # Third line in green
            self.axs[i].set_xlim(0, 100)
            self.axs[i].set_ylim(0, 100)
            self.axs[i].set_xlabel('Itération')
            self.axs[i].set_ylabel('Valeur')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=1, columnspan=3, padx=5, pady=5)

        self.current_iteration = 0

        self.status_label = ttk.Label(self.root, text="Statut de la simulation : Pas encore fait")
        self.status_label.grid(row=2, columnspan=3, padx=5, pady=5)

        self.iterations_max = iterations_max
        self.ecart_affichage = 10


    def add_value(self, y_dyn: List[float], y_bb: List[float], y_original: List[float], x: int) -> None:
        """
        Add a new data point to the plot.

        Parameters:
            y_dyn (List[float]): List of y-values for dynamic progress.
            y_bb (List[float]): List of y-values for original value.
            y_original (List[float]): List of y-values for nomad value.
            x (int): The x-value.
        """
        for i in range(5):
            self.x_data[i].append(x)
            self.y_data[i].append(y_dyn[i])
            self.y_data_2[i].append(y_bb[i])
            self.y_data_3[i].append(y_original[i])

            for j, line in enumerate(self.lines[i]):  # Loop through each line in subplot
                if j == 0:
                    line.set_xdata(self.x_data[i])
                    line.set_ydata(self.y_data[i])
                elif j == 1:
                    line.set_xdata(self.x_data[i])
                    line.set_ydata(self.y_data_2[i])
                elif j == 2:
                    line.set_xdata(self.x_data[i])
                    line.set_ydata(self.y_data_3[i])

            self.axs[i].relim()
            self.axs[i].set_xlim(min(self.x_data[i]) - 1, max(self.x_data[i]) + 1)
            self.axs[i].set_ylim(min(self.y_data[i] + self.y_data_2[i] + self.y_data_3[i]) - self.ecart_affichage,
                                max(self.y_data[i] + self.y_data_2[i] + self.y_data_3[i]) + self.ecart_affichage)
            self.axs[i].autoscale_view()
            self.axs[i].legend()

        self.canvas.draw()
        self.status_label.config(text=f"Statut de la simulation : En cours ({x}/{self.iterations_max})")
    
    def final_plot(self) -> None:
        """Plot the final result."""
        for i in range(5):
            self.axs[i].clear()
            self.axs[i].plot(self.x_data[i], self.y_data[i], 'b-', label='prog dynamique')
            self.axs[i].plot(self.x_data[i], self.y_data_2[i], 'r-', label='valeur original')
            self.axs[i].plot(self.x_data[i], self.y_data_3[i], 'g-', label='valeur nomad')
            self.axs[i].set_xlim(min(self.x_data[i]), max(self.x_data[i]))
            self.axs[i].set_ylim(min([0] + self.y_data[i] + self.y_data_2[i] + self.y_data_3[i]) - self.ecart_affichage,
                                max(self.y_data[i] + self.y_data_2[i] + self.y_data_3[i]) + self.ecart_affichage)
            self.axs[i].set_xlabel('Itération')
            self.axs[i].set_ylabel('Valeur')
            self.axs[i].legend()
        self.canvas.draw()
        self.status_label.config(text="Statut de la simulation : Fini")

if __name__ == "__main__":
    root = tk.Tk()
    app = RealTimePlotAppMulti(root, iterations_max=20)
    root.mainloop()
