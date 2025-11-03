# app_backend.py

from flask import Flask, jsonify, request
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
NOMBRE_ARCHIVO_CULTIVOS = "cultivos.json"

# Inicialización de la aplicación Flask
app = Flask(__name__)

# --- FUNCIONES DE MANEJO DE ARCHIVOS ---

def cargar_datos_cultivos():
    """Lee el archivo JSON de cultivos. Si no existe, devuelve una lista vacía."""
    if not os.path.exists(NOMBRE_ARCHIVO_CULTIVOS):
        return []
    try:
        with open(NOMBRE_ARCHIVO_CULTIVOS, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al cargar datos JSON: {e}")
        return []

def guardar_datos_cultivos(cultivos_lista):
    """Escribe la lista de cultivos actualizada en el archivo JSON."""
    try:
        with open(NOMBRE_ARCHIVO_CULTIVOS, "w") as f:
            # Usamos indent=4 para que el JSON sea legible
            json.dump(cultivos_lista, f, indent=4)
        return True
    except Exception as e:
        print(f"Error al guardar datos JSON: {e}")
        return False

# --- RUTAS DE LA API (Endpoints) ---

@app.route('/', methods=['GET'])
def index():
    """Ruta de bienvenida/prueba, lista todos los endpoints CRUD."""
    return jsonify({
        "status": "ok",
        "mensaje": "Servidor de Asistente de Cultivos (API) activo.",
        "endpoints_disponibles": {
            "/api/v1/cultivos (GET)": "Obtiene todos los cultivos",
            "/api/v1/cultivos (POST)": "Agrega un nuevo cultivo",
            "/api/v1/cultivos/<nombre> (DELETE)": "Elimina un cultivo por nombre",
            "/api/v1/cultivos/<nombre> (PUT)": "Actualiza completamente un cultivo por nombre"
        }
    })


@app.route('/api/v1/cultivos', methods=['GET'])
def obtener_cultivos():
    """
    Endpoint para obtener la lista completa de cultivos, calculando los días restantes.
    """
    cultivos = cargar_datos_cultivos()
    
    hoy = datetime.now().date()
    
    for cultivo in cultivos:
        try:
            fecha_cosecha = datetime.strptime(cultivo["fecha_cosecha"], '%Y-%m-%d').date()
            dias_restantes = (fecha_cosecha - hoy).days
            
            # Cálculo de estado para el JSON
            if dias_restantes < 0:
                cultivo['dias_restantes'] = f"Cosechado hace {abs(dias_restantes)} días"
            elif dias_restantes == 0:
                cultivo['dias_restantes'] = "¡COSECHA HOY!"
            else:
                cultivo['dias_restantes'] = f"{dias_restantes} días"
                
        except (ValueError, KeyError):
            cultivo['dias_restantes'] = "Fecha no válida"
            
    return jsonify(cultivos)


@app.route('/api/v1/cultivos', methods=['POST'])
def agregar_cultivo():
    """
    Endpoint para agregar un nuevo cultivo a la base de datos (cultivos.json).
    """
    if not request.is_json:
        return jsonify({"error": "Falta el cuerpo de la petición (JSON)."}), 400

    datos_cultivo = request.json
    
    # 1. Validación Básica de Campos Requeridos
    campos_requeridos = ["nombre", "fecha_siembra", "fecha_cosecha"]
    for campo in campos_requeridos:
        if campo not in datos_cultivo:
            return jsonify({"error": f"Falta el campo requerido: {campo}"}), 400
            
    # 2. Convertir y validar fechas
    try:
        datetime.strptime(datos_cultivo["fecha_siembra"], '%Y-%m-%d')
        datetime.strptime(datos_cultivo["fecha_cosecha"], '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD (ej: 2026-03-20)."}), 400

    # 3. Preparar el nuevo objeto (Asegurar que todos los campos existan)
    try:
        nuevo_cultivo = {
            "nombre": datos_cultivo["nombre"],
            "fecha_siembra": datos_cultivo["fecha_siembra"],
            "fecha_cosecha": datos_cultivo["fecha_cosecha"],
            "notas": datos_cultivo.get("notas", ""),
            "zona": datos_cultivo.get("zona", ""),
            "precio_compra": float(datos_cultivo.get("precio_compra", 0.0)),
            "precio_venta": float(datos_cultivo.get("precio_venta", 0.0)),
            "dias_alerta": int(datos_cultivo.get("dias_alerta", 0))
        }
    except ValueError:
        return jsonify({"error": "Los campos numéricos (precios, alerta) deben ser números válidos."}), 400
    
    # 4. Cargar, Añadir y Guardar
    cultivos = cargar_datos_cultivos()
    cultivos.append(nuevo_cultivo)
    
    if guardar_datos_cultivos(cultivos):
        return jsonify({
            "status": "success",
            "mensaje": f"Cultivo '{nuevo_cultivo['nombre']}' añadido correctamente.",
            "cultivo_agregado": nuevo_cultivo
        }), 201  # Código 201 Created
    else:
        return jsonify({"error": "Error interno del servidor al guardar el archivo JSON."}), 500


@app.route('/api/v1/cultivos/<string:nombre_cultivo>', methods=['PUT'])
def actualizar_cultivo(nombre_cultivo):
    """
    Endpoint para actualizar completamente un cultivo específico por su nombre.
    """
    if not request.is_json:
        return jsonify({"error": "Falta el cuerpo de la petición (JSON)."}), 400

    cultivos = cargar_datos_cultivos()
    nombre_cultivo_lower = nombre_cultivo.lower()
    datos_actualizados = request.json
    
    # 1. Buscar el índice del cultivo a actualizar
    indice_a_actualizar = -1
    for i, cultivo in enumerate(cultivos):
        if cultivo.get("nombre", "").lower() == nombre_cultivo_lower:
            indice_a_actualizar = i
            break
            
    if indice_a_actualizar == -1:
        return jsonify({"error": f"Cultivo '{nombre_cultivo}' no encontrado."}), 404

    # 2. Validar tipos de datos del cuerpo de la petición (Si existen)
    try:
        if "fecha_siembra" in datos_actualizados:
            datetime.strptime(datos_actualizados["fecha_siembra"], '%Y-%m-%d')
        if "fecha_cosecha" in datos_actualizados:
            datetime.strptime(datos_actualizados["fecha_cosecha"], '%Y-%m-%d')
            
        # Asegurar que los valores numéricos son float/int si están presentes
        datos_actualizados["precio_compra"] = float(datos_actualizados.get("precio_compra", 
                                                                           cultivos[indice_a_actualizar].get("precio_compra", 0.0)))
        datos_actualizados["precio_venta"] = float(datos_actualizados.get("precio_venta", 
                                                                         cultivos[indice_a_actualizar].get("precio_venta", 0.0)))
        datos_actualizados["dias_alerta"] = int(datos_actualizados.get("dias_alerta", 
                                                                      cultivos[indice_a_actualizar].get("dias_alerta", 0)))

    except ValueError:
        return jsonify({"error": "Formato de fecha o valor numérico inválido. Use YYYY-MM-DD y números."}), 400

    # 3. Actualizar el objeto con los nuevos datos (reemplazo de campos)
    cultivo_existente = cultivos[indice_a_actualizar]
    
    cultivo_existente.update({
        # Se usa .get() para actualizar solo los campos que están en el JSON de la petición
        "nombre": datos_actualizados.get("nombre", cultivo_existente.get("nombre")),
        "fecha_siembra": datos_actualizados.get("fecha_siembra", cultivo_existente.get("fecha_siembra")),
        "fecha_cosecha": datos_actualizados.get("fecha_cosecha", cultivo_existente.get("fecha_cosecha")),
        "notas": datos_actualizados.get("notas", cultivo_existente.get("notas", "")),
        "zona": datos_actualizados.get("zona", cultivo_existente.get("zona", "")),
        "precio_compra": datos_actualizados["precio_compra"], # Usamos los valores validados
        "precio_venta": datos_actualizados["precio_venta"],   # Usamos los valores validados
        "dias_alerta": datos_actualizados["dias_alerta"]      # Usamos los valores validados
    })

    # 4. Guardar la lista actualizada
    if guardar_datos_cultivos(cultivos):
        return jsonify({
            "status": "success",
            "mensaje": f"Cultivo '{nombre_cultivo}' actualizado correctamente.",
            "cultivo_actualizado": cultivo_existente
        }), 200
    else:
        return jsonify({"error": "Error interno del servidor al guardar el archivo."}), 500


@app.route('/api/v1/cultivos/<string:nombre_cultivo>', methods=['DELETE'])
def eliminar_cultivo(nombre_cultivo):
    """
    Endpoint para eliminar un cultivo específico por su nombre.
    """
    cultivos = cargar_datos_cultivos()
    nombre_cultivo_lower = nombre_cultivo.lower()
    
    # 1. Buscar el índice del cultivo a eliminar
    indice_a_eliminar = -1
    for i, cultivo in enumerate(cultivos):
        if cultivo.get("nombre", "").lower() == nombre_cultivo_lower:
            indice_a_eliminar = i
            break
            
    if indice_a_eliminar == -1:
        return jsonify({"error": f"Cultivo '{nombre_cultivo}' no encontrado."}), 404

    # 2. Eliminar el cultivo de la lista
    nombre_eliminado = cultivos[indice_a_eliminar]["nombre"]
    del cultivos[indice_a_eliminar]
    
    # 3. Guardar la lista actualizada
    if guardar_datos_cultivos(cultivos):
        return jsonify({
            "status": "success",
            "mensaje": f"Cultivo '{nombre_eliminado}' eliminado correctamente."
        }), 200
    else:
        return jsonify({"error": "Error interno del servidor al guardar el archivo."}), 500


# --- INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    # Se ejecutará en http://127.0.0.1:5000/
    print("Iniciando servidor Flask...")
    app.run(debug=True)
