import asyncio
from logic.request_Functions import send_data, fetch_questions, fetch_historial_data, send_data_progress
from chat_context import ChatContext

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
                await self.push_context(PacienteProgresoHistorialContext)
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
                diagnostico_formatted = diagnostico.replace(";", "\n").replace(".", "\n").replace("-", "\n").replace(" ", "\n").replace(",", "\n")
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
        
class PacienteProgresoHistorialContext(ChatContext):
    async def show_welcome_message(self):
        try:
            self.chat_app.chat_area.add_message("Seleccione una opción:\n1) Indicar progreso\n2) Ver historial de diagnósticos\n3) Volver al menú previo", False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de bienvenida mostrado en PacienteProgresoHistorialContext")
        except Exception as e:
            print(f"ERROR -> Error al mostrar mensaje de bienvenida en PacienteProgresoHistorialContext: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")

    async def handle_message(self, message):
        message = message.strip()
        if not message:
            try:
                self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Elige una opción.", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar mensaje de error en PacienteProgresoHistorialContext: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return
        match message.lower():
            case "1" | "indicar progreso" | "progreso":
                await self.push_context(PacienteProgresoContext)
            case "2" | "ver historial" | "historial":
                await self.push_context(PacienteHistorialContext)
            case "3" | "volver" | "menú":
                self.pop_context()
            case _:
                try:
                    self.chat_app.chat_area.add_message("Opción no válida. Elige:\n1) Indicar progreso\n2) Ver historial de diagnósticos\n3) Volver al menú previo", False, self.chat_app.get_current_theme())
                except Exception as e:
                    print(f"ERROR -> Error al mostrar mensaje de opción no válida en PacienteProgresoHistorialContext: {str(e)}")
                    import traceback
                    print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                    self.chat_app.chat_area.add_message("Ocurrió un error al procesar su solicitud.", False, self.chat_app.get_current_theme())


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
            progress_message = await send_data_progress({"identificacion": self.chat_app.current_user["identificacion"], "descripcion": message})
            print(f"DEBUG -> Respuesta de fetch_historial_data en progreso: {repr(progress_message)}")
            if progress_message and "message" in progress_message:
                self.chat_app.chat_area.add_message(f"{progress_message['message']}", False, self.chat_app.get_current_theme())
            else:
                self.chat_app.chat_area.add_message("Progreso registrado, pero no se recibió confirmación clara.", False, self.chat_app.get_current_theme())
            self.chat_app.chat_area.add_message("Progreso registrado en el historial.", False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de progreso registrado mostrado")
        except Exception as e:
            print(f"ERROR -> Error al mostrar mensaje de progreso en PacienteProgresoContext: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
        self.pop_context()

class PacienteHistorialContext(ChatContext):
    def show_welcome_message(self):
        try:
            self.chat_app.chat_area.add_message("Seleccione una opción:\n1) Ver historial de diagnósticos\n2) Ver ultimo registro de diagnostico\n3) Volver al menú previo", False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de bienvenida mostrado en PacienteHistorialContext")
        except Exception as e:
            print(f"ERROR -> Error al mostrar mensaje de bienvenida en PacienteHistorialContext: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
    
    async def handle_message(self, message):
        message = message.strip()
        if not message:
            try:
                self.chat_app.chat_area.add_message("No puede dejar campos vacíos. Elige una opción.", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar mensaje de error en PacienteHistorialContext: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            return
        match message.lower():
            case "1" | "ver historial" | "historial":
                try:
                    self.chat_app.chat_area.add_message("Mostrando historial de diagnósticos...", False, self.chat_app.get_current_theme())
                    print("DEBUG -> Mensaje de historial mostrado")
                    historial = await fetch_historial_data(self.chat_app.current_user.get("identificacion"))
                    print(f"DEBUG -> Respuesta de fetch_historial_data: {repr(historial)}")
                    if historial and isinstance(historial, dict) and "data" in historial:
                        historial_data = historial.get("data", [])
                        if historial_data:
                            for entry in historial_data:
                                fecha = entry.get("fecha", "Desconocida")
                                diagnostico = entry.get("diagnostico", "No disponible")
                                preguntas_respuestas = entry.get("preguntas_respuestas", [])
                                formatted_preguntas_respuestas = "\n".join([f"{item['pregunta']}: {'Sí' if item['respuesta'] == 1 else 'No' if item['respuesta'] == 0 else 'Desconocido'}" for item in preguntas_respuestas]) if preguntas_respuestas else "No disponible"
                                formatted_diagnostico = self.format_diagnostico(diagnostico)
                                self.chat_app.chat_area.add_message(f"Fecha: {fecha}\nDiagnóstico:\n{formatted_diagnostico}\nPreguntas y Respuestas:\n{formatted_preguntas_respuestas}", False, self.chat_app.get_current_theme())
                        else:
                            self.chat_app.chat_area.add_message("No se encontraron registros en el historial.", False, self.chat_app.get_current_theme())
                    else:
                        error_msg = historial.get("message", "Error al obtener el historial.") if isinstance(historial, dict) else "Error desconocido al obtener el historial."
                        self.chat_app.chat_area.add_message(error_msg, False, self.chat_app.get_current_theme())
                except Exception as e:
                    print(f"ERROR -> Error al obtener o mostrar historial en PacienteHistorialContext: {str(e)}")
                    import traceback
                    print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                    try:
                        self.chat_app.chat_area.add_message(f"Error al obtener el historial: {str(e)}", False, self.chat_app.get_current_theme())
                    except Exception as e:
                        print(f"ERROR -> Error al mostrar mensaje de error en PacienteHistorialContext: {str(e)}")
                        import traceback
                        print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                self.pop_context()
            case "2" | "ver ultimo" | "ultimo":
                try:
                    self.chat_app.chat_area.add_message("Mostrando último registro de diagnóstico...", False, self.chat_app.get_current_theme())
                    print("DEBUG -> Mensaje de último registro mostrado")
                    ultimo = await fetch_historial_data(self.chat_app.current_user.get("identificacion"), last=True)
                    print(f"DEBUG -> Respuesta de fetch_historial_data (último): {repr(ultimo)}")
                    if ultimo and isinstance(ultimo, dict) and "data" in ultimo:
                        ultimo_data = ultimo.get("data", [])
                        if ultimo_data:
                            entry = ultimo_data[0]
                            fecha = entry.get("fecha", "Desconocida")
                            diagnostico = entry.get("diagnostico", "No disponible")
                            preguntas_respuestas = entry.get("preguntas_respuestas", [])
                            formatted_preguntas_respuestas = "\n".join([f"{item['pregunta']}: {'Sí' if item['respuesta'] == 1 else 'No' if item['respuesta'] == 0 else 'Desconocido'}" for item in preguntas_respuestas]) if preguntas_respuestas else "No disponible"
                            formatted_diagnostico = self.format_diagnostico(diagnostico)
                            self.chat_app.chat_area.add_message(f"Fecha: {fecha}\nDiagnóstico:\n{formatted_diagnostico}\nPreguntas y Respuestas:\n{formatted_preguntas_respuestas}", False, self.chat_app.get_current_theme())
                        else:
                            self.chat_app.chat_area.add_message("No se encontró ningún registro en el historial.", False, self.chat_app.get_current_theme())
                    else:
                        error_msg = ultimo.get("message", "Error al obtener el último registro.") if isinstance(ultimo, dict) else "Error desconocido al obtener el último registro."
                        self.chat_app.chat_area.add_message(error_msg, False, self.chat_app.get_current_theme())
                except Exception as e:
                    print(f"ERROR -> Error al obtener o mostrar último registro en PacienteHistorialContext: {str(e)}")
                    import traceback
                    print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                    try:
                        self.chat_app.chat_area.add_message(f"Error al obtener el último registro: {str(e)}", False, self.chat_app.get_current_theme())
                    except Exception as e:
                        print(f"ERROR -> Error al mostrar mensaje de error en PacienteHistorialContext: {str(e)}")
                        import traceback
                        print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                self.pop_context()
            case "3" | "volver" | "menú":
                self.pop_context()
            case _:
                try:
                    self.chat_app.chat_area.add_message("Opción no válida. Elige:\n1) Ver historial de diagnósticos\n2) Ver último registro de diagnóstico\n3) Volver al menú previo", False, self.chat_app.get_current_theme())
                except Exception as e:
                    print(f"ERROR -> Error al mostrar mensaje de opción no válida en PacienteHistorialContext: {str(e)}")
                    import traceback
                    print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                    self.chat_app.chat_area.add_message("Error al mostrar mensaje de opción no válida.", False, self.chat_app.get_current_theme())

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
                diagnostico_formatted = diagnostico.replace(";", "\n").replace(".", "\n").replace("-", "\n").replace(" ", "\n").replace(",", "\n")
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


