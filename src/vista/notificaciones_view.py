import flet as ft
from controlador.notificacion_controller import NotificacionController

class NotificacionesView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.controller = NotificacionController()
        self.role = getattr(page, "user_role", "driver")
        self.user = getattr(page, "user", {})
        self.cedula = self.user.get("cedula", "")

        # Paginación
        self.items_per_page = 5
        self.current_page = 1

        self.data = []
        self.total_pages = 1

        self.get_data()
        self.notification_container = ft.Container()
        self.pagination_controls = self.build_pagination_controls()

    def get_data(self):
        if self.role == "admin":
            self.data = self.controller.get_admin_notificaciones()
        else:
            self.data = self.controller.get_driver_notificaciones(self.cedula)
        self.total_pages = max(1, (len(self.data) + self.items_per_page - 1) // self.items_per_page)
        self.current_page = min(self.current_page, self.total_pages)

    def build_pagination_controls(self):
        self.prev_btn = ft.TextButton(
            "Anterior",
            on_click=lambda e: self.change_page(-1),
            disabled=True
        )
        self.next_btn = ft.TextButton(
            "Siguiente",
            on_click=lambda e: self.change_page(1),
            disabled=True
        )
        self.page_indicators = []
        for i in range(1, 8):  # Hasta 7 páginas max en UI
            btn = ft.Container(
                content=ft.Text(str(i), color="white" if i == 1 else "black"),
                width=26, height=26,
                bgcolor="#1976D2" if i == 1 else "#E0E0E0",
                border_radius=13,
                alignment=ft.alignment.center,
                on_click=lambda e, pg=i: self.go_to_page(pg),
                visible=i <= self.total_pages
            )
            self.page_indicators.append(btn)

        return ft.Row(
            [self.prev_btn, *self.page_indicators, self.next_btn],
            alignment=ft.MainAxisAlignment.CENTER, spacing=6
        )

    def update_pagination(self):
        total_items = len(self.data)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        self.prev_btn.disabled = self.current_page <= 1
        self.next_btn.disabled = self.current_page >= self.total_pages

        for i, btn in enumerate(self.page_indicators):
            page_num = i + 1
            btn.visible = page_num <= self.total_pages
            btn.content.value = str(page_num)
            btn.bgcolor = "#1976D2" if page_num == self.current_page else "#E0E0E0"
            btn.content.color = "white" if page_num == self.current_page else "black"

    def change_page(self, delta):
        new_page = self.current_page + delta
        if 1 <= new_page <= self.total_pages:
            self.current_page = new_page
            self.page.update()

    def go_to_page(self, page_num):
        if 1 <= page_num <= self.total_pages:
            self.current_page = page_num
            self.page.update()

    def show_notification(self, message, success=True):
        color = "#4CAF50" if success else "#D32F2F"
        icon = ft.icons.CHECK_CIRCLE if success else ft.icons.ERROR
        self.notification_container.content = ft.Row(
            [
                ft.Icon(icon, color="white", size=20),
                ft.Text(message, color="white", weight="bold", size=14),
            ],
            spacing=8
        )
        self.notification_container.bgcolor = color
        self.notification_container.visible = True
        self.page.update()
        import threading, time
        def hide():
            time.sleep(2)
            self.notification_container.visible = False
            self.page.update()
        threading.Thread(target=hide, daemon=True).start()

    def on_accion_admin(self, notif_id):
        try:
            self.controller.marcar_enviada_admin(notif_id)
            self.get_data()
            self.update_pagination()
            self.show_notification("✅ Notificación enviada correctamente", True)
            self.page.update()
        except Exception as e:
            self.show_notification("❌ Error al enviar notificación", False)

    def on_accion_driver(self, notif_id):
        try:
            self.controller.marcar_vista_driver(notif_id)
            self.get_data()
            self.update_pagination()
            self.show_notification("✅ Notificación aceptada", True)
            self.page.update()
        except Exception as e:
            self.show_notification("❌ Error al aceptar notificación", False)

    def build(self):
        self.get_data()
        self.update_pagination()
        start = (self.current_page - 1) * self.items_per_page
        end = start + self.items_per_page
        page_data = self.data[start:end]
        rows = []

        if not page_data:
            rows.append(
                ft.Container(
                    content=ft.Text(
                        "¡No tienes notificaciones pendientes hoy! 🎉",
                        size=20, weight="bold", color="#1976D2", text_align=ft.TextAlign.CENTER
                    ),
                    alignment=ft.alignment.center,
                    padding=30,
                    expand=True
                )
            )
        else:
            for notif in page_data:
                placa = notif.get("placa", "")
                nombre = notif.get("nombre", "")
                fecha = notif.get("fecha", "")
                mensaje = notif.get("mensaje", "")
                notif_id = str(notif.get("_id"))

                if self.role == "admin":
                    fila = ft.Container(
                        ft.Column([
                            # Primera fila: Placa y Fecha
                            ft.Row([
                                ft.Row([
                                    ft.Icon(ft.icons.DIRECTIONS_CAR_FILLED, color="#1976D2", size=20),
                                    ft.Text("Placa:", size=14, weight="bold", color="#444"),
                                    ft.Text(placa, size=14, weight="bold", color="#1976D2")
                                ], spacing=5),
                                ft.Row([
                                    ft.Icon(ft.icons.EVENT, color="#1976D2", size=18),
                                    ft.Text("Fecha:", size=13, color="#444"),
                                    ft.Text(fecha, size=13, color="#1976D2")
                                ], spacing=5),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            # Segunda fila: Botón enviar centrado
                            ft.Container(
                                content=ft.ElevatedButton(
                                    "Enviar",
                                    icon=ft.icons.SEND,
                                    on_click=lambda e, id=notif_id: self.on_accion_admin(id),
                                    bgcolor="#1976D2",
                                    color="white",
                                    style=ft.ButtonStyle(
                                        padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                        shape=ft.RoundedRectangleBorder(radius=8)
                                    ),
                                ),
                                alignment=ft.alignment.center,
                                margin=ft.margin.only(top=8)
                            )
                        ], spacing=8),
                        bgcolor="#FFF8E1",
                        border_radius=12,
                        padding=ft.padding.symmetric(vertical=14, horizontal=12),
                        margin=ft.margin.only(bottom=16),
                        expand=True
                    )
                else:
                    fila = ft.Container(
                        ft.Column([
                            ft.Row([
                                ft.Text("Nombre: ", size=15, weight="bold", color="#1976D2"),
                                ft.Text(nombre, size=15, color="#333"),
                            ]),
                            ft.Text(
                                mensaje,
                                size=15,
                                color="#D32F2F",
                                expand=True,
                                max_lines=3
                            ),
                            ft.Container(
                                ft.ElevatedButton(
                                    "Aceptar",
                                    icon=ft.icons.CHECK,
                                    on_click=lambda e, id=notif_id: self.on_accion_driver(id),
                                    bgcolor="#388E3C",
                                    color="white",
                                    style=ft.ButtonStyle(
                                        padding=ft.padding.symmetric(horizontal=14, vertical=7),
                                        shape=ft.RoundedRectangleBorder(radius=8)
                                    ),
                                ),
                                alignment=ft.alignment.center,
                                margin=ft.margin.only(top=8)
                            )
                        ], spacing=7),
                        bgcolor="#E3F2FD",
                        border_radius=12,
                        padding=ft.padding.symmetric(vertical=13, horizontal=13),
                        margin=ft.margin.only(bottom=14),
                        expand=True
                    )
                rows.append(fila)

        # Título mejorado
        titulo = ft.Container(
            ft.Row([
                ft.Icon(ft.icons.NOTIFICATIONS_ACTIVE, color="#1976D2", size=24),
                ft.Text(
                    "Notificaciones Pendientes",
                    size=20, weight="bold", color="#1976D2"
                ),
            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            padding=ft.padding.symmetric(vertical=8, horizontal=10)
        )

        return ft.Container(
            content=ft.Column([
                self.notification_container,
                titulo,
                *rows,
                ft.Container(
                    self.pagination_controls,
                    padding=10,
                    alignment=ft.alignment.center
                )
            ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=8),
            expand=True,
            alignment=ft.alignment.center
        )