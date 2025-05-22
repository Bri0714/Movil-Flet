#import flet as ft
#from controlador.encuesta_controller import EncuestaController
#
#class AdminGestionEncuestasView:
#    def __init__(self, page: ft.Page):
#        self.page = page
#        self.controller = EncuestaController()
#        self.encuestas = self.controller.obtener_encuestas(role="admin", cedula="")
#
#    def build(self):
#        rows = []
#        if not self.encuestas:
#            rows.append(
#                ft.Container(
#                    ft.Text("No hay encuestas creadas.", size=16, color="#888", text_align=ft.TextAlign.CENTER),
#                    padding=16, alignment=ft.alignment.center
#                )
#            )
#        else:
#            for enc in self.encuestas:
#                color = enc.get("color", "grey")
#                categoria = enc.get("categoria", "Sin nombre")
#                enc_id = str(enc.get("_id"))
#                rows.append(
#                    ft.Container(
#                        ft.Row([
#                            ft.Container(
#                                ft.Text(categoria, size=16, weight="bold", color="white", text_align=ft.TextAlign.LEFT),
#                                bgcolor=color,
#                                border_radius=8,
#                                padding=ft.padding.symmetric(horizontal=14, vertical=10),
#                                expand=True
#                            ),
#                            ft.IconButton(
#                                icon=ft.icons.EDIT,
#                                tooltip="Editar encuesta",
#                                icon_color="#1976D2",
#                                on_click=lambda e, id=enc_id: self.on_editar(id),
#                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7))
#                            ),
#                            ft.IconButton(
#                                icon=ft.icons.DELETE,
#                                tooltip="Eliminar encuesta",
#                                icon_color="#D32F2F",
#                                on_click=lambda e, id=enc_id: self.on_eliminar(id),
#                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7))
#                            )
#                        ], spacing=12, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
#                        bgcolor="#F5F5F5",
#                        border_radius=12,
#                        padding=ft.padding.symmetric(horizontal=8, vertical=6),
#                        margin=ft.margin.only(bottom=11),
#                        expand=True
#                    )
#                )
#
#        # Título y botón volver
#        titulo = ft.Container(
#            ft.Row([
#                ft.Icon(ft.icons.LIST_ALT, color="#1976D2", size=26),
#                ft.Text("Administración de encuestas", size=21, weight="bold", color="#1976D2"),
#            ], spacing=12, alignment=ft.MainAxisAlignment.CENTER),
#            alignment=ft.alignment.center,
#            padding=ft.padding.only(top=16, bottom=14)
#        )
#
#        volver_btn = ft.ElevatedButton(
#            "Volver",
#            icon=ft.icons.ARROW_BACK,
#            bgcolor="#1976D2", color="white",
#            width=150,
#            on_click=lambda e: self.page.go("/home")
#        )
#
#        return ft.Container(
#            content=ft.Column(
#                [
#                    titulo,
#                    ft.Divider(),
#                    *rows,
#                    ft.Container(volver_btn, alignment=ft.alignment.center, padding=14)
#                ],
#                expand=True, scroll=ft.ScrollMode.AUTO, spacing=6
#            ),
#            expand=True,
#            padding=ft.padding.symmetric(horizontal=14, vertical=5),
#            alignment=ft.alignment.center
#        )
#
#    # Métodos vacíos para implementar después
#    def on_editar(self, encuesta_id):
#        # Aquí luego muestras un formulario de edición
#        pass
#
#    def on_eliminar(self, encuesta_id):
#        # Aquí luego implementas confirmación y borrado
#        pass

# archivo: vista/admin_gestion_encuestas_view.py

import flet as ft
from controlador.encuesta_controller import EncuestaController
import threading, time

