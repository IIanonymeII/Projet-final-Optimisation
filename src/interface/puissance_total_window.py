
import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class RealTimePlotApp:
    def __init__(self, root: tk.Tk, iterations_max: int = 20) -> None:
        """
        Initialize the Real Time Plot Application.

        Parameters:
            root (tk.Tk): The root Tkinter window.
            iterations_max (int): Maximum number of iterations.
        """
        self.root = root
        self.root.title("Real Time Plot")

        self.status_label = ttk.Label(self.root, text="Statut de la simulation : Pas encore fait")
        self.status_label.grid(row=2, columnspan=3, padx=5, pady=5)

        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'b-', label='prog dynamique')
        self.line2, = self.ax.plot([], [], 'r-', label='valeur original')

        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel('Itération')
        self.ax.set_ylabel('Valeur')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=1, columnspan=3, padx=5, pady=5)

        self.x_data = []
        self.y_data = []        
        self.y_data_2 = []

        self.iterations_max = iterations_max
        self.ecart_affichage = 10


    def add_value(self, y: int, y_2: int, x: int) -> None:
        """
        Add a new data point to the plot.

        Parameters:
            y (int): The y-value for power calculated.
            y_2 (int): The y-value for original value.
            x (int): The x-value.
        """
        self.x_data.append(x)
        self.y_data.append(y)
        self.y_data_2.append(y_2)

        self.line.set_xdata(self.x_data)
        self.line.set_ydata(self.y_data)
        self.line2.set_xdata(self.x_data)
        self.line2.set_ydata(self.y_data_2)
        self.ax.relim()

        self.ax.set_xlim(min(self.x_data) - 1, max(self.x_data) + 1)
        self.ax.set_ylim(min([0] + self.y_data + self.y_data_2) - self.ecart_affichage, max(self.y_data + self.y_data_2) + self.ecart_affichage)

        self.ax.autoscale_view()
        self.canvas.draw()

        self.status_label.config(text=f"Statut de la simulation : En cours ({x}/{self.iterations_max})")

    def final_plot(self) -> None:
        """Plot the final result."""
        self.ax.clear()
        self.ax.plot(self.x_data, self.y_data, 'b-', label='prog dynamique')
        self.ax.plot(self.x_data, self.y_data_2, 'r-', label='valeur original')
        self.ax.set_xlim(min(self.x_data), max(self.x_data))
        self.ax.set_ylim(min([0] + self.y_data + self.y_data_2) - self.ecart_affichage, max(self.y_data + self.y_data_2) + self.ecart_affichage)
        self.ax.set_xlabel('Itération')
        self.ax.set_ylabel('Valeur')
        self.ax.legend()
        self.canvas.draw()

        self.status_label.config(text="Statut de la simulation : Fini")


if __name__ == "__main__":
    root = tk.Tk()
    app = RealTimePlotApp(root, iterations_max=20)

    root.mainloop()