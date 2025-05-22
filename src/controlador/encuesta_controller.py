from modelo.encuesta_model import EncuestaModel

class EncuestaController:
    def __init__(self):
        self.model = EncuestaModel()

    def crear_encuesta(self, categoria: str, descripcion: str, opciones: list[str], color: str) -> str:
        return self.model.crear_encuesta(categoria, descripcion, opciones, color)

    def obtener_encuestas(self, role: str, cedula: str) -> list[dict]:
        return self.model.obtener_encuestas()

    def guardar_inspeccion(self, placa: str, kilometraje: int, respuestas: list[dict], evidencias: list[str], observaciones: str, cedula: str, nombre: str) -> str:
        return self.model.guardar_inspeccion(placa, kilometraje, respuestas, evidencias, observaciones, cedula, nombre)

    def obtener_inspecciones(self, fecha_ini, fecha_fin, role="driver", cedula=None):
        return self.model.obtener_inspecciones(fecha_ini, fecha_fin, role, cedula)

    def actualizar_encuesta(self, encuesta_id, categoria, descripcion, opciones, color):
        return self.model.actualizar_encuesta(encuesta_id, categoria, descripcion, opciones, color)

    def eliminar_encuesta(self, encuesta_id):
        return self.model.eliminar_encuesta(encuesta_id)
