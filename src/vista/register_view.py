# src/vista/register_view.py

import flet as ft
import datetime
from src.controlador.register_controller import RegisterController

class RegisterView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.controller = RegisterController()

        # Campo: Nombre completo
        self.nombre_input = ft.TextField(
            width=280,
            height=40,
            hint_text="Nombre completo",
            border="underline",
            prefix_icon=ft.icons.PERSON,
        )
        # Campo: Cédula
        self.cedula_input = ft.TextField(
            width=280,
            height=40,
            hint_text="Número de cédula",
            border="underline",
            prefix_icon=ft.icons.DOCUMENT_SCANNER,
        )
        # Campo: Fecha de expedición (manual, con hint)
        self.fecha_input = ft.TextField(
            width=280,
            height=40,
            hint_text="Fecha de expedición (YYYY-MM-DD)",
            border="underline",
            prefix_icon=ft.icons.CALENDAR_MONTH,
        )
        # Campo: Edad
        self.edad_input = ft.TextField(
            width=280,
            height=40,
            hint_text="Edad",
            border="underline",
            prefix_icon=ft.icons.CALENDAR_VIEW_DAY,
        )
        # Campo: Teléfono
        self.telefono_input = ft.TextField(
            width=280,
            height=40,
            hint_text="Número de teléfono",
            border="underline",
            prefix_icon=ft.icons.PHONE,
        )
        # Campo: Placa de vehículo
        self.placa_input = ft.TextField(
            width=280,
            height=40,
            hint_text="Placa del vehículo",
            border="underline",
            prefix_icon=ft.icons.DIRECTIONS_CAR,
        )
        # Campo: Contraseña
        self.password_input = ft.TextField(
            width=280,
            height=40,
            hint_text="Contraseña",
            border="underline",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.icons.LOCK,
        )
        # Dropdown: Rol (Conductor o Administrador)
        self.role_dropdown = ft.Dropdown(
            width=280,
            options=[
                ft.dropdown.Option("Conductor", "driver"),
                ft.dropdown.Option("Administrador", "admin"),
            ],
            value="driver",
        )
        # Texto para mostrar errores o éxito
        self.feedback_text = ft.Text(
            value="",
            size=14,
            weight="w600",
            text_align="center",
        )

    def build(self):
        """Construye y devuelve el layout completo de la pantalla."""
        # Agrupamos todos los campos en una columna con scroll
        form = ft.Column(
            [
                ft.Text("Crear Cuenta", size=30, weight="w900"),
                self.nombre_input,
                self.cedula_input,
                self.fecha_input,
                self.edad_input,
                self.telefono_input,
                self.placa_input,
                self.password_input,
                self.role_dropdown,
                ft.Container(
                    ft.ElevatedButton(
                        text="REGISTRARSE",
                        width=280,
                        on_click=self.on_register_click  # handler recibe automáticamente el evento
                    ),
                    padding=ft.padding.symmetric(vertical=20),
                ),
                self.feedback_text,
                ft.Row(
                    [
                        ft.Text("¿Ya tiene una cuenta?"),
                        ft.TextButton("Iniciar sesión", on_click=lambda e: self.page.go("/login"))
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,  # habilita scroll si hace falta
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Contenedor con degradado de fondo
        container = ft.Container(
            content=form,
            gradient=ft.LinearGradient(colors=["red", "orange"]),
            width=380,
            border_radius=20,
            padding=20,
        )

        # Centrar el contenedor en la página
        return ft.Container(
            content=ft.Row([container], alignment=ft.MainAxisAlignment.CENTER),
            padding=10,
        )

    def on_register_click(self, e):
        """Se ejecuta al pulsar 'REGISTRARSE'."""
        # Leemos valores
        nombre = self.nombre_input.value.strip()
        cedula = self.cedula_input.value.strip()
        fecha_str = self.fecha_input.value.strip()
        edad = self.edad_input.value.strip()
        telefono = self.telefono_input.value.strip()
        placa = self.placa_input.value.strip()
        password = self.password_input.value
        role = self.role_dropdown.value

        # Validaciones básicas
        if not all([nombre, cedula, fecha_str, edad, telefono, placa, password]):
            self.feedback_text.value = "❌ Todos los campos son obligatorios."
            self.feedback_text.color = "red"
            self.page.update()
            return

        # Fecha: comprobamos formato y existencia
        try:
            fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            self.feedback_text.value = "❌ Fecha inválida. Formato YYYY-MM-DD."
            self.feedback_text.color = "red"
            self.page.update()
            return

        # Edad numérica y ≥ 18
        if not edad.isdigit() or int(edad) < 18:
            self.feedback_text.value = "❌ Edad debe ser número ≥ 18."
            self.feedback_text.color = "red"
            self.page.update()
            return

        # Teléfono numérico
        if not telefono.isdigit():
            self.feedback_text.value = "❌ Teléfono inválido."
            self.feedback_text.color = "red"
            self.page.update()
            return

        # Intentamos registrar en el controlador
        ok = self.controller.registrar(
            nombre, cedula, fecha_str, edad, telefono, placa, password, role
        )
        if ok:
            # Éxito: mensaje verde y redirección inmediata
            self.feedback_text.value = "✔️ Registro exitoso. Redirigiendo..."
            self.feedback_text.color = "green"
            self.page.update()
            # redirigimos al login
            self.page.go("/login")
        else:
            # Ya existe usuario o fallo interno
            self.feedback_text.value = "❌ Error en registro (usuario ya existe?)."
            self.feedback_text.color = "red"
            self.page.update()
