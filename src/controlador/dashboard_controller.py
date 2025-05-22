# Actualmente sólo esqueleto; luego pondrás métodos para cada pestaña
class DashboardController:
    def __init__(self):
        pass

    def load_encuestas(self, role):
        # Si role == "admin": traer todas las encuestas
        # else: traer sólo la encuesta asignada al conductor
        ...

    def load_notificaciones(self, role, user_id):
        # Si admin: todas las notifs
        # else: sólo las del user_id
        ...

    def load_reportes(self, role, user_id):
        # Igual que arriba
        ...