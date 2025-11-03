# Módulos estándar de Python
import datetime
import json
import os
# Módulos para la Interfaz Gráfica de Usuario (GUI)
import tkinter as tk
from tkinter import ttk, messagebox
# ¡NUEVO! Módulo para el calendario
from tkcalendar import Calendar 

# --- CONFIGURACIÓN DE DATOS PERMANENTES (Sin cambios) ---
lista_cultivos = []
NOMBRE_ARCHIVO = "cultivos.json"

# --- 1. CLASE MODELO Y FUNCIONES DE GUARDADO (Sin cambios) ---

class Cultivo:
    """Clase base para guardar la información de un cultivo."""
    def __init__(self, nombre, fecha_siembra, fecha_cosecha):
        self.nombre = nombre
        self.fecha_siembra = fecha_siembra
        self.fecha_cosecha = fecha_cosecha

# El resto de las funciones 'validar_fecha', 'cargar_cultivos' y 'guardar_cultivos'
# son las mismas que en la versión anterior y NO se muestran aquí por brevedad,
# pero deben estar incluidas en el código final de tu archivo.
# Asegúrate de que las tienes copiadas de la Versión 3.0.

def validar_fecha(fecha_texto):
    """Convierte texto a un objeto de fecha (YYYY-MM-DD)."""
    try:
        return datetime.datetime.strptime(fecha_texto, '%Y-%m-%d').date()
    except ValueError:
        return None

def cargar_cultivos():
    # ... (cuerpo de la función cargar_cultivos)
    global lista_cultivos
    lista_cultivos = []
    
    if not os.path.exists(NOMBRE_ARCHIVO):
        return
    
    try:
        with open(NOMBRE_ARCHIVO, "r") as f:
            datos_cargados = json.load(f)
            for item in datos_cargados:
                siembra = validar_fecha(item["fecha_siembra"])
                cosecha = validar_fecha(item["fecha_cosecha"])
                
                if siembra and cosecha:
                    nuevo = Cultivo(item["nombre"], siembra, cosecha)
                    lista_cultivos.append(nuevo)
                    
    except Exception as e:
        messagebox.showerror("Error de Carga", f"Hubo un error al cargar el archivo: {e}")

