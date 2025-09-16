import time
import re
class ChatContext:
    def __init__(self, chat_app):
        self.chat_app = chat_app

    def handle_message(self, message):
        raise NotImplementedError("Subclasses must implement handle_message()")

    def push_context(self, new_context_class, silent=False):
        self.chat_app.context_stack.append((self.__class__, silent))
        self.chat_app.context = new_context_class(self.chat_app)
        if not silent:
            self.chat_app.context.show_welcome_message()

    def pop_context(self, silent=False):
        if self.chat_app.context_stack:
            prev_context_class, was_silent = self.chat_app.context_stack.pop()
            self.chat_app.context = prev_context_class(self.chat_app)
            if not silent and not was_silent:
                self.chat_app.context.show_welcome_message()
        else:
            self.reset_to_login()

    def reset_to_login(self, clear_chat=True):
        if clear_chat:
            self.chat_app.chat_area.messages.controls.clear()
        self.chat_app.context_stack.clear()
        self.chat_app.context = InitialContext(self.chat_app)
        self.chat_app.context.show_welcome_message()

    def show_welcome_message(self):
        pass

# Base de datos simulada de usuarios
USERS_DB = {
    "pperes": {"password": "123456789", "name": "Pepito Pérez", "role": "paciente"},
    "jacosta": {"password": "123456789", "name": "José Acosta", "role": "medico"},
    "paciente1": {"password": "pass123", "name": "María García", "role": "paciente"},
    "medico1": {"password": "pass456", "name": "Carlos López", "role": "medico"}
}

class InitialContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("¿Hola cómo estás? ¿Indicar su nombre usuario y contraseña?", False, self.chat_app.get_current_theme())
    
    def handle_message(self, message):
        if not message.strip():
            self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Por favor, ingresa usuario y contraseña.", False, self.chat_app.get_current_theme())
            return
            
        # Buscar usuario y contraseña en el mensaje
        match = re.search(r'(\w+)\s+(\w+)', message)
        if match:
            username = match.group(1)
            password = match.group(2)
            
            if username in USERS_DB and USERS_DB[username]["password"] == password:
                user = USERS_DB[username]
                self.chat_app.current_user = user
                self.chat_app.chat_area.add_message("Validando la información...", False, self.chat_app.get_current_theme())
                time.sleep(1)
                self.chat_app.chat_area.add_message(f"Bienvenido {user['name']} rol {user['role']}", False, self.chat_app.get_current_theme())
                self.push_context(LoginOptionsContext)
            else:
                self.chat_app.chat_area.add_message("Usuario y/o contraseña no válidos. Intenta de nuevo.", False, self.chat_app.get_current_theme())
        else:
            self.chat_app.chat_area.add_message("Formato incorrecto. Debe ser: usuario contraseña", False, self.chat_app.get_current_theme())

class LoginOptionsContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("¿Deseas hacer uso de las funciones? (Si/No)", False, self.chat_app.get_current_theme())
    
    def handle_message(self, message):
        if not message.strip():
            self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Responde Si o No.", False, self.chat_app.get_current_theme())
            return
            
        match message.lower():
            case "si" | "sí" | "s" | "yes" | "y":
                if self.chat_app.current_user["role"] == "paciente":
                    self.push_context(PacienteMainMenuContext)
                else:
                    self.push_context(MedicoMainMenuContext)
            case "no" | "n":
                self.chat_app.chat_area.add_message(f"Gracias por usar nuestros servicios señor {self.chat_app.current_user['name']}", False, self.chat_app.get_current_theme())
                time.sleep(2)
                self.chat_app.page.window.close()
            case _:
                self.chat_app.chat_area.add_message("Opción no válida. Por favor, responde Si o No.", False, self.chat_app.get_current_theme())

