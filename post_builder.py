"""
post_builder.py — Formatos de postagem além do carrossel
Cada formato tem dimensões, layout e propósito próprios.
Não modifica slide_builder.py — são builders independentes.
"""
from datetime import datetime

# ─── CSS BASE COMPARTILHADO ──────────────────────────────────────────────────

_FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,400&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">'

THEMES = {
    "dark": {
        "bg": "#0e0c0a", "text": "#f4f0e8", "gold": "#b8873a",
        "muted": "rgba(244,240,232,0.4)", "border": "rgba(244,240,232,0.08)",
        "card_bg": "#1a1714", "subtle": "rgba(244,240,232,0.06)",
    },
    "light": {
        "bg": "#f5f1e8", "text": "#0e0c0a", "gold": "#7a4e18",
        "muted": "rgba(14,12,10,0.4)", "border": "rgba(14,12,10,0.08)",
        "card_bg": "#ece8de", "subtle": "rgba(14,12,10,0.04)",
    },
    "ferrugem": {
        "bg": "#1a0a04", "text": "#f5e8d5", "gold": "#c8683a",
        "muted": "rgba(245,232,213,0.4)", "border": "rgba(245,232,213,0.08)",
        "card_bg": "#280e06", "subtle": "rgba(245,232,213,0.06)",
    },
}


def _t(theme: str) -> dict:
    return THEMES.get(theme, THEMES["dark"])


# ─── FORMATO: TWEET / QUOTE (1080×1080) ─────────────────────────────────────

def build_tweet(data: dict, theme: str = "dark", avatar_url: str | None = None) -> str:
    """
    Formato tweet/quote — 1080×1080 quadrado.
    data: { quote, author, handle, timestamp }
    """
    t = _t(theme)
    quote = data.get("quote", "")
    author = data.get("author", "Julio Carvalho")
    handle = data.get("handle", "@j.karv")
    ts = data.get("timestamp", datetime.now().strftime("%H:%M · %d %b %Y"))

    avatar_html = f'<img src="{avatar_url}" style="width:100%;height:100%;object-fit:cover;">' if avatar_url else "J"

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{_FONT_LINK}
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1080px;height:1080px;overflow:hidden;background:{t['bg']};}}

/* Grain */
body::before{{content:'';position:absolute;inset:0;z-index:10;pointer-events:none;opacity:0.22;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");
  background-size:128px 128px;mix-blend-mode:overlay;}}

/* Vignette */
body::after{{content:'';position:absolute;inset:0;z-index:9;pointer-events:none;
  background:radial-gradient(ellipse at center,transparent 40%,{t['bg']}80 100%);}}

.post{{
  width:1080px;height:1080px;display:flex;flex-direction:column;
  padding:100px 96px;position:relative;z-index:2;
}}
.header{{display:flex;align-items:center;gap:20px;margin-bottom:auto;}}
.avatar{{width:64px;height:64px;border-radius:50%;background:{t['gold']};
  display:flex;align-items:center;justify-content:center;overflow:hidden;
  font-family:'Fraunces',serif;font-size:26px;font-weight:900;color:{t['bg']};flex-shrink:0;}}
.name{{font-family:'Fraunces',serif;font-size:24px;font-weight:700;color:{t['text']};}}
.handle{{font-family:'DM Mono',monospace;font-size:18px;color:{t['gold']};letter-spacing:0.03em;margin-top:2px;}}
.quote{{
  font-family:'Fraunces',serif;font-size:72px;font-weight:700;
  line-height:1.12;letter-spacing:-0.03em;color:{t['text']};
  margin:auto 0;max-width:900px;
}}
.footer{{display:flex;align-items:center;justify-content:space-between;margin-top:auto;}}
.timestamp{{font-family:'DM Mono',monospace;font-size:18px;color:{t['muted']};letter-spacing:0.05em;}}
.bar{{width:64px;height:4px;background:{t['gold']};}}
.engagement{{display:flex;gap:40px;}}
.eng-item{{font-family:'DM Mono',monospace;font-size:16px;color:{t['muted']};}}
.eng-num{{font-family:'Fraunces',serif;font-size:22px;font-weight:900;color:{t['text']};margin-right:6px;}}
</style></head><body>
<div class="post">
  <div class="header">
    <div class="avatar">{avatar_html}</div>
    <div>
      <div class="name">{author}</div>
      <div class="handle">{handle}</div>
    </div>
  </div>
  <div class="quote">{quote}</div>
  <div class="bar"></div>
  <div class="footer">
    <div class="timestamp">{ts}</div>
  </div>
