"""
renderer.py — Screenshot engine via Playwright
Renderiza slides HTML em PNG 1080x1440px
"""

import asyncio
import base64
import io
import zipfile
from pathlib import Path

from playwright.async_api import async_playwright


# ─── RENDERIZAÇÃO ─────────────────────────────────────────────────────────────

async def _render_slides_async(slides_html: list[str]) -> list[bytes]:
    """
    Renderiza cada slide HTML como PNG 1080x1440.
    Aguarda fontes do Google carregarem antes de capturar.
    """
    pngs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            viewport={"width": 1080, "height": 1440},
            device_scale_factor=1,
        )
        page = await context.new_page()

        for i, html in enumerate(slides_html):
            print(f"[Renderer] Renderizando slide {i + 1}/{len(slides_html)}...")

            await page.set_content(html, wait_until="networkidle")

            # Aguarda fontes do Google carregarem
            try:
                await page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass  # Continua mesmo se timeout

            # Aguarda pequeno delay para fontes renderizarem
            await page.wait_for_timeout(300)

            png = await page.screenshot(
                type="png",
                clip={"x": 0, "y": 0, "width": 1080, "height": 1440},
                full_page=False,
            )
            pngs.append(png)

        await browser.close()

    return pngs


def render_slides(slides_html: list[str]) -> list[bytes]:
    """
    Interface síncrona para renderizar slides.
    Roda em thread separada para não conflitar com o event loop do FastAPI.
    """
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(asyncio.run, _render_slides_async(slides_html))
        return future.result(timeout=120)


# ─── EMPACOTAMENTO ────────────────────────────────────────────────────────────

def criar_zip(pngs: list[bytes], prefixo: str = "slide") -> bytes:
    """
    Empacota lista de PNGs em um arquivo ZIP em memória.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as zf:
        for i, png in enumerate(pngs, 1):
            filename = f"{prefixo}_{i:02d}.png"
            zf.writestr(filename, png)
    buf.seek(0)
    return buf.read()


def pngs_para_base64(pngs: list[bytes]) -> list[str]:
    """
    Converte lista de PNG bytes para data URLs base64 (para preview no browser).
    """
    return [
        "data:image/png;base64," + base64.b64encode(png).decode()
        for png in pngs
    ]


# ─── PIPELINE COMPLETO ────────────────────────────────────────────────────────

def renderizar_e_empacotar(
    slides_html: list[str],
    prefixo: str = "julio_carvalho",
) -> tuple[bytes, list[str]]:
    """
    Renderiza slides e retorna (zip_bytes, lista_base64_preview).
    """
    pngs    = render_slides(slides_html)
    zip_b   = criar_zip(pngs, prefixo)
    previews = pngs_para_base64(pngs)
    return zip_b, previews
