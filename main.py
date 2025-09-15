import flet as ft
import darkdetect
from flet import Page, MainAxisAlignment, CrossAxisAlignment, ImageFit
import sys

sys.path.append("./interface")
from interface.chat import ChatApp

def main(page: Page):

    is_light_theme = darkdetect.isLight()

    page.title = "Sistema Cardiovascular"
    page.vertical_alignment = MainAxisAlignment.START
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.window.width = 1000  # Ancho en píxeles
    page.window.height = 650  # Alto en píxeles
    page.window.center()

    app = ChatApp(page, is_light_theme)
ft.app(target=main)