import tkinter as tk

class TwoButtonSwitch(tk.Frame):
    def __init__(self, master=None, switch_callback=None, **kw):
        super().__init__(master, **kw)
        self.switch_state = tk.BooleanVar()
        self.switch_state.set(False)
        self.switch_callback = switch_callback
        
        self.button_manual = tk.Button(self, text="Depuis un fichier excel", command=self.switch_on, state=tk.DISABLED, bg="lightgray", fg="white")
        self.button_file = tk.Button(self, text="Saisie manuelle", command=self.switch_off, bg="gray", fg="white")
        
        self.button_manual.pack(side=tk.LEFT)
        self.button_file.pack(side=tk.LEFT)
    
    def switch_on(self):
        self.switch_state.set(True)
        self.button_manual.config(state=tk.DISABLED, bg="lightgray", fg="white")
        self.button_file.config(state=tk.NORMAL, bg="gray", fg="white")
        if self.switch_callback:
            self.switch_callback(True)
        
    
    def switch_off(self):
        self.switch_state.set(False)
        self.button_file.config(state=tk.DISABLED, bg="lightgray", fg="white")
        self.button_manual.config(state=tk.NORMAL, bg="gray", fg="white")
        if self.switch_callback:
            self.switch_callback(False)
        
