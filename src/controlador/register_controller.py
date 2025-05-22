# src/controlador/register_controller.py

from modelo.usuario_model import UsuarioModel

class RegisterController:
    def __init__(self):
        # Instanciamos el modelo que habla con MongoDB
        self.usuario_model = UsuarioModel()

    def registrar(
        self,
        nombre_completo: str,
        cedula: str,
        fecha_licencia: str,
        edad: str,
        telefono: str,
        placa: str,
        password: str,
        role: str
    ) -> bool:
        """
        Valida los datos de entrada y normaliza el rol antes de llamar al modelo.
        """

        # 1) Comprobaciones básicas de campos requeridos
        if not (nombre_completo and cedula and fecha_licencia and edad and telefono and placa and password and role):
            return False

        # 2) Validar que la edad sea un número y >= 18
        try:
            if int(edad) < 18:
                return False
        except ValueError:
            return False

        # 3) Validar que el teléfono sólo contenga dígitos
        if not telefono.isdigit():
            return False

        # 4) Normalizar el rol (aceptar en español o en inglés, mayúsculas/minúsculas)
        role_norm = role.strip().lower()
        if role_norm in ("administrador", "admin"):
            role_norm = "admin"
        elif role_norm in ("conductor", "driver"):
            role_norm = "driver"
        else:
            # rol desconocido → rechazamos
            return False

        # 5) Delegamos al modelo para que inserte el usuario en la BD
        return self.usuario_model.registrar_usuario(
            nombre_completo=nombre_completo,
            cedula=cedula,
            fecha_licencia=fecha_licencia,
            edad=edad,
            telefono=telefono,
            placa=placa,
            password=password,
            role=role_norm  # pasamos ya el rol normalizado
        )
