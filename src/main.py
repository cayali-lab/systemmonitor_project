import flet as ft
import psutil
import random


def main(page: ft.Page):
    page.title = "System Monitor"
    page.window.width = 380
    page.window.height = 350
    page.bgcolor = "#e8f0fe"
    page.padding = 20

    cpu_text = ft.Text("CPU: -", size=16)
    ram_text = ft.Text("RAM: -", size=16)
    temp_text = ft.Text("Temperatur: -", size=16)
    status_text = ft.Text("Status: Ready", size=16, weight="bold")

    def update_info(e):
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        temp = random.randint(30, 90)

        cpu_text.value = f"CPU: {cpu}%"
        ram_text.value = f"RAM: {ram}%"
        temp_text.value = f"Temperatur: {temp} °C"

        if temp < 50:
            status_text.value = "Status: Normal"
            status_text.color = "green"
        elif temp < 70:
            status_text.value = "Status: Varm"
            status_text.color = "orange"
        else:
            status_text.value = "Status: Hög"
            status_text.color = "red"

        page.update()

    def auto_update():
        while True:
            update_info(None)

    page.add(
        ft.Text("System Monitor", size=24, weight="bold"),
        ft.Button("Uppdatera systeminfo", on_click=update_info),
        ft.Divider(),
        cpu_text,
        ram_text,
        temp_text,
        status_text,
    )

    page.run_thread(auto_update)


ft.run(main)
