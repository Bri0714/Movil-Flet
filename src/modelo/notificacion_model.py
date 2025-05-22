from pymongo import MongoClient
from datetime import datetime

class NotificacionModel:
    def __init__(self):
        self.client = MongoClient("mongodb://root:rootpassword@mongo:27017")
        self.db = self.client["preop_escolar_db"]
        self.col = self.db["notificaciones"]
        self.users = self.db["usuarios"]
        self.inspecciones = self.db["inspecciones"]

    def generar_notificaciones_pendientes(self):
        hoy = datetime.now().strftime("%Y-%m-%d")
        conductores = list(self.users.find({"role": "driver"}))
        for user in conductores:
            cedula = user["cedula"]
            placa = user.get("placa", "")
            nombre = user.get("nombre_completo", "")
            inspeccion_hoy = self.inspecciones.find_one({
                "cedula": cedula,
                "fecha_envio": {"$regex": f"^{hoy}"}
            })
            ya_tiene_notif = self.col.find_one({
                "cedula": cedula, "fecha": hoy, "tipo": "pendiente", "vista_admin": False
            })
            if not inspeccion_hoy and not ya_tiene_notif:
                self.col.insert_one({
                    "cedula": cedula,
                    "placa": placa,
                    "nombre": nombre,
                    "fecha": hoy,
                    "mensaje": f"El usuario {nombre} ({placa}) no ha realizado la inspección de hoy ({hoy}).",
                    "tipo": "pendiente",
                    "enviada": False,
                    "vista_admin": False,
                    "vista_driver": False,
                    "fecha_creacion": datetime.now()
                })

    def get_admin_notificaciones(self):
        return list(self.col.find({"tipo": "pendiente", "enviada": False, "vista_admin": False}))

    def marcar_enviada_admin(self, notif_id):
        from bson import ObjectId
        self.col.update_one({"_id": ObjectId(notif_id)}, {"$set": {"enviada": True, "vista_admin": True}})

    def get_driver_notificaciones(self, cedula):
        hoy = datetime.now().strftime("%Y-%m-%d")
        return list(self.col.find({"cedula": cedula, "tipo": "pendiente", "enviada": True, "vista_driver": False, "fecha": hoy}))

    def marcar_vista_driver(self, notif_id):
        from bson import ObjectId
        self.col.update_one({"_id": ObjectId(notif_id)}, {"$set": {"vista_driver": True}})
