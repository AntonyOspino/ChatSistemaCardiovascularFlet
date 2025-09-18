import flet as ft
from flet import Column, Row, TextField, ElevatedButton, ListView, Container, Text, Icons, MainAxisAlignment, TextOverflow, BoxConstraints, padding, margin

class ChatArea:
    """Componente reutilizable para el área de chat (mensajes, campo de entrada y botón)."""
    def __init__(self, on_send_message, theme):
        self.page = None  # Se establecerá cuando se añada a la página
        self.messages = ListView(expand=True, spacing=10, padding=20, auto_scroll=True)
        self.input_field = TextField(
            hint_text="Escribe un mensaje...",
            expand=True,
            bgcolor=theme["neutral"],
            color=theme["text"],
            on_submit=on_send_message
        )
        self.send_button = ElevatedButton(
            text="Enviar",
            icon=Icons.ARROW_FORWARD,
            on_click=on_send_message,
            bgcolor="#1E90FF",
            color="white",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=20,
                elevation=5
            )
        )
        
        self.container = Column(
            controls=[
                self.messages,
                Row(
                    [self.input_field, self.send_button],
                    alignment=MainAxisAlignment.CENTER,
                    spacing=12,
                ),
            ],
            expand=True,
        )

    def set_page(self, page):
        """Establece la referencia a la página de Flet para actualizaciones."""
        self.page = page

    """def add_message(self, message: str, is_user: bool, theme):
        Añade un mensaje al ListView con color según el emisor.
        try:
            print(f"DEBUG -> Agregando mensaje: {message}, is_user: {is_user}")
            bubble_color = theme["primary"] if is_user else theme["secondary"]
            alignment = ft.alignment.center_right if is_user else ft.alignment.center_left

            # Contenedor del mensaje con ancho limitado
            message_container = Container(
                content=Text(
                    value=message,
                    color="white",
                    font_family="Courier New",
                    no_wrap=False,
                    max_lines=None,
                    overflow=TextOverflow.VISIBLE
                ),
                padding=padding.symmetric(horizontal=15, vertical=10),
                bgcolor=bubble_color,
                border_radius=10,
                alignment=alignment,
                margin=margin.symmetric(vertical=5),
                expand=False,
                width=400
            )


            # Fila que controla la alineación (izquierda o derecha)
            message_row = Row(
                controls=[message_container],
                alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
            )

            self.messages.controls.append(message_row)
            print("DEBUG -> Mensaje añadido al ListView")
            self.messages.update()  # Actualizar explícitamente el ListView
            self.scroll_to_bottom()
            print("DEBUG -> Mensaje mostrado y desplazado al final")
        except Exception as e:
            print(f"ERROR -> Error al agregar mensaje: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            raise
        """

    def add_message(self, message: str, is_user: bool, theme, msg_type="normal"):
        """Añade un mensaje al ListView con estilos según emisor y tipo."""
        # Definir colores según tipo de mensaje
        if msg_type == "error":
            bubble_color = "red"
            text_color = "white"
        elif is_user:
            bubble_color = theme["primary"]   # color usuario
            text_color = "white"
        else:
            bubble_color = theme["secondary"]  # color chatbot
            text_color = theme["text"]

        alignment = ft.alignment.center_right if is_user else ft.alignment.center_left

        # 🔹 Ancho dinámico: 60% del ancho de la ventana
        max_width = int(self.page.window_width * 0.6) if self.page and self.page.window_width else 600

        message_container = ft.Container(
            content=ft.Text(
                value=message,
                color=text_color,
                size=14,
                font_family="Verdana",
                no_wrap=False,
                max_lines=None,
                overflow=ft.TextOverflow.CLIP
            ),
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            bgcolor=bubble_color,
            border_radius=15,
            alignment=alignment,
            margin=ft.margin.symmetric(vertical=5),
            width=max_width  # 👈 Aquí se aplica el ancho dinámico
        )

        message_row = ft.Row(
            controls=[message_container],
            alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        )

        self.messages.controls.append(message_row)
        self.scroll_to_bottom()
        

    def clear_input(self):
        """Limpia el campo de entrada."""
        try:
            self.input_field.value = ""
            self.input_field.update()
            print("DEBUG -> Campo de entrada limpiado")
        except Exception as e:
            print(f"ERROR -> Error al limpiar campo de entrada: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            raise

    def focus_input(self):
        """Establece el enfoque en el campo de entrada."""
        try:
            self.input_field.focus()
            print("DEBUG -> Campo de entrada enfocado")
        except Exception as e:
            print(f"ERROR -> Error al enfocar campo de entrada: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            raise

    def scroll_to_bottom(self):
        """Desplaza el ListView al final."""
        try:
            if self.page:
                self.messages.scroll_to(key=len(self.messages.controls) - 1, duration=300)
                self.page.update()
                print("DEBUG -> ListView desplazado al final")
            else:
                print("WARNING -> No se puede desplazar: página no establecida")
        except Exception as e:
            print(f"ERROR -> Error al desplazar ListView: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            raise

    def update_theme(self, theme):
        """Actualiza los colores del ChatArea según el tema."""
        try:
            self.input_field.bgcolor = theme["neutral"]
            self.input_field.color = theme["text"]
            self.input_field.update()
            #self.send_button.bgcolor = theme["primary"]
            
            # Actualizar colores de los mensajes existentes
            for row in self.messages.controls:
                if isinstance(row, Row) and len(row.controls) > 0:
                    message_container = row.controls[0]
                    if isinstance(message_container, Container):
                        # Determinar si es mensaje de usuario o del sistema
                        is_user = row.alignment == ft.MainAxisAlignment.END
                        message_container.bgcolor = theme["primary"] if is_user else theme["secondary"]
            
            self.messages.update()
            if self.page:
                self.page.update()
            print("DEBUG -> Tema actualizado en ChatArea")
        except Exception as e:
            print(f"ERROR -> Error al actualizar tema: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            raise