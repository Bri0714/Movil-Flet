## src/vista/admin_encuesta_view.py
#
#import flet as ft
#from controlador.encuesta_controller import EncuestaController
#import threading
#import time
#
#class AdminEncuestaView:
#    def __init__(self, page: ft.Page):
#        self.page = page
#        self.controller = EncuestaController()
#        self.opt_fields = [ft.TextField(label="Opción 1", width=300)]
#        colores = ["Red","Orange","Yellow","Green","Blue","Indigo","Violet","Pink","Teal",
#                  "Cyan","Magenta","Lime","Amber","DeepOrange","Brown","Grey","BlueGrey",
#                  "LightBlue","LightGreen","DeepPurple"]
#        self.color_dropdown = ft.Dropdown(
#            label="Color del contenedor",
#            width=300,
#            options=[ft.dropdown.Option(c, c.lower()) for c in colores],
#            value="blue"
#        )
#        self.cat_input  = ft.TextField(label="Categoría",    width=300)
#        self.desc_input = ft.TextField(label="Descripción",  width=300, multiline=True)
#        self.options_container = ft.Column(self.opt_fields, spacing=10)
#        
#        # Notificación tipo container (inicialmente oculta)
#        self.notification_container = ft.Container(
#            content=ft.Row([
#                ft.Icon(ft.icons.CHECK_CIRCLE, color="white", size=20),
#                ft.Text("Mensaje", color="white", weight="bold", size=14),
#            ], spacing=8),
#            bgcolor="#4CAF50",  # Verde por defecto
#            padding=ft.padding.symmetric(horizontal=16, vertical=12),
#            border_radius=8,
#            margin=ft.margin.only(top=10, bottom=0),
#            visible=False,  # Oculto al inicio
#            shadow=ft.BoxShadow(
#                spread_radius=1,
#                blur_radius=8,
#                color=ft.colors.with_opacity(0.3, ft.colors.BLACK),
#                offset=ft.Offset(0, 2),
#            )
#        )
#
#    def show_notification(self, message, success=True, duration=5):
#        if success:
#            color = "#4CAF50"  # Verde
#            icon = ft.icons.CHECK_CIRCLE
#        else:
#            color = "#F44336"  # Rojo
#            icon = ft.icons.ERROR
#
#        self.notification_container.bgcolor = color
#        self.notification_container.content.controls[0].name = icon
#        self.notification_container.content.controls[1].value = message
#        self.notification_container.visible = True
#        self.page.update()
#
#        def hide_notification():
#            time.sleep(duration)
#            self.notification_container.visible = False
#            self.page.update()
#        threading.Thread(target=hide_notification, daemon=True).start()
#
#    def _refresh_options(self):
#        for i, f in enumerate(self.opt_fields, start=1):
#            f.label = f"Opción {i}"
#        self.options_container.controls = list(self.opt_fields)
#        self.page.update()
#
#    def on_add_option(self, e):
#        if len(self.opt_fields) < 20:
#            self.opt_fields.append(ft.TextField(label=f"Opción {len(self.opt_fields)+1}", width=300))
#            self._refresh_options()
#
#    def on_remove_option(self, e):
#        if len(self.opt_fields) > 1:
#            self.opt_fields.pop()
#            self._refresh_options()
#
#    def on_create(self, e):
#        cat = self.cat_input.value.strip()
#        desc = self.desc_input.value.strip()
#        color = self.color_dropdown.value
#        opts = [f.value.strip() for f in self.opt_fields if f.value.strip()]
#        if not cat or not desc or not opts:
#            self.show_notification("❌ Completa categoría, descripción y al menos 1 opción", success=False)
#            return
#        self.controller.crear_encuesta(cat, desc, opts, color)
#        self.show_notification("✅ Encuesta creada correctamente", success=True)
#        # limpiar
#        self.cat_input.value = ""; self.desc_input.value = ""
#        self.color_dropdown.value = "blue"
#        for f in self.opt_fields: f.value = ""
#        self.page.update()
#
#    def build(self):
#        role = getattr(self.page, "user_role", "driver").lower()
#        title = "Crear nueva encuesta (Administrador)" if role=="admin" else "Crear nueva encuesta (Conductor)"
#        
#        admin_btn = None
#        if role == "admin":
#            admin_btn = ft.ElevatedButton(
#                "Administración de encuestas",
#                icon=ft.icons.MANAGE_ACCOUNTS,
#                bgcolor="#1976D2",
#                color="white",
#                on_click=self.goto_gestion_encuestas,
#                width=260,
#                style=ft.ButtonStyle(
#                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
#                    shape=ft.RoundedRectangleBorder(radius=10)
#                )
#            )
#
#        main = ft.Column(
#            [
#                ft.Text(title, size=22, weight="bold"),
#                ft.Divider(),
#                self.cat_input,
#                self.desc_input,
#                self.color_dropdown,
#                ft.Row(
#                    [
#                        ft.ElevatedButton("➕ Añadir opción", on_click=self.on_add_option),
#                        ft.ElevatedButton("➖ Eliminar opción", on_click=self.on_remove_option),
#                    ],
#                    spacing=20
#                ),
#                self.options_container,
#                ft.ElevatedButton("Crear encuesta", on_click=self.on_create, width=200),
#                admin_btn if admin_btn else ft.Container(),
#                self.notification_container
#            ],
#            spacing=15,
#            scroll=ft.ScrollMode.AUTO,
#            expand=True,
#            horizontal_alignment=ft.CrossAxisAlignment.CENTER
#        )
#        return ft.Container(
#            content=main,
#            padding=20,
#            alignment=ft.alignment.center,
#            expand=True
#        )
#
#    def goto_gestion_encuestas(self, e):
#        # Cambia la página a la nueva vista (agrega esta ruta en tu router si es necesario)
#        self.page.go("/admin_gestion_encuestas")

