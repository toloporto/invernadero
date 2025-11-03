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
    """Clase base para guardar la información de un cultivo, incluyendo datos financieros y de ubicación."""
    def __init__(self, nombre, fecha_siembra, fecha_cosecha, notas="", zona="", precio_compra=0.0, precio_venta=0.0):
        self.nombre = nombre
        self.fecha_siembra = fecha_siembra
        self.fecha_cosecha = fecha_cosecha
        self.notas = notas
        self.zona = zona 
        self.precio_compra = precio_compra 
        self.precio_venta = precio_venta 

# --- 2. FUNCIONES DE MANEJO DE ARCHIVOS Y DATOS ---

def validar_fecha(fecha_texto):
    """Convierte texto a un objeto de fecha (YYYY-MM-DD)."""
    try:
        return datetime.datetime.strptime(fecha_texto, '%Y-%m-%d').date()
    except ValueError:
        return None

def cargar_cultivos():
    """Carga los cultivos desde el archivo JSON, manejando nuevos campos."""
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
                zona = item.get("zona", "") 
                # Aseguramos que sean floats para operaciones matemáticas
                precio_compra = float(item.get("precio_compra", 0.0))
                precio_venta = float(item.get("precio_venta", 0.0))
                
                if siembra and cosecha:
                    nuevo = Cultivo(item["nombre"], siembra, cosecha, notas, zona, precio_compra, precio_venta)
                    lista_cultivos.append(nuevo)
                    
    except Exception as e:
        messagebox.showerror("Error de Carga", f"Hubo un error al cargar el archivo: {e}")

