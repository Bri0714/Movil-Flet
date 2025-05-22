# src/controlador/usuario_controller.py

from modelo.usuario_model import UsuarioModel

class UsuarioController:
    def __init__(self):
        self.model = UsuarioModel()

    def actualizar_usuario(self, cedula, nombre_completo, fecha_licencia, edad, telefono, placa):
        return self.model.actualizar_usuario(cedula, nombre_completo, fecha_licencia, edad, telefono, placa)