</div>
</body></html>"""


# ─── FORMATO: FEED SINGLE (1080×1350) ────────────────────────────────────────

def build_feed_single(data: dict, theme: str = "dark", avatar_url: str | None = None) -> str:
    """
    Imagem única pra feed — 1080×1350 (4:5).
    data: { eyebrow, headline, body, author }
    """
    t = _t(theme)
    eyebrow = data.get("eyebrow", "")
    headline = data.get("headline", "")
    body = data.get("body", "")
    author = data.get("author", "Julio Carvalho")
    handle = data.get("handle", "@j.karv")

    avatar_html = f'<img src="{avatar_url}" style="width:100%;height:100%;object-fit:cover;">' if avatar_url else "J"

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{_FONT_LINK}
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1080px;height:1350px;overflow:hidden;background:{t['bg']};}}
body::before{{content:'';position:absolute;inset:0;z-index:10;pointer-events:none;opacity:0.22;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");
  background-size:128px 128px;mix-blend-mode:overlay;}}
body::after{{content:'';position:absolute;inset:0;z-index:9;pointer-events:none;
  background:radial-gradient(ellipse at center,transparent 40%,{t['bg']}80 100%);}}
.post{{width:1080px;height:1350px;display:flex;flex-direction:column;justify-content:center;
  padding:100px 96px;position:relative;z-index:2;}}
.eyebrow{{font-family:'DM Mono',monospace;font-size:20px;letter-spacing:0.25em;
  text-transform:uppercase;color:{t['gold']};margin-bottom:40px;}}
.headline{{font-family:'Fraunces',serif;font-size:84px;font-weight:900;
  line-height:0.95;letter-spacing:-0.04em;color:{t['text']};max-width:900px;margin-bottom:48px;}}
.bar{{width:64px;height:4px;background:{t['gold']};margin-bottom:40px;}}
.body{{font-family:'DM Sans',sans-serif;font-size:40px;font-weight:300;
  line-height:1.5;color:{t['muted']};max-width:850px;}}
.sig{{display:flex;align-items:center;gap:18px;margin-top:auto;padding-top:48px;}}
.sig-avatar{{width:56px;height:56px;border-radius:50%;background:{t['gold']};
  display:flex;align-items:center;justify-content:center;overflow:hidden;
  font-family:'Fraunces',serif;font-size:22px;font-weight:900;color:{t['bg']};flex-shrink:0;}}
.sig-name{{font-family:'Fraunces',serif;font-size:22px;font-weight:700;color:{t['text']};}}
.sig-handle{{font-family:'DM Mono',monospace;font-size:16px;color:{t['gold']};margin-top:2px;}}
</style></head><body>
<div class="post">
  {'<div class="eyebrow">' + eyebrow + '</div>' if eyebrow else ''}
  <div class="headline">{headline}</div>
  <div class="bar"></div>
  {'<div class="body">' + body + '</div>' if body else ''}
  <div class="sig">
    <div class="sig-avatar">{avatar_html}</div>
    <div><div class="sig-name">{author}</div><div class="sig-handle">{handle}</div></div>
  </div>
</div>
</body></html>"""


# ─── FORMATO: STORY (1080×1920) ──────────────────────────────────────────────

