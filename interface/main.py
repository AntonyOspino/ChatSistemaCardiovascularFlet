from chat import ChatApp
import flet as ft
from flet import Page, MainAxisAlignment, CrossAxisAlignment

def main(page: Page):
    page.title = "Sistema Cardiovascular"
    page.vertical_alignment = MainAxisAlignment.START
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.window.width = 1000  # Ancho en píxeles
    page.window.height = 650  # Alto en píxeles
    page.window.center()
    app = ChatApp(page)

ft.app(target=main)