def guardar_cultivos():
    # ... (cuerpo de la función guardar_cultivos)
    datos_para_json = []
    for cultivo in lista_cultivos:
        cultivo_dict = {
            "nombre": cultivo.nombre,
            "fecha_siembra": cultivo.fecha_siembra.isoformat(),
            "fecha_cosecha": cultivo.fecha_cosecha.isoformat()
        }
        datos_para_json.append(cultivo_dict)
        
    try:
        with open(NOMBRE_ARCHIVO, "w") as f:
            json.dump(datos_para_json, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error de Guardado", f"No se pudo guardar la información: {e}")

# --- 2. LA CLASE DE LA APLICACIÓN (TKINTER) ---

class AppCultivos(tk.Tk):
    # ... (método __init__ de la versión anterior)
    def __init__(self):
        super().__init__()
        self.title("Asistente de Cultivos (GUI con Calendario)")
        self.geometry("800x600") 
        
        cargar_cultivos() 
        self.crear_widgets()
        self.actualizar_lista_cultivos()
        self.revisar_cosechas_al_inicio()

    def crear_widgets(self):
        """¡MODIFICADO! Reemplazamos los Entry de fecha por botones y etiquetas."""
        
        # Configuramos el diseño (Sin cambios)
        self.columnconfigure(0, weight=1) 
        self.columnconfigure(1, weight=3) 
        self.rowconfigure(0, weight=1)
        
        # --- Marco Izquierdo (Para añadir un cultivo) ---
        frame_agregar = ttk.LabelFrame(self, text="🌱 Añadir Cultivo", padding="10")
        frame_agregar.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Variables para capturar la entrada de texto
        self.nombre_var = tk.StringVar()
        
        # ¡NUEVO! Variables para almacenar las fechas como texto (para mostrar)
        self.siembra_display_var = tk.StringVar(value="Seleccionar fecha...")
        self.cosecha_display_var = tk.StringVar(value="Seleccionar fecha...")
        
        # ¡NUEVO! Variables internas para guardar los objetos 'date' reales
        self.fecha_siembra_obj = None
        self.fecha_cosecha_obj = None
        
        # 1. Nombre (Sin cambios)
        ttk.Label(frame_agregar, text="Nombre:").pack(fill='x', pady=5)
        ttk.Entry(frame_agregar, textvariable=self.nombre_var).pack(fill='x', pady=2)
        
        # 2. Fecha de Siembra (¡MODIFICADO!)
        ttk.Label(frame_agregar, text="Fecha Siembra:").pack(fill='x', pady=5)
        ttk.Label(frame_agregar, textvariable=self.siembra_display_var, foreground='blue').pack(fill='x', pady=2)
        # El comando llama a mostrar_calendario y le pasa un identificador
        ttk.Button(frame_agregar, text="Elegir Fecha de Siembra", 
                   command=lambda: self.mostrar_calendario("siembra")).pack(fill='x', pady=5)
        
        # 3. Fecha de Cosecha (¡MODIFICADO!)
        ttk.Label(frame_agregar, text="Fecha Cosecha:").pack(fill='x', pady=5)
        ttk.Label(frame_agregar, textvariable=self.cosecha_display_var, foreground='blue').pack(fill='x', pady=2)
        ttk.Button(frame_agregar, text="Elegir Fecha de Cosecha", 
                   command=lambda: self.mostrar_calendario("cosecha")).pack(fill='x', pady=5)
        
        # Botón para añadir (Sin cambios)
        ttk.Button(frame_agregar, text="Añadir a la Lista", 
                   command=self.manejar_agregar_cultivo).pack(fill='x', pady=15)

        # ... (Resto de frame_mostrar: lista_tree, recordatorio_label)
        frame_mostrar = ttk.LabelFrame(self, text="🗓 Mis Cultivos", padding="10")
        frame_mostrar.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        frame_mostrar.rowconfigure(1, weight=1) 

        self.recordatorio_label = ttk.Label(frame_mostrar, text="Recordatorios aparecerán aquí.", font=('Helvetica', 12, 'bold'))
        self.recordatorio_label.pack(fill='x', pady=5)
        
        self.lista_tree = ttk.Treeview(frame_mostrar, columns=('siembra', 'cosecha'), show='headings')
        self.lista_tree.heading('siembra', text='Siembra')
        self.lista_tree.heading('cosecha', text='Cosecha')
        
        self.lista_tree.column('#0', width=200, anchor='w') 
        self.lista_tree.column('siembra', width=100, anchor='center')
        self.lista_tree.column('cosecha', width=100, anchor='center')
        
        self.lista_tree.pack(fill='both', expand=True, pady=10)

    # --- NUEVA FUNCIÓN: Abrir el Calendario ---
    def mostrar_calendario(self, campo_destino):
        """Abre una nueva ventana con el widget de calendario."""
        
        def set_fecha():
            """Función interna que se ejecuta al seleccionar una fecha en el calendario."""
            # Obtiene la fecha seleccionada en formato texto 'MM/DD/YY'
            fecha_str = cal.get_date() 
            # Convierte al formato deseado 'YYYY-MM-DD'
            fecha_obj = datetime.datetime.strptime(fecha_str, '%m/%d/%y').date()
            
            # Actualiza las variables de la aplicación principal
            if campo_destino == "siembra":
                self.fecha_siembra_obj = fecha_obj
                self.siembra_display_var.set(fecha_obj.strftime('%Y-%m-%d'))
            elif campo_destino == "cosecha":
                self.fecha_cosecha_obj = fecha_obj
                self.cosecha_display_var.set(fecha_obj.strftime('%Y-%m-%d'))
                
            # Cierra la ventana emergente del calendario
            top.destroy()
        
        # 1. Crear la ventana emergente
        top = tk.Toplevel(self)
        top.title(f"Seleccionar Fecha de {campo_destino.capitalize()}")
        
        # 2. Crear el widget de calendario
        cal = Calendar(top, 
                       selectmode='day', 
                       date_pattern='mm/dd/yy', # Formato interno del widget
                       year=datetime.date.today().year,
                       month=datetime.date.today().month,
                       day=datetime.date.today().day)
        cal.pack(padx=10, pady=10)
        
        # 3. Botón para confirmar la selección
        ttk.Button(top, text="Confirmar", command=set_fecha).pack(pady=10)


    def manejar_agregar_cultivo(self):
        """¡MODIFICADO! Usa las variables de objeto 'date' del calendario."""
        nombre = self.nombre_var.get().strip()

        # Usamos los objetos 'date' guardados por el calendario
        fecha_siembra = self.fecha_siembra_obj
        fecha_cosecha = self.fecha_cosecha_obj

        # 1. Validación de datos
        if not nombre:
            messagebox.showerror("Error", "El nombre debe ser completado.")
            return

        if not fecha_siembra or not fecha_cosecha:
            messagebox.showerror("Error", "Debe seleccionar ambas fechas usando los botones de calendario.")
            return

        if fecha_cosecha < fecha_siembra:
            messagebox.showerror("Error", "La fecha de cosecha no puede ser anterior a la siembra.")
            return

        # 2. Creación y guardado
        nuevo_cultivo = Cultivo(nombre, fecha_siembra, fecha_cosecha)
        lista_cultivos.append(nuevo_cultivo)
        guardar_cultivos()
        
        # 3. Actualizar la interfaz y limpiar campos
        self.actualizar_lista_cultivos()
        self.revisar_cosechas_al_inicio()
        
        self.nombre_var.set("")
        self.siembra_display_var.set("Seleccionar fecha...")
        self.cosecha_display_var.set("Seleccionar fecha...")
        self.fecha_siembra_obj = None
        self.fecha_cosecha_obj = None
        messagebox.showinfo("Éxito", f"'{nombre}' añadido y guardado correctamente.")

    # ... (El resto de funciones como actualizar_lista_cultivos y revisar_cosechas_al_inicio son iguales)
    def actualizar_lista_cultivos(self):
        # ... (cuerpo de la función)
        for item in self.lista_tree.get_children():
            self.lista_tree.delete(item)
            
        for cultivo in lista_cultivos:
            siembra_f = cultivo.fecha_siembra.strftime('%d-%m-%Y')
            cosecha_f = cultivo.fecha_cosecha.strftime('%d-%m-%Y')
            self.lista_tree.insert('', tk.END, text=cultivo.nombre, values=(siembra_f, cosecha_f))

    def revisar_cosechas_al_inicio(self):
        # ... (cuerpo de la función)
        hoy = datetime.date.today()
        cosechas_listas = []
        
        for cultivo in lista_cultivos:
            if cultivo.fecha_cosecha <= hoy:
                cosechas_listas.append(cultivo.nombre)
                
        if cosechas_listas:
            mensaje = "¡ATENCIÓN! Cosecha Pendiente:\n" + ", ".join(cosechas_listas)
            self.recordatorio_label.config(text=mensaje, foreground='red')
            messagebox.showwarning("¡Recordatorio de Cosecha!", mensaje)
        else:
            self.recordatorio_label.config(text="Todo al día. Ninguna cosecha lista hoy.", foreground='green')

# --- INICIO DE LA APLICACIÓN (Sin cambios) ---
if __name__ == "__main__":
    app = AppCultivos()
    app.mainloop()
