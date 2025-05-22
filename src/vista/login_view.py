import flet as ft
from controlador.login_controller import LoginController

class LoginView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.controller = LoginController()
        self.cedula_input = ft.TextField(
            width=280,
            height=40,
            hint_text="Cédula",
            border="underline",
            color="black",
            prefix_icon=ft.icons.DOCUMENT_SCANNER
        )
        self.password_input = ft.TextField(
            width=280,
            height=40,
            hint_text="Contraseña",
            border="underline",
            color="black",
            prefix_icon=ft.icons.LOCK,
            password=True,
            can_reveal_password=True
        )
        self.error_text = ft.Text(value="", color="white", size=15, weight="w500", text_align="center")

    def build(self):
        login_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Iniciar Sesión", width=360, size=30, weight="w900", text_align="center"),
                    ft.Container(self.cedula_input, padding=ft.padding.symmetric(horizontal=20, vertical=10)),
                    ft.Container(self.password_input, padding=ft.padding.symmetric(horizontal=20, vertical=10)),
                    ft.Container(ft.Checkbox(label="Recordar contraseña", check_color="black"), padding=ft.padding.only(top=20)),
                    ft.Container(
                        ft.ElevatedButton(
                            content=ft.Text("INICIAR", color="white", weight="w500"),
                            width=280,
                            bgcolor="black",
                            on_click=lambda e: self.on_login_click()
                        ),
                        padding=ft.padding.symmetric(vertical=25, horizontal=10)
                    ),
                    self.error_text,
                    ft.Container(
                        ft.Row(
                            [
                                ft.Text("¿No tiene una cuenta?"),
                                ft.TextButton("Crear una cuenta", on_click=lambda e: self.page.go("/register"))
                            ],
                            spacing=8,
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        padding=ft.padding.only(top=20)
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            gradient=ft.LinearGradient(colors=["red", "orange"]),
            width=380,
            height=460,
            border_radius=20,
            padding=20
        )

        body = ft.Container(
            content=ft.Row([login_container], alignment=ft.MainAxisAlignment.CENTER),
            padding=10
        )
        return body

    def on_login_click(self):
        cedula = self.cedula_input.value
        password = self.password_input.value
        usuario = self.controller.login(cedula, password)
        if usuario:
            self.error_text.value = "Login exitoso."
            # Guarda la información del usuario en page para usarla luego
            self.page.user = usuario
            self.page.user_role = usuario.get("role", "driver")
            self.page.go("/home")
        else:
            self.error_text.value = "Cédula o contraseña incorrectos."
        self.page.update()
