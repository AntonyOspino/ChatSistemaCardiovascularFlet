import asyncio
from logic.request_Functions import fetch_questions, send_data_fetch, fetch_pacients_progress
from logic.nlp_processing import procesar_historial
from chat_context import ChatContext
from reporting import generar_pdf_paciente, enviar_pdfs  # importa tus funciones reales


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
            self.chat_app.chat_area.add_message("Sistema de reglas activado. Responde las siguientes preguntas sobre el paciente para el diagnóstico:", False, self.chat_app.get_current_theme())
            print("DEBUG -> Verificando primera pregunta")
            first_question = questions_data[0]["pregunta"] + " (Sí/No)"
            print(f"DEBUG -> Primera pregunta: {first_question}")
            self.chat_app.chat_area.add_message(f"1. ¿El paciente presenta {first_question.lower().replace('¿', '').replace('? (sí/no)', '')}? (Sí/No)", False, self.chat_app.get_current_theme())
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
                self.chat_app.chat_area.add_message(f"{len(respuestas) + 1}. ¿El paciente presenta {next_question.lower().replace('¿', '').replace('? (sí/no)', '')}? (Sí/No)", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al mostrar la siguiente pregunta: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                self.chat_app.chat_area.add_message(f"Error al mostrar la siguiente pregunta: {str(e)}", False, self.chat_app.get_current_theme())
                self.pop_context()
                return
        else:
            try:
                # Preparar el cuerpo de la solicitud al endpoint
                respuestas_formatted = [
                    {"id_pregunta": question["id"], "respuesta_valor": respuesta in ["sí", "si"]}
                    for question, respuesta in zip(questions, respuestas)
                ]
                payload = {"respuestas": respuestas_formatted}
                print(f"DEBUG -> Payload enviado al endpoint: {payload}")

                # Realizar la solicitud al endpoint usando send_data_fetch
                result = await send_data_fetch(payload)
                print(f"DEBUG -> Respuesta del endpoint: {result}")

                if result and "diagnostico" in result:
                    diagnostico = result["diagnostico"]
                    diagnostico_formatted = self.format_diagnostico(diagnostico)
                    self.chat_app.chat_area.add_message(f"Diagnóstico para el paciente:\n{diagnostico_formatted}", False, self.chat_app.get_current_theme())
                    self.chat_app.chat_area.add_message("Información NO almacenada (solo para consulta médica).", False, self.chat_app.get_current_theme())
                elif result and "error" in result:
                    self.chat_app.chat_area.add_message(f"Error al obtener diagnóstico: {result['error']}", False, self.chat_app.get_current_theme())
                else:
                    self.chat_app.chat_area.add_message("No se pudo determinar el diagnóstico.", False, self.chat_app.get_current_theme())
            except Exception as e:
                print(f"ERROR -> Error al procesar el diagnóstico: {str(e)}")
                import traceback
                print(f"DEBUG -> Traceback: {traceback.format_exc()}")
                self.chat_app.chat_area.add_message(f"Error al procesar el diagnóstico: {str(e)}", False, self.chat_app.get_current_theme())
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
            historial_progreso = await fetch_pacients_progress(identificacion=int(message), progreso=True)
            historial_data = historial_progreso["data"][0]
            progreso = historial_data.get("progreso")  # Usar get para evitar KeyError
            print(f"DEBUG -> Historial de progreso obtenido: {repr(progreso)}")
            if not progreso or not isinstance(progreso, list):
                self.pop_context()
                self.chat_app.chat_area.add_message("No se encontraron entradas de progreso en el historial.", False, self.chat_app.get_current_theme())
                return

            # Procesar y mostrar cada entrada del historial
            for i, entry in enumerate(progreso, 1):
                texto_original = entry.get("progreso", "No hay texto disponible")
                fecha = entry.get("fecha")  # Obtener la fecha del historial
                processed = await procesar_historial(texto_original, fecha=fecha)
                mensaje = f"""
                📅 Entrada #{i} - {processed['fecha'] if processed['fecha'] else 'Sin fecha'}
                📝 Original: {processed['original']}
                🔍 Resumen: {processed['resumen']}
                😊 Sentimiento: {processed['sentimiento']}
                🌐 Traducción: {processed['traduccion']}
                🏷️ Palabras clave: {', '.join(processed['palabras_clave']) if processed['palabras_clave'] else 'Ninguna'}

                """.strip()

                self.chat_app.chat_area.add_message(mensaje, False, self.chat_app.get_current_theme())
                await asyncio.sleep(1)

            self.chat_app.chat_area.add_message("Fin del historial.", False, self.chat_app.get_current_theme())
            print("DEBUG -> Mensaje de fin de historial mostrado")
        except Exception as e:
            print(f"ERROR -> Error al procesar el historial: {str(e)}")
            import traceback
            print(f"DEBUG -> Traceback: {traceback.format_exc()}")
            self.chat_app.chat_area.add_message(f"Error al procesar el historial: {str(e)}", False, self.chat_app.get_current_theme())            
        await asyncio.sleep(1)
        self.pop_context()



class MedicoReporteContext(ChatContext):
    def __init__(self, chat_app):
        super().__init__(chat_app)
        self.estado = "esperando_paciente"
        self.cedulas = []

    def show_welcome_message(self):
        self.chat_app.chat_area.add_message(
            "Sistema de reportes.\nIngresa la cédula de paciente o cédulas separadas por coma:",
            False,
            self.chat_app.get_current_theme()
        )

    async def handle_message(self, message):
        if not message.strip():
            self.chat_app.chat_area.add_message(
                "⚠️ No puede dejar campos vacíos.",
                False,
                self.chat_app.get_current_theme()
            )
            return

        # Paso 1: ingresar cédulas
        if self.estado == "esperando_paciente":
            self.cedulas = [c.strip() for c in message.split(",") if c.strip().isdigit()]
            if not self.cedulas:
                self.chat_app.chat_area.add_message(
                    "⚠️ Ingresa cédulas válidas (numéricas, separadas por coma).",
                    False,
                    self.chat_app.get_current_theme()
                )
                return

            self.chat_app.chat_area.add_message(
                "✅ Cédulas recibidas.\nAhora ingresa el correo electrónico de destino:",
                False,
                self.chat_app.get_current_theme()
            )
            self.estado = "esperando_correo"
            return

        # Paso 2: ingresar correo
        if self.estado == "esperando_correo":
            if "@" not in message or "." not in message:
                self.chat_app.chat_area.add_message(
                    "⚠️ Correo electrónico no válido. Intenta de nuevo.",
                    False,
                    self.chat_app.get_current_theme()
                )
                return

            correo_destino = message
            try:
                self.chat_app.chat_area.add_message(
                    f"📄 Generando reporte(s) y enviando a {correo_destino}...",
                    False,
                    self.chat_app.get_current_theme()
                )

                archivos_pdf = []
                # Generar un PDF por cada cédula ingresada
                for cedula in self.cedulas:
                    pdf_path = generar_pdf_paciente(cedula)
                    archivos_pdf.append(pdf_path)

                # Enviar PDF(s) al correo
                remitente = "tonny1998frenesi@gmail.com"
                clave = "pgfv hyzs fukn rrqe"  # clave de aplicación de Gmail
                enviar_pdfs(correo_destino, remitente, clave, archivos_pdf)

                await asyncio.sleep(2)
                self.chat_app.chat_area.add_message(
                    "✅ Reporte(s) enviado(s) exitosamente.",
                    False,
                    self.chat_app.get_current_theme()
                )

            except Exception as e:
                self.chat_app.chat_area.add_message(
                    f"❌ Error al enviar el reporte: {e}",
                    False,
                    self.chat_app.get_current_theme()
                )

            # Terminar contexto
            self.pop_context()

