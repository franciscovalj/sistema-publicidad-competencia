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
- Se comprueba que el PDF esté COMPLETO (%PDF, %%EOF y tamaño estable), no que pese
  más de X: un informe corto pesa poco y se declaraba fallido estando bien.
- El navegador nace en su propio grupo de procesos y se cierra el grupo entero, porque
  los hijos de Chromium sobreviven al padre. La limpieza va en un finally, para que
  ocurra también si cortan el programa a mitad.
- El presupuesto de tiempo virtual le da aire para descargar las tipografías del informe.
- Solo se cierra el proceso exacto que abrimos, jamás "todos los Chrome".

Licencia MIT · Francisco Val
"""

import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def _pdf_completo(pdf, tamano_anterior):
    """¿El PDF está entero? Devuelve (listo, tamaño para la próxima vuelta).

    Antes esto medía "¿pesa más de 20.000 bytes?", y un informe corto pesa menos:
    el programa declaraba fallido un PDF perfectamente bueno y además esperaba
    los 90 segundos completos antes de decirlo. Ahora se comprueba lo que de
    verdad define un PDF terminado: que empiece por %PDF, que traiga su marca de
    cierre %%EOF, y que no haya cambiado de tamaño entre dos lecturas seguidas
    (el navegador escribe el archivo de a poco y no siempre avisa que terminó).
    """
    if not os.path.exists(pdf):
        return False, -1
    tamano = os.path.getsize(pdf)
    if tamano < 1000 or tamano != tamano_anterior:
        return False, tamano          # todavía creciendo, o recién aparecido
    with open(pdf, "rb") as f:
        cabeza = f.read(5)
        f.seek(max(0, tamano - 2048))
        cola = f.read()
    return cabeza.startswith(b"%PDF") and b"%%EOF" in cola, tamano


def _cerrar_navegador(proceso):
    """Cierra el navegador que abrimos, con sus hijos, y SOLO ese.

    Nunca por nombre: matar "todos los Chrome" cerraría el navegador real del
    usuario con sus pestañas abiertas.
    """
    if proceso.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(os.getpgid(proceso.pid), signal.SIGTERM)
        else:
            proceso.terminate()
    except (ProcessLookupError, PermissionError, OSError):
        proceso.terminate()
    try:
        proceso.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            if os.name == "posix":
                os.killpg(os.getpgid(proceso.pid), signal.SIGKILL)
            else:
                proceso.kill()
        except (ProcessLookupError, PermissionError, OSError):
            pass


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
    #
    # start_new_session pone al navegador en su PROPIO grupo de procesos. Hace
    # falta porque los hijos de Chromium sobreviven a su padre: cerrar solo el
    # padre deja procesos vivos que nadie va a limpiar.
    extra = {"start_new_session": True} if os.name == "posix" else {}
    proceso = subprocess.Popen(
        [navegador, "--headless", f"--user-data-dir={perfil}",
         "--no-pdf-header-footer", "--virtual-time-budget=10000",
         f"--print-to-pdf={pdf}", Path(html).as_uri()],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **extra
    )

    # El try/finally existe para que la limpieza ocurra aunque esto falle o lo
    # corten con Ctrl+C. Sin él, un corte a mitad deja el navegador corriendo.
    try:
        anterior = -1
        for _ in range(90):
            time.sleep(1)
            listo, anterior = _pdf_completo(pdf, anterior)
            if listo:
                break
    finally:
        _cerrar_navegador(proceso)
        shutil.rmtree(perfil, ignore_errors=True)

    listo, _ = _pdf_completo(pdf, os.path.getsize(pdf) if os.path.exists(pdf) else -1)
    if not listo:
        sys.exit(
            "El PDF no se generó o quedó incompleto. Casi siempre es una ruta con error\n"
            "en el HTML o un navegador demasiado antiguo. Prueba la vía manual: abre el\n"
            "HTML, Imprimir, 'Guardar como PDF', márgenes 'Ninguno', 'Gráficos de fondo'."
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
