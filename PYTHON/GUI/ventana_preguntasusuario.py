# ventana_preguntasusuario.py
import time
import random

import tkinter as tk
from tkinter import ttk

from PYTHON.GUI.ventana_menu import VentanaMenu
from PYTHON.utilidades import database, funciones_auxiliares, constantes
from PYTHON.algoritmos.nsga2 import ag_nsga2_penalizacion_estatica

# Conectar a la base de datos
comida_basedatos = database.conexion_comida_basedatos()

# Establecer como semilla la hora del sistema
seed = int(time.time())
random.seed(seed)

class VentanaCalorias:
    """Ventana de calculo de calorias"""
    def __init__(self, root, ventana_principal):
        
        self.root = root
        self.ventana_principal = ventana_principal
        self.root.title("Preguntas al usuario")
        self.root.minsize(800, 900)

        # Crea el marco principal
        frame = ttk.Frame(root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=2)
        frame.rowconfigure(10, weight=1)

        # Variables para los datos del usuario
        self.peso = tk.DoubleVar()
        self.altura = tk.DoubleVar()
        self.edad = tk.IntVar()
        self.sexo = tk.StringVar(value="hombre")
        self.nivel_actividad = tk.StringVar(value="Sedentario (poco o ningún ejercicio)")

        # Obtiene los grupos de comida
        grupos_comida = self.obtener_grupos_comida(constantes.GruposComida)
        self.diccionario_grupos = self.obtener_diccionario_grupos(constantes.GruposComida)

        # Crea el formulario y los botones
        self.crear_formulario(frame, grupos_comida)
        self.crear_botones(frame)

        self.resultado = ttk.Label(frame, text="")
        self.resultado.grid(row=9, column=0, columnspan=2, pady=10, sticky="ew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)


    def obtener_grupos_comida(self, clase, nivel=0):
        """Obtiene los grupos de comida"""
        grupos = []
        
        for nombre, subclase in vars(clase).items():
            if isinstance(subclase, tuple):
                tab = " " * (2 * (len(subclase[0]) - 1))
                grupos.append(f"{tab}{subclase[0]} - {subclase[1]}")
            elif isinstance(subclase, type):
                grupos.extend(self.obtener_grupos_comida(subclase, nivel + 1))

        return grupos


    def obtener_diccionario_grupos(self, clase):
        """Obtiene el diccionario de los grupos de comida"""
        diccionario = {}

        for nombre, subclase in vars(clase).items():

            if isinstance(subclase, tuple):
                diccionario[subclase[0]] = subclase[1]
            elif isinstance(subclase, type):
                diccionario.update(self.obtener_diccionario_grupos(subclase))

        return diccionario


    def crear_listbox(self, frame, etiqueta, fila, grupos_comida):
        """Crea una lista de seleccion multiple"""
        ttk.Label(frame, text=etiqueta).grid(row=fila, column=0, sticky=tk.W, pady=5)
        lista = tk.Listbox(frame, selectmode='multiple', width=50, height=10, exportselection=False)

        for grupo in grupos_comida:
            lista.insert(tk.END, grupo)

        lista.grid(row=fila, column=1, pady=5, sticky="ew")

        return lista


    def crear_formulario(self, frame, grupos_comida):
        """Crea el formulario"""

        ttk.Label(frame, text="Introduce tu peso en kg:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.peso).grid(row=0, column=1, pady=5, sticky="ew")

        ttk.Label(frame, text="Introduce tu altura en cm:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.altura).grid(row=1, column=1, pady=5, sticky="ew")

        ttk.Label(frame, text="Introduce tu edad:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.edad).grid(row=2, column=1, pady=5, sticky="ew")

        ttk.Label(frame, text="Introduce tu sexo:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(frame, textvariable=self.sexo, values=["hombre", "mujer"]).grid(row=3, column=1, pady=5, sticky="ew")

        ttk.Label(frame, text="Elige tu nivel de actividad:").grid(row=4, column=0, sticky=tk.W, pady=5)
        actividad_descripciones = [actividad.value[0] for actividad in constantes.NivelActividad]
        ttk.Combobox(frame, textvariable=self.nivel_actividad, values=actividad_descripciones).grid(row=4, column=1, pady=5, sticky="ew")

        self.lista_alergia = self.crear_listbox(frame, "Grupos de comida a los que eres alérgico:", 5, grupos_comida)
        self.lista_gusta = self.crear_listbox(frame, "Grupos de comida que te gustan:", 6, grupos_comida)
        self.lista_no_gusta = self.crear_listbox(frame, "Grupos de comida que no te gustan:", 7, grupos_comida)


    def crear_botones(self, frame):
        """Crea los botones"""
        ttk.Button(frame, text="Calcular Calorías", command=self.calcular_calorias).grid(row=8, column=0, pady=10)
        ttk.Button(frame, text="Mostrar Menú", command=self.mostrar_menu).grid(row=8, column=1, pady=10)
        ttk.Button(frame, text="Volver", command=self.volver).grid(row=10, column=0, columnspan=2, pady=10)


    def expandir_selecciones(self, lista):
        """Selecciona los subgrupos del grupo de comida seleccionado"""
        seleccionados = [lista.get(i).split()[0] for i in lista.curselection()]
        expandido = set()

        for seleccionado in seleccionados:
            for codigo, descripcion in self.diccionario_grupos.items():
                
                if codigo.startswith(seleccionado):
                    expandido.add(codigo)

        return list(expandido)

    
    def calcular_calorias(self):
        """Calcula calorias a partir de datos de usuario"""

        peso = self.peso.get()
        altura = self.altura.get()
        edad = self.edad.get()
        sexo = self.sexo.get()
        nivel_actividad_desc = self.nivel_actividad.get()

        factor_actividad = next((actividad.value[1] for actividad in constantes.NivelActividad if actividad.value[0] == nivel_actividad_desc), 1.2)

        if sexo == 'hombre':
            tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
        else:
            tmb = (10 * peso) + (6.25 * altura) - (5 * edad) - 161

        calorias_ajustadas = round (tmb * factor_actividad, 2)

        self.resultado.config(text=f"Calorías diarias: {calorias_ajustadas:.2f}")
        return calorias_ajustadas

    def mostrar_menu(self):
        """Calcula el menu con los datos insertados y muestra la ventana Menu"""

        grupos_alergia = self.expandir_selecciones(self.lista_alergia)
        calorias_ajustadas = self.calcular_calorias()
        grupos_gusta = self.expandir_selecciones(self.lista_gusta)
        grupos_no_gusta = self.expandir_selecciones(self.lista_no_gusta)
        
        resultado = ag_nsga2_penalizacion_estatica.ejecutar_algoritmo_genetico(comida_basedatos, calorias_ajustadas, self.edad.get(), grupos_alergia, grupos_gusta, grupos_no_gusta, seed)

        cv = resultado.F[:, 0]
        least_infeas = cv.argmin()
        x = resultado.X[least_infeas]

        menu, datos_dia = funciones_auxiliares.traducir_solucion(x, comida_basedatos)
        
        self.root.withdraw()
        
        VentanaMenu(tk.Toplevel(), menu, datos_dia, objetivo_calorico=calorias_ajustadas, ventana_preguntas=self.root)


    def volver(self):
        """Volver a ventana principal"""
        self.root.destroy()
        self.ventana_principal.deiconify()