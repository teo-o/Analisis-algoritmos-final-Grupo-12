"""Genera ``informe_final.pdf`` a partir del ``README.md`` del repositorio.

Responsable: Mateo Orozco Oquendo.

Convierte el Markdown a HTML con la biblioteca ``markdown`` y lo imprime a
PDF con Microsoft Edge o Google Chrome en modo sin ventana, para que el PDF
tenga exactamente el mismo contenido del README, gráficas incluidas.

Ejecución, desde la raíz del repositorio:
    python herramientas/generar_pdf.py
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parents[1]
README = RAIZ / "README.md"
HTML_TEMPORAL = RAIZ / "informe_final.html"
PDF = RAIZ / "informe_final.pdf"

NAVEGADORES = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
]
NOMBRES_EN_PATH = ["msedge", "google-chrome", "chromium", "chrome"]

ESTILO = """
@page { size: A4; margin: 14mm 14mm; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 9.5pt;
       line-height: 1.35; color: #1a1a1a; }
h1 { font-size: 20pt; border-bottom: 2px solid #333; padding-bottom: 4px; }
h2 { font-size: 15pt; border-bottom: 1px solid #999; margin-top: 22px;
     page-break-after: avoid; }
h3 { font-size: 12.5pt; margin-top: 16px; page-break-after: avoid; }
h4 { font-size: 11pt; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 8px 0;
        font-size: 8.5pt; page-break-inside: avoid; }
th, td { border: 1px solid #bbb; padding: 3px 6px; vertical-align: top; }
th { background: #eee; }
code { font-family: Consolas, monospace; font-size: 9pt;
       background: #f3f3f3; padding: 0 2px; }
pre { background: #f6f6f6; border: 1px solid #ddd; padding: 8px;
      font-size: 8.5pt; white-space: pre-wrap; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
img { max-width: 78%; display: block; margin: 6px auto;
      page-break-inside: avoid; }
blockquote { color: #555; border-left: 3px solid #ccc; margin-left: 0;
             padding-left: 10px; }
a { color: #1a4f8b; text-decoration: none; }
"""


def readme_a_html(texto: str) -> str:
    """Convierte el Markdown del README a un documento HTML completo.

    Args:
        texto: contenido del README en Markdown.

    Returns:
        El documento HTML con estilos para impresión en A4.
    """
    cuerpo = markdown.markdown(
        texto, extensions=["tables", "fenced_code", "sane_lists"]
    )
    return (
        "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
        f"<title>Informe final — Grupo 12</title><style>{ESTILO}</style>"
        f"</head><body>{cuerpo}</body></html>"
    )


def buscar_navegador() -> Path:
    """Encuentra Microsoft Edge o Google Chrome en el equipo.

    Returns:
        La ruta del ejecutable del navegador.

    Raises:
        FileNotFoundError: si no se encuentra ninguno.
    """
    for ruta in NAVEGADORES:
        if ruta.exists():
            return ruta
    for nombre in NOMBRES_EN_PATH:
        encontrado = shutil.which(nombre)
        if encontrado:
            return Path(encontrado)
    raise FileNotFoundError(
        "No se encontró Microsoft Edge ni Google Chrome para imprimir el PDF."
    )


def imprimir_pdf(navegador: Path, html: Path, pdf: Path) -> None:
    """Imprime el HTML a PDF con el navegador en modo sin ventana.

    Args:
        navegador: ejecutable de Edge o Chrome.
        html: archivo HTML de entrada (junto al README, para que las rutas
            relativas de las gráficas funcionen).
        pdf: archivo PDF de salida.
    """
    pdf.unlink(missing_ok=True)
    # Un perfil temporal evita que el navegador le pase la orden a una
    # ventana que el usuario ya tenga abierta y termine sin imprimir.
    with tempfile.TemporaryDirectory() as perfil:
        subprocess.run(
            [
                str(navegador),
                "--headless=new",
                "--disable-gpu",
                "--no-first-run",
                f"--user-data-dir={perfil}",
                "--no-pdf-header-footer",
                f"--print-to-pdf={pdf}",
                html.resolve().as_uri(),
            ],
            check=True,
            timeout=120,
            capture_output=True,
        )
    if not pdf.exists():
        raise RuntimeError("El navegador terminó pero no generó el PDF.")


def main() -> None:
    """Genera el PDF del informe y borra el HTML temporal."""
    sys.stdout.reconfigure(encoding="utf-8")  # consola de Windows
    HTML_TEMPORAL.write_text(
        readme_a_html(README.read_text(encoding="utf-8")), encoding="utf-8"
    )
    try:
        imprimir_pdf(buscar_navegador(), HTML_TEMPORAL, PDF)
    finally:
        HTML_TEMPORAL.unlink(missing_ok=True)
    print(f"PDF generado: {PDF}")


if __name__ == "__main__":
    main()
