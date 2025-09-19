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
                error_msg = login_result.get("message", "Usuario y/o contraseña no válidos. Intenta de nuevo.") if isinstance(login_result, dict) else "Error desconocido al iniciar sesión."
                try:
                    self.chat_app.chat_area.add_message(error_msg, False, self.chat_app.get_current_theme())
                except Exception as e:
                    print(f"ERROR -> Error al mostrar mensaje de error de login: {str(e)}")
                    import traceback
                    print(f"DEBUG -> Traceback: {traceback.format_exc()}")
        else:
            try:
                self.chat_app.chat_area.add_message("Formato incorrecto ❌. Por favor escribe: usuario contraseña (ejemplo: pperes 123456789).", False, self.chat_app.get_current_theme())
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
                    from pacient_contexts import PacienteMainMenuContext
                    await self.push_context(PacienteMainMenuContext)
                elif rol == "médico":
                    from medic_contexts import MedicoMainMenuContext
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