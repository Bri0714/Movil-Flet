#from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
import os
import flet as ft
import pandas as pd
from datetime import datetime, timedelta
from controlador.encuesta_controller import EncuestaController
import asyncio
import threading
import time
from vista.inspeccion_detalle_view import InspeccionDetalleView

class ReportesView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.controller = EncuestaController()
        self.user = getattr(page, "user", {})
        self.role = getattr(page, "user_role", "driver")
        self.cedula = self.user.get("cedula", "")

        # Inicialización de fechas
        hoy = datetime.now()
        hace_7dias = hoy - timedelta(days=7)
        self.fecha_ini = hace_7dias
        self.fecha_fin = hoy

        # Inicialización de datos y estados
        self.data = []
        self.filtered_data = []
        self.expanded_indices = set()  # Para saber qué filas están expandidas

        # Paginación
        self.items_per_page = 6
        self.current_page = 1
        self.total_pages = 1

        # Configuración de selectores de fecha
        self.fecha_ini_picker = ft.DatePicker(on_change=self.on_fecha_ini_selected)
        self.fecha_fin_picker = ft.DatePicker(on_change=self.on_fecha_fin_selected)

        page.overlay.append(self.fecha_ini_picker)
        page.overlay.append(self.fecha_fin_picker)

        # Campos de fecha en formato YYYY-MM-DD
        self.fecha_ini_field = ft.TextField(
            label="Fecha Inicial",
            value=self.fecha_ini.strftime("%Y-%m-%d"),
            hint_text="aaaa-mm-dd",
            read_only=False,  # Permitir edición manual
            on_submit=self.on_fecha_manual_change,
        )

        self.fecha_fin_field = ft.TextField(
            label="Fecha Final",
            value=self.fecha_fin.strftime("%Y-%m-%d"),
            hint_text="aaaa-mm-dd",
            read_only=False,  # Permitir edición manual
            on_submit=self.on_fecha_manual_change,
        )

        # Campo de búsqueda
        self.search_field = ft.TextField(
            label="Buscar por placa",
            width=200,
            on_change=self.on_search_change
        )

        # Botones de exportación
        self.export_csv_btn = ft.ElevatedButton(
            "CSV",
            icon=ft.icons.TABLE_CHART,
            on_click=self.export_csv,
            bgcolor="#0277BD",
            color="white",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))
        )

        self.export_xls_btn = ft.ElevatedButton(
            "Excel",
            icon=ft.icons.GRID_ON,
            on_click=self.export_xls,
            bgcolor="#388E3C",
            color="white",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))
        )

        self.export_pdf_btn = ft.ElevatedButton(
            "PDF",
            icon=ft.icons.PICTURE_AS_PDF,
            on_click=self.export_pdf,
            bgcolor="#C62828",
            color="white",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))
        )
        
        # AGREGAR: Sistema de notificaciones
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

        # Mensaje cuando no hay datos
        self.no_data_msg = ft.Text(
            "No hay inspecciones para mostrar.",
            size=16,
            color="#999",
            italic=True,
            visible=False
        )

        # Encabezados de la tabla SIN botón Ver (se movió al panel expandido)
        self.table_header = ft.Container(
            content=ft.Row(
                [
                    ft.Container(width=40),  # Espacio para el botón expandir
                    ft.Text("PLACA", weight="bold"),
                    ft.Text("FECHA", weight="bold", expand=True),
                    ft.Text("KM", weight="bold"),
                ],
                spacing=8
            ),
            padding=ft.padding.symmetric(vertical=12, horizontal=10),
            bgcolor="#E3F2FD",
            border=ft.border.only(bottom=ft.BorderSide(1, "#BBDEFB")),
        )

        # Columna para la tabla
        self.table_column = ft.Column([], expand=True)

        # Controles de paginación similares al mockup
        self.pagination_controls = self.build_pagination_controls()

        self.get_data_and_refresh()

    def show_notification(self, message, success=True, duration=5):
        """
        Muestra una notificación en la ventana que desaparece automáticamente
        """
        # Configurar el color y icono según el tipo
        if success:
            color = "#4CAF50"  # Verde
            icon = ft.icons.CHECK_CIRCLE
        else:
            color = "#F44336"  # Rojo
            icon = ft.icons.ERROR
        
        # Actualizar el contenido de la notificación
        self.notification_container.bgcolor = color
        self.notification_container.content.controls[0].name = icon
        self.notification_container.content.controls[1].value = message
        
        # Mostrar la notificación
        self.notification_container.visible = True
        self.page.update()
        
        # Función para ocultar después del tiempo especificado
        def hide_notification():
            time.sleep(duration)
            self.notification_container.visible = False
            self.page.update()
        
        # Ejecutar en un hilo separado
        hide_thread = threading.Thread(target=hide_notification)
        hide_thread.daemon = True  # Se cierra con la aplicación
        hide_thread.start()

    def build_pagination_controls(self):
        """Construye los controles de paginación similares al mockup"""
        self.prev_btn = ft.TextButton(
            "Previous",
            on_click=lambda e: self.change_page(-1),
            disabled=True
        )

        self.page_indicators = []
        for i in range(1, 6):  # Crear 5 botones para páginas
            btn = ft.Container(
                content=ft.Text(str(i), color="white" if i == 1 else "black"),
                width=24,
                height=24,
                bgcolor="#1976D2" if i == 1 else "#E0E0E0",
                border_radius=12,
                alignment=ft.alignment.center,
                on_click=lambda e, pg=i: self.go_to_page(pg),
                visible=i <= self.total_pages
            )
            self.page_indicators.append(btn)

        self.next_btn = ft.TextButton(
            "Next",
            on_click=lambda e: self.change_page(1),
            disabled=self.total_pages <= 1
        )

        self.pagination_info = ft.Text(
            f"Showing 1 to {min(self.items_per_page, len(self.filtered_data))} of {len(self.filtered_data)} entries",
            size=12
        )

        # Contenedor para los controles de paginación
        pagination_row = ft.Row(
            [
                self.prev_btn,
                *self.page_indicators,
                self.next_btn
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=4
        )

        return ft.Column(
            [
                self.pagination_info,
                pagination_row
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8
        )

    def update_pagination(self):
        """Actualiza los controles de paginación"""
        total_items = len(self.filtered_data)
        self.total_pages = (total_items + self.items_per_page - 1) // self.items_per_page

        if self.current_page > self.total_pages and self.total_pages > 0:
            self.current_page = self.total_pages

        # Actualizar texto informativo
        start_index = (self.current_page - 1) * self.items_per_page + 1 if total_items > 0 else 0
        end_index = min(self.current_page * self.items_per_page, total_items)
        self.pagination_info.value = f"Showing {start_index} to {end_index} of {total_items} entries"

        # Actualizar botones de paginación
        self.prev_btn.disabled = self.current_page <= 1
        self.next_btn.disabled = self.current_page >= self.total_pages

        # Mostrar u ocultar los indicadores de página según el total de páginas
        for i, btn in enumerate(self.page_indicators):
            page_num = i + 1
            btn.visible = page_num <= self.total_pages
            btn.content.value = str(page_num)
            btn.bgcolor = "#1976D2" if page_num == self.current_page else "#E0E0E0"
            btn.content.color = "white" if page_num == self.current_page else "black"

    def change_page(self, delta):
        """Cambia la página actual sumando delta"""
        new_page = self.current_page + delta
        if 1 <= new_page <= self.total_pages:
            self.current_page = new_page
            self.refresh_table()

    def go_to_page(self, page_num):
        """Va a una página específica"""
        if 1 <= page_num <= self.total_pages:
            self.current_page = page_num
            self.refresh_table()

    def get_data_and_refresh(self):
        fecha_ini = datetime(self.fecha_ini.year, self.fecha_ini.month, self.fecha_ini.day, 0, 0, 0)
        fecha_fin = datetime(self.fecha_fin.year, self.fecha_fin.month, self.fecha_fin.day, 23, 59, 59)
        if self.role == "admin":
            self.data = self.controller.obtener_inspecciones(fecha_ini, fecha_fin, role="admin")
        else:
            self.data = self.controller.obtener_inspecciones(fecha_ini, fecha_fin, role="driver", cedula=self.cedula)
        self.filtered_data = self.data
        self.expanded_indices = set()  # Reinicia al filtrar
        self.current_page = 1  # Volver a la primera página
        self.refresh_table()

    def on_fecha_ini_selected(self, e):
        if self.fecha_ini_picker.value:
            self.fecha_ini = self.fecha_ini_picker.value
            self.fecha_ini_field.value = self.fecha_ini.strftime("%Y-%m-%d")
            self.page.update()

    def on_fecha_fin_selected(self, e):
        if self.fecha_fin_picker.value:
            self.fecha_fin = self.fecha_fin_picker.value
            self.fecha_fin_field.value = self.fecha_fin.strftime("%Y-%m-%d")
            self.page.update()

    def on_fecha_manual_change(self, e):
        """Maneja cambios manuales en los campos de fecha"""
        try:
            # Intentar parsear las fechas ingresadas manualmente
            if e.control == self.fecha_ini_field:
                self.fecha_ini = datetime.strptime(self.fecha_ini_field.value, "%Y-%m-%d")
            elif e.control == self.fecha_fin_field:
                self.fecha_fin = datetime.strptime(self.fecha_fin_field.value, "%Y-%m-%d")
        except ValueError:
            # Si hay error de formato, mostrar mensaje y restaurar valor anterior
            self.show_notification("❌ Formato de fecha incorrecto. Use AAAA-MM-DD", success=False)
            # Restaurar valores anteriores
            self.fecha_ini_field.value = self.fecha_ini.strftime("%Y-%m-%d")
            self.fecha_fin_field.value = self.fecha_fin.strftime("%Y-%m-%d")
        self.page.update()

    def on_search_change(self, e):
        search_text = self.search_field.value.strip().upper()
        self.filtered_data = [
            row for row in self.data if search_text in row.get("placa", "").upper()
        ]
        self.expanded_indices = set()
        self.current_page = 1  # Volver a la primera página
        self.refresh_table()

    def on_filtrar_click(self, e):
        """Aplica el filtro por fechas"""
        try:
            # Validar el formato de las fechas
            self.fecha_ini = datetime.strptime(self.fecha_ini_field.value, "%Y-%m-%d")
            self.fecha_fin = datetime.strptime(self.fecha_fin_field.value, "%Y-%m-%d")
            self.get_data_and_refresh()
        except ValueError:
            # Si hay error de formato, mostrar mensaje
            self.show_notification("❌ Formato de fecha incorrecto. Use AAAA-MM-DD", success=False)

    def refresh_table(self):
        rows = []
        if not self.filtered_data:
            self.no_data_msg.visible = True
        else:
            self.no_data_msg.visible = False

            # Calcular datos para la página actual
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = min(start_idx + self.items_per_page, len(self.filtered_data))
            page_data = self.filtered_data[start_idx:end_idx]

            for i, inspeccion in enumerate(page_data):
                idx = start_idx + i  # Índice global
                placa = inspeccion.get("placa", "")
                fecha_envio = inspeccion.get("fecha_envio")
                if isinstance(fecha_envio, datetime):
                    fecha_envio = fecha_envio.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    fecha_envio = str(fecha_envio)[:19]
                km = inspeccion.get("kilometraje", "")

                expanded = idx in self.expanded_indices

                icon_btn = ft.IconButton(
                    icon=ft.icons.REMOVE if expanded else ft.icons.ADD,
                    icon_color="#D32F2F" if expanded else "#1976D2",
                    tooltip="Cerrar" if expanded else "Ver detalles",
                    on_click=lambda e, i=idx: self.toggle_expand(i)
                )

                # Fila principal: Placa, Fecha, Km (SIN botón Ver)
                fila = ft.Container(
                    ft.Row([
                        icon_btn,
                        ft.Text(placa, size=15, weight="bold"),
                        ft.Text(fecha_envio, size=15, expand=True),
                        ft.Text(str(km), size=15),
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.START),
                    padding=ft.padding.symmetric(vertical=8, horizontal=6),
                    bgcolor="#F5F7FA" if expanded else "white",
                    border=ft.border.only(bottom=ft.BorderSide(1, "#E0E0E0")),
                )

                rows.append(fila)

                # Si está expandido, muestra el panel detalle con el botón Ver
                if expanded:
                    respuestas = inspeccion.get("respuestas", [])
                    campos_no_marcados = [r["texto"] for r in respuestas if not r.get("valor")]
                    estado = "Completo" if not campos_no_marcados else "Incompleto"
                    color_estado = "#4CAF50" if estado == "Completo" else "#D32F2F"
                    obs = inspeccion.get("observaciones", "")

                    # Evidencias robustas (lista, dict o string)
                    evidencias = inspeccion.get("evidencias", "")
                    if isinstance(evidencias, dict):
                        evidencia_str = "; ".join(f"{k}: {v}" for k, v in evidencias.items() if v)
                    elif isinstance(evidencias, list):
                        if all(isinstance(x, dict) for x in evidencias):
                            evidencia_str = "; ".join(
                                ", ".join(f"{k}: {v}" for k, v in d.items() if v) for d in evidencias
                            )
                        else:
                            evidencia_str = "; ".join(str(x) for x in evidencias if x)
                    else:
                        evidencia_str = str(evidencias) if evidencias else "No"

                    # Botón Ver dentro del panel expandido
                    ver_btn = ft.Container(
                        content=ft.Text("Ver", color="white", size=12, weight="bold"),
                        bgcolor="#1976D2",
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=4,
                        on_click=lambda e, insp=inspeccion: self.on_ver_click(insp),
                        width=60,
                        alignment=ft.alignment.center
                    )

                    # Panel de detalles con botón Ver incluido
                    detail_panel = ft.Container(
                        ft.Column([
                            # Observaciones
                            ft.Column([
                                ft.Text("Observaciones:", weight="bold"),
                                ft.Text(obs or "Sin observaciones")
                            ], spacing=2),

                            # Estado de la inspección
                            ft.Row([
                                ft.Text("Estado:", weight="bold"),
                                ft.Text(estado, color=color_estado, weight="bold"),
                            ], spacing=6),

                            # Campos sin marcar
                            ft.Column([
                                ft.Text("Campos sin marcar:", weight="bold"),
                                ft.Text(
                                    ", ".join(campos_no_marcados) if campos_no_marcados else "Todo diligenciado",
                                    color="#D32F2F" if campos_no_marcados else "#4CAF50"
                                )
                            ], spacing=2),

                            ft.Row([
                                ft.Text("Evidencias:", weight="bold"),
                                ft.Text(evidencia_str or "No")
                            ], spacing=6),

                            # Botón Ver en el panel expandido
                            ft.Container(
                                content=ver_btn,
                                alignment=ft.alignment.center,
                                margin=ft.margin.only(top=10)
                            )
                        ],
                        spacing=10),
                        bgcolor="#F9F9FC",
                        border=ft.border.all(1, "#E1E4EA"),
                        border_radius=8,
                        padding=10,
                        margin=ft.margin.only(left=28, bottom=10)
                    )
                    rows.append(detail_panel)

        # Actualizar paginación
        self.update_pagination()

        # Actualiza la tabla con encabezado y filas
        self.table_column.controls = [self.table_header, self.no_data_msg] + rows
        self.page.update()

    def toggle_expand(self, idx):
        # Permite solo uno expandido a la vez (como un acordeón móvil)
        if idx in self.expanded_indices:
            self.expanded_indices.remove(idx)
        else:
            self.expanded_indices = {idx}
        self.refresh_table()


    def on_ver_click(self, inspeccion):
        detalle = InspeccionDetalleView(self.page, inspeccion)
        self.page.clean()  # Limpia la página antes de cargar el detalle
        self.page.add(detalle.build())


    # ---------- EXPORTACIONES CON NOTIFICACIONES ------------
    def export_csv(self, e):
        try:
            dir_path = os.path.join("exportados", str(self.cedula))
            os.makedirs(dir_path, exist_ok=True)
            file_path = os.path.join(dir_path, "inspecciones.csv")

            lista = []
            for i in self.filtered_data:
                respuestas = i.get("respuestas", [])
                campos_no_marcados = [r["texto"] for r in respuestas if not r.get("valor")]
                estado = "Completo" if not campos_no_marcados else "Incompleto"
                obs = i.get("observaciones", "")

                evidencias = i.get("evidencias", "")
                if isinstance(evidencias, dict):
                    evidencia_str = "; ".join(f"{k}: {v}" for k, v in evidencias.items() if v)
                elif isinstance(evidencias, list):
                    if all(isinstance(x, dict) for x in evidencias):
                        evidencia_str = "; ".join(
                            ", ".join(f"{k}: {v}" for k, v in d.items() if v) for d in evidencias
                        )
                    else:
                        evidencia_str = "; ".join(str(x) for x in evidencias if x)
                else:
                    evidencia_str = str(evidencias) if evidencias else "No"

                lista.append({
                    "Placa": i.get("placa", ""),
                    "Fecha": i.get("fecha_envio", ""),
                    "Kilometraje": i.get("kilometraje", ""),
                    "Estado": estado,
                    "Observaciones": obs or "",
                    "Evidencias": evidencia_str or "No",
                    "Campos sin marcar": ", ".join(campos_no_marcados) if campos_no_marcados else "Todo diligenciado",
                    "Cantidad sin marcar": len(campos_no_marcados)
                })

            df = pd.DataFrame(lista)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            self.show_notification("✅ Archivo CSV exportado correctamente", success=True)
        except Exception as ex:
            self.show_notification(f"❌ Error al exportar CSV: {str(ex)}", success=False)

    def export_xls(self, e):
        try:
            dir_path = os.path.join("exportados", str(self.cedula))
            os.makedirs(dir_path, exist_ok=True)
            file_path = os.path.join(dir_path, "inspecciones.xlsx")

            lista = []
            for i in self.filtered_data:
                respuestas = i.get("respuestas", [])
                campos_no_marcados = [r["texto"] for r in respuestas if not r.get("valor")]
                estado = "Completo" if not campos_no_marcados else "Incompleto"
                obs = i.get("observaciones", "")

                evidencias = i.get("evidencias", "")
                if isinstance(evidencias, dict):
                    evidencia_str = "; ".join(f"{k}: {v}" for k, v in evidencias.items() if v)
                elif isinstance(evidencias, list):
                    if all(isinstance(x, dict) for x in evidencias):
                        evidencia_str = "; ".join(
                            ", ".join(f"{k}: {v}" for k, v in d.items() if v) for d in evidencias
                        )
                    else:
                        evidencia_str = "; ".join(str(x) for x in evidencias if x)
                else:
                    evidencia_str = str(evidencias) if evidencias else "No"

                lista.append({
                    "Placa": i.get("placa", ""),
                    "Fecha": i.get("fecha_envio", ""),
                    "Kilometraje": i.get("kilometraje", ""),
                    "Estado": estado,
                    "Observaciones": obs or "",
                    "Evidencias": evidencia_str or "No",
                    "Campos sin marcar": ", ".join(campos_no_marcados) if campos_no_marcados else "Todo diligenciado",
                    "Cantidad sin marcar": len(campos_no_marcados)
                })

            df = pd.DataFrame(lista)
            df.to_excel(file_path, index=False)
            self.show_notification("✅ Archivo Excel exportado correctamente", success=True)
        except Exception as ex:
            self.show_notification(f"❌ Error al exportar Excel: {str(ex)}", success=False)

    def export_pdf(self, e):
        try:
            dir_path = os.path.join("exportados", str(self.cedula))
            os.makedirs(dir_path, exist_ok=True)
            file_path = os.path.join(dir_path, "inspecciones.pdf")

            doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=18, leftMargin=18, topMargin=24, bottomMargin=18)
            styles = getSampleStyleSheet()
            style_cell = ParagraphStyle(
                "cell",
                fontSize=8,
                leading=10,
                spaceAfter=0,
                spaceBefore=0,
                alignment=0, # izquierda
                wordWrap='CJK',  # Wrap for long words/texts
            )
            style_header = ParagraphStyle(
                "header",
                fontSize=8,
                leading=10,
                alignment=1, # centro
                textColor=colors.white,
                spaceAfter=0,
                spaceBefore=0,
                fontName="Helvetica-Bold"
            )

            elems = [Paragraph("Reporte de Inspecciones", styles["Heading1"]), Spacer(1, 12)]

            # Titulos (como Paragraph para formatear igual que celdas)
            headers = [
                Paragraph("Placa", style_header),
                Paragraph("Fecha", style_header),
                Paragraph("Kilometraje", style_header),
                Paragraph("Estado", style_header),
                Paragraph("Observaciones", style_header),
                Paragraph("Campos sin marcar", style_header)
            ]
            data = [headers]

            for i in self.filtered_data:
                respuestas = i.get("respuestas", [])
                campos_no_marcados = [r["texto"] for r in respuestas if not r.get("valor")]
                estado = "Completo" if not campos_no_marcados else "Incompleto"
                obs = i.get("observaciones", "")

                fecha_envio = i.get("fecha_envio")
                if isinstance(fecha_envio, datetime):
                    fecha_envio = fecha_envio.strftime("%Y-%m-%d %H:%M")

                if campos_no_marcados:
                    campos_paragraph = Paragraph("<br/>".join(campos_no_marcados), style_cell)
                else:
                    campos_paragraph = Paragraph("Todo diligenciado", style_cell)

                data.append([
                    Paragraph(i.get("placa", ""), style_cell),
                    Paragraph(fecha_envio or "", style_cell),
                    Paragraph(str(i.get("kilometraje", "")), style_cell),
                    Paragraph(estado, style_cell),
                    Paragraph(obs or "", style_cell),
                    campos_paragraph
                ])

            # Puedes ajustar los anchos en la lista siguiente (en puntos, 1 pulgada = 72pt)
            col_widths = [52, 70, 60, 50, 130, 120]  # ajusta según lo necesites

            t = Table(data, repeatRows=1, colWidths=col_widths)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976D2")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
            ]))
            elems.append(t)
            doc.build(elems)
            self.show_notification("✅ Archivo PDF exportado correctamente", success=True)
        except Exception as ex:
            self.show_notification(f"❌ Error al exportar PDF: {str(ex)}", success=False)

    def build(self):
        # Cabecera con título
        titulo = ft.Container(
            content=ft.Column([
                ft.Text("📋 Listado de inspecciones de vehículos",
                        size=22,
                        weight="bold"),
                ft.Divider(height=2),
            ], spacing=10),
            margin=ft.margin.only(bottom=10)
        )

        # Panel de filtros responsive
        filtros = ft.Container(
            content=ft.Column([
                # Primera fila de filtros: fechas y botón filtrar
                ft.Row([
                    ft.Container(self.fecha_ini_field, padding=ft.padding.only(right=8)),
                    ft.Container(self.fecha_fin_field, padding=ft.padding.only(right=8)),
                    ft.ElevatedButton(
                        "Filtrar",
                        icon=ft.icons.FILTER_ALT,
                        on_click=self.on_filtrar_click,
                        bgcolor="#FFA000",
                        color="black"
                    )
                ], wrap=True, spacing=10),

                # Segunda fila: búsqueda y exportación
                ft.Row([
                    self.search_field,
                    ft.Container(width=10),  # Espaciador
                    self.export_csv_btn,
                    self.export_xls_btn,
                    self.export_pdf_btn
                ], wrap=True, spacing=10),
            ], spacing=15),
            bgcolor="#F9F9FC",
            border_radius=10,
            padding=ft.padding.all(16),
            margin=ft.margin.only(bottom=14)
        )

        # Info de formato de fecha
        formato_fecha = ft.Container(
            content=ft.Text("Formato de fecha: aaaa-mm-dd", size=12, color="#1976D2"),
            margin=ft.margin.only(bottom=10),
            padding=ft.padding.all(8),
            border_radius=8,
            bgcolor="#E3F2FD",
        )

        # Tabla en un contenedor responsive
        tabla_contenedor = ft.Container(
            content=ft.Column([
                formato_fecha,
                ft.Container(
                    content=self.table_column,
                    bgcolor="white",
                    border=ft.border.all(1, "#E1E4EA"),
                    border_radius=12,
                    padding=0,
                    expand=True
                ),
                # Agregar paginación debajo de la tabla
                ft.Container(
                    content=self.pagination_controls,
                    padding=ft.padding.symmetric(vertical=16),
                    alignment=ft.alignment.center
                )
            ]),
            expand=True
        )

        # Layout general responsive
        return ft.Container(
            content=ft.Column([
                self.notification_container,
                titulo,
                filtros,
                tabla_contenedor
            ], spacing=8, scroll=ft.ScrollMode.AUTO, expand=True),
            padding=ft.padding.all(8),
            expand=True
        )

    def did_mount(self):
        # Se ejecuta cuando el componente se monta en la página
        self.get_data_and_refresh()

    def will_unmount(self):
        # Limpieza cuando el componente se desmonta
        pass