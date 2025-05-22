from modelo.usuario_model import UsuarioModel

class LoginController:
    def __init__(self):
        self.usuario_model = UsuarioModel()

    def login(self, cedula, password):
        if not cedula or not password:
            return None
        return self.usuario_model.login_usuario(cedula, password)

    def recuperar_password(self, cedula, nuevo_password):
        if not cedula or not nuevo_password:
            return False
        return self.usuario_model.actualizar_password(cedula, nuevo_password)
