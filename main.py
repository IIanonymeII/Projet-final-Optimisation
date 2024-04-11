import tkinter as tk

from src.interface.main_window import MainApp

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()