# Importamos el módulo datetime, que es esencial para manejar fechas
import datetime

# Esta será nuestra "base de datos" temporal. Es una lista que guardará todos los cultivos.
lista_cultivos = []

# --- 1. El "molde" para nuestros cultivos ---
class Cultivo:
    """
    Esta clase es una plantilla para crear objetos "Cultivo".
    Cada cultivo tendrá un nombre, una fecha de siembra y una fecha de cosecha.
    """
    def __init__(self, nombre, fecha_siembra, fecha_cosecha):
        self.nombre = nombre
        self.fecha_siembra = fecha_siembra
        self.fecha_cosecha = fecha_cosecha

# --- 2. Funciones de la aplicación ---

def validar_fecha(fecha_texto):
    """
    Una función de ayuda para asegurarnos de que la fecha que escribe
    el usuario tiene el formato correcto (YYYY-MM-DD).
    """
    try:
        # Intenta convertir el texto a un objeto de fecha
        return datetime.datetime.strptime(fecha_texto, '%Y-%m-%d').date()
    except ValueError:
        # Si falla (p.ej., el usuario escribe "hola"), devuelve None
        return None

def agregar_cultivo():
    """
    Esta función pide al usuario los datos para añadir un nuevo cultivo.
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
            fecha_cosecha = None # Reinicia para volver a preguntar

    # Creamos el nuevo cultivo usando nuestra clase "molde"
    nuevo_cultivo = Cultivo(nombre, fecha_siembra, fecha_cosecha)
    
    # Añadimos el cultivo a nuestra lista principal
    lista_cultivos.append(nuevo_cultivo)
    
    print(f"\n¡Perfecto! Cultivo '{nombre}' añadido con éxito.")

def mostrar_cultivos():
    """
    Esta función recorre la lista de cultivos y los muestra en pantalla.
    """
    print("\n--- Mis Cultivos Guardados ---")
    
    if not lista_cultivos:
        print("No tienes ningún cultivo guardado todavía.")
        return
        
    # Recorremos la lista e imprimimos la información de cada uno
    for i, cultivo in enumerate(lista_cultivos):
        # .strftime() nos ayuda a formatear la fecha para que se vea bonita
        siembra_bonita = cultivo.fecha_siembra.strftime('%d-%m-%Y')
        cosecha_bonita = cultivo.fecha_cosecha.strftime('%d-%m-%Y')
        
        print(f"{i + 1}. {cultivo.nombre}")
        print(f"   - Siembra:   {siembra_bonita}")
        print(f"   - Cosecha:   {cosecha_bonita}")
        print("-" * 20) # Una línea para separar

def revisar_cosechas():
    """
    Esta es la función clave: revisa qué cultivos están listos.
    """
    print("\n--- Recordatorios de Cosecha ---")
    
    # Obtenemos la fecha de HOY
    hoy = datetime.date.today()
    print(f"Revisando con fecha de hoy: {hoy.strftime('%d-%m-%Y')}\n")
    
    hay_recordatorios = False
    
    for cultivo in lista_cultivos:
        # Comparamos la fecha de cosecha con la fecha de hoy
        if cultivo.fecha_cosecha <= hoy:
            print(f"¡ATENCIÓN! Es hora de cosechar tus: {cultivo.nombre}")
            print(f"  (Fecha de cosecha estimada: {cultivo.fecha_cosecha.strftime('%d-%m-%Y')})")
            hay_recordatorios = True
            
    if not hay_recordatorios:
        print("Todo en orden. Aún no hay cultivos listos para cosechar.")

# --- 3. El Menú Principal ---

def menu_principal():
    """
    El bucle principal que mantiene la aplicación funcionando
    y muestra las opciones al usuario.
    """
    print("¡Bienvenido a tu Asistente de Cultivos!")
    
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
            break # Rompe el bucle y termina el programa
        else:
            print("\n¡Opción no válida! Por favor, elige un número del 1 al 4.")

# --- 4. Iniciar la aplicación ---
# Esta línea especial asegura que el menú solo se ejecute
# cuando corremos este archivo directamente.
if __name__ == "__main__":
    menu_principal()
