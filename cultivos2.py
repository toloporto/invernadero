# Importamos el módulo datetime, que es esencial para manejar fechas
import datetime
# ¡NUEVO! Importamos 'json' para guardar y cargar datos
import json
# ¡NUEVO! Importamos 'os' para comprobar si el archivo de guardado existe
import os

# Esta será nuestra "base de datos" temporal.
# Se llenará con los datos del archivo .json al iniciar.
lista_cultivos = []
# ¡NUEVO! Nombre de nuestro archivo de guardado
NOMBRE_ARCHIVO = "cultivos.json"

# --- 1. El "molde" para nuestros cultivos (Sin cambios) ---
class Cultivo:
    """
    Esta clase es una plantilla para crear objetos "Cultivo".
    """
    def __init__(self, nombre, fecha_siembra, fecha_cosecha):
        self.nombre = nombre
        self.fecha_siembra = fecha_siembra
        self.fecha_cosecha = fecha_cosecha

# --- 2. Funciones de la aplicación ---

def validar_fecha(fecha_texto):
    """
    (Sin cambios)
    Una función de ayuda para asegurarnos de que la fecha que escribe
    el usuario tiene el formato correcto (YYYY-MM-DD).
    """
    try:
        return datetime.datetime.strptime(fecha_texto, '%Y-%m-%d').date()
    except ValueError:
        return None

# ¡NUEVA FUNCIÓN!
def cargar_cultivos():
    """
    Revisa si existe el archivo JSON. Si existe, carga los datos
    en la variable global 'lista_cultivos'.
    """
    # Usamos 'global' para poder modificar la lista principal
    global lista_cultivos
    
    if not os.path.exists(NOMBRE_ARCHIVO):
        print("[Sistema: No se encontró archivo de guardado. Empezando de cero.]")
        return # El archivo no existe, la lista empieza vacía.

    try:
        with open(NOMBRE_ARCHIVO, "r") as f:
            # Carga los datos del archivo
            datos_cargados = json.load(f)
            
            # Ahora, convertimos cada "diccionario" de vuelta a un "objeto" Cultivo
            for item in datos_cargados:
                # ¡Importante! Convertimos las fechas de texto a objetos 'date'
                siembra = validar_fecha(item["fecha_siembra"])
                cosecha = validar_fecha(item["fecha_cosecha"])
                
                if siembra and cosecha:
                    nuevo = Cultivo(item["nombre"], siembra, cosecha)
                    lista_cultivos.append(nuevo)
                    
        print(f"\n[Sistema: ¡Éxito! Se cargaron {len(lista_cultivos)} cultivos guardados.]")
        
    except Exception as e:
        print(f"\n[Error al cargar {NOMBRE_ARCHIVO}: {e}]")
        print("[Sistema: Empezando con una lista vacía para evitar errores.]")
        # Si el archivo está corrupto, es más seguro empezar de cero.
        lista_cultivos = []

# ¡NUEVA FUNCIÓN!
def guardar_cultivos():
    """
    Convierte la 'lista_cultivos' (que contiene objetos) a un formato
    que JSON entienda (diccionarios) y lo guarda en el archivo.
    """
    
    # 1. Convertir nuestra lista de objetos a una lista de diccionarios
    datos_para_json = []
    for cultivo in lista_cultivos:
        cultivo_dict = {
            "nombre": cultivo.nombre,
            # ¡Importante! Convertimos los objetos 'date' a texto
            "fecha_siembra": cultivo.fecha_siembra.isoformat(), # formato "YYYY-MM-DD"
            "fecha_cosecha": cultivo.fecha_cosecha.isoformat()
        }
        datos_para_json.append(cultivo_dict)
        
    # 2. Guardar la lista de diccionarios en el archivo JSON
    try:
        with open(NOMBRE_ARCHIVO, "w") as f:
            # 'indent=4' hace que el archivo .json sea legible para humanos
            json.dump(datos_para_json, f, indent=4)
        
        print("\n[Sistema: Cultivos guardados exitosamente.]")
            
    except Exception as e:
        print(f"\n[¡Error crítico al guardar! {e}]")


