import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TurbineApp(tk.Tk):
    def __init__(self, puissance_total_dyn=127,puissance_total_nomad=127, debit_total_dyn=250,debit_total_nomad=250, puissance_debit=[(100,150,200, 200), (150,150, 220, 220), (120,120, 180, 180), (130,130, 240, 240), (90,90, 160, 160)]):
        super().__init__()

        self.title("Turbine Performance Analyzer")
        self.geometry("800x700")

        self.create_widgets(puissance_total_dyn, puissance_total_nomad, debit_total_dyn, debit_total_nomad, puissance_debit)

    def create_widgets(self, puissance_total_dyn, puissance_total_nomad, debit_total_dyn, debit_total_nomad, puissance_debit):
        # Labels for turbine parameters
        tk.Label(self, text="Turbine   ", bg="lightgray").grid(row=0, column=1)
        tk.Label(self, text="Dynamic Power (MW)", bg="lightblue").grid(row=0, column=2)
        tk.Label(self, text="Nomad Power (MW)", bg="lightblue").grid(row=0, column=3)
        tk.Label(self, text="Dynamic Flow (m^3/s)", bg="lightpink").grid(row=0, column=4)
        tk.Label(self, text="Nomad Flow (m^3/s)", bg="lightpink").grid(row=0, column=5)

        # Create labels for each turbine
        for i, (puissance_dyn, puissance_nomad, debit_dyn, debit_nomad) in enumerate(puissance_debit, start=1):
            tk.Label(self, text=f"Turbine {i}", bg="lightgray").grid(row=i, column=1)

            # Labels for dynamic power and flow
            dyn_power_label = tk.Label(self, text=puissance_dyn)
            dyn_power_label.grid(row=i, column=2)

            nomad_power_label = tk.Label(self, text=puissance_nomad)
            nomad_power_label.grid(row=i, column=3)

            # Entries for dynamic flow
            dyn_flow_entry = tk.Label(self, text=debit_dyn)
            dyn_flow_entry.grid(row=i, column=4)

            # Entries for nomad flow
            nomad_flow_entry = tk.Label(self, text=debit_nomad)
            nomad_flow_entry.grid(row=i, column=5)

        # Labels for total parameters
        tk.Label(self, text=f" TOTAL ", bg="lightgray", font=("Arial", 10, "bold")).grid(row=i+1, column=1)

        self.total_power_dyn_label = tk.Label(self, text=str(puissance_total_dyn), font=("Arial", 10, "bold"))
        self.total_power_dyn_label.grid(row=i+1, column=2)

        self.total_power_nomad_label = tk.Label(self, text=str(puissance_total_nomad), font=("Arial", 10, "bold"))
        self.total_power_nomad_label.grid(row=i+1, column=3)

        self.total_flow_dyn_label = tk.Label(self, text=str(debit_total_dyn), font=("Arial", 10, "bold"))
        self.total_flow_dyn_label.grid(row=i+1, column=4)

        self.total_flow_nomad_label = tk.Label(self, text=str(debit_total_nomad), font=("Arial", 10, "bold"))
        self.total_flow_nomad_label.grid(row=i+1, column=5)





        # Plot for power
        fig = plt.figure(figsize=(8, 5))
        ax1 = fig.add_subplot(211)
        ax1.plot(range(1, 6), [puissance for puissance, _, _, _ in puissance_debit], label='Dynamic Power (MW)')
        ax1.plot(range(1, 6), [puissance for _, puissance, _, _ in puissance_debit], label='Nomad Power (MW)')
        ax1.set_xlabel('Turbine')
        ax1.set_ylabel('Power (MW)')
        ax1.set_title('Turbine Power')
        ax1.legend()
        ax1.grid(True)

        # Plot for flow
        ax2 = fig.add_subplot(212)
        ax2.plot(range(1, 6), [debit for _, _, debit, _ in puissance_debit], label='Dynamic Flow')
        ax2.plot(range(1, 6), [debit for _, _, _, debit in puissance_debit], label='Nomad Flow')
        ax2.set_xlabel('Turbine')
        ax2.set_ylabel('Flow')
        ax2.set_title('Turbine Flow')
        ax2.legend()
        ax2.grid(True)

        # Adjust the height ratio between the two subplots
        plt.subplots_adjust(hspace=0.5)

        # Embedding plot in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=7, columnspan=7)

        


if __name__ == "__main__":
    app = TurbineApp()
    app.mainloop()
