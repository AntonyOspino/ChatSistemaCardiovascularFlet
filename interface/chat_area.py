import flet as ft
from flet import Column, Row, TextField, ElevatedButton, ListView, Container, Text, Icons, MainAxisAlignment, TextOverflow, BoxConstraints, padding, margin

class ChatArea:
    """Componente reutilizable para el área de chat (mensajes, campo de entrada y botón)."""
    def __init__(self, on_send_message, theme):
        self.messages = ListView(expand=True, spacing=10, padding=20, auto_scroll=True)
        self.input_field = TextField(hint_text="Escribe un mensaje...", expand=True, bgcolor=theme["neutral"], color=theme["text"])
        self.send_button = ElevatedButton(text="Enviar", icon=Icons.SEND, on_click=on_send_message, bgcolor=theme["primary"], color="white")
        
        self.container = Column(
            controls=[
                self.messages,
                Row(
                    [self.input_field, self.send_button],
                    alignment=MainAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
            expand=True,
        )

    def add_message(self, message: str, is_user: bool, theme):
        """Añade un mensaje al ListView con color según el emisor."""
        bubble_color = theme["primary"] if is_user else theme["secondary"]
        alignment = ft.alignment.center_right if is_user else ft.alignment.center_left

        # Contenedor del mensaje con ancho limitado
        message_container = Container(
            content=Text(
                value=message, 
                color="white", 
                font_family="Arial", 
                no_wrap=False, 
                max_lines=None, 
                overflow=TextOverflow.VISIBLE,
                width=None
            ),
            padding=padding.symmetric(horizontal=15, vertical=10),
            bgcolor=bubble_color,
            border_radius=15,
            alignment=alignment,
            margin=margin.symmetric(vertical=5),
            width=BoxConstraints(max_width=0.8 * 500)
        )

        # Fila que controla la alineación (izquierda o derecha)
        message_row = Row(
            controls=[message_container],
            alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        )

        self.messages.controls.append(message_row)
        self.scroll_to_bottom()

    def clear_input(self):
        """Limpia el campo de entrada."""
        self.input_field.value = ""
        self.input_field.update()

    def focus_input(self):
        """Establece el enfoque en el campo de entrada."""
        self.input_field.focus()

    def scroll_to_bottom(self):
        """Desplaza el ListView al final."""
        self.messages.scroll_to(offset=999999, duration=300)

    def update_theme(self, theme):
        """Actualiza los colores del ChatArea según el tema."""
        self.input_field.bgcolor = theme["neutral"]
        self.input_field.color = theme["text"]
        self.send_button.bgcolor = theme["primary"]
        
        # Actualizar colores de los mensajes existentes
        for row in self.messages.controls:
            if isinstance(row, Row) and len(row.controls) > 0:
                message_container = row.controls[0]
                if isinstance(message_container, Container):
                    # Determinar si es mensaje de usuario o del sistema
                    is_user = row.alignment == ft.MainAxisAlignment.END
                    message_container.bgcolor = theme["primary"] if is_user else theme["secondary"]
        
        self.messages.update()