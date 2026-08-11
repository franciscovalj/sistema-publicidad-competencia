#!/usr/bin/env python3
"""
renderizar_pdf.py — convierte el informe HTML en un PDF idéntico en cualquier computador.

Usa el navegador que ya tienes instalado (Chrome, Edge o Chromium) en modo silencioso.
No instala nada, no abre ventanas, no toca tu navegador abierto: corre con un perfil
temporal propio que se borra al terminar.

USO
---
    python3 scripts/renderizar_pdf.py informe.html informe.pdf

Si no encuentra ningún navegador compatible, te lo dice y te da las dos salidas:
instalar Chrome (gratis) o abrir el HTML y usar Imprimir → Guardar como PDF.

Las decisiones de este programa vienen de errores reales cometidos al construirlo:
- El perfil temporal aislado evita chocar con tu navegador abierto.
- La espera activa existe porque el navegador a veces no avisa cuándo terminó de escribir.
- El presupuesto de tiempo virtual le da aire para descargar las tipografías del informe.
- Solo se cierra el proceso exacto que abrimos, jamás "todos los Chrome".

Licencia MIT · Francisco Val
"""

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def encontrar_navegador():
    """Busca un navegador con modo de impresión silenciosa, por sistema operativo."""
    if sys.platform == "darwin":
        candidatos = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        ]
    elif sys.platform.startswith("win"):
        candidatos = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        ]
    else:
        candidatos = []
        for nombre in ("google-chrome", "google-chrome-stable", "chromium",
                       "chromium-browser", "microsoft-edge", "brave-browser"):
            ruta = shutil.which(nombre)
            if ruta:
                candidatos.append(ruta)

    for ruta in candidatos:
        if ruta and os.path.exists(ruta):
            return ruta
    return None


def main():
    if len(sys.argv) != 3:
        sys.exit("Uso: python3 scripts/renderizar_pdf.py informe.html informe.pdf")

    html = os.path.abspath(sys.argv[1])
    pdf = os.path.abspath(sys.argv[2])
    if not os.path.exists(html):
        sys.exit(f"No existe el archivo {html}")

    navegador = encontrar_navegador()
    if navegador is None:
        sys.exit(
            "No encontré Chrome, Edge ni Chromium en este computador.\n\n"
            "Dos salidas, cualquiera sirve:\n"
            "  1. Instala Google Chrome (gratis, google.com/chrome) y vuelve a correr esto.\n"
            "  2. Manual: abre el archivo HTML en el navegador que uses, Imprimir\n"
            "     (Ctrl+P o Cmd+P), destino 'Guardar como PDF', márgenes 'Ninguno',\n"
            "     y activa 'Gráficos de fondo'. El resultado es el mismo."
        )

    perfil = tempfile.mkdtemp(prefix="perfil-render-")
    if os.path.exists(pdf):
        os.unlink(pdf)

    # Path.as_uri() arma la URL correcta en cualquier sistema (en Windows,
    # "file://C:\..." a mano es inválida y produce un PDF vacío)
    proceso = subprocess.Popen(
        [navegador, "--headless", f"--user-data-dir={perfil}",
         "--no-pdf-header-footer", "--virtual-time-budget=10000",
         f"--print-to-pdf={pdf}", Path(html).as_uri()],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    # esperar a que el PDF exista y pese; el navegador no siempre avisa que terminó
    for _ in range(90):
        if os.path.exists(pdf) and os.path.getsize(pdf) > 20000:
            time.sleep(1)
            break
        time.sleep(1)

    if proceso.poll() is None:
        proceso.terminate()   # SOLO este proceso, jamás el navegador del usuario
    shutil.rmtree(perfil, ignore_errors=True)

    if not os.path.exists(pdf) or os.path.getsize(pdf) < 20000:
        sys.exit(
            "El PDF no se generó o quedó vacío. Casi siempre es una ruta con error en el\n"
            "HTML o un navegador demasiado antiguo. Prueba la vía manual: abre el HTML,\n"
            "Imprimir, 'Guardar como PDF', márgenes 'Ninguno', 'Gráficos de fondo' activado."
        )

    with open(pdf, "rb") as f:
        contenido = f.read()
    paginas = contenido.count(b"/Type /Page") - contenido.count(b"/Type /Pages")
    print(f"PDF listo: {pdf}")
    print(f"  {paginas} páginas · {os.path.getsize(pdf) // 1024} KB")
    print("  Antes de darlo por bueno: ábrelo y revisa página por página que nada")
    print("  quede cortado ni pegado a los bordes. Si algo se ve mal, se corrige el")
    print("  HTML y se vuelve a correr este programa.")


if __name__ == "__main__":
    main()
