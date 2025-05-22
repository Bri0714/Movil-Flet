from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

class EncuestaModel:
    def __init__(self):
        self.client = MongoClient("mongodb://root:rootpassword@mongo:27017")
        self.db = self.client["preop_escolar_db"]
        self.encuestas = self.db["encuestas"]
        self.inspecciones = self.db["inspecciones"]

    def crear_encuesta(self, categoria: str, descripcion: str, opciones: list[str], color: str) -> str:
        doc = {
            "categoria": categoria,
            "descripcion": descripcion,
            "opciones": [{"texto": o, "orden": i} for i, o in enumerate(opciones)],
            "color": color,
            "fecha_creacion": datetime.now()
        }
        result = self.encuestas.insert_one(doc)
        return str(result.inserted_id)

    def obtener_encuestas(self) -> list[dict]:
        return list(self.encuestas.find())

    def guardar_inspeccion(
        self,
        placa: str,
        kilometraje: int,
        respuestas: list[dict],
        evidencias: list[str],
        observaciones: str,
        cedula: str,
        nombre: str
    ) -> str:
        doc = {
            "nombre": nombre,
            "cedula": cedula,
            "placa": placa,
            "kilometraje": kilometraje,
            "respuestas": respuestas,
            "evidencias": evidencias,
            "observaciones": observaciones,
            "fecha_envio": datetime.now()
        }
        result = self.inspecciones.insert_one(doc)
        return str(result.inserted_id)

    def obtener_inspecciones(self, fecha_ini=None, fecha_fin=None, role="driver", cedula=None):
        filtro = {}
        if fecha_ini and fecha_fin:
            filtro["fecha_envio"] = {"$gte": fecha_ini, "$lte": fecha_fin}
        if role == "driver" and cedula:
            filtro["cedula"] = cedula
        inspecciones = list(self.inspecciones.find(filtro))
        return inspecciones

    def actualizar_encuesta(self, encuesta_id, categoria, descripcion, opciones, color):
        update = {
            "categoria": categoria,
            "descripcion": descripcion,
            "opciones": [{"texto": o, "orden": i} for i, o in enumerate(opciones)],
            "color": color
        }
        result = self.encuestas.update_one({"_id": ObjectId(encuesta_id)}, {"$set": update})
        return result.modified_count > 0

    def eliminar_encuesta(self, encuesta_id):
        print(f"[DEBUG] Intentando eliminar encuesta con id: {encuesta_id} ({type(encuesta_id)})")
        try:
            # Forzar conversión a ObjectId para evitar errores
            if not isinstance(encuesta_id, ObjectId):
                encuesta_id = ObjectId(str(encuesta_id))
        except Exception as e:
            print(f"[ERROR] No se pudo convertir a ObjectId: {e}")
            return False
        result = self.encuestas.delete_one({"_id": encuesta_id})
        print(f"[DEBUG] Eliminados: {result.deleted_count}")
        return result.deleted_count > 0
