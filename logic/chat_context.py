import asyncio
import re
from logic.request_Functions import login, send_data, fetch_questions

class ChatContext:
    def __init__(self, chat_app):
        self.chat_app = chat_app

    async def handle_message(self, message):
        raise NotImplementedError("Subclasses must implement handle_message()")

    async def push_context(self, new_context_class, silent=False):
        """Guarda el contexto actual en la pila y cambia al nuevo."""
        self.chat_app.context_stack.append((self.__class__, silent))
        try:
            self.chat_app.context = new_context_class(self.chat_app)
            print(f"DEBUG -> Cambiando a contexto desde push_context: {self.chat_app.context.__class__.__name__}")
            if not silent:
                if asyncio.iscoroutinefunction(self.chat_app.context.show_welcome_message):
                    print(f"DEBUG -> Ejecutando show_welcome_message asíncrono para {self.chat_app.context.__class__.__name__}")
                    await self.chat_app.context.show_welcome_message()
                else:
                    print(f"DEBUG -> Ejecutando show_welcome_message síncrono para {self.chat_app.context.__class__.__name__}")
                    self.chat_app.context.show_welcome_message()
        except Exception as e:
            print(f"ERROR -> Error al cambiar al contexto {new_context_class.__name__}: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            self.chat_app.chat_area.add_message(f"Error al cambiar de contexto: {str(e)}", False, self.chat_app.get_current_theme())
            self.chat_app.context = InitialContext(self.chat_app)
            self.chat_app.context.show_welcome_message()

    def pop_context(self, silent=False):
        """Regresa al contexto anterior de la pila."""
        if self.chat_app.context_stack:
            prev_context_class, was_silent = self.chat_app.context_stack.pop()
            try:
                self.chat_app.context = prev_context_class(self.chat_app)
                print(f"DEBUG -> Restaurando contexto desde pop_context: {self.chat_app.context.__class__.__name__}")
                if not silent and not was_silent:
                    if asyncio.iscoroutinefunction(self.chat_app.context.show_welcome_message):
                        asyncio.create_task(self.chat_app.context.show_welcome_message())
                    else:
                        self.chat_app.context.show_welcome_message()
            except Exception as e:
                print(f"ERROR -> Error al restaurar contexto {prev_context_class.__name__}: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                self.chat_app.chat_area.add_message(f"Error al restaurar contexto: {str(e)}", False, self.chat_app.get_current_theme())
                self.chat_app.context = InitialContext(self.chat_app)
                self.chat_app.context.show_welcome_message()
        else:
            self.reset_to_login()

    def reset_to_login(self, clear_chat=True):
        """Reinicia al contexto inicial."""
        if clear_chat:
            try:
                self.chat_app.chat_area.messages.controls.clear()
                self.chat_app.chat_area.messages.update()
                print("DEBUG -> Área de mensajes limpiada")
            except Exception as e:
                print(f"ERROR -> Error al limpiar área de mensajes: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
        self.chat_app.context_stack.clear()
        self.chat_app.context = InitialContext(self.chat_app)
        print(f"DEBUG -> Reiniciando a InitialContext")
        self.chat_app.context.show_welcome_message()

    def show_welcome_message(self):
        pass


class InitialContext(ChatContext):
    def show_welcome_message(self):
        try:
            self.chat_app.chat_area.add_message("¿Hola cómo estás? ¿Indicar su nombre usuario y contraseña?", False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de bienvenida mostrado en InitialContext")
        except Exception as e:
            print(f"ERROR -> Error al mostrar mensaje de bienvenida en InitialContext: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")

    async def handle_message(self, message):
        if not message.strip():
            try:
                self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Por favor, ingresa usuario y contraseña.", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar mensaje de error en InitialContext: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return
            
        match = re.search(r'([^\s]+)\s+([^\s]+)', message)
        if match:
            username = match.group(1).strip()
            password = match.group(2).strip()
            print(f"DEBUG -> username: {repr(username)}, password: {repr(password)}")
            try:
                login_result = await login(username, password)
                print("DEBUG -> login_result:", repr(login_result))
            except Exception as e:
                print(f"ERROR -> Error en login: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                self.chat_app.chat_area.add_message(f"Error al iniciar sesión: {str(e)}", False, self.chat_app.get_current_theme())
                return

            if login_result and login_result["message"] == "Inicio de sesión exitoso":
                user = login_result["data"]
                self.chat_app.current_user = user
                try:
                    self.chat_app.chat_area.add_message("Validando la información...", False, self.chat_app.get_current_theme())
                    await asyncio.sleep(1)
                    self.chat_app.chat_area.add_message(f"Bienvenido {user['rol']} {user['nombre']} ", False, self.chat_app.get_current_theme())
                except Exception as e:
                    print(f"ERROR -> Error al mostrar mensajes de login en InitialContext: {str(e)}")
                    import traceback
                    print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                    return
                await self.push_context(LoginOptionsContext)
            else:
                error_msg = login_result.get("error", "Usuario y/o contraseña no válidos. Intenta de nuevo.") if isinstance(login_result, dict) else "Error desconocido al iniciar sesión."
                try:
                    self.chat_app.chat_area.add_message(error_msg, False, self.chat_app.get_current_theme())
                except Exception as e:
                    print(f"ERROR -> Error al mostrar mensaje de error de login: {str(e)}")
                    import traceback
                    print(f"DEBUG -> Traceback: {traceback.format_exc()}")
        else:
            try:
                self.chat_app.chat_area.add_message("Formato incorrecto. Debe ser: usuario contraseña", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar mensaje de formato incorrecto: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")

class LoginOptionsContext(ChatContext):
    def show_welcome_message(self):
        try:
            self.chat_app.chat_area.add_message("¿Deseas hacer uso de las funciones? (Sí/No)", False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de bienvenida mostrado en LoginOptionsContext")
        except Exception as e:
            print(f"ERROR -> Error al mostrar mensaje de bienvenida en LoginOptionsContext: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")

    async def handle_message(self, message):
        if not message.strip():
            try:
                self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Responde Sí o No.", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar mensaje de error en LoginOptionsContext: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return
            
        match message.lower():
            case "si" | "sí" | "s" | "yes" | "y":
                rol = self.chat_app.current_user["rol"].lower()
                print(f"DEBUG -> Rol del usuario: {rol}")
                if rol == "paciente":
                    await self.push_context(PacienteMainMenuContext)
                elif rol == "médico":
                    await self.push_context(MedicoMainMenuContext)
                else:
                    try:
                        self.chat_app.chat_area.add_message(f"Error: Rol de usuario '{rol}' no reconocido.", False, self.chat_app.get_current_theme())
                    except Exception as e:
                        print(f"ERROR -> Error al mostrar mensaje de rol no reconocido: {str(e)}")
                        import traceback
                        print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            case "no" | "n":
                try:
                    self.chat_app.chat_area.add_message(f"Gracias por usar nuestros servicios señor {self.chat_app.current_user['nombre']}", False, self.chat_app.get_current_theme())
                except Exception as e:
                    print(f"ERROR -> Error al mostrar mensaje de salida en LoginOptionsContext: {str(e)}")
                    import traceback
                    print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                await asyncio.sleep(2)
                self.chat_app.page.window.close()
            case _:
                try:
                    self.chat_app.chat_area.add_message("Opción no válida. Por favor, responde Sí o No.", False, self.chat_app.get_current_theme())
                except Exception as e:
                    print(f"ERROR -> Error al mostrar mensaje de opción no válida: {str(e)}")
                    import traceback
                    print(f"DEBUG -> Traceback: {traceback.format_exc()}")

class PacienteMainMenuContext(ChatContext):
    def show_welcome_message(self):
        try:
            # Mostrar opciones con saltos de línea para mejor legibilidad
            options_message = "Opciones disponibles:\n1) Sistema de reglas\n2) Indicar progreso/historial\n3) Salir del sistema"
            self.chat_app.chat_area.add_message(options_message, False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de bienvenida mostrado en PacienteMainMenuContext")
        except Exception as e:
            print(f"ERROR -> Error al mostrar mensaje de bienvenida en PacienteMainMenuContext: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")

    async def handle_message(self, message):
        if not message.strip():
            try:
                self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Elige una opción.", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar mensaje de error en PacienteMainMenuContext: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return
            
        match message.lower():
            case "1" | "sistema de reglas" | "reglas":
                print("DEBUG -> Intentando cambiar a PacienteReglasContext")
                await self.push_context(PacienteReglasContext)
            case "2" | "indicar progreso" | "progreso" | "historial":
                await self.push_context(PacienteProgresoContext)
            case "3" | "salir":
                try:
                    self.chat_app.chat_area.add_message(f"Gracias por usar nuestros servicios {self.chat_app.current_user['nombre']}", False, self.chat_app.get_current_theme())
                except Exception as e:
                    print(f"ERROR -> Error al mostrar mensaje de salida en PacienteMainMenuContext: {str(e)}")
                    import traceback
                    print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                await asyncio.sleep(2)
                self.reset_to_login()
            case _:
                try:
                    self.chat_app.chat_area.add_message("Opción no válida. Elige:\n1) Sistema de reglas\n2) Indicar progreso/historial\n3) Salir", False, self.chat_app.get_current_theme())
                except Exception as e:
                    print(f"ERROR -> Error al mostrar mensaje de opción no válida en PacienteMainMenuContext: {str(e)}")
                    import traceback
                    print(f"DEBUG -> Traceback: {traceback.format_exc()}")

class PacienteReglasContext(ChatContext):
    async def show_welcome_message(self):
        try:
            questions = await fetch_questions()
            print(f"DEBUG -> Respuesta de fetch_questions: {repr(questions)}")
        except Exception as e:
            print(f"ERROR -> Error en fetch_questions: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            self.chat_app.chat_area.add_message(f"Error al obtener preguntas: {str(e)}", False, self.chat_app.get_current_theme())
            self.pop_context()
            return
        
        # Verificar la estructura de questions
        if not isinstance(questions, dict) or "data" not in questions:
            error_msg = "Formato de respuesta inesperado de la API de preguntas."
            print(f"DEBUG -> Error en preguntas: {error_msg}")
            self.chat_app.chat_area.add_message(error_msg, False, self.chat_app.get_current_theme())
            self.pop_context()
            return
        
        questions_data = questions.get("data", [])
        if not questions_data:
            error_msg = "No se encontraron preguntas en la respuesta de la API."
            print(f"DEBUG -> Error en preguntas: {error_msg}")
            self.chat_app.chat_area.add_message(error_msg, False, self.chat_app.get_current_theme())
            self.pop_context()
            return
        
        self.chat_app.questions = questions_data
        self.chat_app.reglas_respuestas = []
        
        try:
            print("DEBUG -> Agregando mensaje de bienvenida")
            self.chat_app.chat_area.add_message("Sistema de reglas activado. Responde las siguientes preguntas para el diagnóstico:", False, self.chat_app.get_current_theme())
            print("DEBUG -> Verificando primera pregunta")
            first_question = questions_data[0]["pregunta"] + " (Sí/No)"
            print(f"DEBUG -> Primera pregunta: {first_question}")
            self.chat_app.chat_area.add_message(f"1. {first_question}", False, self.chat_app.get_current_theme())
        except Exception as e:
            print(f"ERROR -> Error al agregar mensajes en show_welcome_message: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            self.chat_app.chat_area.add_message(f"Error al mostrar preguntas: {str(e)}", False, self.chat_app.get_current_theme())
            self.pop_context()
            return

    async def handle_message(self, message):
        if not message.strip():
            try:
                self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Responde la pregunta.", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar mensaje de campo vacío: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return
        
        if message.lower() not in ["sí", "si", "no"]:
            try:
                self.chat_app.chat_area.add_message("Respuesta no válida. Por favor, responde Sí o No.", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar mensaje de respuesta no válida: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return
            
        respuestas = self.chat_app.reglas_respuestas
        respuestas.append(message.lower())
        print("DEBUG -> Respuestas hasta ahora:", respuestas)
        
        questions = getattr(self.chat_app, 'questions', [])
        
        if len(respuestas) < len(questions):
            try:
                next_question = questions[len(respuestas)]["pregunta"] + " (Sí/No)"
                print(f"DEBUG -> Mostrando siguiente pregunta: {next_question}")
                self.chat_app.chat_area.add_message(f"{len(respuestas) + 1}. {next_question}", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar la siguiente pregunta: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                self.chat_app.chat_area.add_message(f"Error al mostrar la siguiente pregunta: {str(e)}", False, self.chat_app.get_current_theme())
                self.pop_context()
                return
        else:
            respuestas_formatted = [
                {
                    "id_pregunta": question["id"],
                    "respuesta_valor": respuesta in ["sí", "si"]
                }
                for question, respuesta in zip(questions, respuestas)
            ]
            data_to_send = {
                "nombre": self.chat_app.current_user.get("nombre", "unknown"),
                "apellido": self.chat_app.current_user.get("apellido", "unknown"),
                "identificacion": self.chat_app.current_user.get("identificacion", "unknown"),
                "edad": self.chat_app.current_user.get("edad", 0),
                "sexo": self.chat_app.current_user.get("sexo", "unknown"),
                "respuestas": respuestas_formatted,
                # No se envía diagnóstico local, ya que la API lo genera
            }
            print("DEBUG -> Datos enviados:", data_to_send)
            
            try:
                send_result = await send_data(data_to_send)
                print(f"DEBUG -> Respuesta de send_data: {repr(send_result)}")
                if send_result and "message" in send_result and send_result["message"] == "Consulta y diagnóstico procesados exitosamente.":
                    try:
                        # Obtener y formatear el diagnóstico de la API
                        diagnostico_api = send_result["diagnostico"]
                        diagnostico_formatted = self.format_diagnostico(diagnostico_api)
                        self.chat_app.chat_area.add_message("Información almacenada exitosamente.", False, self.chat_app.get_current_theme())
                        self.chat_app.chat_area.add_message(f"Diagnóstico:\n{diagnostico_formatted}", False, self.chat_app.get_current_theme())
                    except Exception as e:
                        print(f"ERROR -> Error al mostrar diagnóstico de la API: {str(e)}")
                        import traceback
                        print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                        # Usar diagnóstico local como respaldo
                        diagnostico_local = self.generar_diagnostico(respuestas)
                        diagnostico_formatted = self.format_diagnostico(diagnostico_local)
                        self.chat_app.chat_area.add_message("Información almacenada exitosamente.", False, self.chat_app.get_current_theme())
                        self.chat_app.chat_area.add_message(f"Diagnóstico (local, debido a error en API):\n{diagnostico_formatted}", False, self.chat_app.get_current_theme())
                else:
                    error_msg = send_result.get("error", "Error al almacenar la información.") if isinstance(send_result, dict) else "Error desconocido al almacenar."
                    try:
                        self.chat_app.chat_area.add_message(error_msg, False, self.chat_app.get_current_theme())
                        # Usar diagnóstico local como respaldo
                        diagnostico_local = self.generar_diagnostico(respuestas)
                        diagnostico_formatted = self.format_diagnostico(diagnostico_local)
                        self.chat_app.chat_area.add_message(f"Diagnóstico (local, debido a error en API):\n{diagnostico_formatted}", False, self.chat_app.get_current_theme())
                    except Exception as e:
                        print(f"ERROR -> Error al mostrar mensaje de error o diagnóstico local: {str(e)}")
                        import traceback
                        print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            except Exception as e:
                print(f"ERROR -> Error en send_data: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                try:
                    self.chat_app.chat_area.add_message(f"Error al almacenar la información: {str(e)}", False, self.chat_app.get_current_theme())
                    # Usar diagnóstico local como respaldo
                    diagnostico_local = self.generar_diagnostico(respuestas)
                    diagnostico_formatted = self.format_diagnostico(diagnostico_local)
                    self.chat_app.chat_area.add_message(f"Diagnóstico (local, debido a error en API):\n{diagnostico_formatted}", False, self.chat_app.get_current_theme())
                except Exception as e:
                    print(f"ERROR -> Error al mostrar mensaje de error o diagnóstico local: {str(e)}")
                    import traceback
                    print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            
            self.pop_context()

    def format_diagnostico(self, diagnostico):
        """Formatea el diagnóstico con saltos de línea para mejor legibilidad."""
        try:
            if isinstance(diagnostico, dict):
                # Si es un diccionario, concatenar los valores con saltos de línea
                lines = []
                for key, value in diagnostico.items():
                    if isinstance(value, str):
                        lines.append(f"{key.capitalize()}: {value}")
                    else:
                        lines.append(f"{key.capitalize()}: {str(value)}")
                return "\n".join(lines)
            elif isinstance(diagnostico, str):
                # Si es una cadena, reemplazar ciertos caracteres con saltos de línea
                diagnostico_formatted = diagnostico.replace(";", "\n").replace(".", "\n").replace("-", "\n").replace(" ", "\n")
                # Elimina espacios en blanco adicionales y líneas vacías consecutivas
                lines = [line.strip() for line in diagnostico_formatted.split("\n") if line.strip()]
                return "\n".join(lines)
            else:
                # Si no es ni dict ni str, devolver como string
                return str(diagnostico)
        except Exception as e:
            print(f"ERROR -> Error al formatear diagnóstico: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return str(diagnostico)

    def generar_diagnostico(self, respuestas):
        """Genera un diagnóstico local como respaldo si la API falla."""
        dolor_pecho = respuestas[0] if len(respuestas) > 0 else "no"
        falta_aire = respuestas[1] if len(respuestas) > 1 else "no"
        hinchazon = respuestas[2] if len(respuestas) > 2 else "no"
        palpitaciones = respuestas[3] if len(respuestas) > 3 else "no"
        mareos = respuestas[4] if len(respuestas) > 4 else "no"

        if dolor_pecho in ["sí", "si"] or falta_aire in ["sí", "si"]:
            return "Posible problema cardiovascular grave - Contacte a un médico inmediatamente"
        elif hinchazon in ["sí", "si"] or palpitaciones in ["sí", "si"]:
            return "Posible insuficiencia cardíaca o arritmia - Consulte a un médico"
        elif mareos in ["sí", "si"]:
            return "Posible problema de presión arterial o deshidratación - Beba agua y consulte si persiste"
        else:
            return "Síntomas leves, recomiendo reposo y observación"

class PacienteProgresoContext(ChatContext):
    def show_welcome_message(self):
        try:
            self.chat_app.chat_area.add_message("Sistema de progreso/historial. Describe cómo te sientes o tus avances de salud:", False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de bienvenida mostrado en PacienteProgresoContext")
        except Exception as e:
            print(f"ERROR -> Error al mostrar mensaje de bienvenida en PacienteProgresoContext: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")

    async def handle_message(self, message):
        if not message.strip():
            try:
                self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Describe tu progreso.", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar mensaje de error en PacienteProgresoContext: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return
            
        try:
            self.chat_app.chat_area.add_message("Progreso registrado en el historial.", False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de progreso registrado mostrado")
        except Exception as e:
            print(f"ERROR -> Error al mostrar mensaje de progreso en PacienteProgresoContext: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
        self.pop_context()

class MedicoMainMenuContext(ChatContext):
    def show_welcome_message(self):
        try:
            # Mostrar opciones con saltos de línea para mejor legibilidad
            options_message = "Opciones disponibles:\n1) Sistema de reglas\n2) Seguimiento paciente\n3) Reporte\n4) Salir del sistema"
            self.chat_app.chat_area.add_message(options_message, False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de bienvenida mostrado en MedicoMainMenuContext")
        except Exception as e:
            print(f"ERROR -> Error al mostrar mensaje de bienvenida en MedicoMainMenuContext: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")

    async def handle_message(self, message):
        if not message.strip():
            try:
                self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Elige una opción.", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar mensaje de error en MedicoMainMenuContext: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return
            
        match message.lower():
            case "1" | "sistema de reglas" | "reglas":
                print("DEBUG -> Intentando cambiar a MedicoReglasContext")
                await self.push_context(MedicoReglasContext)
            case "2" | "seguimiento paciente" | "seguimiento":
                await self.push_context(MedicoSeguimientoContext)
            case "3" | "reporte":
                await self.push_context(MedicoReporteContext)
            case "4" | "salir":
                try:
                    self.chat_app.chat_area.add_message(f"Gracias por usar nuestros servicios Dr. {self.chat_app.current_user['nombre']}", False, self.chat_app.get_current_theme())
                except Exception as e:
                    print(f"ERROR -> Error al mostrar mensaje de salida en MedicoMainMenuContext: {str(e)}")
                    import traceback
                    print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                await asyncio.sleep(2)
                self.reset_to_login()
            case _:
                try:
                    self.chat_app.chat_area.add_message("Opción no válida. Elige:\n1) Sistema de reglas\n2) Seguimiento paciente\n3) Reporte\n4) Salir", False, self.chat_app.get_current_theme())
                except Exception as e:
                    print(f"ERROR -> Error al mostrar mensaje de opción no válida en MedicoMainMenuContext: {str(e)}")
                    import traceback
                    print(f"DEBUG -> Traceback: {traceback.format_exc()}")

class MedicoReglasContext(ChatContext):
    def show_welcome_message(self):
        try:
            self.chat_app.chat_area.add_message("Sistema de reglas para médico. Responde las preguntas para diagnóstico:", False, self.chat_app.get_current_theme())
            self.chat_app.chat_area.add_message("1. ¿El paciente tiene fiebre? (Sí/No)", False, self.chat_app.get_current_theme())
            self.chat_app.reglas_respuestas = []
            print("DEBUG -> Mensaje de bienvenida mostrado en MedicoReglasContext")
        except Exception as e:
            print(f"ERROR -> Error al mostrar mensaje de bienvenida en MedicoReglasContext: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")

    async def handle_message(self, message):
        if not message.strip():
            try:
                self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Responde la pregunta.", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar mensaje de error en MedicoReglasContext: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return
            
        respuestas = self.chat_app.reglas_respuestas
        respuestas.append(message.lower())
        print("DEBUG -> Respuestas hasta ahora:", respuestas)
        
        if len(respuestas) == 1:
            try:
                self.chat_app.chat_area.add_message("2. ¿El paciente tiene tos persistente? (Sí/No)", False, self.chat_app.get_current_theme())
                print("DEBUG -> Segunda pregunta mostrada en MedicoReglasContext")
            except Exception as e:
                print(f"ERROR -> Error al mostrar segunda pregunta: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
        elif len(respuestas) == 2:
            try:
                self.chat_app.chat_area.add_message("3. ¿El paciente tiene dificultad para respirar? (Sí/No)", False, self.chat_app.get_current_theme())
                print("DEBUG -> Tercera pregunta mostrada en MedicoReglasContext")
            except Exception as e:
                print(f"ERROR -> Error al mostrar tercera pregunta: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
        elif len(respuestas) == 3:
            try:
                diagnostico = self.generar_diagnostico(respuestas)
                diagnostico_formatted = self.format_diagnostico(diagnostico)
                self.chat_app.chat_area.add_message(f"Diagnóstico:\n{diagnostico_formatted}", False, self.chat_app.get_current_theme())
                self.chat_app.chat_area.add_message("Información NO almacenada (solo para consulta médica).", False, self.chat_app.get_current_theme())
                print("DEBUG -> Diagnóstico mostrado en MedicoReglasContext")
            except Exception as e:
                print(f"ERROR -> Error al mostrar diagnóstico en MedicoReglasContext: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            self.pop_context()
    
    def format_diagnostico(self, diagnostico):
        """Formatea el diagnóstico con saltos de línea para mejor legibilidad."""
        try:
            if isinstance(diagnostico, dict):
                # Si es un diccionario, concatenar los valores con saltos de línea
                lines = []
                for key, value in diagnostico.items():
                    if isinstance(value, str):
                        lines.append(f"{key.capitalize()}: {value}")
                    else:
                        lines.append(f"{key.capitalize()}: {str(value)}")
                return "\n".join(lines)
            elif isinstance(diagnostico, str):
                # Si es una cadena, buscar patrones específicos para dividir
                # Solo dividir en puntos seguidos de espacio o al final de la cadena
                lines = []
                current_line = ""
                
                # Dividir por puntos pero preservando la estructura del texto
                parts = diagnostico.split('. ')
                for i, part in enumerate(parts):
                    if part:  # Ignorar partes vacías
                        # Si es la última parte y no termina con punto, agregar el punto
                        if i == len(parts) - 1 and not part.endswith('.'):
                            lines.append(part)
                        else:
                            lines.append(part + ".")
                
                # Si no se encontraron puntos con espacios, usar el método original pero más conservador
                if len(lines) <= 1:
                    # Solo dividir en punto y coma y guiones, no en puntos
                    diagnostico_formatted = diagnostico.replace(";", "\n").replace(" - ", "\n")
                    lines = [line.strip() for line in diagnostico_formatted.split("\n") if line.strip()]
                
                return "\n".join(lines)
            else:
                # Si no es ni dict ni str, devolver como string
                return str(diagnostico)
        except Exception as e:
            print(f"ERROR -> Error al formatear diagnóstico: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return str(diagnostico)

    def generar_diagnostico(self, respuestas):
        """Genera un diagnóstico para médicos."""
        fiebre, tos_persistente, dificultad_respirar = respuestas
        if dificultad_respirar in ["sí", "si"]:
            return "Posible neumonía o enfermedad respiratoria grave - Derivar a especialista"
        elif fiebre in ["sí", "si"] and tos_persistente in ["sí", "si"]:
            return "Posible bronquitis o infección respiratoria"
        else:
            return "Síntomas leves, recomendar reposo y observación"

class MedicoSeguimientoContext(ChatContext):
    def show_welcome_message(self):
        try:
            self.chat_app.chat_area.add_message("Sistema de seguimiento. Ingresa la cédula del paciente:", False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de bienvenida mostrado en MedicoSeguimientoContext")
        except Exception as e:
            print(f"ERROR -> Error al mostrar mensaje de bienvenida en MedicoSeguimientoContext: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")

    async def handle_message(self, message):
        if not message.strip():
            try:
                self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Ingresa la cédula.", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar mensaje de error en MedicoSeguimientoContext: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return
            
        try:
            self.chat_app.chat_area.add_message(f"Buscando historial del paciente con cédula: {message}", False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de búsqueda de historial mostrado")
        except Exception as e:
            print(f"ERROR -> Error al mostrar mensaje de búsqueda en MedicoSeguimientoContext: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return
            
        await asyncio.sleep(1)
        
        historial = [
            "Consulta 01/09/2025: Paciente con fiebre y tos - Diagnóstico: Gripe común",
            "Progreso 05/09/2025: Me siento mejor, pero aún con algo de tos",
            "Consulta 10/09/2025: Síntomas mejorados, recomendar reposo adicional"
        ]
        
        for item in historial:
            try:
                self.chat_app.chat_area.add_message(f"• {item}", False, self.chat_app.get_current_theme())
                print(f"DEBUG -> Elemento de historial mostrado: {item}")
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"ERROR -> Error al mostrar elemento de historial: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                return
        
        try:
            self.chat_app.chat_area.add_message("Fin del historial.", False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de fin de historial mostrado")
        except Exception as e:
            print(f"ERROR -> Error al mostrar mensaje de fin de historial: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
        self.pop_context()

class MedicoReporteContext(ChatContext):
    def show_welcome_message(self):
        try:
            self.chat_app.chat_area.add_message("Sistema de reportes. Ingresa el correo electrónico para enviar el reporte:", False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de bienvenida mostrado en MedicoReporteContext")
        except Exception as e:
            print(f"ERROR -> Error al mostrar mensaje de bienvenida en MedicoReporteContext: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")

    async def handle_message(self, message):
        if not message.strip():
            try:
                self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Ingresa el correo.", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar mensaje de error en MedicoReporteContext: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return
            
        if "@" not in message or "." not in message:
            try:
                self.chat_app.chat_area.add_message("Correo electrónico no válido. Intenta de nuevo.", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar mensaje de correo no válido: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return
            
        try:
            self.chat_app.chat_area.add_message(f"Generando reporte y enviando a: {message}", False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de generación de reporte mostrado")
            await asyncio.sleep(2)
            self.chat_app.chat_area.add_message("Reporte enviado exitosamente. Revisa tu correo.", False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de reporte enviado mostrado")
        except Exception as e:
            print(f"ERROR -> Error al mostrar mensajes de reporte: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
        self.pop_context()