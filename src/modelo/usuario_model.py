from pymongo import MongoClient
from datetime import datetime
import bcrypt

class UsuarioModel:
    def __init__(self):
        self.client = MongoClient("mongodb://root:rootpassword@mongo:27017")
        self.db = self.client["preop_escolar_db"]
        self.collection = self.db["usuarios"]

    def registrar_usuario(self, nombre_completo, cedula, fecha_licencia, edad, telefono, placa, password, role="driver"):
        if self.collection.find_one({"cedula": cedula}):
            return False  # Usuario ya registrado

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        usuario_data = {
            "nombre_completo": nombre_completo,
            "cedula": cedula,
            "fecha_licencia": fecha_licencia,
            "edad": edad,
            "telefono": telefono,
            "placa": placa,
            "password": hashed_password,
            "role": role,  # "driver" o "admin"
            "fecha_registro": datetime.now()
        }
        self.collection.insert_one(usuario_data)
        return True

    def login_usuario(self, cedula, password):
        usuario = self.collection.find_one({"cedula": cedula})
        if not usuario:
            return None
        if bcrypt.checkpw(password.encode("utf-8"), usuario["password"]):
            return usuario
        return None

    # src/modelo/usuario_model.py

    def actualizar_usuario(self, cedula, nombre_completo, fecha_licencia, edad, telefono, placa):
        update_result = self.collection.update_one(
            {"cedula": cedula},
            {
                "$set": {
                    "nombre_completo": nombre_completo,
                    "fecha_licencia": fecha_licencia,
                    "edad": edad,
                    "telefono": telefono,
                    "placa": placa
                }
            }
        )
        return update_result.modified_count > 0


    def actualizar_password(self, cedula, nuevo_password):
        if not self.collection.find_one({"cedula": cedula}):
            return False
        hashed_password = bcrypt.hashpw(nuevo_password.encode("utf-8"), bcrypt.gensalt())
        self.collection.update_one({"cedula": cedula}, {"$set": {"password": hashed_password}})
        return True
