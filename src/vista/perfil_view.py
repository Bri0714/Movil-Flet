import flet as ft
import threading, time
from controlador.usuario_controller import UsuarioController

class PerfilView:
    """Formulario de perfil con mensaje de éxito/error siempre visible.
    La notificación se coloca ahora *justo debajo* del título para que no
    quede fuera de la vista cuando la columna haga scroll.
    """
    def __init__(self, page: ft.Page):
        self.page = page
        self.controller = UsuarioController()

        # --- Datos de la sesión ---
        user = getattr(page, "user", {})
        self.cedula = user.get("cedula", "")
        self.nombre = user.get("nombre_completo", "")
        self.fecha_licencia = user.get("fecha_licencia", "")
        self.edad = user.get("edad", "")
        self.telefono = user.get("telefono", "")
        self.placa = user.get("placa", "")

        # --- Campos ---
        self.cedula_field = ft.TextField(label="Cédula", value=self.cedula, read_only=True, width=320)
        self.nombre_field = ft.TextField(label="Nombre completo", value=self.nombre, width=320)
        self.fecha_licencia_field = ft.TextField(label="Fecha de licencia", value=self.fecha_licencia, width=320)
        self.edad_field = ft.TextField(label="Edad", value=str(self.edad), width=320)
        self.tel_field = ft.TextField(label="Teléfono", value=self.telefono, width=320, keyboard_type=ft.KeyboardType.PHONE)
        self.placa_field = ft.TextField(label="Placa", value=self.placa, width=320)

        # --- Notificación reutilizable (oculta) ---
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

    # ------------------------------------------------------------------
    # Notificación
    # ------------------------------------------------------------------
    def show_notification(self, message: str, success: bool = True, duration: int = 4):
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
    # Guardar
    # ------------------------------------------------------------------
    def on_save(self, _):
        nombre = self.nombre_field.value.strip()
        fecha_licencia = self.fecha_licencia_field.value.strip()
        edad = self.edad_field.value.strip()
        telefono = self.tel_field.value.strip()
        placa = self.placa_field.value.strip()

        # Validaciones
        if not all([nombre, fecha_licencia, edad, telefono, placa]):
            self.show_notification("❌ Todos los campos son obligatorios.", success=False)
            return
        if not edad.isdigit() or int(edad) < 18:
            self.show_notification("❌ Edad no válida (>= 18).", success=False)
            return

        updated = self.controller.actualizar_usuario(
            cedula=self.cedula,
            nombre_completo=nombre,
            fecha_licencia=fecha_licencia,
            edad=edad,
            telefono=telefono,
            placa=placa,
        )
        if updated:
            self.show_notification("✅ Perfil actualizado correctamente.", success=True)
            # Actualizar en sesión
            self.page.user.update({
                "nombre_completo": nombre,
                "fecha_licencia": fecha_licencia,
                "edad": edad,
                "telefono": telefono,
                "placa": placa,
            })
        else:
            self.show_notification("❌ Error al actualizar perfil.", success=False)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------
    def build(self):
        content = ft.Column([
            # Barra superior
            ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.page.go("/home")),
                ft.Text("Perfil de usuario", size=22, weight="bold"),
            ], alignment=ft.MainAxisAlignment.START),
            # Notificación SIEMPRE CERCA DE ARRIBA
            self.notification_container,
            ft.Divider(),
            self.cedula_field,
            self.nombre_field,
            self.fecha_licencia_field,
            self.edad_field,
            self.tel_field,
            self.placa_field,
            ft.ElevatedButton(
                "Guardar cambios",
                icon=ft.icons.SAVE,
                on_click=self.on_save,
                width=200,
                style=ft.ButtonStyle(color="white", bgcolor="#1976D2", elevation=5),
            ),
        ], spacing=14, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        return ft.Container(content=content, padding=20, expand=True, alignment=ft.alignment.center)
