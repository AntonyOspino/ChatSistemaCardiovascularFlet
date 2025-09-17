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
        self.current_user = None
        self.context_stack = []
        self.context = None  # Inicializar como None temporalmente
        self.LIGHT_THEME = {
            "bg": "#F0F4F8",
            "primary": "#C8102E",
            "secondary": "#007BFF",
            "positive": "#2ECC40",
            "text": "#333333",
            "neutral": "#E0E0E0"
        }
        
        self.DARK_THEME = {
            "bg": "#1E1E1E",
            "primary": "#FF4D4D",
            "secondary": "#3399FF",
            "positive": "#45CE5A",
            "text": "#E0E0E0",
            "neutral": "#2F2F2F"
        }

        # Botón para alternar tema
        self.theme_switch = ft.IconButton(
            icon=Icons.BRIGHTNESS_4,
            on_click=self.toggle_theme,
            tooltip="Cambiar tema",
            icon_color=self.get_current_theme()["primary"]
        )

        # Encabezado con icono + título
        self.header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Image(
                        src="assets/heart-beat.png",
                        width=40,
                        height=40,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    ft.Text("Sistema Cardiovascular", size=22, weight="bold", color=self.get_current_theme()["text"]),
                    self.theme_switch
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=10,
            bgcolor=self.get_current_theme()["neutral"],
            border_radius=10,
            margin=ft.margin.symmetric(horizontal=10, vertical=5)
        )

        # Agregamos encabezado + área de chat
        self.page.add(self.header)
        self.chat_area = ChatArea(self.send_message, self.get_current_theme())
        self.page.add(self.chat_area.container)
        self.page.on_keyboard_event = self.handle_keyboard_event

        # Inicializar el contexto
        self.context = InitialContext(self)
        print(f"DEBUG -> Contexto inicializado: {self.context.__class__.__name__}")
        self.context.show_welcome_message()
        self.apply_theme(is_light_theme)
        self.page.update()

    def push_context(self, new_context_class, silent=False):
        """Guarda el contexto actual en la pila y cambia al nuevo."""
        print(f"DEBUG -> Guardando contexto actual: {self.context.__class__.__name__ if self.context else 'None'}")
        self.context_stack.append((self.context.__class__, silent))
        self.context = new_context_class(self)
        print(f"DEBUG -> Cambiando a contexto: {self.context.__class__.__name__}")
        if not silent:
            self.context.show_welcome_message()

    def pop_context(self, silent=False):
        """Regresa al contexto anterior de la pila."""
        if self.context_stack:
            prev_context_class, was_silent = self.context_stack.pop()
            self.context = prev_context_class(self)
            print(f"DEBUG -> Restaurando contexto: {self.context.__class__.__name__}")
            if not silent and not was_silent:
                self.context.show_welcome_message()
        else:
            print("DEBUG -> Pila vacía, reiniciando a InitialContext")
            self.context = InitialContext(self)
            self.context.show_welcome_message()

    async def send_message(self, e):
        message = self.chat_area.input_field.value.strip().lower()
        if not message:
            return

        print(f"DEBUG -> Enviando mensaje: {message}, contexto actual: {self.context.__class__.__name__ if self.context else 'None'}")
        self.chat_area.add_message(message, True, self.get_current_theme())
        self.chat_area.clear_input()
        self.chat_area.scroll_to_bottom()
        self.chat_area.focus_input()

        if self.context is None:
            print("ERROR -> self.context es None")
            self.chat_area.add_message("Error: Contexto no inicializado. Por favor, reinicia la aplicación.", False, self.get_current_theme())
            self.context = InitialContext(self)
            self.context.show_welcome_message()
            self.page.update()
            return

        try:
            await self.context.handle_message(message)
        except Exception as ex:
            print(f"ERROR -> Excepción en handle_message: {str(ex)}")
            self.chat_area.add_message(f"Error al procesar el mensaje: {str(ex)}", False, self.get_current_theme())

        self.page.update()

    async def handle_keyboard_event(self, e):
        print(f"DEBUG -> Evento de teclado: {e.key}, contexto actual: {self.context.__class__.__name__ if self.context else 'None'}")
        if e.key == "Enter" and not e.shift:
            await self.send_message(e)
        elif e.key == "Escape":
            self.page.window.close()
        self.page.update()

    def apply_theme(self, is_light_theme: bool):
        theme = self.LIGHT_THEME if is_light_theme else self.DARK_THEME
        self.page.bgcolor = theme["bg"]
        self.chat_area.update_theme(theme)
        self.theme_switch.icon_color = theme["primary"]
        self.header.bgcolor = theme["neutral"]
        self.header.content.controls[1].color = theme["text"]
        self.page.update()

    def toggle_theme(self, e):
        """Alterna entre temas y actualiza la interfaz."""
        self.is_light_theme = not self.is_light_theme
        self.apply_theme(self.is_light_theme)

    def get_current_theme(self):
        return self.LIGHT_THEME if self.is_light_theme else self.DARK_THEME