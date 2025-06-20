from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from jsonschema import validate, ValidationError

load_dotenv()  # Carga las variables del archivo .env

app = Flask(__name__)

# Lee las variables de entorno
SUPABASE_URL_ENVIAR_REQUISITOS = os.environ.get("SUPABASE_URL_ENVIAR_REQUISITOS")
API_KEY = os.environ.get("SUPABASE_API_KEY")
AUTH_TOKEN = os.environ.get("SUPABASE_AUTH_TOKEN")

HEADERS = {
    "apikey": API_KEY,
    "Authorization": AUTH_TOKEN,
    "Prefer": "resolution=merge-duplicates",
    "Content-Type": "application/json"
}

# Definir el esquema de validación
schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "requerimiento_id": {"type": "string"},
            "descripcion": {"type": "string"},
            "referencia_normativa": {"type": "string"},
            "prioridad": {"type": "string"},
            "justificacion": {"type": "string"},
            "metodo_validacion": {"type": "string"},
            "dependencias_exclusiones": {"type": "string"},
            "categoria": {"type": "string"},
            "ejemplo_practico": {"type": "string"}
        },
        "required": [
            "requerimiento_id",
            "descripcion",
            "referencia_normativa",
            "prioridad",
            "justificacion",
            "metodo_validacion",
            "dependencias_exclusiones",
            "categoria",
            "ejemplo_practico"
        ],
        "additionalProperties": False
    }
}

@app.route('/enviar-requisitos', methods=['POST'])
def enviar_requisitos():
    try:
        data = request.get_json(force=True)
        if not isinstance(data, list):
            return jsonify({"error": "El cuerpo de la petición debe ser un arreglo JSON."}), 400



        # Validar el JSON usando el esquema definido
        try:
            validate(instance=data, schema=schema)
        except ValidationError as err:
            return jsonify({
                "error": "El JSON no cumple con la estructura requerida.",
                "detalle": err.message
            }), 400

        # Enviar el JSON a la URL definida en tu .env
        response = requests.post(SUPABASE_URL_ENVIAR_REQUISITOS, headers=HEADERS, json=data)

        # Código de depuración: imprimir datos de la respuesta de Supabase
        print("Status code de Supabase:", response.status_code)
        print("response.text =>", response.text)

        # Justo tras recibir la respuesta de Supabase
        if response.status_code in [200, 201]:
            if response.text.strip():  # Si hay texto, intentar parsearlo como JSON
                data_supabase = response.json()
                return jsonify({
                    "mensaje": "Requisitos enviados correctamente a Supabase",
                    "respuesta": data_supabase
                }), response.status_code
            else:
                # Supabase devolvió 200 pero sin cuerpo de respuesta
                return jsonify({
                    "mensaje": "Requisitos enviados correctamente a Supabase (sin cuerpo de respuesta)"
                }), response.status_code
        else:
            return jsonify({
                "error": "Error al enviar los requisitos",
                "detalle": response.text
            }), response.status_code

    except Exception as e:
        return jsonify({
            "error": "Excepción al procesar la petición",
            "detalle": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
