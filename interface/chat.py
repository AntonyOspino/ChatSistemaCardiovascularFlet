import flet as ft
from flet import Page, TextField, ElevatedButton, Column, Row, Text, ListView, Container, MainAxisAlignment, CrossAxisAlignment, Icons


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

        self.messages.controls.append(
            Container(
                content=Text(value=message, color="white", font_family="Arial"),
                padding=10,
                bgcolor=bubble_color,
                border_radius=5,
                alignment=ft.alignment.center_left if not is_user else ft.alignment.center_right
            )
        )
        self.scroll_to_bottom()

    def clear_input(self):
        """Limpia el campo de entrada."""
        self.input_field.value = ""

    def focus_input(self):
        """Establece el enfoque en el campo de entrada."""
        self.input_field.focus()

    def scroll_to_bottom(self):
        """Desplaza el ListView al final."""
        self.messages.scroll_to(offset=999999, duration=100)

    def update_theme(self, theme):
        """Actualiza los colores del ChatArea según el tema."""
        self.input_field.bgcolor = theme["neutral"]
        self.input_field.color = theme["text"]
        self.send_button.bgcolor = theme["primary"]
        for msg in self.messages.controls:
            msg.bgcolor = theme["primary"] if msg.alignment == ft.alignment.center_right else theme["secondary"]
        self.messages.update()


