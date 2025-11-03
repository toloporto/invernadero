# ... (Módulos estándar de Python e imports de Tkinter/tkcalendar)

# --- 1. CLASE MODELO (LA LÓGICA DE NEGOCIO) ---

class Cultivo:
    """Clase base para guardar la información de un cultivo."""
    def __init__(self, nombre, fecha_siembra, fecha_cosecha, notas=""): #! CAMBIO NOTAS: Nuevo argumento
        self.nombre = nombre
        self.fecha_siembra = fecha_siembra
        self.fecha_cosecha = fecha_cosecha
        self.notas = notas #! CAMBIO NOTAS: Nuevo atributo

# --- 2. FUNCIONES DE MANEJO DE ARCHIVOS Y DATOS ---

# ... (validar_fecha se mantiene igual)

def cargar_cultivos():
    """Carga los cultivos desde el archivo JSON."""
    global lista_cultivos
    lista_cultivos = [] 
    # ... (cuerpo de la función)
    if not os.path.exists(NOMBRE_ARCHIVO):
        return
    try:
        with open(NOMBRE_ARCHIVO, "r") as f:
            datos_cargados = json.load(f)
            for item in datos_cargados:
                siembra = validar_fecha(item["fecha_siembra"])
                cosecha = validar_fecha(item["fecha_cosecha"])
                # Aseguramos que 'notas' exista, si no, es cadena vacía (para compatibilidad con archivos viejos)
                notas = item.get("notas", "") #! CAMBIO NOTAS: Leemos el campo 'notas'
                
                if siembra and cosecha:
                    # ¡Pasamos el nuevo argumento 'notas'!
                    nuevo = Cultivo(item["nombre"], siembra, cosecha, notas) #! CAMBIO NOTAS
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
            "notas": cultivo.notas #! CAMBIO NOTAS: Guardamos el campo 'notas'
        }
        datos_para_json.append(cultivo_dict)
        
    # ... (Resto de la lógica de guardado)
    try:
        with open(NOMBRE_ARCHIVO, "w") as f:
            json.dump(datos_para_json, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error de Guardado", f"No se pudo guardar la información: {e}")


# --- 3. LA CLASE DE LA APLICACIÓN (TKINTER) ---
class AppCultivos(tk.Tk):
    # ... (__init__ igual)
    
    def limpiar_campos(self):
        """Función auxiliar para limpiar la interfaz. #! CAMBIO NOTAS"""
        self.nombre_var.set("")
        self.siembra_display_var.set("Seleccionar fecha...")
        self.cosecha_display_var.set("Seleccionar fecha...")
        self.notas_var.set("") #! CAMBIO NOTAS: Limpiamos el campo de notas
        self.fecha_siembra_obj = None
        self.fecha_cosecha_obj = None
        self.btn_guardar.config(text="Añadir a la Lista")
        self.cultivo_seleccionado_indice = None 
        
    def crear_widgets(self):
        """Define la disposición de todos los elementos. #! CAMBIO NOTAS"""
        # ... (Configuración de grid)
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
        self.notas_var = tk.StringVar() #! CAMBIO NOTAS: Variable para el campo de notas
        
        # ... (Widgets para Nombre, Siembra, Cosecha - iguales)
        ttk.Label(frame_agregar, text="Nombre:").pack(fill='x', pady=5)
        ttk.Entry(frame_agregar, textvariable=self.nombre_var).pack(fill='x', pady=2)
        
        ttk.Label(frame_agregar, text="Fecha Siembra:").pack(fill='x', pady=5)
        ttk.Label(frame_agregar, textvariable=self.siembra_display_var, foreground='blue').pack(fill='x', pady=2)
        ttk.Button(frame_agregar, text="Elegir Fecha de Siembra", 
                   command=lambda: self.mostrar_calendario("siembra")).pack(fill='x', pady=5)
        
        ttk.Label(frame_agregar, text="Fecha Cosecha:").pack(fill='x', pady=5)
        ttk.Label(frame_agregar, textvariable=self.cosecha_display_var, foreground='blue').pack(fill='x', pady=2)
        ttk.Button(frame_agregar, text="Elegir Fecha de Cosecha", 
                   command=lambda: self.mostrar_calendario("cosecha")).pack(fill='x', pady=5)

        # #! CAMBIO NOTAS: Nuevo widget para notas
        ttk.Label(frame_agregar, text="Notas (Opcional):").pack(fill='x', pady=5)
        ttk.Entry(frame_agregar, textvariable=self.notas_var).pack(fill='x', pady=2)
        
        self.btn_guardar = ttk.Button(frame_agregar, text="Añadir a la Lista", 
                                     command=self.manejar_agregar_o_editar)
        self.btn_guardar.pack(fill='x', pady=15)
        
        ttk.Button(frame_agregar, text="Limpiar Campos", command=self.limpiar_campos).pack(fill='x', pady=5)


        # --- Marco Derecho (Lista y Botones) ---
        frame_mostrar = ttk.LabelFrame(self, text="🗓 Mis Cultivos", padding="10")
        frame_mostrar.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        frame_mostrar.rowconfigure(1, weight=1) 

        # ... (recordatorio_label)
        self.recordatorio_label = ttk.Label(frame_mostrar, text="Recordatorios aparecerán aquí.", font=('Helvetica', 12, 'bold'))
        self.recordatorio_label.pack(fill='x', pady=5)
        
        # #! CAMBIO NOTAS: Añadimos la columna 'notas' al Treeview
        self.lista_tree = ttk.Treeview(frame_mostrar, columns=('siembra', 'cosecha', 'notas'), show='headings')
        self.lista_tree.heading('siembra', text='Siembra')
        self.lista_tree.heading('cosecha', text='Cosecha')
        self.lista_tree.heading('notas', text='Notas') #! CAMBIO NOTAS
        
        self.lista_tree.column('#0', width=150, anchor='w')
        self.lista_tree.column('siembra', width=90, anchor='center')
        self.lista_tree.column('cosecha', width=90, anchor='center')
        self.lista_tree.column('notas', width=150, anchor='w') #! CAMBIO NOTAS: Configuramos la nueva columna
        self.lista_tree.pack(fill='both', expand=True, pady=10)

        # ... (Botones de Eliminar/Editar - iguales)
        frame_botones_lista = ttk.Frame(frame_mostrar)
        frame_botones_lista.pack(fill='x', pady=5)
        
        ttk.Button(frame_botones_lista, text="❌ Eliminar", 
                   command=self.manejar_eliminar_cultivo).pack(side='left', expand=True, fill='x', padx=5)

        ttk.Button(frame_botones_lista, text="✏️ Editar Seleccionado", 
                   command=self.manejar_editar_cultivo).pack(side='right', expand=True, fill='x', padx=5)

    # --- 4. FUNCIONES CONECTADAS A LA INTERFAZ ---

    def manejar_agregar_o_editar(self):
        """Función Única: Añade un nuevo cultivo O guarda los cambios. #! CAMBIO NOTAS"""
        nombre = self.nombre_var.get().strip()
        fecha_siembra = self.fecha_siembra_obj
        fecha_cosecha = self.fecha_cosecha_obj
        notas = self.notas_var.get().strip() #! CAMBIO NOTAS: Obtenemos el valor de las notas

        # 1. Validación (se mantiene igual)
        if not nombre or not fecha_siembra or not fecha_cosecha:
            messagebox.showerror("Error", "Debe completar el nombre y seleccionar ambas fechas.")
            return
        if fecha_cosecha < fecha_siembra:
            messagebox.showerror("Error", "La fecha de cosecha no puede ser anterior a la siembra.")
            return

        # 2. Lógica de Adición o Edición
        if self.cultivo_seleccionado_indice is None:
            # --- MODO AÑADIR ---
            # ¡Pasamos el nuevo argumento 'notas'!
            nuevo_cultivo = Cultivo(nombre, fecha_siembra, fecha_cosecha, notas) #! CAMBIO NOTAS
            lista_cultivos.append(nuevo_cultivo)
            msg = f"'{nombre}' añadido con éxito."
        else:
            # --- MODO EDITAR ---
            indice = self.cultivo_seleccionado_indice
            cultivo_a_editar = lista_cultivos[indice]
            
            # Actualizamos las propiedades incluyendo 'notas'
            cultivo_a_editar.nombre = nombre
            cultivo_a_editar.fecha_siembra = fecha_siembra
            cultivo_a_editar.fecha_cosecha = fecha_cosecha
            cultivo_a_editar.notas = notas #! CAMBIO NOTAS: Actualizamos las notas
            msg = f"'{nombre}' actualizado con éxito."
            
        # 3. Guardar, actualizar y limpiar
        guardar_cultivos()
        self.actualizar_lista_cultivos()
        self.revisar_cosechas_al_inicio()
        self.limpiar_campos() 
        messagebox.showinfo("Éxito", msg)


    def manejar_editar_cultivo(self):
        """Carga los datos del cultivo seleccionado en los campos de entrada. #! CAMBIO NOTAS"""
        seleccion_id = self.lista_tree.selection()
        
        if not seleccion_id:
            messagebox.showwarning("Advertencia", "Selecciona un cultivo para editar.")
            return

        # Obtenemos el índice del elemento seleccionado
        try:
            indice = int(self.lista_tree.focus())
        except ValueError:
            messagebox.showerror("Error", "Error al identificar el cultivo.")
            return

        # 1. Cargar datos del objeto en los campos
        cultivo_a_editar = lista_cultivos[indice]
        
        self.nombre_var.set(cultivo_a_editar.nombre)
        self.notas_var.set(cultivo_a_editar.notas) #! CAMBIO NOTAS: Cargamos las notas
        
        # Cargar los objetos de fecha (igual)
        self.fecha_siembra_obj = cultivo_a_editar.fecha_siembra
        self.siembra_display_var.set(cultivo_a_editar.fecha_siembra.strftime('%Y-%m-%d'))
        self.fecha_cosecha_obj = cultivo_a_editar.fecha_cosecha
        self.cosecha_display_var.set(cultivo_a_editar.fecha_cosecha.strftime('%Y-%m-%d'))
        
        # 2. Entrar en modo edición (igual)
        self.cultivo_seleccionado_indice = indice 
        self.btn_guardar.config(text=f"✏️ Guardar Cambios (Editando {cultivo_a_editar.nombre})")
        messagebox.showinfo("Modo Edición", f"Datos de '{cultivo_a_editar.nombre}' cargados. Haz tus cambios y pulsa 'Guardar Cambios'.")


    def actualizar_lista_cultivos(self):
        """Refresca los datos mostrados en la lista Treeview. #! CAMBIO NOTAS"""
        
        # ... (Borrar contenido anterior - igual)
        for item in self.lista_tree.get_children():
            self.lista_tree.delete(item)
            
        # Insertamos los nuevos datos
        for i, cultivo in enumerate(lista_cultivos):
            siembra_f = cultivo.fecha_siembra.strftime('%d-%m-%Y')
            cosecha_f = cultivo.fecha_cosecha.strftime('%d-%m-%Y')
            
            # #! CAMBIO NOTAS: Insertamos el valor de notas
            self.lista_tree.insert('', tk.END, iid=str(i), 
                                   text=cultivo.nombre, 
                                   values=(siembra_f, cosecha_f, cultivo.notas)) #! CAMBIO NOTAS

    # ... (El resto de funciones como manejar_eliminar_cultivo, mostrar_calendario, revisar_cosechas_al_inicio se mantienen igual)
    
# --- 5. INICIO DE LA APLICACIÓN (Sin cambios) ---
if __name__ == "__main__":
    # ... (app = AppCultivos(), app.mainloop())
    app = AppCultivos()
    app.mainloop()
