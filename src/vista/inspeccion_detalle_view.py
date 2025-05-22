import flet as ft

class InspeccionDetalleView:
    def __init__(self, page: ft.Page, inspeccion: dict):
        self.page = page
        self.inspeccion = inspeccion

    def build(self):
        # Datos generales
        info = [
            ft.Text(
                f"Datos de la inspección {self.inspeccion.get('fecha_envio', '')}",
                weight="bold", size=18, text_align=ft.TextAlign.CENTER
            ),
            ft.Divider(),
            ft.Text(f"Placa: {self.inspeccion.get('placa', '')}", size=15),
            ft.Text(f"Kilometraje: {self.inspeccion.get('kilometraje', '')}", size=15),
            ft.Text(f"Conductor: {self.inspeccion.get('nombre', '')}", size=15),
        ]

        # Respuestas agrupadas
        respuestas = self.inspeccion.get("respuestas", [])
        bloques = []
        cat_actual = ""
        for r in respuestas:
            cat = r.get("categoria", "")
            if cat and cat != cat_actual:
                bloques.append(
                    ft.Container(
                        ft.Text(cat, weight="bold", color="#1976D2", size=17),
                        bgcolor="#E3F2FD", border_radius=7, padding=10, margin=ft.margin.only(top=14, bottom=2)
                    )
                )
                cat_actual = cat
            check_icon = ft.Icon(
                ft.icons.CHECK_CIRCLE if r.get("valor") else ft.icons.CANCEL,
                color="#228B22" if r.get("valor") else "#D32F2F",
                size=18
            )
            bloques.append(
                ft.Row([
                    check_icon,
                    ft.Container(
                        ft.Text(
                            r.get("texto", ""),
                            size=15,
                            max_lines=None,
                        ),
                        expand=True,
                        padding=ft.padding.only(left=0, right=0),
                        alignment=ft.alignment.center_left,
                        width=320  # Limita el ancho para móvil y evita que se salga
                    ),
                ], spacing=8, expand=True)
            )

        # Evidencias (si tienes)
        evidencias = self.inspeccion.get("evidencias", [])
        if evidencias:
            bloques.append(
                ft.Container(
                    ft.Text("Evidencias:", weight="bold", color="#0277BD", size=16),
                    bgcolor="#E3F2FD", border_radius=7, padding=8, margin=ft.margin.only(top=14, bottom=2)
                )
            )
            for idx, ev in enumerate(evidencias):
                bloques.append(ft.Text(f"{idx+1}. {ev}", size=14, max_lines=2))

        # Observaciones
        obs = self.inspeccion.get("observaciones", "")
        bloques.append(
            ft.Container(
                ft.Text(f"Observaciones:\n{obs or 'Sin observaciones'}", size=14, max_lines=None),
                bgcolor="#FAFAFA", border_radius=7, padding=8, margin=ft.margin.only(top=14)
            )
        )

        # Botón volver bien centrado abajo
        boton_volver = ft.Row(
            [
                ft.ElevatedButton(
                    "Volver",
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: self.page.go("/dashboard"),  # Cambia a tu ruta principal de encuesta si es otra
                    bgcolor="#1976D2", color="white",
                    width=150
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )

        return ft.Container(
            ft.Column(
                info + bloques + [ft.Divider(), boton_volver],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            padding=18,
            alignment=ft.alignment.center,
            expand=True
        )
