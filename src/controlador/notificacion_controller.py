from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

class NotificacionController:
    def __init__(self):
        self.client = MongoClient("mongodb://root:rootpassword@mongo:27017")
        self.db = self.client["preop_escolar_db"]
        self.col_usuarios = self.db["usuarios"]
        self.col_inspecciones = self.db["inspecciones"]
        self.col_notificaciones = self.db["notificaciones"]

    def generar_notificaciones_pendientes(self):
        hoy = datetime.now().date()
        for user in self.col_usuarios.find({"role": "driver"}):
            cedula = user["cedula"]
            inspeccion_hoy = self.col_inspecciones.find_one({
                "cedula": cedula,
                "$expr": {
                    "$eq": [
                        { "$dateToString": { "format": "%Y-%m-%d", "date": "$fecha_envio" } },
                        hoy.strftime("%Y-%m-%d")
                    ]
                }
            })
            if not inspeccion_hoy:
                existe = self.col_notificaciones.find_one({
                    "cedula": cedula,
                    "fecha": hoy.strftime("%Y-%m-%d"),
                    "tipo": "pendiente",
                    "estado": {"$in": ["pendiente", "enviada"]}
                })
                if not existe:
                    self.col_notificaciones.insert_one({
                        "cedula": cedula,
                        "nombre": user["nombre_completo"],
                        "placa": user.get("placa", ""),
                        "fecha": hoy.strftime("%Y-%m-%d"),
                        "mensaje": f"El usuario {user['nombre_completo']} no ha realizado la inspección del día {hoy.strftime('%Y-%m-%d')}",
                        "tipo": "pendiente",
                        "estado": "pendiente",  # pendiente → enviada → vista
                        "creado": datetime.now()
                    })

    def get_admin_notificaciones(self):
        hoy = datetime.now().date().strftime("%Y-%m-%d")
        # Solo las pendientes para enviar hoy
        return list(self.col_notificaciones.find({
            "fecha": hoy,
            "tipo": "pendiente",
            "estado": "pendiente"
        }).sort("creado", -1))

    def get_driver_notificaciones(self, cedula):
        hoy = datetime.now().date().strftime("%Y-%m-%d")
        # Solo las que el admin ya envió y el driver aún no vio
        return list(self.col_notificaciones.find({
            "cedula": cedula,
            "fecha": hoy,
            "tipo": "pendiente",
            "estado": "enviada"
        }).sort("creado", -1))

    def marcar_enviada_admin(self, notif_id):
        self.col_notificaciones.update_one(
            {"_id": ObjectId(notif_id)},
            {"$set": {"estado": "enviada"}}
        )

    def marcar_vista_driver(self, notif_id):
        self.col_notificaciones.update_one(
            {"_id": ObjectId(notif_id)},
            {"$set": {"estado": "vista"}}
        )