class ChatApp:
    """Controlador principal de la aplicación de chat."""

    def __init__(self, page: Page, is_light_theme: bool):
        self.page = page
        self.is_light_theme = is_light_theme
        self.context = "initial"  # Estado del contexto: initial, login_options, diagnosis_menu, history_menu, etc.
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
        self.apply_theme(is_light_theme)
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

        # Manejo de respuestas según el contexto
        match self.context:
            case "initial":
                if "usuario" in message and "contraseña" in message:
                    self.chat_area.add_message("¡Bienvenido! Rol: Paciente. ¿Deseas usar las funciones? (Sí/No)", False, self.get_current_theme())
                    self.push_context("login_options")
                else:
                    self.chat_area.add_message("Por favor, ingresa un usuario y contraseña válidos.", False, self.get_current_theme())

            case "login_options":
                match message:
                    case "sí" | "si" | "SI" | "Sí":
                        self.chat_area.add_message("Opciones: 1) Diagnóstico, 2) Historial, 3) Salir", False, self.get_current_theme())
                        self.push_context("main_menu")
                    case "no" | "No" | "NO" | "nO":
                        self.chat_area.add_message("Has elegido no usar las funciones. ¿Deseas salir? (Sí/No)", False, self.get_current_theme())
                        self.push_context("initial")
                    case _:
                        self.chat_area.add_message("Por favor, responde Sí o No.", False, self.get_current_theme())
                        
            case "main_menu":
                match message:
                    case "1" | "diagnóstico":
                        self.chat_area.add_message("Diagnóstico: a) Medir presión, b) Evaluar ritmo cardíaco, c) Volver", False, self.get_current_theme())
                        self.push_context("diagnosis_menu")
                    case "2" | "historial":
                        self.chat_area.add_message("Historial: a) Ver consultas, b) Agregar nota, c) Volver", False, self.get_current_theme())
                        self.push_context("history_menu")
                    case "3" | "salir":
                        self.chat_area.add_message("¿Estás seguro de salir? (Sí/No)", False, self.get_current_theme())
                        self.push_context("exit_confirm")
                    case _:
                        self.chat_area.add_message("Elige una opción válida: 1) Diagnóstico, 2) Historial, 3) Salir", False, self.get_current_theme())

            case "diagnosis_menu":
                match message:
                    case "a" | "medir presión":
                        self.chat_area.add_message("Simulación: Presión arterial: 120/80 mmHg (Normal). ¿Continuar? (Sí/No)", False, self.get_current_theme())
                        self.push_context("diagnosis_result")
                    case "b" | "evaluar ritmo cardíaco":
                        self.chat_area.add_message("Simulación: Ritmo cardíaco: 72 bpm (Normal). ¿Continuar? (Sí/No)", False, self.get_current_theme())
                        self.push_context("diagnosis_result")
                    case "c" | "volver":
                        self.pop_context()
                        self.chat_area.add_message("Opciones: 1) Diagnóstico, 2) Historial, 3) Salir", False, self.get_current_theme())
                    case _:
                        self.chat_area.add_message("Elige una opción válida: a) Medir presión, b) Evaluar ritmo, c) Volver", False, self.get_current_theme())

            case "history_menu":
                match message:
                    case "a" | "ver consultas":
                        self.chat_area.add_message("Historial: Consulta 1: 12/09/2025 - Normal, Consulta 2: 10/08/2025 - Revisión. ¿Volver? (Sí)", False, self.get_current_theme())
                        self.push_context("history_result")
                    case "b" | "agregar nota":
                        self.chat_area.add_message("Ingresa una nota para el historial:", False, self.get_current_theme())
                        self.push_context("add_note")
                    case "c" | "volver":
                        self.pop_context()
                        self.chat_area.add_message("Opciones: 1) Diagnóstico, 2) Historial, 3) Salir", False, self.get_current_theme())
                    case _:
                        self.chat_area.add_message("Elige una opción válida: a) Ver consultas, b) Agregar nota, c) Volver", False, self.get_current_theme())

            case "diagnosis_result" | "history_result":
                match message:
                    case "sí" | "volver":
                        self.pop_context()
                        self.chat_area.add_message("Opciones: 1) Diagnóstico, 2) Historial, 3) Salir", False, self.get_current_theme())
                    case "no":
                        self.chat_area.add_message("Saliendo del submenú. ¿Volver al menú principal? (Sí/No)", False, self.get_current_theme())
                        self.push_context("return_prompt")
                    case _:
                        self.chat_area.add_message("Por favor, responde Sí o No.", False, self.get_current_theme())


            case "add_note":
                match message:
                    case m if m:
                        self.chat_area.add_message(f"Nota agregada: {message}. ¿Volver al menú? (Sí)", False, self.get_current_theme())
                        self.pop_context()  # Regresa a history_result o anterior
                    case _:
                        self.chat_area.add_message("Por favor, ingresa una nota.", False, self.get_current_theme())

            case "exit_prompt" | "exit_confirm" | "return_prompt":
                match message:
                    case "sí" | "si" | "SI" | "Sí":
                        if self.context == "exit_confirm":
                            self.page.window.close()
                        else:
                            self.pop_context()
                            if self.context == "main_menu":
                                self.chat_area.add_message("Opciones: 1) Diagnóstico, 2) Historial, 3) Salir", False, self.get_current_theme())
                            else:
                                self.chat_area.add_message("Regresando al menú anterior.", False, self.get_current_theme())
                    case "no" | "No" | "NO" | "nO":
                        self.chat_area.add_message("Saliendo. ¿Deseas continuar? (Sí/No)", False, self.get_current_theme())
                        self.context = "exit_prompt"
                    case _:
                        self.chat_area.add_message("Por favor, responde Sí o No.", False, self.get_current_theme())

            case _:
                self.chat_area.add_message("Error de contexto. Reiniciando. Ingresa usuario y contraseña.", False, self.get_current_theme())
                self.context_stack.clear()
                self.context = "initial"

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
        self.chat_area.input_field.color = theme["text"]
        self.page.update()

    def toggle_theme(self, e):
        """Alterna entre temas y actualiza la interfaz."""
        self.is_light_theme = not self.is_light_theme
        self.apply_theme(self.is_light_theme)
        self.theme_switch.icon_color = self.get_current_theme()["primary"]


    
    def get_current_theme(self):
        return self.LIGHT_THEME if self.is_light_theme else self.DARK_THEME