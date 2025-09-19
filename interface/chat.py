import asyncio
import flet as ft
from flet import Page, MainAxisAlignment, CrossAxisAlignment, Icons
from interface.chat_area import ChatArea
import sys
sys.path.append("./logic")
from logic.chat_context import InitialContext

class ChatApp:
    """Controlador principal de la aplicación de chat."""

    def __init__(self, page: Page, is_light_theme: bool):
        # Página principal de la app
        self.page = page
        # Estado del tema (True = claro, False = oscuro)
        self.is_light_theme = is_light_theme
        # Usuario actual (puede usarse para autenticación)
        self.current_user = None
        # Pila para manejar navegación entre contextos
        self.context_stack = []
        # Contexto actual (maneja el flujo de la conversación)
        self.context = None  # Inicializar como None temporalmente

        # Definición de colores para el tema claro
        self.LIGHT_THEME = {
            "bg": "#F0F4F8",
            "primary": "#C8102E",
            "secondary": "#007BFF",
            "positive": "#2ECC40",
            "text": "#333333",
            "neutral": "#E0E0E0"
        }
        # Definición de colores para el tema oscuro
        self.DARK_THEME = {
            "bg": "#1E1E1E",
            "primary": "#FF4D4D",
            "secondary": "#3399FF",
            "positive": "#45CE5A",
            "text": "#E0E0E0",
            "neutral": "#2F2F2F"
        }

        # Botón para alternar entre tema claro/oscuro, con animación de rotación
        self.theme_switch = ft.IconButton(
            icon=Icons.BRIGHTNESS_4,
            on_click=self.toggle_theme,
            tooltip="Cambiar tema",
            icon_color=self.get_current_theme()["primary"],
            rotate=0,
            animate_rotation=300
        )

        # Encabezado de la app: imagen, título y botón de tema
        self.header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Image(
                        src="assets/heart-beat.png",  # Imagen personalizada como icono
                        width=40,
                        height=40,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    ft.Text(
                        "Sistema Cardiovascular",
                        size=22,
                        weight="bold",
                        color="#FFFFFF" if is_light_theme else self.get_current_theme()["text"]  # Blanco en modo claro
                    ),
                    self.theme_switch
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=10,
            # Gradiente lineal en el fondo del header
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=[
                    self.get_current_theme()["primary"],
                    self.get_current_theme()["secondary"]
                ]
            ),
            border_radius=10,
            margin=ft.margin.symmetric(horizontal=10, vertical=5)
        )

        # Agrega el encabezado a la página
        self.page.add(self.header)
        # Inicializa el área de chat y la agrega a la página
        self.chat_area = ChatArea(self.send_message, self.get_current_theme())
        self.page.add(self.chat_area.container)
        # Asigna el manejador de eventos de teclado
        self.page.on_keyboard_event = self.handle_keyboard_event

        # Inicializa el contexto de conversación (flujo principal)
        self.context = InitialContext(self)
        print(f"DEBUG -> Contexto inicializado: {self.context.__class__.__name__}")
        # Muestra el mensaje de bienvenida del contexto inicial
        self.context.show_welcome_message()
        # Aplica el tema seleccionado (claro/oscuro)
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
        """Envía el mensaje del usuario y procesa la respuesta del contexto."""
        import re  # asegurarse de tenerlo para normalizar el input

        # Leer el texto tal y como lo escribió el usuario (sin modificar)
        raw = self.chat_area.input_field.value or ""
        # Normalizar: reemplaza saltos de línea, tabs y múltiples espacios por uno solo y hace strip
        message_normalizado = re.sub(r"\s+", " ", raw).strip()

        # Validación: si está vacío, mostrar burbuja de error y no avanzar
        if not message_normalizado:
            self.chat_area.add_message(
                "No puede dejar campos vacíos. Por favor, responde la pregunta.",
                False,
                self.get_current_theme(),
                msg_type="error"
            )
            self.chat_area.focus_input()
            self.page.update()
            return

        # Mostrar el mensaje del usuario (usar texto normalizado para UX consistente)
        self.chat_area.add_message(message_normalizado, True, self.get_current_theme())
        # Guardar versión lower para procesamiento
        message = message_normalizado.lower()

        # Limpiar input y preparar UI
        try:
            self.chat_area.clear_input()
        except Exception:
            # Si clear_input falla, no queremos interrumpir el flujo principal
            pass
        self.chat_area.scroll_to_bottom()
        self.chat_area.focus_input()

        # Verificación de contexto
        if self.context is None:
            print("ERROR -> self.context es None")
            self.chat_area.add_message(
                "Error: Contexto no inicializado. Por favor, reinicia la aplicación.",
                False,
                self.get_current_theme()
            )
            self.context = InitialContext(self)
            # show_welcome_message puede ser síncrono o asíncrono; aquí se asume síncrono
            try:
                if hasattr(self.context, "show_welcome_message") and asyncio.iscoroutinefunction(self.context.show_welcome_message):
                    await self.context.show_welcome_message()
                else:
                    self.context.show_welcome_message()
            except Exception as ex:
                print(f"ERROR -> al mostrar bienvenida tras reiniciar contexto: {ex}")
            self.page.update()
            return

        # Procesar el mensaje en el contexto actual (asíncrono)
        try:
            await self.context.handle_message(message)
        except Exception as ex:
            print(f"ERROR -> Excepción en handle_message: {str(ex)}")
            self.chat_area.add_message(
                f"Error al procesar el mensaje: {str(ex)}",
                False,
                self.get_current_theme()
            )

        self.page.update()


    async def handle_keyboard_event(self, e):
        """Maneja eventos de teclado (Enter para enviar, Escape para cerrar)."""
        print(f"DEBUG -> Evento de teclado: {e.key}, contexto actual: {self.context.__class__.__name__ if self.context else 'None'}")

        if e.key == "Enter":
            e.prevent_default()  # <-- Evita que el Enter haga doble efecto (envío + salto de línea)
            if not e.shift:
                await self.send_message(e)
            else:
                # Shift+Enter: permite salto de línea sin enviar
                self.chat_area.input_field.value += "\n"

        elif e.key == "Escape":
            e.prevent_default()
            self.page.window.close()

        self.page.update()

    def apply_theme(self, is_light_theme: bool):
        """Aplica el tema claro u oscuro a toda la interfaz."""
        theme = self.LIGHT_THEME if is_light_theme else self.DARK_THEME
        self.page.bgcolor = theme["bg"]
        self.chat_area.update_theme(theme)
        self.theme_switch.icon_color = theme["primary"]
        # Actualiza el gradiente del header al cambiar el tema
        self.header.gradient = ft.LinearGradient(
            begin=ft.Alignment(-1, 0),
            end=ft.Alignment(1, 0),
            colors=[
                theme["primary"],
                theme["secondary"]
            ]
        )
        # Cambia el color del texto del header según el tema
        self.header.content.controls[1].color = "#FFFFFF" if is_light_theme else theme["text"]
        self.page.update()

    def toggle_theme(self, e):
        """Alterna entre temas y actualiza la interfaz, animando el botón."""
        self.is_light_theme = not self.is_light_theme
        # Animar rotación del botón de tema
        self.theme_switch.rotate = (self.theme_switch.rotate + 1) % 2  # 0 -> 1 -> 0 (180 grados)
        self.theme_switch.update()
        self.apply_theme(self.is_light_theme)

    def get_current_theme(self):
        """Devuelve el diccionario de colores del tema actual."""
        return self.LIGHT_THEME if self.is_light_theme else self.DARK_THEME
    
    