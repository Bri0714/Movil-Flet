#import flet as ft
#from vista.login_view import LoginView
#from vista.register_view import RegisterView
#from vista.dashboard_view import DashboardView
#from vista.perfil_view import PerfilView
#from vista.inspeccion_detalle_view import InspeccionDetalleView
#
#def main(page: ft.Page):
#    page.title = "PreopEscolar"
#    page.window_width = 800
#    page.window_height = 650
#    page.padding = 0
#    page.vertical_alignment = "center"
#    page.horizontal_alignment = "center"
#
#    def route_change(route):
#        page.clean()
#        view = None
#
#        # Si el usuario está autenticado
#        if getattr(page, "user", None) is not None:
#            # Si intenta ir a login o registro, redirigimos a /home
#            if page.route in ["/login", "/register"]:
#                page.go("/home")
#                return
#
#            # --------- VISTAS PROTEGIDAS ----------
#            if page.route in ["/home", "/dashboard"]:
#                dashboard = DashboardView(page)
#                page.end_drawer = dashboard.end_drawer
#                view = dashboard.build()
#
#            elif page.route == "/perfil":
#                from vista.perfil_view import PerfilView
#                perfil_view = PerfilView(page)
#                view = perfil_view.build()
#
#            elif page.route == "/detalle":
#                # Busca el dict de inspección a mostrar, por ejemplo en session o como atributo temporal
#                inspeccion = getattr(page, "inspeccion_actual", None)
#                if inspeccion:
#                    from vista.inspeccion_detalle_view import InspeccionDetalleView
#                    view = InspeccionDetalleView(page, inspeccion).build()
#                else:
#                    view = ft.Text("No hay detalle para mostrar.", size=20)
#            elif page.route == "/admin_gestion_encuestas":
#                from vista.admin_gestion_encuestas_view import AdminGestionEncuestasView
#                view = AdminGestionEncuestasView(page).build()
#            else:
#                # Cualquier otra ruta → dashboard por defecto
#                dashboard = DashboardView(page)
#                page.end_drawer = dashboard.end_drawer
#                view = dashboard.build()
#
#        else:
#            # Usuario NO autenticado
#            page.end_drawer = None
#            if page.route == "/register":
#                view = RegisterView(page).build()
#            elif page.route == "/login":
#                view = LoginView(page).build()
#            else:
#                page.go("/login")
#                return
#
#        page.add(view)
#        page.update()
#
#    # Asigna la función para manejo de rutas
#    page.on_route_change = route_change
#
#    # Ruta inicial
#    page.go("/login")
#
#ft.app(
#    target=main,
#    view=ft.AppView.WEB_BROWSER,
#    port=8550,
#    host="0.0.0.0"
#)
import flet as ft
from vista.login_view import LoginView
from vista.register_view import RegisterView
from vista.dashboard_view import DashboardView
from vista.perfil_view import PerfilView
from vista.inspeccion_detalle_view import InspeccionDetalleView

# 👇 Importa tus nuevas vistas para administración de encuestas
from vista.admin_gestion_encuestas_view import AdminGestionEncuestasView
from vista.admin_encuesta_view import AdminEncuestaView

def main(page: ft.Page):
    page.title = "PreopEscolar"
    page.window_width = 800
    page.window_height = 650
    page.padding = 0
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    def route_change(route):
        page.clean()
        view = None

        # Si el usuario está autenticado
        if getattr(page, "user", None) is not None:
            # Si intenta ir a login o registro, redirigimos a /home
            if page.route in ["/login", "/register"]:
                page.go("/home")
                return

            # --------- VISTAS PROTEGIDAS ----------
            if page.route in ["/home", "/dashboard"]:
                dashboard = DashboardView(page)
                page.end_drawer = dashboard.end_drawer
                view = dashboard.build()

            elif page.route == "/perfil":
                perfil_view = PerfilView(page)
                view = perfil_view.build()

            elif page.route == "/detalle":
                inspeccion = getattr(page, "inspeccion_actual", None)
                if inspeccion:
                    view = InspeccionDetalleView(page, inspeccion).build()
                else:
                    view = ft.Text("No hay detalle para mostrar.", size=20)

            # 👇 NUEVAS RUTAS de admin para encuestas
            elif page.route == "/admin_gestion_encuestas":
                view = AdminGestionEncuestasView(page).build()

            elif page.route == "/admin_encuesta":
                view = AdminEncuestaView(page).build()

            else:
                dashboard = DashboardView(page)
                page.end_drawer = dashboard.end_drawer
                view = dashboard.build()

        else:
            # Usuario NO autenticado
            page.end_drawer = None
            if page.route == "/register":
                view = RegisterView(page).build()
            elif page.route == "/login":
                view = LoginView(page).build()
            else:
                page.go("/login")
                return

        page.add(view)
        page.update()

    # Asigna la función para manejo de rutas
    page.on_route_change = route_change

    # Ruta inicial
    page.go("/login")

ft.app(
    target=main,
    view=ft.AppView.WEB_BROWSER,
    port=8550,
    host="0.0.0.0"
)
