import flet as ft
from flet import Page, MainAxisAlignment, CrossAxisAlignment, Icons
from interface.chat_area import ChatArea
import sys
sys.path.append("./logic")
from logic.chat_context import InitialContext

class ChatApp:
    """Controlador principal de la aplicación de chat."""

    def __init__(self, page: Page, is_light_theme: bool):
        self.page = page
        self.is_light_theme = is_light_theme
        self.context = InitialContext(self)  # Estado del contexto: initial, login_options, diagnosis_menu, history_menu, etc.
        self.context_stack = []  # Pila para contextos anteriores (para "volver")
        self.LIGHT_THEME = {
            "bg": "#F0F4F8",  # Fondo claro
            "primary": "#C8102E",  # Rojo corazón
            "secondary": "#007BFF",  # Azul médico
            "positive": "#2ECC40",  # Verde salud
            "text": "#333333",  # Texto oscuro
            "neutral": "#E0E0E0"  # Fondo neutro
        }
        
        self.DARK_THEME = {
            "bg": "#1E1E1E",  # Fondo oscuro
            "primary": "#FF4D4D",  # Rojo más claro para contraste
            "secondary": "#3399FF",  # Azul más claro
            "positive": "#45CE5A",  # Verde más claro
            "text": "#E0E0E0",  # Texto claro
            "neutral": "#2F2F2F"  # Fondo neutro oscuro
        }
        self.chat_area = ChatArea(self.send_message, self.get_current_theme())
        # Añadimos el componente de chat a la página
        self.page.add(self.chat_area.container)
        self.chat_area.focus_input()
        self.page.on_keyboard_event = self.handle_keyboard_event
        # Botón para alternar tema
        self.theme_switch = ft.IconButton(
            icon=Icons.BRIGHTNESS_4,
            on_click=self.toggle_theme,
            tooltip="Cambiar tema",
            icon_color=self.get_current_theme()["primary"]
        )
        self.page.add(ft.Row([self.theme_switch], alignment=MainAxisAlignment.START, vertical_alignment=CrossAxisAlignment.START))
         # Mensaje de bienvenida
        self.chat_area.add_message("¡Hola! Por favor, ingresa tu usuario y contraseña para continuar.", False, self.get_current_theme())
        self.apply_theme(is_light_theme)
        self.page.update()

    def push_context(self, new_context: str):
        """Guarda el contexto actual en la pila y cambia al nuevo."""
        self.context_stack.append(self.context)
        self.context = new_context

    def pop_context(self):
        """Regresa al contexto anterior de la pila."""
        if self.context_stack:
            self.context = self.context_stack.pop()
        else:
            self.context = "initial"  # Fallback si la pila está vacía

    def send_message(self, e):
        message = self.chat_area.input_field.value.strip().lower()
        if not message:
            return

        self.chat_area.add_message(message, True, self.get_current_theme())
        self.chat_area.clear_input()
        self.chat_area.scroll_to_bottom()
        self.chat_area.focus_input()

        self.context.handle_message(message)

        self.page.update()

    def handle_keyboard_event(self, e):
        if e.key == "Enter" and not e.shift:
            self.send_message(e)
        elif e.key == "Escape":
            self.page.window.close()
        self.page.update()

    def apply_theme(self, is_light_theme: bool):
        theme = self.LIGHT_THEME if is_light_theme else self.DARK_THEME
        self.page.bgcolor = theme["bg"]
        self.chat_area.update_theme(theme)
        self.page.update()

    def toggle_theme(self, e):
        """Alterna entre temas y actualiza la interfaz."""
        self.is_light_theme = not self.is_light_theme
        self.apply_theme(self.is_light_theme)
        self.theme_switch.icon_color = self.get_current_theme()["primary"]


    
    def get_current_theme(self):
        return self.LIGHT_THEME if self.is_light_theme else self.DARK_THEME