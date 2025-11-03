# --- IMPORTS ---
import datetime
import json
import os
# Módulos para la Interfaz Gráfica de Usuario (GUI)
import tkinter as tk
from tkinter import ttk, messagebox
# Módulo para el calendario
from tkcalendar import Calendar 

# --- CONFIGURACIÓN DE DATOS PERMANENTES ---
lista_cultivos = []
NOMBRE_ARCHIVO = "cultivos.json"

# --- 1. CLASE MODELO (LA LÓGICA DE NEGOCIO) ---

class Cultivo:
    """Clase base para guardar la información de un cultivo."""
    def __init__(self, nombre, fecha_siembra, fecha_cosecha, notas=""):
        self.nombre = nombre
        self.fecha_siembra = fecha_siembra
        self.fecha_cosecha = fecha_cosecha
        self.notas = notas

# --- 2. FUNCIONES DE MANEJO DE ARCHIVOS Y DATOS ---

def validar_fecha(fecha_texto):
    """Convierte texto a un objeto de fecha (YYYY-MM-DD)."""
    try:
        return datetime.datetime.strptime(fecha_texto, '%Y-%m-%d').date()
    except ValueError:
        return None

def cargar_cultivos():
    """Carga los cultivos desde el archivo JSON."""
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
                notas = item.get("notas", "")
                
                if siembra and cosecha:
                    nuevo = Cultivo(item["nombre"], siembra, cosecha, notas)
                    lista_cultivos.append(nuevo)
                    
    except Exception as e:
        messagebox.showerror("Error de Carga", f"Hubo un error al cargar el archivo: {e}")