class AdminGestionEncuestasView:
    """Vista para listar, editar y **eliminar** encuestas.

    ‣ Eliminar ahora es **directo**: se ejecuta la operación en MongoDB
      y se refresca la lista sin diálogo de confirmación.
    ‣ Se muestra una notificación tipo *snack* igual que en
      `DriverEncuestaView`.
    """

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------
    def __init__(self, page: ft.Page):
        self.page = page
        self.controller = EncuestaController()
        self.encuestas_container: ft.Column | None = None
        self.notification_container: ft.Container | None = None

    # ------------------------------------------------------------------
    # Notificación reutilizable
    # ------------------------------------------------------------------
    def _show_notification(self, message: str, success: bool = True, duration: int = 4):
        color, icon = ("#4CAF50", ft.icons.CHECK_CIRCLE) if success else ("#F44336", ft.icons.ERROR)
        self.notification_container.bgcolor = color
        self.notification_container.content.controls[0].name = icon
        self.notification_container.content.controls[1].value = message
        self.notification_container.visible = True
        self.page.update()

        def hide():
            time.sleep(duration)
            self.notification_container.visible = False
            self.page.update()

        threading.Thread(target=hide, daemon=True).start()

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------
    def _load_rows(self):
        """Recupera las encuestas y construye las filas en el Column."""
        encuestas = self.controller.obtener_encuestas("admin", "")
        rows: list[ft.Control] = []
        if not encuestas:
            rows.append(
                ft.Container(
                    ft.Text("No hay encuestas disponibles", size=16, color="#666666", text_align=ft.TextAlign.CENTER),
                    alignment=ft.alignment.center,
                    padding=20,
                )
            )
        else:
            for enc in encuestas:
                rows.append(self._build_row(enc))
        self.encuestas_container.controls = rows
        self.page.update()

    def _build_row(self, encuesta: dict) -> ft.Container:
        color = encuesta.get("color", "#1976D2")
        categoria = encuesta.get("categoria", "Sin nombre")
        return ft.Container(
            ft.Row([
                ft.Container(
                    ft.Text(categoria, size=15, weight="bold", color="white"),
                    bgcolor=color,
                    border_radius=7,
                    padding=ft.padding.symmetric(horizontal=14, vertical=8),
                    expand=True,
                ),
                ft.IconButton(
                    ft.icons.EDIT,
                    tooltip="Editar",
                    icon_color="#FFC107",
                    on_click=lambda e, enc=encuesta: self.on_editar(enc),
                ),
                ft.IconButton(
                    ft.icons.DELETE,
                    tooltip="Eliminar",
                    icon_color="#F44336",
                    on_click=lambda e, enc=encuesta: self.on_eliminar(enc),
                ),
            ], spacing=10),
            bgcolor="#F5F5F5",
            border_radius=10,
            padding=ft.padding.symmetric(vertical=7, horizontal=10),
            margin=ft.margin.only(bottom=9),
        )

    # ------------------------------------------------------------------
    # Eventos
    # ------------------------------------------------------------------
    def on_editar(self, encuesta):
        self.page.encuesta_editar = encuesta
        self.page.go("/admin_encuesta")

    def on_eliminar(self, encuesta):
        """Elimina la encuesta SIN confirmación y actualiza la lista."""
        enc_id = str(encuesta["_id"])
        print("[DEBUG] Eliminar encuesta:", enc_id)
        eliminado = False
        try:
            eliminado = self.controller.eliminar_encuesta(enc_id)
            print("[DEBUG] Resultado deleted_count>", eliminado)
        except Exception as ex:
            print("[ERROR] excepción al eliminar:", ex)
        if eliminado:
            self._show_notification("Encuesta eliminada correctamente")
        else:
            self._show_notification("No se pudo eliminar la encuesta", success=False)
        # Refrescar tabla siempre
        self._load_rows()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------
    def build(self):
        # Contenedor de notificaciones (invisible por defecto)
        self.notification_container = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.CHECK_CIRCLE, color="white", size=18),
                ft.Text("", color="white", weight="bold"),
            ], spacing=8),
            bgcolor="#4CAF50",
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border_radius=8,
            visible=False,
        )

        # Column con scroll para listas
        self.encuestas_container = ft.Column(
            [],
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
        self._load_rows()

        main = ft.Column([
            self.notification_container,
            ft.Row([
                ft.Icon(ft.icons.LIBRARY_BOOKS, color="#1976D2"),
                ft.Text("Administración de encuestas", size=21, weight="bold", color="#1976D2"),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            ft.Divider(),
            ft.Container(content=self.encuestas_container, expand=True, padding=ft.padding.symmetric(horizontal=5)),
            ft.Container(
                ft.ElevatedButton("← Volver", width=180, bgcolor="#1976D2", color="white", on_click=lambda e: self.page.go("/home")),
                alignment=ft.alignment.center,
                margin=ft.margin.only(top=12),
            ),
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

        return ft.Container(content=main, padding=18, expand=True, alignment=ft.alignment.center)
