#__main__.py

import sys
import os

import tkinter as tk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.GUI.ventana_principal import MainApp

# Lanza la aplicacion
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()