def guardar_cultivos():
    """Guarda la lista de cultivos en el archivo JSON, incluyendo todos los campos."""
    datos_para_json = []
    for cultivo in lista_cultivos:
        cultivo_dict = {
            "nombre": cultivo.nombre,
            "fecha_siembra": cultivo.fecha_siembra.isoformat(),
            "fecha_cosecha": cultivo.fecha_cosecha.isoformat(),
            "notas": cultivo.notas,
            "zona": cultivo.zona, 
            "precio_compra": cultivo.precio_compra,
            "precio_venta": cultivo.precio_venta 
        }
        datos_para_json.append(cultivo_dict)
        
    try:
        with open(NOMBRE_ARCHIVO, "w") as f:
            json.dump(datos_para_json, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error de Guardado", f"No se pudo guardar la información: {e}")


# --- 3. LA CLASE DE LA APLICACIÓN (TKINTER) ---

class AppCultivos(tk.Tk):
    """Clase principal de la aplicación GUI."""
    def __init__(self):
        super().__init__()
        self.title("Asistente de Cultivos (Completo)")
        self.geometry("950x700") 
        
        self.cultivo_seleccionado_indice = None
        
        self.configurar_estilos() 
        
        cargar_cultivos() 
        self.crear_widgets()
        self.actualizar_lista_cultivos()
        self.revisar_cosechas_al_inicio()
        
    def configurar_estilos(self):
        """Define los temas, estilos, tags y fuentes de la aplicación."""
        
        style = ttk.Style(self)
        
        try:
            style.theme_use('clam') 
        except tk.TclError:
            pass 

        # Colores generales
        self.configure(background='#F5F5F5')
        style.configure('TLabel', background='#F5F5F5', font=('Helvetica', 10))
        style.configure('TLabelframe', background='#F5F5F5')
        style.configure('TLabelframe.Label', font=('Helvetica', 12, 'bold'), foreground='#38761D')

        # Treeview Styles
        style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'), background='#E0E0E0', foreground='#333333')
        style.map('Treeview', background=[('selected', '#C9DFFF')]) 
        
        # Tags de color para las filas del Treeview (Reporte)
        self.lista_tree = ttk.Treeview(self) 
        self.lista_tree.tag_configure('cosecha_pasada', background='#F0F0F0', foreground='#888888') 
        self.lista_tree.tag_configure('cosecha_hoy', background='#FFEB99', foreground='#9C6500', font=('Helvetica', 10, 'bold'))
        self.lista_tree.tag_configure('cosecha_futura', background='#D9EAD3', foreground='#38761D')

        # Botones y Alertas
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
        self.zona_var.set("")
        self.compra_var.set("")
        self.venta_var.set("")
        self.fecha_siembra_obj = None
        self.fecha_cosecha_obj = None
        
        self.btn_guardar.config(text="Añadir a la Lista", style='Principal.TButton')
        self.cultivo_seleccionado_indice = None
        
    def crear_widgets(self):
        """Define la disposición de todos los elementos, incluyendo el panel de totales."""
        
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
        self.zona_var = tk.StringVar()
        self.compra_var = tk.StringVar()
        self.venta_var = tk.StringVar()

        # Nombre
        ttk.Label(frame_agregar, text="Nombre:").pack(fill='x', pady=2)
        ttk.Entry(frame_agregar, textvariable=self.nombre_var).pack(fill='x', pady=1)

        # Zona (Combobox)
        ttk.Label(frame_agregar, text="Zona de Cultivo:").pack(fill='x', pady=2)
        zonas_posibles = ["Zona A", "Zona B", "Zona C", "Zona D", "Invernadero", "Exterior"]
        self.zona_combobox = ttk.Combobox(frame_agregar, textvariable=self.zona_var, values=zonas_posibles, state="readonly")
        self.zona_combobox.pack(fill='x', pady=1)

        # Fechas
        ttk.Label(frame_agregar, text="Fecha Siembra:").pack(fill='x', pady=2)
        ttk.Label(frame_agregar, textvariable=self.siembra_display_var, foreground='#38761D').pack(fill='x', pady=1)
        ttk.Button(frame_agregar, text="Elegir Fecha de Siembra", command=lambda: self.mostrar_calendario("siembra")).pack(fill='x', pady=2)
        
        ttk.Label(frame_agregar, text="Fecha Cosecha:").pack(fill='x', pady=2)
        ttk.Label(frame_agregar, textvariable=self.cosecha_display_var, foreground='#38761D').pack(fill='x', pady=1)
        ttk.Button(frame_agregar, text="Elegir Fecha de Cosecha", command=lambda: self.mostrar_calendario("cosecha")).pack(fill='x', pady=2)

        # Precios (Frame para layout en dos columnas)
        frame_precios = ttk.Frame(frame_agregar)
        frame_precios.pack(fill='x', pady=5)
        
        frame_precios.columnconfigure(0, weight=1)
        ttk.Label(frame_precios, text="Costo (€):").grid(row=0, column=0, sticky='w', padx=2)
        ttk.Entry(frame_precios, textvariable=self.compra_var, width=15).grid(row=1, column=0, sticky='ew', padx=2)
        
        frame_precios.columnconfigure(1, weight=1)
        ttk.Label(frame_precios, text="Venta Est. (€):").grid(row=0, column=1, sticky='w', padx=2)
        ttk.Entry(frame_precios, textvariable=self.venta_var, width=15).grid(row=1, column=1, sticky='ew', padx=2)

        # Notas y Botones
        ttk.Label(frame_agregar, text="Notas (Opcional):").pack(fill='x', pady=2)
        ttk.Entry(frame_agregar, textvariable=self.notas_var).pack(fill='x', pady=1)
        
        self.btn_guardar = ttk.Button(frame_agregar, text="Añadir a la Lista", 
                                     command=self.manejar_agregar_o_editar, style='Principal.TButton')
        self.btn_guardar.pack(fill='x', pady=10)
        
        ttk.Button(frame_agregar, text="Limpiar Campos", command=self.limpiar_campos).pack(fill='x', pady=2)


        # --- Marco Derecho (Lista, Reporte y Botones) ---
        frame_mostrar = ttk.LabelFrame(self, text="🗓 Mis Cultivos", padding="10")
        frame_mostrar.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # 1. Panel de Resumen Financiero
        frame_totales = ttk.LabelFrame(frame_mostrar, text="💸 Resumen Financiero Potencial", padding="5")
        frame_totales.pack(fill='x', pady=5)
        
        # Configuración interna del frame de totales para centrar/distribuir
        frame_totales.columnconfigure(0, weight=1)
        frame_totales.columnconfigure(1, weight=1)
        frame_totales.columnconfigure(2, weight=1)
        
        # Etiquetas (Guardamos referencias para poder actualizarlas)
        ttk.Label(frame_totales, text="Costo Total:").grid(row=0, column=0, sticky='w')
        self.label_costo_total = ttk.Label(frame_totales, text="€0.00", font=('Helvetica', 10, 'bold'), foreground='#990000') 
        self.label_costo_total.grid(row=1, column=0, sticky='w')

        ttk.Label(frame_totales, text="Venta Estimada Total:").grid(row=0, column=1, sticky='w')
        self.label_venta_total = ttk.Label(frame_totales, text="€0.00", font=('Helvetica', 10, 'bold'), foreground='#1E8449')
        self.label_venta_total.grid(row=1, column=1, sticky='w')
        
        ttk.Label(frame_totales, text="Margen Potencial:").grid(row=0, column=2, sticky='w')
        self.label_margen_total = ttk.Label(frame_totales, text="€0.00", font=('Helvetica', 10, 'bold'))
        self.label_margen_total.grid(row=1, column=2, sticky='w')

        # 2. Recordatorio y Lista
        self.recordatorio_label = ttk.Label(frame_mostrar, text="Recordatorios aparecerán aquí.", font=('Helvetica', 12, 'bold'), style='Alerta.TLabel')
        self.recordatorio_label.pack(fill='x', pady=5)
        
        # Aseguramos que la lista se expanda
        frame_mostrar.rowconfigure(2, weight=1) 
        
        # Treeview con todas las columnas
        self.lista_tree = ttk.Treeview(frame_mostrar, columns=('zona', 'siembra', 'cosecha', 'notas', 'compra', 'venta', 'margen', 'faltan'), show='headings')
        
        self.lista_tree.heading('#0', text='Cultivo')
        self.lista_tree.heading('zona', text='Zona') 
        self.lista_tree.heading('siembra', text='Siembra')
        self.lista_tree.heading('cosecha', text='Cosecha')
        self.lista_tree.heading('notas', text='Notas')
        self.lista_tree.heading('compra', text='Costo') 
        self.lista_tree.heading('venta', text='Venta') 
        self.lista_tree.heading('margen', text='Margen') 
        self.lista_tree.heading('faltan', text='Faltan')
        
        # Ajustamos anchos
        self.lista_tree.column('#0', width=120, anchor='w')
        self.lista_tree.column('zona', width=70, anchor='center')
        self.lista_tree.column('siembra', width=70, anchor='center')
        self.lista_tree.column('cosecha', width=70, anchor='center')
        self.lista_tree.column('notas', width=100, anchor='w')
        self.lista_tree.column('compra', width=60, anchor='center')
        self.lista_tree.column('venta', width=60, anchor='center')
        self.lista_tree.column('margen', width=60, anchor='center')
        self.lista_tree.column('faltan', width=100, anchor='center')
        self.lista_tree.pack(fill='both', expand=True, pady=10)

        # Botones de lista
        frame_botones_lista = ttk.Frame(frame_mostrar)
        frame_botones_lista.pack(fill='x', pady=5)
        
        ttk.Button(frame_botones_lista, text="❌ Eliminar", command=self.manejar_eliminar_cultivo).pack(side='left', expand=True, fill='x', padx=5)
        ttk.Button(frame_botones_lista, text="✏️ Editar Seleccionado", command=self.manejar_editar_cultivo).pack(side='right', expand=True, fill='x', padx=5)


    # --- 4. FUNCIONES CONECTADAS A LA INTERFAZ ---
    
    def calcular_totales_financieros(self):
        """
        Calcula el costo total y la venta potencial total de todos los cultivos activos.
        Retorna una tupla (total_compra, total_venta).
        """
        total_compra = 0.0
        total_venta = 0.0
        
        for cultivo in lista_cultivos:
            total_compra += cultivo.precio_compra
            total_venta += cultivo.precio_venta
            
        return total_compra, total_venta

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
        zona = self.zona_var.get().strip()

        # Validación y conversión de Precios
        try:
            precio_compra = float(self.compra_var.get().strip() or 0.0)
            precio_venta = float(self.venta_var.get().strip() or 0.0)
        except ValueError:
            messagebox.showerror("Error", "Los campos de Costo y Venta deben ser números válidos.")
            return

        # 1. Validación de campos obligatorios
        if not nombre or not fecha_siembra or not fecha_cosecha:
            messagebox.showerror("Error", "Debe completar el nombre y seleccionar ambas fechas.")
            return
        if fecha_cosecha < fecha_siembra:
            messagebox.showerror("Error", "La fecha de cosecha no puede ser anterior a la siembra.")
            return

        # 2. Lógica de Adición o Edición
        if self.cultivo_seleccionado_indice is None:
            # MODO AÑADIR
            nuevo_cultivo = Cultivo(nombre, fecha_siembra, fecha_cosecha, notas, zona, precio_compra, precio_venta)
            lista_cultivos.append(nuevo_cultivo)
            msg = f"'{nombre}' añadido con éxito."
        else:
            # MODO EDITAR
            indice = self.cultivo_seleccionado_indice
            cultivo_a_editar = lista_cultivos[indice]
            
            # Actualizamos las propiedades
            cultivo_a_editar.nombre = nombre
            cultivo_a_editar.fecha_siembra = fecha_siembra
            cultivo_a_editar.fecha_cosecha = fecha_cosecha
            cultivo_a_editar.notas = notas
            cultivo_a_editar.zona = zona
            cultivo_a_editar.precio_compra = precio_compra
            cultivo_a_editar.precio_venta = precio_venta
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
        self.zona_var.set(cultivo_a_editar.zona)
        # Formatear a dos decimales
        self.compra_var.set(f"{cultivo_a_editar.precio_compra:.2f}")
        self.venta_var.set(f"{cultivo_a_editar.precio_venta:.2f}")
        
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
        """Refresca los datos mostrados en la lista Treeview y actualiza el panel de totales."""
        
        # 1. Limpiar lista
        for item in self.lista_tree.get_children():
            self.lista_tree.delete(item)
            
        # 2. Llenar lista
        for i, cultivo in enumerate(lista_cultivos):
            siembra_f = cultivo.fecha_siembra.strftime('%d-%m-%Y')
            cosecha_f = cultivo.fecha_cosecha.strftime('%d-%m-%Y')
            
            tiempo_restante = self.calcular_tiempo_restante(cultivo.fecha_cosecha) 
            margen = cultivo.precio_venta - cultivo.precio_compra
            
            # Lógica de color condicional
            hoy = datetime.date.today()
            if cultivo.fecha_cosecha < hoy:
                tag = 'cosecha_pasada'
            elif cultivo.fecha_cosecha == hoy:
                tag = 'cosecha_hoy'
            else:
                tag = 'cosecha_futura'
                
            # Insertamos la fila con todos los valores
            self.lista_tree.insert('', tk.END, iid=str(i), 
                                   text=cultivo.nombre, 
                                   values=(cultivo.zona, siembra_f, cosecha_f, cultivo.notas, 
                                           f"€{cultivo.precio_compra:.2f}", 
                                           f"€{cultivo.precio_venta:.2f}", 
                                           f"€{margen:.2f}", 
                                           tiempo_restante),
                                   tags=(tag,))

        # 3. Actualizar Reporte Financiero Global
        total_compra, total_venta = self.calcular_totales_financieros()
        total_margen = total_venta - total_compra
        
        self.label_costo_total.config(text=f"€{total_compra:.2f}")
        self.label_venta_total.config(text=f"€{total_venta:.2f}")
        
        self.label_margen_total.config(text=f"€{total_margen:.2f}")
        
        # Aplicar color al margen total
        if total_margen < 0:
            self.label_margen_total.config(foreground='#990000') # Rojo si hay pérdida
        elif total_margen > 0:
            self.label_margen_total.config(foreground='#1E8449') # Verde si hay ganancia
        else:
            self.label_margen_total.config(foreground='#333333')


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
