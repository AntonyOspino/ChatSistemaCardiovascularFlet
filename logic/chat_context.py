class ChatContext:
    def __init__(self, chat_app):
        self.chat_app = chat_app

    def handle_message(self, message):
        """Método abstracto que cada contexto debe implementar."""
        raise NotImplementedError("Subclasses must implement handle_message()")

    def push_context(self, new_context_class, silent=False):
        """Cambia al nuevo contexto y guarda el actual en la pila."""
        self.chat_app.context_stack.append((self.__class__, silent))
        self.chat_app.context = new_context_class(self.chat_app)
        if not silent:
            self.chat_app.context.show_welcome_message()

    def pop_context(self, silent=False):
        """Regresa al contexto anterior de la pila."""
        if self.chat_app.context_stack:
            prev_context_class, was_silent = self.chat_app.context_stack.pop()
            self.chat_app.context = prev_context_class(self.chat_app)
            if not silent and not was_silent:
                self.chat_app.context.show_welcome_message()
        else:
            self.reset_to_login()

    def reset_to_login(self, clear_chat=True):
        """Reinicia la aplicación al estado inicial de login."""
        if clear_chat:
            self.chat_app.chat_area.messages.controls.clear()
        self.chat_app.context_stack.clear()
        self.chat_app.context = InitialContext(self.chat_app)
        self.chat_app.context.show_welcome_message()

    def show_welcome_message(self):
        """Muestra el mensaje de bienvenida del contexto (opcional para cada contexto)."""
        pass

# Contextos específicos
class InitialContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("¡Hola! Por favor, ingresa tu usuario y contraseña para continuar.", False, self.chat_app.get_current_theme())
    
    def handle_message(self, message):
        if "usuario" in message and "contraseña" in message:
            self.push_context(LoginOptionsContext)
        else:
            self.chat_app.chat_area.add_message("Por favor, ingresa un usuario y contraseña válidos. Intenta de nuevo.", False, self.chat_app.get_current_theme())

class LoginOptionsContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("¡Bienvenido! Rol: Paciente. ¿Deseas usar las funciones? (Sí/No)", False, self.chat_app.get_current_theme())
    
    def handle_message(self, message):
        match message.lower():
            case "sí" | "si" | "s" | "yes" | "y":
                self.push_context(MainMenuContext)
            case "no" | "n":
                self.chat_app.chat_area.add_message("Has elegido no usar las funciones. ¿Deseas salir? (Sí/No)", False, self.chat_app.get_current_theme())
                self.push_context(ExitPromptContext)
            case _:
                self.chat_app.chat_area.add_message("Opción no válida. Por favor, responde Sí o No.", False, self.chat_app.get_current_theme())

class MainMenuContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("Opciones disponibles: 1) Diagnóstico, 2) Historial, 3) Salir", False, self.chat_app.get_current_theme())
    
    def handle_message(self, message):
        match message.lower():
            case "1" | "diagnóstico" | "diagnostico":
                self.push_context(DiagnosisMenuContext)
            case "2" | "historial":
                self.push_context(HistoryMenuContext)
            case "3" | "salir":
                self.push_context(ExitConfirmContext)
            case _:
                self.chat_app.chat_area.add_message("Opción no válida. Elige: 1) Diagnóstico, 2) Historial, 3) Salir", False, self.chat_app.get_current_theme())

class DiagnosisMenuContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("Menú de Diagnóstico: a) Medir presión, b) Evaluar ritmo cardíaco, c) Volver", False, self.chat_app.get_current_theme())
    
    def handle_message(self, message):
        match message.lower():
            case "a" | "medir presión" | "medir presion" | "presión" | "presion":
                self.chat_app.chat_area.add_message("Simulación: Presión arterial: 120/80 mmHg (Normal). ¿Continuar? (Sí/No)", False, self.chat_app.get_current_theme())
                self.push_context(DiagnosisResultContext, silent=True)
            case "b" | "evaluar ritmo cardíaco" | "ritmo" | "cardiaco":
                self.chat_app.chat_area.add_message("Simulación: Ritmo cardíaco: 72 bpm (Normal). ¿Continuar? (Sí/No)", False, self.chat_app.get_current_theme())
                self.push_context(DiagnosisResultContext, silent=True)
            case "c" | "volver" | "atrás" | "atras":
                self.pop_context(silent=False)
            case _:
                self.chat_app.chat_area.add_message("Opción no válida. Elige: a) Medir presión, b) Evaluar ritmo, c) Volver", False, self.chat_app.get_current_theme())

class HistoryMenuContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("Menú de Historial: a) Ver consultas, b) Agregar nota, c) Volver", False, self.chat_app.get_current_theme())
    
    def handle_message(self, message):
        match message.lower():
            case "a" | "ver consultas" | "consultas":
                self.chat_app.chat_area.add_message("Historial mostrado: Consulta 1: 12/09/2025 - Normal, Consulta 2: 10/08/2025 - Revisión. ¿Volver? (Sí)", False, self.chat_app.get_current_theme())
                self.push_context(HistoryResultContext, silent=True)
            case "b" | "agregar nota" | "nota":
                self.push_context(AddNoteContext)
            case "c" | "volver" | "atrás" | "atras":
                self.pop_context(silent=False)
            case _:
                self.chat_app.chat_area.add_message("Opción no válida. Elige: a) Ver consultas, b) Agregar nota, c) Volver", False, self.chat_app.get_current_theme())

class DiagnosisResultContext(ChatContext):
    def handle_message(self, message):
        match message.lower():
            case "sí" | "si" | "s" | "volver":
                self.pop_context(silent=True)
            case "no" | "n":
                self.push_context(ReturnPromptContext)
            case _:
                self.chat_app.chat_area.add_message("Opción no válida. Por favor, responde Sí o No.", False, self.chat_app.get_current_theme())

class HistoryResultContext(ChatContext):
    def handle_message(self, message):
        match message.lower():
            case "sí" | "si" | "s" | "volver":
                self.pop_context(silent=True)
            case _:
                self.chat_app.chat_area.add_message("Opción no válida. Por favor, responde Sí.", False, self.chat_app.get_current_theme())

class AddNoteContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("Ingresa una nota para el historial.", False, self.chat_app.get_current_theme())
    
    def handle_message(self, message):
        if message.strip():
            self.chat_app.chat_area.add_message(f"Nota agregada: {message}.", False, self.chat_app.get_current_theme())
            self.pop_context(silent=True)
        else:
            self.chat_app.chat_area.add_message("Nota no ingresada. Por favor, ingresa una nota.", False, self.chat_app.get_current_theme())

# Contextos específicos (modificados)
class ExitPromptContext(ChatContext):
    def handle_message(self, message):
        match message.lower():
            case "sí" | "si" | "s":
                self.chat_app.chat_area.add_message("Cerrando sesión...", False, self.chat_app.get_current_theme())
                self.reset_to_login()
            case "no" | "n":
                self.pop_context()
            case _:
                self.chat_app.chat_area.add_message("Opción no válida. Por favor, responde Sí o No.", False, self.chat_app.get_current_theme())

class ExitConfirmContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("Confirmación de salida solicitada. ¿Estás seguro que deseas cerrar sesión? (Sí/No)", False, self.chat_app.get_current_theme())
    
    def handle_message(self, message):
        match message.lower():
            case "sí" | "si" | "s" | "yes" | "y":
                self.chat_app.chat_area.add_message("Cerrando sesión...", False, self.chat_app.get_current_theme())
                self.reset_to_login()
            case "no" | "n":
                self.pop_context()
            case _:
                self.chat_app.chat_area.add_message("Opción no válida. Por favor, responde Sí o No.", False, self.chat_app.get_current_theme())

class ReturnPromptContext(ChatContext):
    def handle_message(self, message):
        match message.lower():
            case "sí" | "si" | "s":
                self.pop_context()
            case "no" | "n":
                self.chat_app.chat_area.add_message("Cerrando sesión...", False, self.chat_app.get_current_theme())
                self.reset_to_login()
            case _:
                self.chat_app.chat_area.add_message("Opción no válida. Por favor, responde Sí o No.", False, self.chat_app.get_current_theme())