def guardar_cultivos():
    """Guarda la lista de cultivos en el archivo JSON."""
    datos_para_json = []
    for cultivo in lista_cultivos:
        cultivo_dict = {
            "nombre": cultivo.nombre,
            "fecha_siembra": cultivo.fecha_siembra.isoformat(),
            "fecha_cosecha": cultivo.fecha_cosecha.isoformat(),
            "notas": cultivo.notas
        }
        datos_para_json.append(cultivo_dict)
        
    try:
        with open(NOMBRE_ARCHIVO, "w") as f:
            json.dump(datos_para_json, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error de Guardado", f"No se pudo guardar la información: {e}")


# --- 3. LA CLASE DE LA APLICACIÓN (TKINTER) ---

class AppCultivos(tk.Tk):
    """Clase principal de la aplicación GUI con estilos personalizados."""
    def __init__(self):
        super().__init__()
        self.title("Asistente de Cultivos (Estilo Moderno)")
        self.geometry("850x650") 
        
        self.cultivo_seleccionado_indice = None
        
        # Configuración de estilos y temas
        self.configurar_estilos()
        
        cargar_cultivos() 
        self.crear_widgets()
        self.actualizar_lista_cultivos()
        self.revisar_cosechas_al_inicio()
        
    def configurar_estilos(self):
        """Define los temas, estilos y fuentes de la aplicación, incluyendo tags para el Treeview."""
        
        style = ttk.Style(self)
        
        # 1. Aplicar un Tema Base
        try:
            style.theme_use('clam') 
        except tk.TclError:
            pass 

        # 2. Configurar colores de fondo y etiquetas generales
        self.configure(background='#F5F5F5')
        style.configure('TLabel', background='#F5F5F5', font=('Helvetica', 10))
        style.configure('TLabelframe', background='#F5F5F5')
        style.configure('TLabelframe.Label', font=('Helvetica', 12, 'bold'), foreground='#38761D')

        # 3. Configurar la Lista (Treeview)
        style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'), background='#E0E0E0', foreground='#333333')
        style.map('Treeview', background=[('selected', '#C9DFFF')]) 
        
        # Tags (etiquetas) de color para las filas del Treeview (Reporte)
        self.lista_tree = ttk.Treeview(self) # Instanciar para que tag_configure funcione
        # Cosecha Pasada (Gris claro y texto atenuado)
        self.lista_tree.tag_configure('cosecha_pasada', background='#F0F0F0', foreground='#888888') 
        # Cosecha Hoy (Amarillo/Naranja de alerta)
        self.lista_tree.tag_configure('cosecha_hoy', background='#FFEB99', foreground='#9C6500', font=('Helvetica', 10, 'bold'))
        # Cosecha Futura (Verde suave)
        self.lista_tree.tag_configure('cosecha_futura', background='#D9EAD3', foreground='#38761D')

        # 4. Configurar Alertas de Recordatorio y Botones
        style.configure('Alerta.TLabel', foreground='red', font=('Helvetica', 12, 'bold'), background='#FFF2CC', padding=5, borderwidth=1, relief="solid")
        style.configure('TButton', font=('Helvetica', 10, 'bold'), foreground='#FFFFFF', background='#6AA84F') 
        style.map('TButton', background=[('active', '#8FBC8F')]) 
        
        style.configure('Principal.TButton', font=('Helvetica', 11, 'bold'), background='#1E8449')
        style.map('Principal.TButton', background=[('active', '#2ECC71')])

    def limpiar_campos(self):
        """Función auxiliar para limpiar la interfaz y salir del modo edición."""
        self.nombre_var.set("")
        self.siembra_display_var.set("Seleccionar fecha...")
        self.cosecha_display_var.set("Seleccionar fecha...")
        self.notas_var.set("") 
        self.fecha_siembra_obj = None
        self.fecha_cosecha_obj = None
        
        self.btn_guardar.config(text="Añadir a la Lista", style='Principal.TButton')
        self.cultivo_seleccionado_indice = None
        
    def crear_widgets(self):
        """Define la disposición de todos los elementos."""
        
        # Configuración del diseño
        self.columnconfigure(0, weight=1) 
        self.columnconfigure(1, weight=3) 
        self.rowconfigure(0, weight=1)
        
        # --- Marco Izquierdo (Añadir/Editar Cultivo) ---
        frame_agregar = ttk.LabelFrame(self, text="🌱 Añadir/Editar Cultivo", padding="10")
        frame_agregar.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.nombre_var = tk.StringVar()
        self.siembra_display_var = tk.StringVar(value="Seleccionar fecha...")
        self.cosecha_display_var = tk.StringVar(value="Seleccionar fecha...")
        self.fecha_siembra_obj = None
        self.fecha_cosecha_obj = None
        self.notas_var = tk.StringVar()
        
        ttk.Label(frame_agregar, text="Nombre:").pack(fill='x', pady=5)
        ttk.Entry(frame_agregar, textvariable=self.nombre_var).pack(fill='x', pady=2)
        
        ttk.Label(frame_agregar, text="Fecha Siembra:").pack(fill='x', pady=5)
        ttk.Label(frame_agregar, textvariable=self.siembra_display_var, foreground='#38761D').pack(fill='x', pady=2)
        ttk.Button(frame_agregar, text="Elegir Fecha de Siembra", 
                   command=lambda: self.mostrar_calendario("siembra")).pack(fill='x', pady=5)
        
        ttk.Label(frame_agregar, text="Fecha Cosecha:").pack(fill='x', pady=5)
        ttk.Label(frame_agregar, textvariable=self.cosecha_display_var, foreground='#38761D').pack(fill='x', pady=2)
        ttk.Button(frame_agregar, text="Elegir Fecha de Cosecha", 
                   command=lambda: self.mostrar_calendario("cosecha")).pack(fill='x', pady=5)

        ttk.Label(frame_agregar, text="Notas (Opcional):").pack(fill='x', pady=5)
        ttk.Entry(frame_agregar, textvariable=self.notas_var).pack(fill='x', pady=2)
        
        self.btn_guardar = ttk.Button(frame_agregar, text="Añadir a la Lista", 
                                     command=self.manejar_agregar_o_editar, style='Principal.TButton')
        self.btn_guardar.pack(fill='x', pady=15)
        
        ttk.Button(frame_agregar, text="Limpiar Campos", command=self.limpiar_campos).pack(fill='x', pady=5)


        # --- Marco Derecho (Lista y Botones) ---
        frame_mostrar = ttk.LabelFrame(self, text="🗓 Mis Cultivos", padding="10")
        frame_mostrar.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        frame_mostrar.rowconfigure(1, weight=1) 

        self.recordatorio_label = ttk.Label(frame_mostrar, text="Recordatorios aparecerán aquí.", font=('Helvetica', 12, 'bold'), style='Alerta.TLabel')
        self.recordatorio_label.pack(fill='x', pady=5)
        
        # Re-instanciar Treeview con columnas de reporte
        self.lista_tree = ttk.Treeview(frame_mostrar, columns=('siembra', 'cosecha', 'notas', 'faltan'), show='headings')
        self.lista_tree.heading('siembra', text='Siembra')
        self.lista_tree.heading('cosecha', text='Cosecha')
        self.lista_tree.heading('notas', text='Notas')
        self.lista_tree.heading('faltan', text='Faltan')
        
        self.lista_tree.column('#0', width=130, anchor='w')
        self.lista_tree.column('siembra', width=80, anchor='center')
        self.lista_tree.column('cosecha', width=80, anchor='center')
        self.lista_tree.column('notas', width=120, anchor='w')
        self.lista_tree.column('faltan', width=100, anchor='center')
        self.lista_tree.pack(fill='both', expand=True, pady=10)

        # Marco para los botones de lista
        frame_botones_lista = ttk.Frame(frame_mostrar)
        frame_botones_lista.pack(fill='x', pady=5)
        
        ttk.Button(frame_botones_lista, text="❌ Eliminar", 
                   command=self.manejar_eliminar_cultivo).pack(side='left', expand=True, fill='x', padx=5)

        ttk.Button(frame_botones_lista, text="✏️ Editar Seleccionado", 
                   command=self.manejar_editar_cultivo).pack(side='right', expand=True, fill='x', padx=5)

    # --- 4. FUNCIONES CONECTADAS A LA INTERFAZ ---
    
    def calcular_tiempo_restante(self, fecha_objetivo):
        """Calcula el tiempo restante entre hoy y la fecha de cosecha."""
        hoy = datetime.date.today()
        
        if fecha_objetivo < hoy:
            dias = (hoy - fecha_objetivo).days
            return f"¡COSECHADO HACE {dias} DÍAS!"
        elif fecha_objetivo == hoy:
            return "¡COSECHA HOY!"
        else:
            dias = (fecha_objetivo - hoy).days
            return f"{dias} Días Restantes"

    def mostrar_calendario(self, campo_destino):
        """Abre una nueva ventana con el widget de calendario."""
        
        def set_fecha():
            fecha_str = cal.get_date() 
            fecha_obj = datetime.datetime.strptime(fecha_str, '%m/%d/%y').date()
            
            if campo_destino == "siembra":
                self.fecha_siembra_obj = fecha_obj
                self.siembra_display_var.set(fecha_obj.strftime('%Y-%m-%d'))
            elif campo_destino == "cosecha":
                self.fecha_cosecha_obj = fecha_obj
                self.cosecha_display_var.set(fecha_obj.strftime('%Y-%m-%d'))
                
            top.destroy()
        
        top = tk.Toplevel(self)
        top.title(f"Seleccionar Fecha de {campo_destino.capitalize()}")
        
        cal = Calendar(top, 
                       selectmode='day', 
                       date_pattern='mm/dd/yy',
                       year=datetime.date.today().year,
                       month=datetime.date.today().month,
                       day=datetime.date.today().day)
        cal.pack(padx=10, pady=10)
        
        ttk.Button(top, text="Confirmar", command=set_fecha).pack(pady=10)
        
    def manejar_agregar_o_editar(self):
        """Añade un nuevo cultivo O guarda los cambios del cultivo seleccionado."""
        nombre = self.nombre_var.get().strip()
        fecha_siembra = self.fecha_siembra_obj
        fecha_cosecha = self.fecha_cosecha_obj
        notas = self.notas_var.get().strip()

        # 1. Validación
        if not nombre or not fecha_siembra or not fecha_cosecha:
            messagebox.showerror("Error", "Debe completar el nombre y seleccionar ambas fechas.")
            return
        if fecha_cosecha < fecha_siembra:
            messagebox.showerror("Error", "La fecha de cosecha no puede ser anterior a la siembra.")
            return

        # 2. Lógica de Adición o Edición
        if self.cultivo_seleccionado_indice is None:
            # MODO AÑADIR
            nuevo_cultivo = Cultivo(nombre, fecha_siembra, fecha_cosecha, notas)
            lista_cultivos.append(nuevo_cultivo)
            msg = f"'{nombre}' añadido con éxito."
        else:
            # MODO EDITAR
            indice = self.cultivo_seleccionado_indice
            cultivo_a_editar = lista_cultivos[indice]
            
            cultivo_a_editar.nombre = nombre
            cultivo_a_editar.fecha_siembra = fecha_siembra
            cultivo_a_editar.fecha_cosecha = fecha_cosecha
            cultivo_a_editar.notas = notas
            msg = f"'{nombre}' actualizado con éxito."
            
        # 3. Guardar, actualizar y limpiar
        guardar_cultivos()
        self.actualizar_lista_cultivos()
        self.revisar_cosechas_al_inicio()
        self.limpiar_campos()
        messagebox.showinfo("Éxito", msg)


    def manejar_editar_cultivo(self):
        """Carga los datos del cultivo seleccionado en los campos de entrada."""
        seleccion_id = self.lista_tree.selection()
        
        if not seleccion_id:
            messagebox.showwarning("Advertencia", "Selecciona un cultivo para editar.")
            return

        try:
            indice = int(self.lista_tree.focus())
        except ValueError:
            messagebox.showerror("Error", "Error al identificar el cultivo.")
            return

        # 1. Cargar datos del objeto en los campos
        cultivo_a_editar = lista_cultivos[indice]
        
        self.nombre_var.set(cultivo_a_editar.nombre)
        self.notas_var.set(cultivo_a_editar.notas)
        
        self.fecha_siembra_obj = cultivo_a_editar.fecha_siembra
        self.siembra_display_var.set(cultivo_a_editar.fecha_siembra.strftime('%Y-%m-%d'))
        self.fecha_cosecha_obj = cultivo_a_editar.fecha_cosecha
        self.cosecha_display_var.set(cultivo_a_editar.fecha_cosecha.strftime('%Y-%m-%d'))
        
        # 2. Entrar en modo edición
        self.cultivo_seleccionado_indice = indice
        self.btn_guardar.config(text=f"✏️ Guardar Cambios (Editando {cultivo_a_editar.nombre})", style='Principal.TButton')
        messagebox.showinfo("Modo Edición", f"Datos de '{cultivo_a_editar.nombre}' cargados. Haz tus cambios y pulsa 'Guardar Cambios'.")


    def manejar_eliminar_cultivo(self):
        """Función que elimina el cultivo seleccionado de la lista."""
        
        seleccion_id = self.lista_tree.selection()
        if not seleccion_id:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un cultivo de la lista para eliminar.")
            return

        try:
            indice_a_eliminar = int(self.lista_tree.focus()) 
        except ValueError:
            messagebox.showerror("Error", "Error al identificar el cultivo. Intenta seleccionar otra vez.")
            return

        nombre_cultivo = lista_cultivos[indice_a_eliminar].nombre
        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de que quieres eliminar '{nombre_cultivo}' de tus cultivos?"
        )

        if confirmar:
            del lista_cultivos[indice_a_eliminar] 
            guardar_cultivos()
            self.actualizar_lista_cultivos()
            self.revisar_cosechas_al_inicio()
            self.limpiar_campos() 
            messagebox.showinfo("Éxito", f"El cultivo '{nombre_cultivo}' ha sido eliminado.")

    def actualizar_lista_cultivos(self):
        """Refresca los datos mostrados en la lista Treeview, aplicando color."""
        
        for item in self.lista_tree.get_children():
            self.lista_tree.delete(item)
            
        for i, cultivo in enumerate(lista_cultivos):
            siembra_f = cultivo.fecha_siembra.strftime('%d-%m-%Y')
            cosecha_f = cultivo.fecha_cosecha.strftime('%d-%m-%Y')
            
            tiempo_restante = self.calcular_tiempo_restante(cultivo.fecha_cosecha) 
            
            # Lógica de color condicional
            hoy = datetime.date.today()
            if cultivo.fecha_cosecha < hoy:
                tag = 'cosecha_pasada'
            elif cultivo.fecha_cosecha == hoy:
                tag = 'cosecha_hoy'
            else:
                tag = 'cosecha_futura'
                
            # Insertamos la fila usando el Tag
            self.lista_tree.insert('', tk.END, iid=str(i), 
                                   text=cultivo.nombre, 
                                   values=(siembra_f, cosecha_f, cultivo.notas, tiempo_restante),
                                   tags=(tag,))

    def revisar_cosechas_al_inicio(self):
        """Revisa y muestra una alerta si hay cultivos listos hoy."""
        hoy = datetime.date.today()
        cosechas_listas = []
        
        for cultivo in lista_cultivos:
            if cultivo.fecha_cosecha <= hoy:
                cosechas_listas.append(cultivo.nombre)
                
        if cosechas_listas:
            mensaje = "¡ATENCIÓN! Cosecha Pendiente:\n" + ", ".join(cosechas_listas)
            self.recordatorio_label.config(text=mensaje, style='Alerta.TLabel')
            messagebox.showwarning("¡Recordatorio de Cosecha!", mensaje)
        else:
            self.recordatorio_label.config(text="Todo al día. Ninguna cosecha lista hoy.", style='TLabel', foreground='#38761D')


# --- 5. INICIO DE LA APLICACIÓN ---
if __name__ == "__main__":
    app = AppCultivos()
    app.mainloop()
               