# ROL PACIENTE
class PacienteMainMenuContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("Opciones disponibles: 1) Sistema de reglas 2) Indicar progreso/historial 3) Salir del sistema", False, self.chat_app.get_current_theme())
    
    def handle_message(self, message):
        if not message.strip():
            self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Elige una opción.", False, self.chat_app.get_current_theme())
            return
            
        match message.lower():
            case "1" | "sistema de reglas" | "reglas":
                self.push_context(PacienteReglasContext)
            case "2" | "indicar progreso" | "progreso" | "historial":
                self.push_context(PacienteProgresoContext)
            case "3" | "salir":
                self.chat_app.chat_area.add_message(f"Gracias por usar nuestros servicios {self.chat_app.current_user['name']}", False, self.chat_app.get_current_theme())
                time.sleep(2)
                self.reset_to_login()
            case _:
                self.chat_app.chat_area.add_message("Opción no válida. Elige: 1) Sistema de reglas 2) Indicar progreso/historial 3) Salir", False, self.chat_app.get_current_theme())

class PacienteReglasContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("Sistema de reglas activado. Responde las siguientes preguntas para el diagnóstico:", False, self.chat_app.get_current_theme())
        self.chat_app.chat_area.add_message("1. ¿Tiene fiebre? (Si/No)", False, self.chat_app.get_current_theme())
        self.chat_app.reglas_respuestas = []
    
    def handle_message(self, message):
        if not message.strip():
            self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Responde la pregunta.", False, self.chat_app.get_current_theme())
            return
            
        respuestas = self.chat_app.reglas_respuestas
        respuestas.append(message.lower())
        
        if len(respuestas) == 1:
            self.chat_app.chat_area.add_message("2. ¿Tiene tos? (Si/No)", False, self.chat_app.get_current_theme())
        elif len(respuestas) == 2:
            self.chat_app.chat_area.add_message("3. ¿Tiene dolor de cabeza? (Si/No)", False, self.chat_app.get_current_theme())
        elif len(respuestas) == 3:
            # Simular diagnóstico basado en reglas
            diagnostico = self.generar_diagnostico(respuestas)
            self.chat_app.chat_area.add_message(f"Diagnóstico: {diagnostico}", False, self.chat_app.get_current_theme())
            self.chat_app.chat_area.add_message("Información almacenada en la base de datos.", False, self.chat_app.get_current_theme())
            self.pop_context()
    
    def generar_diagnostico(self, respuestas):
        fiebre, tos, dolor_cabeza = respuestas
        if fiebre == "si" and tos == "si":
            return "Posible gripe o resfriado común"
        elif fiebre == "si" and dolor_cabeza == "si":
            return "Posible infección viral"
        elif tos == "si":
            return "Problema respiratorio leve"
        else:
            return "Síntomas normales, recomiendo descanso"

class PacienteProgresoContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("Sistema de progreso/historial. Describe cómo te sientes o tus avances de salud:", False, self.chat_app.get_current_theme())
    
    def handle_message(self, message):
        if not message.strip():
            self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Describe tu progreso.", False, self.chat_app.get_current_theme())
            return
            
        self.chat_app.chat_area.add_message("Progreso registrado en el historial.", False, self.chat_app.get_current_theme())
        self.pop_context()

# ROL MÉDICO
class MedicoMainMenuContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("Opciones disponibles: 1) Sistema de reglas 2) Seguimiento paciente 3) Reporte 4) Salir del sistema", False, self.chat_app.get_current_theme())
    
    def handle_message(self, message):
        if not message.strip():
            self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Elige una opción.", False, self.chat_app.get_current_theme())
            return
            
        match message.lower():
            case "1" | "sistema de reglas" | "reglas":
                self.push_context(MedicoReglasContext)
            case "2" | "seguimiento paciente" | "seguimiento":
                self.push_context(MedicoSeguimientoContext)
            case "3" | "reporte":
                self.push_context(MedicoReporteContext)
            case "4" | "salir":
                self.chat_app.chat_area.add_message(f"Gracias por usar nuestros servicios Dr. {self.chat_app.current_user['name']}", False, self.chat_app.get_current_theme())
                time.sleep(2)
                self.reset_to_login()
            case _:
                self.chat_app.chat_area.add_message("Opción no válida. Elige: 1) Sistema de reglas 2) Seguimiento paciente 3) Reporte 4) Salir", False, self.chat_app.get_current_theme())

class MedicoReglasContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("Sistema de reglas para médico. Responde las preguntas para diagnóstico:", False, self.chat_app.get_current_theme())
        self.chat_app.chat_area.add_message("1. ¿El paciente tiene fiebre? (Si/No)", False, self.chat_app.get_current_theme())
        self.chat_app.reglas_respuestas = []
    
    def handle_message(self, message):
        if not message.strip():
            self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Responde la pregunta.", False, self.chat_app.get_current_theme())
            return
            
        respuestas = self.chat_app.reglas_respuestas
        respuestas.append(message.lower())
        
        if len(respuestas) == 1:
            self.chat_app.chat_area.add_message("2. ¿El paciente tiene tos persistente? (Si/No)", False, self.chat_app.get_current_theme())
        elif len(respuestas) == 2:
            self.chat_app.chat_area.add_message("3. ¿El paciente tiene dificultad para respirar? (Si/No)", False, self.chat_app.get_current_theme())
        elif len(respuestas) == 3:
            diagnostico = self.generar_diagnostico(respuestas)
            self.chat_app.chat_area.add_message(f"Diagnóstico: {diagnostico}", False, self.chat_app.get_current_theme())
            self.chat_app.chat_area.add_message("Información NO almacenada (solo para consulta médica).", False, self.chat_app.get_current_theme())
            self.pop_context()
    
    def generar_diagnostico(self, respuestas):
        fiebre, tos_persistente, dificultad_respirar = respuestas
        if dificultad_respirar == "si":
            return "Posible neumonía o enfermedad respiratoria grave - Derivar a especialista"
        elif fiebre == "si" and tos_persistente == "si":
            return "Posible bronquitis o infección respiratoria"
        else:
            return "Síntomas leves, recomendar reposo y observación"

class MedicoSeguimientoContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("Sistema de seguimiento. Ingresa la cédula del paciente:", False, self.chat_app.get_current_theme())
    
    def handle_message(self, message):
        if not message.strip():
            self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Ingresa la cédula.", False, self.chat_app.get_current_theme())
            return
            
        # Simular búsqueda en base de datos
        self.chat_app.chat_area.add_message(f"Buscando historial del paciente con cédula: {message}", False, self.chat_app.get_current_theme())
        time.sleep(1)
        
        # Historial simulado
        historial = [
            "Consulta 01/09/2025: Paciente con fiebre y tos - Diagnóstico: Gripe común",
            "Progreso 05/09/2025: Me siento mejor, pero aún con algo de tos",
            "Consulta 10/09/2025: Síntomas mejorados, recomendar reposo adicional"
        ]
        
        for item in historial:
            self.chat_app.chat_area.add_message(f"• {item}", False, self.chat_app.get_current_theme())
            time.sleep(0.5)
        
        self.chat_app.chat_area.add_message("Fin del historial.", False, self.chat_app.get_current_theme())
        self.pop_context()

class MedicoReporteContext(ChatContext):
    def show_welcome_message(self):
        self.chat_app.chat_area.add_message("Sistema de reportes. Ingresa el correo electrónico para enviar el reporte:", False, self.chat_app.get_current_theme())
    
    def handle_message(self, message):
        if not message.strip():
            self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Ingresa el correo.", False, self.chat_app.get_current_theme())
            return
            
        if "@" not in message or "." not in message:
            self.chat_app.chat_area.add_message("Correo electrónico no válido. Intenta de nuevo.", False, self.chat_app.get_current_theme())
            return
            
        self.chat_app.chat_area.add_message(f"Generando reporte y enviando a: {message}", False, self.chat_app.get_current_theme())
        time.sleep(2)
        self.chat_app.chat_area.add_message("Reporte enviado exitosamente. Revisa tu correo.", False, self.chat_app.get_current_theme())
        self.pop_context()