import flet as ft
from controlador.dashboard_controller import DashboardController
from controlador.notificacion_controller import NotificacionController   # <--- IMPORTANTE
from vista.admin_encuesta_view import AdminEncuestaView
from vista.driver_encuesta_view import DriverEncuestaView
from vista.reportes_view import ReportesView
from vista.perfil_view import PerfilView
from vista.notificaciones_view import NotificacionesView

class DashboardView:
    def __init__(self, page: ft.Page):
        self.page = page
        # Controlador de lógica compartida (aún vacío)
        self.controller = DashboardController()
        # Índice de la pestaña activa (0=Encuesta, 1=Notificaciones, 2=Reportes)
        self.selected_index = 0

        # ─── Genera notificaciones pendientes si el usuario es admin ───
        role = getattr(self.page, "user_role", "").lower()
        if role == "admin":
            # Solo si es admin
            NotificacionController().generar_notificaciones_pendientes()

        # ─── DRAWER LATERAL (perfil, logout) ─────────────────────────────────────
        self.end_drawer = ft.NavigationDrawer(
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            # Logo en la cabecera del drawer
                            ft.Container(
                                ft.Image(src="logo.jpg", width=120),
                                alignment=ft.alignment.center,
                                padding=ft.padding.all(20)
                            ),
                            ft.Divider(),
                            # Opción: ver perfil
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.PERSON),
                                title=ft.Text("Perfil"),
                                on_click=self.ver_perfil
                            ),
                            # Opción: cerrar sesión
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.LOGOUT),
                                title=ft.Text("Cerrar sesión"),
                                on_click=self.cerrar_sesion
                            ),
                        ],
                        spacing=10
                    )
                )
            ]
        )

        # ─── BARRA DE NAVEGACIÓN INFERIOR ──────────────────────────────────────────
        is_admin = role == "admin"
        nav_icon = ft.icons.ADD_BOX if is_admin else ft.icons.LIST_ALT

        self.nav = ft.NavigationBar(
            selected_index=self.selected_index,
            on_change=self.on_nav_change,
            destinations=[
                ft.NavigationBarDestination(icon=nav_icon, label="Encuesta"),
                ft.NavigationBarDestination(icon=ft.icons.NOTIFICATIONS, label="Notificaciones"),
                ft.NavigationBarDestination(icon=ft.icons.ASSESSMENT, label="Reportes"),
            ],
        )

    def build(self):
        # ─── TOP BAR ───────────────────────────────────────────────────────────────
        top_bar = ft.Row(
            [
                ft.IconButton(icon=ft.icons.MENU, on_click=self.abrir_drawer),
                ft.Image(src="logo.jpg", width=100, height=50, fit=ft.ImageFit.CONTAIN)
            ],
            alignment=ft.MainAxisAlignment.START
        )

        self.content = ft.Container(
            content=self._get_body(),
            expand=True,
            padding=20
        )

        self.page.end_drawer = self.end_drawer

        return ft.Column(
            [
                top_bar,
                self.content,
                ft.Divider(),
                self.nav,
            ],
            expand=True,
        )

    def abrir_drawer(self, e):
        self.page.end_drawer.open = True
        self.page.update()

    def _get_body(self):
        raw_role = getattr(self.page, "user_role", "driver")
        role = raw_role.lower() if isinstance(raw_role, str) else raw_role

        if self.selected_index == 0:
            if role == "admin":
                return AdminEncuestaView(self.page).build()
            else:
                return DriverEncuestaView(self.page).build()

        elif self.selected_index == 1:
            # Reemplaza el texto por la vista real
            return NotificacionesView(self.page).build()


        elif self.selected_index == 2:
            return ReportesView(self.page).build()
    
        return ft.Text("Sección desconocida", size=20)

    def on_nav_change(self, e: ft.ControlEvent):
        self.selected_index = e.control.selected_index
        self.content.content = self._get_body()
        self.page.update()

    def ver_perfil(self, e):
        self.selected_index = -1
        self.content.content = PerfilView(self.page).build()
        self.page.end_drawer.open = False
        self.page.update()

    def cerrar_sesion(self, e):
        self.page.user = None
        self.page.user_role = None
        self.page.end_drawer = None
        self.page.go("/login")