# src/vista/admin_encuesta_view.py

import flet as ft
import threading, time
from controlador.encuesta_controller import EncuestaController

class AdminEncuestaView:
    """Crear o editar encuestas (admin) con notificación visible.

    El problema era que el contenedor de notificación quedaba al final del
    `Column`, fuera del viewport cuando el scroll estaba arriba, por eso el
    usuario no lo veía. Ahora se ubica justo debajo del título, como en las
    otras vistas.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.controller = EncuestaController()

        # ¿Modo edición?
        encuesta_editar = getattr(self.page, "encuesta_editar", None)
        self.editando = encuesta_editar is not None
        self.encuesta_id: str | None = None

        # --------------------------------------
        # Campos base
        # --------------------------------------
        def _color_dd(value="blue"):
            colores = [
                "Red","Orange","Yellow","Green","Blue","Indigo","Violet","Pink","Teal",
                "Cyan","Magenta","Lime","Amber","DeepOrange","Brown","Grey","BlueGrey",
                "LightBlue","LightGreen","DeepPurple"
            ]
            return ft.Dropdown(
                label="Color del contenedor",
                width=300,
                value=value,
                options=[ft.dropdown.Option(c, c.lower()) for c in colores],
            )

        if self.editando:
            self.encuesta_id = str(encuesta_editar["_id"])
            self.cat_input = ft.TextField(label="Categoría", value=encuesta_editar.get("categoria", ""), width=300)
            self.desc_input = ft.TextField(label="Descripción", value=encuesta_editar.get("descripcion", ""), width=300, multiline=True)
            self.color_dropdown = _color_dd(encuesta_editar.get("color", "blue"))
            self.opt_fields = [
                ft.TextField(label=f"Opción {i+1}", value=o["texto"], width=300)
                for i, o in enumerate(encuesta_editar.get("opciones", []))
            ] or [ft.TextField(label="Opción 1", width=300)]
        else:
            self.cat_input = ft.TextField(label="Categoría", width=300)
            self.desc_input = ft.TextField(label="Descripción", width=300, multiline=True)
            self.color_dropdown = _color_dd()
            self.opt_fields = [ft.TextField(label="Opción 1", width=300)]

        self.options_container = ft.Column(self.opt_fields, spacing=10)
        self._init_notification()

    # ------------------------------------------------------------------
    # Notificación
    # ------------------------------------------------------------------
    def _init_notification(self):
        self.notification_container = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.CHECK_CIRCLE, color="white", size=20),
                ft.Text("Mensaje", color="white", weight="bold", size=14),
            ], spacing=8),
            bgcolor="#4CAF50",
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_radius=8,
            visible=False,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.colors.with_opacity(0.3, ft.colors.BLACK), offset=ft.Offset(0, 2)),
        )

    def _show_notification(self, msg: str, success: bool = True, duration: int = 3):
        color, icon = ("#4CAF50", ft.icons.CHECK_CIRCLE) if success else ("#F44336", ft.icons.ERROR)
        self.notification_container.bgcolor = color
        self.notification_container.content.controls[0].name = icon
        self.notification_container.content.controls[1].value = msg
        self.notification_container.visible = True
        self.page.update()

        def hide():
            time.sleep(duration)
            self.notification_container.visible = False
            self.page.update()
        threading.Thread(target=hide, daemon=True).start()

    # ------------------------------------------------------------------
    # Utilidades de opciones
    # ------------------------------------------------------------------
    def _refresh_options(self):
        for i, field in enumerate(self.opt_fields, start=1):
            field.label = f"Opción {i}"
        self.options_container.controls = list(self.opt_fields)
        self.page.update()

    def on_add_option(self, _):
        if len(self.opt_fields) < 20:
            self.opt_fields.append(ft.TextField(label=f"Opción {len(self.opt_fields)+1}", width=300))
            self._refresh_options()

    def on_remove_option(self, _):
        if len(self.opt_fields) > 1:
            self.opt_fields.pop()
            self._refresh_options()

    # ------------------------------------------------------------------
    # Crear / Actualizar
    # ------------------------------------------------------------------
    def _collect_values(self):
        cat = self.cat_input.value.strip()
        desc = self.desc_input.value.strip()
        color = self.color_dropdown.value
        opts = [f.value.strip() for f in self.opt_fields if f.value.strip()]
        return cat, desc, color, opts

    def on_create(self, _):
        cat, desc, color, opts = self._collect_values()
        if not (cat and desc and opts):
            self._show_notification("❌ Completa categoría, descripción y al menos 1 opción", success=False)
            return
        self.controller.crear_encuesta(cat, desc, opts, color)
        self._show_notification("✅ Encuesta creada correctamente")
        # Limpiar campos
        self.cat_input.value = ""
        self.desc_input.value = ""
        self.color_dropdown.value = "blue"
        for f in self.opt_fields:
            f.value = ""
        # Si venía de modo edición, limpiamos flag
        if hasattr(self.page, "encuesta_editar"):
            delattr(self.page, "encuesta_editar")
        self.page.update()

    def on_update(self, _):
        cat, desc, color, opts = self._collect_values()
        if not (cat and desc and opts):
            self._show_notification("❌ Completa categoría, descripción y al menos 1 opción", success=False)
            return
        ok = self.controller.actualizar_encuesta(self.encuesta_id, cat, desc, opts, color)
        if ok:
            self._show_notification("✅ Encuesta actualizada correctamente")
            if hasattr(self.page, "encuesta_editar"):
                delattr(self.page, "encuesta_editar")
            self.page.go("/admin_encuesta")  # Reset a modo creación
        else:
            self._show_notification("❌ Error al actualizar encuesta", success=False)

    # ------------------------------------------------------------------
    # Navegación
    # ------------------------------------------------------------------
    def on_admin_gestion(self, _):
        self.page.go("/admin_gestion_encuestas")

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------
    def build(self):
        title = "Editar encuesta" if self.editando else "Crear nueva encuesta (Administrador)"
        layout = ft.Column([
            ft.Text(title, size=22, weight="bold"),
            self.notification_container,  # ¡Notificación justo debajo del título!
            ft.Divider(),
            ft.ElevatedButton("Administrar encuestas", icon=ft.icons.LIBRARY_BOOKS, on_click=self.on_admin_gestion, width=220, bgcolor="#1976D2", color="white"),
            self.cat_input,
            self.desc_input,
            self.color_dropdown,
            ft.Row([
                ft.ElevatedButton("➕ Añadir opción", on_click=self.on_add_option),
                ft.ElevatedButton("➖ Eliminar opción", on_click=self.on_remove_option),
            ], spacing=20),
            self.options_container,
            ft.ElevatedButton(
                "Actualizar encuesta" if self.editando else "Crear encuesta",
                on_click=self.on_update if self.editando else self.on_create,
                width=200,
                bgcolor="#1976D2" if self.editando else "#388E3C",
                color="white",
            ),
        ], spacing=15, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

        return ft.Container(content=layout, padding=20, alignment=ft.alignment.center, expand=True)
