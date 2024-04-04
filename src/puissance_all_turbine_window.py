import tkinter as tk
from tkinter import ttk
import random
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

        self.clear_and_reset()

        self.status_label = ttk.Label(self.root, text="Statut de la simulation : Pas encore fait")
        self.status_label.grid(row=2, columnspan=3, padx=5, pady=5)

        self.iterations_max = iterations_max
        self.ecart_affichage = 10

        self.run_simulation()

    def run_simulation(self) -> None:
        """Run the simulation."""
        try:
            self.clear_and_reset()
        except ValueError:
            tk.messagebox.showerror("Erreur", "Nettoyage de la figure")
            return

        self.animate()

    def animate(self) -> None:
        """Animate the simulation."""
        if self.current_iteration < self.iterations_max:
            self.current_iteration += 1
            x = self.current_iteration
            y = [random.randint(0, 100) for _ in range(5)]  # Generate 5 random values
            for i in range(5):
                self.x_data[i].append(x)
                self.y_data[i].append(y[i])

                self.lines[i].set_xdata(self.x_data[i])
                self.lines[i].set_ydata(self.y_data[i])
                self.axs[i].relim()

                self.axs[i].set_xlim(min(self.x_data[i]) - 1, max(self.x_data[i]) + 1)
                self.axs[i].set_ylim(min([0] + self.y_data[i]) - self.ecart_affichage,
                                      max(self.y_data[i]) + self.ecart_affichage)

            self.canvas.draw()
            self.status_label.config(
                text=f"Statut de la simulation : En cours ({self.current_iteration}/{self.iterations_max})")
            self.root.after(100, self.animate)
        else:
            self.axs[0].clear()
            for i in range(5):
                self.axs[i].plot(self.x_data[i], self.y_data[i], 'b-')
                self.axs[i].set_xlim(min(self.x_data[i]), max(self.x_data[i]))
                self.axs[i].set_ylim(min([0] + self.y_data[i]) - self.ecart_affichage,
                                      max(self.y_data[i]) + self.ecart_affichage)
                self.axs[i].set_xlabel('Itération')
                self.axs[i].set_ylabel('Valeur')
            self.canvas.draw()
            self.status_label.config(text="Statut de la simulation : Fini")

    def clear_and_reset(self) -> None:
        """Clear and reset the plot."""
        self.fig, self.axs = plt.subplots(5, 1, figsize=(8, 10))
        self.lines = []
        self.x_data = [[] for _ in range(5)]
        self.y_data = [[] for _ in range(5)]
        for i in range(5):
            self.lines.append(self.axs[i].plot([], [], 'b-')[0])
            self.axs[i].set_xlim(0, 100)
            self.axs[i].set_ylim(0, 100)
            self.axs[i].set_xlabel('Itération')
            self.axs[i].set_ylabel('Valeur')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=1, columnspan=3, padx=5, pady=5)

        self.current_iteration = 0


if __name__ == "__main__":
    root = tk.Tk()
    app = RealTimePlotAppMulti(root, iterations_max=20)
    root.mainloop()
