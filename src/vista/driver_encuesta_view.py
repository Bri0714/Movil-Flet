import flet as ft
from controlador.encuesta_controller import EncuestaController
import threading
import time

class DriverEncuestaView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.controller = EncuestaController()

        user = getattr(page, "user", {})
        self.cedula = user.get("cedula", "")
        self.placa = user.get("placa", "")
        self.nombre = user.get("nombre_completo", "")  # NUEVO: obtener el nombre

        self.placa_field = ft.TextField(
            label="Placa",
            value=self.placa,
            read_only=True,
            width=200,
            dense=True,
        )

        self.km_input = ft.TextField(
            label="Kilometraje",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
            dense=True,
            hint_text="Obligatorio",
            border_color="#B0B0B0",
            focused_border_color="#E91E63",
            helper_text="Ingrese el kilometraje actual",
        )

        # Evidencias (FilePicker)
        self.file_picker = ft.FilePicker(on_result=self.on_file_result)
        page.overlay.append(self.file_picker)
        self.evidencias = {"Foto 1": "", "Foto 2": "", "Foto 3": ""}
        self.last_fp_key = ""

        # Para mostrar nombres de archivos seleccionados
        self.fp_names = {k: ft.Text("", size=12, italic=True) for k in self.evidencias.keys()}

        # Encuestas
        self.encuestas = self.controller.obtener_encuestas(self.page.user_role, self.cedula)
        self.resp_widgets = {}  # id: [{"cb": cb, "row": row, "text": t}, ...]

        # --- Notificación tipo Container, oculta por defecto ---
        self.notification_container = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.CHECK_CIRCLE, color="white", size=20),
                ft.Text("Mensaje", color="white", weight="bold", size=14),
            ], spacing=8),
            bgcolor="#4CAF50",  # Verde por defecto
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_radius=8,
            margin=ft.margin.only(bottom=10),
            visible=False,  # Inicialmente oculto
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                offset=ft.Offset(0, 2),
            )
        )

    def show_notification(self, message, success=True, duration=5):
        if success:
            color = "#4CAF50"  # Verde
            icon = ft.icons.CHECK_CIRCLE
        else:
            color = "#F44336"  # Rojo
            icon = ft.icons.ERROR

        self.notification_container.bgcolor = color
        self.notification_container.content.controls[0].name = icon
        self.notification_container.content.controls[1].value = message
        self.notification_container.visible = True
        self.page.update()

        # Oculta después de N segundos en hilo aparte
        def hide_notification():
            time.sleep(duration)
            self.notification_container.visible = False
            self.page.update()
        threading.Thread(target=hide_notification, daemon=True).start()

    def on_file_result(self, e: ft.FilePickerResultEvent):
        # El usuario elige un archivo
        if e.files:
            key = self.last_fp_key
            f = e.files[0]
            self.evidencias[key] = f.path or f.name
            self.fp_names[key].value = f.name
            self.page.update()

    def build(self):
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = "#FFFFFF"
        self.page.update()

        # --- Contenedor Datos Inspección ---
        header = ft.Container(
            content=ft.Column([
                ft.Text("Datos de la inspección", weight="bold", text_align=ft.TextAlign.CENTER),
                ft.Row([
                    self.placa_field,
                    self.km_input
                ], alignment=ft.MainAxisAlignment.CENTER, wrap=True, spacing=30)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#F6F7FA",
            border_radius=8,
            border=ft.border.all(1, "#B0B0B0"),
            padding=30,
            margin=ft.margin.symmetric(vertical=15, horizontal=20),
            width=400,
            alignment=ft.alignment.center,
        )

        controls = [
            ft.Container(
                content=header,
                alignment=ft.alignment.center
            ),
            ft.Divider()
        ]

        # --- Sección: Encuestas dinámicas ---
        if not self.encuestas:
            controls.append(ft.Text("No hay encuestas disponibles.", italic=True))
        else:
            for enc in self.encuestas:
                enc_id = str(enc["_id"])
                color = enc.get("color", "gray")
                categoria = enc.get("categoria", "")
                descripcion = enc.get("descripcion", "")
                opciones = enc.get("opciones", [])

                # Contenedor del título coloreado, solo la categoría
                cat_container = ft.Container(
                    ft.Text(
                        categoria,
                        size=16,
                        weight="bold",
                        color="white",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    bgcolor=color,
                    border_radius=7,
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    margin=ft.margin.only(bottom=2, top=12)
                )
                if color.lower() in ["white", "#ffffff", "#fff"]:
                    cat_container.bgcolor = "#E91E63"  # Rosa fuerte si el color era blanco
                controls.append(cat_container)

                # Descripción y opciones
                opciones_rows = []
                check_items = []
                for o in opciones:
                    texto = o["texto"]
                    check = ft.Checkbox(value=False, scale=1.15)
                    t_widget = ft.Text(
                        texto,
                        size=14,
                        weight="w400",
                        color="#000000",
                        max_lines=None,
                        expand=True,
                        visible=True
                    )
                    row = ft.Row(
                        [check, t_widget],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    )
                    def on_checked(e, t=t_widget, texto=texto, cb=check, row=row):
                        if cb.value:
                            t.value = f"Conforme. {texto}"
                            t.color = "#228B22"
                            t.weight = "bold"
                        else:
                            t.value = texto
                            t.color = "#000000"
                            t.weight = "w400"
                        self.page.update()
                    check.on_change = on_checked
                    opciones_rows.append(row)
                    check_items.append({"cb": check, "row": row, "text": t_widget})

                self.resp_widgets[enc_id] = check_items

                controls.append(
                    ft.Container(
                        ft.Column([
                            ft.Text(descripcion, size=13, color="#000000", weight="w500"),
                            *opciones_rows
                        ], spacing=10),
                        bgcolor="white",
                        border=ft.border.all(1, "#E1E4EA"),
                        border_radius=8,
                        padding=16,
                        margin=ft.margin.only(bottom=8)
                    )
                )

        controls.append(ft.Divider())

        # --- Sección Evidencias ---
        controls.append(ft.Text("Evidencias", weight="bold", size=15))
        for key in self.evidencias.keys():
            controls.append(
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.UPLOAD_FILE,
                        tooltip=f"Seleccionar {key}",
                        on_click=lambda e, k=key: self._pick_file(k)
                    ),
                    ft.Text(key, size=13),
                    self.fp_names[key],
                ], spacing=8, alignment=ft.MainAxisAlignment.START)
            )
        controls.append(ft.Divider())

        # --- Observaciones ---
        self.obs_input = ft.TextField(
            label="Observaciones",
            multiline=True,
            min_lines=2,
            max_lines=5,
            expand=True,
            border_radius=6
        )
        controls.append(self.obs_input)

        # --- Botón enviar y notificación debajo ---
        controls.append(
            ft.Container(
                content=ft.Column([
                    ft.ElevatedButton(
                        "Enviar respuestas",
                        on_click=self.on_send,
                        width=200,
                        style=ft.ButtonStyle(
                            color="white",
                            bgcolor="#E91E63",
                            elevation=5,
                        ),
                        icon=ft.icons.SEND,
                    ),
                    ft.Text(
                        "* El kilometraje es obligatorio",
                        size=12,
                        italic=True,
                        color="#D32F2F"
                    ),
                    self.notification_container  # <<<< Aquí va la notificación
                ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                padding=14
            )
        )

        # --- Layout final, con scroll y adaptable ---
        return ft.Container(
            ft.Column(
                controls,
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            padding=20,
            expand=True
        )

    def _pick_file(self, key):
        self.last_fp_key = key
        self.file_picker.pick_files(allow_multiple=False)

    def on_send(self, e):
        km = self.km_input.value or ""
        # Validación de kilometraje obligatorio
        if not km:
            self.km_input.error_text = "Campo obligatorio"
            self.show_notification("❌ El kilometraje es obligatorio", success=False)
            self.page.update()
            return
        if not km.isdigit():
            self.km_input.error_text = "Solo números"
            self.show_notification("❌ Ingresa un kilometraje válido (solo números)", success=False)
            self.page.update()
            return

        # Respuestas
        respuestas = []
        for enc_id, items in self.resp_widgets.items():
            for item in items:
                respuestas.append({
                    "encuesta_id": enc_id,
                    "texto": item["text"].value.replace("Conforme. ", ""),
                    "valor": item["cb"].value
                })

        rutas = [v for v in self.evidencias.values() if v]

        # LLAMA AL CONTROLADOR Y RECIBE EL inserted_id
        inserted_id = self.controller.guardar_inspeccion(
            placa=self.placa,
            kilometraje=int(km),
            respuestas=respuestas,
            evidencias=rutas,
            observaciones=self.obs_input.value or "",
            cedula=self.cedula,
            nombre=self.nombre
        )

        if inserted_id:
            # Limpiar campos tras éxito
            self.km_input.value = ""
            self.obs_input.value = ""
            for items in self.resp_widgets.values():
                for item in items:
                    item["cb"].value = False
                    item["text"].value = item["text"].value.replace("Conforme. ", "")
                    item["text"].color = "#000000"
                    item["text"].weight = "w400"
            for k in self.evidencias.keys():
                self.evidencias[k] = ""
                self.fp_names[k].value = ""
            self.show_notification("✅ Inspección enviada correctamente", success=True)
        else:
            self.show_notification("❌ Error al guardar inspección", success=False)
        self.page.update()