def agregar_cultivo():
    """
    Esta función pide al usuario los datos para añadir un nuevo cultivo.
    (Casi igual, pero con un cambio clave al final)
    """
    print("\n--- Añadir Nuevo Cultivo ---")
    nombre = input("Nombre del cultivo (ej: Tomates): ")
    
    fecha_siembra = None
    while fecha_siembra is None:
        fecha_siembra_str = input("Fecha de siembra (formato YYYY-MM-DD): ")
        fecha_siembra = validar_fecha(fecha_siembra_str)
        if fecha_siembra is None:
            print("¡Error! Formato incorrecto. Inténtalo de nuevo.")
            
    fecha_cosecha = None
    while fecha_cosecha is None:
        fecha_cosecha_str = input("Fecha estimada de cosecha (formato YYYY-MM-DD): ")
        fecha_cosecha = validar_fecha(fecha_cosecha_str)
        if fecha_cosecha is None:
            print("¡Error! Formato incorrecto. Inténtalo de nuevo.")
        elif fecha_cosecha < fecha_siembra:
            print("¡Error! La cosecha no puede ser antes que la siembra.")
            fecha_cosecha = None

    # Creamos el nuevo cultivo
    nuevo_cultivo = Cultivo(nombre, fecha_siembra, fecha_cosecha)
    
    # Añadimos el cultivo a nuestra lista
    lista_cultivos.append(nuevo_cultivo)
    
    # ¡MODIFICADO! Llamamos a la función de guardado
    # Cada vez que añadimos un cultivo, guardamos la lista completa.
    guardar_cultivos()
    
    print(f"\n¡Perfecto! Cultivo '{nombre}' añadido con éxito.")


def mostrar_cultivos():
    """
    (Sin cambios)
    Esta función recorre la lista de cultivos y los muestra en pantalla.
    """
    print("\n--- Mis Cultivos Guardados ---")
    
    if not lista_cultivos:
        print("No tienes ningún cultivo guardado todavía.")
        return
        
    for i, cultivo in enumerate(lista_cultivos):
        siembra_bonita = cultivo.fecha_siembra.strftime('%d-%m-%Y')
        cosecha_bonita = cultivo.fecha_cosecha.strftime('%d-%m-%Y')
        
        print(f"{i + 1}. {cultivo.nombre}")
        print(f"   - Siembra:   {siembra_bonita}")
        print(f"   - Cosecha:   {cosecha_bonita}")
        print("-" * 20)

def revisar_cosechas():
    """
    (Sin cambios)
    Esta es la función clave: revisa qué cultivos están listos.
    """
    print("\n--- Recordatorios de Cosecha ---")
    
    hoy = datetime.date.today()
    print(f"Revisando con fecha de hoy: {hoy.strftime('%d-%m-%Y')}\n")
    
    hay_recordatorios = False
    
    for cultivo in lista_cultivos:
        if cultivo.fecha_cosecha <= hoy:
            print(f"¡ATENCIÓN! Es hora de cosechar tus: {cultivo.nombre}")
            print(f"  (Fecha de cosecha estimada: {cultivo.fecha_cosecha.strftime('%d-%m-%Y')})")
            hay_recordatorios = True
            
    if not hay_recordatorios:
        print("Todo en orden. Aún no hay cultivos listos para cosechar.")

# --- 3. El Menú Principal (Sin cambios) ---

def menu_principal():
    """
    El bucle principal que mantiene la aplicación funcionando
    y muestra las opciones al usuario.
    """
    print("¡Bienvenido a tu Asistente de Cultivos! (V 2.0 con Guardado)")
    
    while True:
        print("\n===== MENÚ PRINCIPAL =====")
        print("1. Añadir un nuevo cultivo")
        print("2. Mostrar todos mis cultivos")
        print("3. Revisar recordatorios de cosecha")
        print("4. Salir")
        
        opcion = input("Elige una opción (1-4): ")
        
        if opcion == '1':
            agregar_cultivo()
        elif opcion == '2':
            mostrar_cultivos()
        elif opcion == '3':
            revisar_cosechas()
        elif opcion == '4':
            print("\n¡Hasta pronto! ¡Feliz cosecha! 🌱")
            break
        else:
            print("\n¡Opción no válida! Por favor, elige un número del 1 al 4.")

# --- 4. Iniciar la aplicación ---

# ¡MODIFICADO!
# Esta línea especial asegura que el menú solo se ejecute
# cuando corremos este archivo directamente.
if __name__ == "__main__":
    # ¡NUEVO! Primero, intentamos cargar los datos guardados.
    cargar_cultivos()
    # Después, iniciamos el menú principal de siempre.
    menu_principal()
