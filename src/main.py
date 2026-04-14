import flet as ft
import psutil
import time


def get_linux_temperature():
    """
    Linux sistemlerde gerçek sıcaklığı okumayı dener.
    Uygun sensör yoksa None döner.
    """
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return None

        # Yaygın sensör adlarını önce dene
        preferred_keys = ["coretemp", "k10temp", "cpu_thermal", "acpitz"]

        for key in preferred_keys:
            if key in temps and temps[key]:
                for entry in temps[key]:
                    if entry.current is not None:
                        return entry.current

        # Hiçbiri yoksa ilk uygun sensörden al
        for entries in temps.values():
            for entry in entries:
                if entry.current is not None:
                    return entry.current

        return None
    except Exception:
        return None


def main(page: ft.Page):
    page.title = "System Monitor"
    page.window.width = 420
    page.window.height = 560
    page.window.resizable = False
    page.padding = 20
    page.bgcolor = "#e8f0fe"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    seconds_running = 0

    title = ft.Text(
        "System Monitor",
        size=26,
        weight=ft.FontWeight.BOLD,
    )

    subtitle = ft.Text(
        "CPU, RAM och temperaturövervakning",
        size=13,
        color=ft.Colors.BLUE_GREY_700,
    )

    timer_text = ft.Text("Körtid: 0 sek", size=14)
    updated_text = ft.Text("Senaste uppdatering: -", size=14)

    cpu_text = ft.Text("CPU: - %", size=16, weight=ft.FontWeight.W_500)
    cpu_bar = ft.ProgressBar(width=300, value=0)

    ram_text = ft.Text("RAM: - %", size=16, weight=ft.FontWeight.W_500)
    ram_bar = ft.ProgressBar(width=300, value=0)

    temp_text = ft.Text("Temperatur: -", size=16, weight=ft.FontWeight.W_500)

    status_text = ft.Text(
        "Status: Ready",
        size=16,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_GREY_800,
    )

    alert_text = ft.Text(
        "",
        size=14,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.RED,
    )

    def get_status(cpu, ram, temp):
        critical = cpu >= 90 or ram >= 90
        warning = cpu >= 75 or ram >= 75

        if temp is not None:
            if temp >= 85:
                return "Kritisk temperatur", ft.Colors.RED
            if temp >= 70:
                return "Hög temperatur", ft.Colors.ORANGE

        if critical:
            return "Kritisk belastning", ft.Colors.RED
        if warning:
            return "Hög belastning", ft.Colors.ORANGE

        return "Normal", ft.Colors.GREEN

    def update_info():
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        temp = get_linux_temperature()

        cpu_text.value = f"CPU: {cpu:.1f}%"
        ram_text.value = f"RAM: {ram:.1f}%"

        cpu_bar.value = min(cpu / 100, 1)
        ram_bar.value = min(ram / 100, 1)

        if temp is None:
            temp_text.value = "Temperatur: Ej tillgänglig i detta system"
        else:
            temp_text.value = f"Temperatur: {temp:.1f} °C"

        status, color = get_status(cpu, ram, temp)
        status_text.value = f"Status: {status}"
        status_text.color = color

        if cpu >= 90 or ram >= 90:
            alert_text.value = "Varning! Systemanvändning över 90%."
        elif temp is not None and temp >= 85:
            alert_text.value = "Varning! Temperaturen är kritiskt hög."
        else:
            alert_text.value = ""

        updated_text.value = time.strftime("Senaste uppdatering: %H:%M:%S")
        page.update()

    def manual_update(e):
        update_info()

    def auto_update():
        nonlocal seconds_running
        while True:
            seconds_running += 2
            timer_text.value = f"Körtid: {seconds_running} sek"
            update_info()
            time.sleep(2)

    info_card = ft.Card(
        content=ft.Container(
            width=360,
            padding=20,
            content=ft.Column(
                [
                    title,
                    subtitle,
                    ft.Divider(),
                    timer_text,
                    updated_text,
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
        )
    )

    monitor_card = ft.Card(
        content=ft.Container(
            width=360,
            padding=20,
            content=ft.Column(
                [
                    cpu_text,
                    cpu_bar,
                    ram_text,
                    ram_bar,
                    temp_text,
                    status_text,
                    alert_text,
                ],
                spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
        )
    )

    controls = ft.Row(
        [
            ft.ElevatedButton("Uppdatera nu", on_click=manual_update),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    page.add(
        info_card,
        monitor_card,
        controls,
    )

    update_info()
    page.run_thread(auto_update)


ft.app(target=main)