import tkinter as tk
from tkinter import ttk
from database import conexion_comida_basedatos

class BaseDatosApp:
    def __init__(self, root, ventana_principal):
        self.root = root
        self.ventana_principal = ventana_principal
        self.root.title("Base de Datos")
        self.root.minsize(400, 300)

        # Obtener los datos de la base de datos
        datos = conexion_comida_basedatos()

        datos_ordenados = sorted(datos, key=lambda item: item["grupo"])

        # Crear el Treeview para mostrar los datos
        self.tree = ttk.Treeview(root, columns=("Nombre", "Grupo", "Calorias", "Grasas", "Proteinas", "Carbohidratos"), show='headings')
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Grupo", text="Grupo")
        self.tree.heading("Calorias", text="Calorias (kcal)")
        self.tree.heading("Grasas", text="Grasas (g)")
        self.tree.heading("Proteinas", text="Proteinas (g)")
        self.tree.heading("Carbohidratos", text="Carbohidratos (g)")

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Agregar datos al Treeview
        for item in datos_ordenados:
            self.tree.insert("", "end", values=(item["nombre"], item["grupo"], item["calorias"], item["grasas"], item["proteinas"], item["carbohidratos"]))

        # Añadir scrollbar
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Botón de regreso a la ventana principal
        tk.Button(root, text="Volver", command=self.volver).grid(row=1, column=0, columnspan=2, pady=10)


        # Configurar redimensionamiento
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)


    def volver(self):
        self.root.destroy()
        self.ventana_principal.deiconify()