def build_story(data: dict, theme: str = "dark", avatar_url: str | None = None) -> str:
    """
    Story — 1080×1920 (9:16).
    data: { headline, cta, body }
    """
    t = _t(theme)
    headline = data.get("headline", "")
    cta = data.get("cta", "")
    body = data.get("body", "")

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{_FONT_LINK}
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:{t['bg']};}}
body::before{{content:'';position:absolute;inset:0;z-index:10;pointer-events:none;opacity:0.22;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");
  background-size:128px 128px;mix-blend-mode:overlay;}}
body::after{{content:'';position:absolute;inset:0;z-index:9;pointer-events:none;
  background:radial-gradient(ellipse at center,transparent 30%,{t['bg']}90 100%);}}
.post{{width:1080px;height:1920px;display:flex;flex-direction:column;justify-content:center;
  align-items:center;text-align:center;padding:120px 80px;position:relative;z-index:2;}}
.headline{{font-family:'Fraunces',serif;font-size:80px;font-weight:900;
  line-height:1.0;letter-spacing:-0.03em;color:{t['text']};max-width:900px;}}
.bar{{width:80px;height:4px;background:{t['gold']};margin:48px auto;}}
.body{{font-family:'DM Sans',sans-serif;font-size:36px;font-weight:300;
  line-height:1.5;color:{t['muted']};max-width:800px;margin-bottom:60px;}}
.cta{{
  display:inline-flex;align-items:center;gap:12px;padding:24px 48px;
  border:2px solid {t['gold']};border-radius:48px;
  font-family:'DM Mono',monospace;font-size:24px;letter-spacing:0.08em;
  text-transform:uppercase;color:{t['gold']};margin-top:auto;
}}
.swipe{{font-family:'DM Mono',monospace;font-size:16px;color:{t['muted']};
  letter-spacing:0.2em;text-transform:uppercase;margin-top:48px;}}
</style></head><body>
<div class="post">
  <div style="flex:1;"></div>
  <div class="headline">{headline}</div>
  <div class="bar"></div>
  {'<div class="body">' + body + '</div>' if body else ''}
  {'<div class="cta">' + cta + ' &rarr;</div>' if cta else ''}
  <div style="flex:0.5;"></div>
  <div class="swipe">&#8593; Arraste pra cima</div>
</div>
</body></html>"""


# ─── DISPATCHER ──────────────────────────────────────────────────────────────

FORMAT_BUILDERS = {
    "tweet": build_tweet,
    "feed_single": build_feed_single,
    "story": build_story,
}

FORMAT_DIMENSIONS = {
    "tweet": (1080, 1080),
    "feed_single": (1080, 1350),
    "story": (1080, 1920),
}

def build_post(formato: str, data: dict, theme: str = "dark", avatar_url: str | None = None) -> str:
    """Gera HTML do post no formato especificado."""
    fn = FORMAT_BUILDERS.get(formato)
    if not fn:
        raise ValueError(f"Formato '{formato}' nao encontrado. Disponiveis: {list(FORMAT_BUILDERS.keys())}")
    return fn(data, theme=theme, avatar_url=avatar_url)


def render_post(formato: str, data: dict, theme: str = "dark", avatar_url: str | None = None) -> bytes:
    """Gera HTML e renderiza como PNG."""
    from renderer import render_slides
    html = build_post(formato, data, theme, avatar_url)

    # Ajustar viewport do Playwright pra dimensão do formato
    w, h = FORMAT_DIMENSIONS.get(formato, (1080, 1080))

    import asyncio
    from playwright.async_api import async_playwright

    async def _render():
        async with async_playwright() as p:
            browser = await p.chromium.launch(args=["--no-sandbox"])
            context = await browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
            page = await context.new_page()
            await page.set_content(html, wait_until="networkidle")
            await page.wait_for_timeout(800)
            png = await page.screenshot(type="png", clip={"x": 0, "y": 0, "width": w, "height": h})
            await browser.close()
            return png

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, _render()).result(timeout=30)
