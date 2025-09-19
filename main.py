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
    page.window.width = 1000
    page.window.height = 650
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
        animate_opacity=250
    )
    page.add(carga)
    page.update()

    # Animación de carga progresiva (exactos 3.0s)
    for i in range(61):  # 0 a 60 → 61 pasos
        progress.value = i / 60  # de 0.0 a 1.0
        page.update()
        await asyncio.sleep(0.05)  # 61 × 0.05s ≈ 3.0s

    # Transición suave al contenido principal
    carga.opacity = 0.0
    page.update()
    await asyncio.sleep(0.25)
    page.controls.clear()

    # Iniciar la app
    app = ChatApp(page, is_light_theme)

ft.app(target=main)