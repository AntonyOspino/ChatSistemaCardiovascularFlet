import flet as ft
from flet import Page, TextField, ElevatedButton, Column, Row, Text, ListView, Container, MainAxisAlignment

class ChatArea:
    """Componente reutilizable para el área de chat (mensajes, campo de entrada y botón)."""
    def __init__(self, on_send_message):
        self.messages = ListView(expand=True, spacing=10, padding=20, auto_scroll=True)
        self.input_field = TextField(hint_text="Escribe un mensaje...", expand=True)
        self.send_button = ElevatedButton(text="Enviar", on_click=on_send_message)
        
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

    def add_message(self, message: str):
        """Añade un mensaje al ListView."""
        self.messages.controls.append(
            Container(
                content=Text(value=message, color="white", font_family="Arial"),
                padding=10,
                bgcolor="#b22424",
                border_radius=5
            )
        )

    def clear_input(self):
        """Limpia el campo de entrada."""
        self.input_field.value = ""

    def focus_input(self):
        """Establece el enfoque en el campo de entrada."""
        self.input_field.focus()

    def scroll_to_bottom(self):
        """Desplaza el ListView al final."""
        self.messages.scroll_to(offset=999999, duration=100)

class ChatApp:
    """Controlador principal de la aplicación de chat."""
    def __init__(self, page: Page):
        self.page = page
        self.chat_area = ChatArea(self.send_message)

        # Añadimos el componente de chat a la página
        self.page.add(self.chat_area.container)
        self.chat_area.focus_input()
        self.page.on_keyboard_event = self.handle_keyboard_event
        self.page.update()

    def send_message(self, e):
        message = self.chat_area.input_field.value.strip()
        if message:
            self.chat_area.add_message(message)
            self.chat_area.clear_input()
            self.chat_area.scroll_to_bottom()
            self.chat_area.focus_input()
            self.page.update()

    def handle_keyboard_event(self, e):
        if e.key == "Enter" and not e.shift:
            self.send_message(e)
        elif e.key == "Escape":
            self.page.window.close()
        self.page.update()