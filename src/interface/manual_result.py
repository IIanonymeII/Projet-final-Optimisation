import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TurbineApp(tk.Tk):
    def __init__(self, puissance_total_dyn=127, puissance_total_nomad=127, debit_total_dyn=250, debit_total_nomad=250, puissance_debit_chutte=[(100, 150, 200, 200,30,30), (150, 150, 220, 220,30,30), (120, 120, 180, 180,30,30), (130, 130, 240, 240,30,30), (90, 90, 160, 160,30,30)]):
        super().__init__()

        self.title("Analyseur de Performance des Turbines")
        self.geometry("1000x700")

        self.create_widgets(puissance_total_dyn, puissance_total_nomad, 
                            puissance_debit_chutte)

    def create_widgets(self, puissance_total_dyn, puissance_total_nomad, puissance_debit_chutte):
        # Labels for turbine parameters
        tk.Label(self, text="Turbine   ", bg="lightgray").grid(row=0, column=1)
        tk.Label(self, text="Puissance Dynamique (MW)", bg="lightblue").grid(row=0, column=2)
        tk.Label(self, text="Puissance Nomade (MW)", bg="lightblue").grid(row=0, column=3)
        tk.Label(self, text="Débit Dynamique (m^3/s)", bg="lightpink").grid(row=0, column=4)
        tk.Label(self, text="Débit Nomade (m^3/s)", bg="lightpink").grid(row=0, column=5)        
        tk.Label(self, text="Chute Nette Dynamique (m)", bg="lightgreen").grid(row=0, column=6)
        tk.Label(self, text="Chute Nette Nomade (m)", bg="lightgreen").grid(row=0, column=7)
        sum_deb_nom = 0
        sum_deb_dyn = 0
        # Create labels for each turbine
        for i, (puissance_dyn, puissance_nomad, debit_dyn, debit_nomad, chutte_nette_dyn, chutte_nette_nomad) in enumerate(puissance_debit_chutte, start=1):
            sum_deb_dyn += debit_dyn
            sum_deb_nom += debit_nomad
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

            # Labels for dynamic and nomad net height
            dyn_net_height_label = tk.Label(self, text=chutte_nette_dyn)
            dyn_net_height_label.grid(row=i, column=6)

            nomad_net_height_label = tk.Label(self, text=chutte_nette_nomad)
            nomad_net_height_label.grid(row=i, column=7)

        # Labels for total parameters
        tk.Label(self, text=f" TOTAL ", bg="lightgray", font=("Arial", 10, "bold")).grid(row=i+1, column=1)

        self.total_power_dyn_label = tk.Label(self, text=str(puissance_total_dyn), font=("Arial", 10, "bold"))
        self.total_power_dyn_label.grid(row=i+1, column=2)

        self.total_power_nomad_label = tk.Label(self, text=str(puissance_total_nomad), font=("Arial", 10, "bold"))
        self.total_power_nomad_label.grid(row=i+1, column=3)

        self.total_flow_dyn_label = tk.Label(self, text=str(sum_deb_dyn), font=("Arial", 10, "bold"))
        self.total_flow_dyn_label.grid(row=i+1, column=4)

        self.total_flow_nomad_label = tk.Label(self, text=str(sum_deb_nom), font=("Arial", 10, "bold"))
        self.total_flow_nomad_label.grid(row=i+1, column=5)

        # Plot for power
        fig = plt.figure(figsize=(10, 5))
        ax1 = fig.add_subplot(311)
        ax1.plot(range(1, 6), [puissance for puissance, _, _, _, _, _ in puissance_debit_chutte], label='Puissance Dynamique (MW)')
        ax1.plot(range(1, 6), [puissance for _, puissance, _, _, _, _ in puissance_debit_chutte], label='Puissance Nomade (MW)')
        ax1.set_xlabel('Turbine')
        ax1.set_ylabel('Puissance (MW)')
        ax1.set_title('Puissance des Turbines')
        ax1.legend()
        ax1.grid(True)

        # Set custom x ticks and labels
        ax1.set_xticks(range(1, 6))
        ax1.set_xticklabels(range(1, 6))

        # Plot for first flow
        ax2 = fig.add_subplot(312)
        ax2.plot(range(1, 6), [debit for _, _, debit, _, _, _ in puissance_debit_chutte], label='Débit Dynamique (m^3/s)')
        ax2.plot(range(1, 6), [debit for _, _, _, debit, _, _ in puissance_debit_chutte], label='Débit Nomade (m^3/s)')
        ax2.set_xlabel('Turbine')
        ax2.set_ylabel('Débit (m^3/s)')
        ax2.set_title('Débit des Turbines')
        ax2.legend()
        ax2.grid(True)

        # Set custom x ticks and labels
        ax2.set_xticks(range(1, 6))
        ax2.set_xticklabels(range(1, 6))

        # Plot for second flow
        ax3 = fig.add_subplot(313)
        ax3.plot(range(1, 6), [chutte for _, _, _, _, chutte, _ in puissance_debit_chutte], label='Chutte nette Dynamique (m)')
        ax3.plot(range(1, 6), [chutte for _, _, _, _, _, chutte in puissance_debit_chutte], label='Chutte nette Nomade (m)')
        ax3.set_xlabel('Turbine')
        ax3.set_ylabel('Chutte nette (m)')
        ax3.set_title('Chutte nette des Turbines')
        ax3.legend()
        ax3.grid(True)

        # Set custom x ticks and labels
        ax3.set_xticks(range(1, 6))
        ax3.set_xticklabels(range(1, 6))

        # Adjust the height ratio between the subplots
        plt.subplots_adjust(hspace=0.8, top=0.9)

        # Embedding plot in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=7, columnspan=7)


if __name__ == "__main__":
    app = TurbineApp()
    app.mainloop()
