import os
import tkinter as tk
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from typing import List

class ExcelMainWindow(tk.Tk):
    def __init__(self, root: tk.Tk, max_iterations=20):
        self.root = root
        self.root.title("Affiche des courbes avec les valeurs Excel")
        self.root.geometry("1400x700")

        # Calculate the requested height and width
        req_height = self.root.winfo_screenheight()
        req_width = self.root.winfo_screenwidth()

        # Height and width of the top plot
        top_plot_height = (req_height - 100) // 8
        top_plot_width = req_width - 20

        # Height and width of the side plots
        side_plot_height = (req_height - top_plot_height - 100) // 5
        side_plot_width = (req_width - 20 - 40) // 5  # Subtract additional 40 pixels for spacing

        # List to hold the figures
        self.figures = []

        # Top plot
        self.top_frame = tk.Frame(self.root, bg="red", height=top_plot_height, width=top_plot_width)
        self.top_frame.pack(fill=tk.BOTH, expand=True)

        # Create top plot
        self.top_fig = Figure(figsize=(10, 2), dpi=100)
        self.top_plot = self.top_fig.add_subplot(111)
        self.top_plot.set_title("Puissance totale", pad=20)  # Add padding to title
        self.top_plot.set_xlabel("Temps", labelpad=10)  # Add padding to xlabel
        self.top_plot.set_ylabel("Puissance", labelpad=10)  # Add padding to ylabel
        self.top_canvas = FigureCanvasTkAgg(self.top_fig, master=self.top_frame)
        self.top_canvas.draw()
        self.top_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.figures.append(self.top_fig)  # Append the top figure to the list

        # Bottom plots
        self.bottom_frame = tk.Frame(self.root, bg="blue", height=(req_height - top_plot_height - 100), width=req_width - 20)
        self.bottom_frame.pack(fill=tk.BOTH, expand=True)

        # Left side plots
        self.left_bottom_frame = tk.Frame(self.bottom_frame, bg="green", height=side_plot_height, width=side_plot_width)
        self.left_bottom_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create side plots - Débit pour turbines 1-5 à gauche
        self.left_side_plots = []
        for i in range(5):
            fig = Figure(figsize=(5, 1), dpi=100)
            plot = fig.add_subplot(111)
            plot.set_title(f"Débit turbine {i+1}", pad=10)  # Add padding to title
            plot.set_xlabel("Temps", labelpad=5)  # Add padding to xlabel
            plot.set_ylabel("Débit", labelpad=5)  # Add padding to ylabel

            canvas = FigureCanvasTkAgg(fig, master=self.left_bottom_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.left_side_plots.append(plot)  # Append the left side plot to the list

        # Right side plots
        self.right_bottom_frame = tk.Frame(self.bottom_frame, bg="yellow", height=side_plot_height, width=side_plot_width)
        self.right_bottom_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create side plots - Puissance pour turbines 1-5 à droite
        self.right_side_plots = []
        for i in range(5):
            fig = Figure(figsize=(5, 1), dpi=100)
            plot = fig.add_subplot(111)
            plot.set_title(f"Puissance turbine {i+1}", pad=10)  # Add padding to title
            plot.set_xlabel("Temps", labelpad=5)  # Add padding to xlabel
            plot.set_ylabel("Puissance", labelpad=5)  # Add padding to ylabel

            canvas = FigureCanvasTkAgg(fig, master=self.right_bottom_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.right_side_plots.append(plot)  # Append the right side plot to the list


        # Initialize data arrays
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.x_data = []
        self.y_puissance_total_original = []
        self.y_puissance_total_dyn = []
        self.y_puissance_total_nomad = []

        self.y_puissance_turbine_original = [[], [], [], [], []]
        self.y_puissance_turbine_dyn = [[], [], [], [], []]
        self.y_puissance_turbine_nomad = [[], [], [], [], []]

        self.y_debit_turbine_original = [[], [], [], [], []]
        self.y_debit_turbine_dyn = [[], [], [], [], []]
        self.y_debit_turbine_nomad = [[], [], [], [], []]

        self.y_chute_turbine_original = [[], [], [], [], []]
        self.y_chute_turbine_dyn = [[], [], [], [], []]
        self.y_chute_turbine_nomad = [[], [], [], [], []]


    def add_value(self, x, y_puissance_total_original: float, y_list_debit_turbine_original: List[float], y_list_puissance_turbine_original: List[float],
                           y_puissance_total_dyn: float     , y_list_debit_turbine_dyn: List[float]     , y_list_puissance_turbine_dyn: List[float]     ,
                           y_puissance_total_nomad: float   , y_list_debit_turbine_nomad: List[float]   , y_list_puissance_turbine_nomad: List[float]   ,
                           y_chute_turbine_nomad : List[float], y_chute_turbine_dyn : List[float],y_chute_turbine_original : List[float],):
        # Append new data to the arrays
        self.x_data.append(x)
        self.y_puissance_total_original.append(y_puissance_total_original)
        self.y_puissance_total_nomad.append(y_puissance_total_nomad)
        self.y_puissance_total_dyn.append(y_puissance_total_dyn)


        for i, y_debit in enumerate(y_list_debit_turbine_original):
            self.y_debit_turbine_original[i].append(y_debit)

        for i, y_debit in enumerate(y_list_debit_turbine_dyn):
            self.y_debit_turbine_dyn[i].append(y_debit)

        for i, y_debit in enumerate(y_list_debit_turbine_nomad):
            self.y_debit_turbine_nomad[i].append(y_debit)


        for i, y_puissance in enumerate(y_list_puissance_turbine_original):
            self.y_puissance_turbine_original[i].append(y_puissance)

        for i, y_puissance in enumerate(y_list_puissance_turbine_dyn):
            self.y_puissance_turbine_dyn[i].append(y_puissance)
        
        for i, y_puissance in enumerate(y_list_puissance_turbine_nomad):
            self.y_puissance_turbine_nomad[i].append(y_puissance)


        for i, y_chute in enumerate(y_chute_turbine_dyn):
            self.y_chute_turbine_dyn[i].append(y_chute)

        for i, y_chute in enumerate(y_chute_turbine_nomad):
            self.y_chute_turbine_nomad[i].append(y_chute)
        
        for i, y_chute in enumerate(y_chute_turbine_original):
            self.y_chute_turbine_original[i].append(y_chute)

        # Update plots with new data
        self.update_plots()

    def update_plots(self):
        # Calculate the average of puissance totale
        moyenne_puissance_totale = np.mean(self.y_puissance_total_original)

        # Update top plot (Puissance totale)
        self.top_plot.clear()
        self.top_plot.plot(self.x_data, self.y_puissance_total_original, label="Original")
        self.top_plot.plot(self.x_data, self.y_puissance_total_nomad   , label="Nomad")
        self.top_plot.plot(self.x_data, self.y_puissance_total_dyn     , label="Dyn")
        self.top_plot.set_title(f"Puissance totale (Moyenne: {moyenne_puissance_totale:.2f} MW)", pad=20)  # Add padding to title and display the average
        self.top_plot.set_xlabel("Temps", labelpad=10)  # Add padding to xlabel
        self.top_plot.set_ylabel("Puissance", labelpad=10)  # Add padding to ylabel
        self.top_plot.legend()
        self.top_canvas.draw()

        for i in range(0,5,1):
            plot = self.left_side_plots[i]
            plot.clear()
            plot.plot(self.x_data, self.y_debit_turbine_original[i], label="Original")
            plot.plot(self.x_data, self.y_debit_turbine_nomad[i]   , label="Nomad")
            plot.plot(self.x_data, self.y_debit_turbine_dyn[i]     , label="Dyn")
            plot.set_title(f"Débit turbine {i + 1}", pad=10)  # Add padding to title
            plot.set_xlabel("Temps", labelpad=5)  # Add padding to xlabel
            plot.set_ylabel("Débit", labelpad=5)  # Add padding to ylabel
            plot.figure.canvas.draw()


        for i in range(0,5,1):
            plot = self.right_side_plots[i]
            plot.clear()
            plot.plot(self.x_data, self.y_puissance_turbine_original[i], label="Original")
            plot.plot(self.x_data, self.y_puissance_turbine_nomad[i]   , label="Nomad")
            plot.plot(self.x_data, self.y_puissance_turbine_dyn[i]     , label="Dyn")
            plot.set_title(f"Puissance turbine {i + 1}", pad=10)  # Add padding to title
            plot.set_xlabel("Temps", labelpad=5)  # Add padding to xlabel
            plot.set_ylabel("Puissance", labelpad=5)  # Add padding to ylabel
            plot.figure.canvas.draw()
    
    
    def plot_final(self):
        # Finalize plots
        for figure in self.figures:
            figure.tight_layout()  # Adjust subplot layout
            figure.canvas.draw()    # Update the figure with the new layout

    def save_difference(self, folder):
        # Calculate differences
        difference_puissance_dyn = np.array(self.y_puissance_total_original) - np.array(self.y_puissance_total_dyn)
        difference_puissance_nomad = np.array(self.y_puissance_total_original) - np.array(self.y_puissance_total_nomad)

        # Calculate average differences
        moyenne_difference_puissance_dyn = np.mean(difference_puissance_dyn)
        moyenne_difference_puissance_nomad = np.mean(difference_puissance_nomad)

        # Create subplots for differences
        fig_difference, ax_difference = plt.subplots()
        ax_difference.plot(self.x_data, difference_puissance_dyn, label="Différence puissance dyn")
        ax_difference.plot(self.x_data, difference_puissance_nomad, label="Différence puissance nomad")
        ax_difference.set_title(f"Differences entre puissance total et dyn / nomad (Moyennes: {moyenne_difference_puissance_dyn:.2f}, {moyenne_difference_puissance_nomad:.2f})")
        ax_difference.set_xlabel("Temps")
        ax_difference.set_ylabel("Difference")
        ax_difference.legend()

        # Save the figure
        fig_difference.savefig(os.path.join(folder, "EXCEL_puissance_differences.png"), bbox_inches='tight', dpi=300)

    def save_chute_figures_as_png(self, folder):
        # Create the folder if it doesn't exist
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Save chute data for each turbine
        for i in range(5):
            # Create a new figure for each turbine
            fig_chute = plt.figure(figsize=(8, 6))  # Adjust figure size as needed
            ax_chute = fig_chute.add_subplot(111)

            # Plot chute data for the current turbine
            ax_chute.plot(self.x_data, self.y_chute_turbine_original[i], label="Original")
            ax_chute.plot(self.x_data, self.y_chute_turbine_nomad[i], label="Nomad")
            ax_chute.plot(self.x_data, self.y_chute_turbine_dyn[i], label="Dyn")

            # Set title and labels
            ax_chute.set_title(f"Chute turbine {i+1}")
            ax_chute.set_xlabel("Temps")
            ax_chute.set_ylabel("Chute")
            ax_chute.legend()

            # Save the figure
            fig_chute.savefig(os.path.join(folder, f"chute_turbine_{i+1}.png"), bbox_inches='tight', dpi=300)  # Adjust dpi as needed

    def save_figures_as_png(self, folder):
        # Create the folder if it doesn't exist
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Save Puissance totale
        self.top_fig.savefig(os.path.join(folder, "EXCEL_puissance_totale.png"), bbox_inches='tight', dpi=300)  # Specify dpi=300 for higher resolution

        # Save Puissance turbine 1 à 5
        for i, plot in enumerate(self.right_side_plots):
            plot.figure.savefig(os.path.join(folder, f"EXCEL_puissance_turbine_{i+1}.png"), bbox_inches='tight', dpi=300)  # Specify dpi=300 for higher resolution

        # Save Débit turbine 1 à 5
        for i, plot in enumerate(self.left_side_plots):
            plot.figure.savefig(os.path.join(folder, f"EXCEL_debit_turbine_{i+1}.png"), bbox_inches='tight', dpi=300)  # Specify dpi=300 for higher resolution
        self.save_difference(folder=folder)
        self.save_chute_figures_as_png(folder=folder)
        

if __name__ == "__main__":
    app = ExcelMainWindow()
    app.mainloop()
