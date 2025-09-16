import flet as ft
import darkdetect
import asyncio
from flet import Page, MainAxisAlignment, CrossAxisAlignment, ImageFit, Colors
import sys

sys.path.append("./interface")
from interface.chat import ChatApp

async def main(page: Page):
    is_light_theme = darkdetect.isLight()

    page.title = "Sistema Cardiovascular"
    page.vertical_alignment = MainAxisAlignment.START
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.window.width = 1000  # Ancho en píxeles
    page.window.height = 650  # Alto en píxeles
    page.window.center()

    # Pantalla de carga
    logo = ft.Image(src="assets/heart-beat.png", width=600, height=600)
    progress = ft.ProgressBar(width=400, color=Colors.RED_400, value=0.0)
    carga = ft.Container(
        content=ft.Column(
            [logo, progress, ft.Text("Cargando...", size=20)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.alignment.center,
        expand=True,
        opacity=1.0,
        animate_opacity=250  # Transición de opacidad en 250ms
    )
    page.add(carga)
    page.update()

    # Animación de carga progresiva
    for i in range(0, 101, 5):  # Incrementa del 0% al 100% en pasos de 5
        progress.value = i / 100
        await asyncio.sleep(0.05)  # Pausa de 50ms por paso (total ~2.5s)
        page.update()

    # Transición suave al contenido principal
    carga.opacity = 0.0
    page.update()
    await asyncio.sleep(0.25)  # Espera la transición de opacidad
    page.controls.clear()

    # Iniciar la app
    app = ChatApp(page, is_light_theme)

ft.app(target=main)