"""slide_builder.py — Sistema de design fechado. Uma regra por vez, nenhuma exceção.

Sistema tipográfico:
  T1 — cover-h  : Fraunces 900  108px / lh 0.90  (covers: ≤ 4 palavras)
  T2 — h2       : Fraunces 700  96px  / lh 0.95  (hooks: ≤ 6 palavras, cta)
  T3 — h3       : Fraunces 700  72px  / lh 1.05  (corpo, diagnostico)
  B1 — body-l   : DM Sans  300  44px  / lh 1.55  (corpo principal)
  L1 — label    : DM Mono  400  26px  / lh 1.4   (eyebrow, slide-num, cta-label, dado-label)

Espaçamento fixo (tokens): 16 · 24 · 40 · 64 · 96
Padding interno mínimo: 96px (> 2× body-l 44px)

Alinhamento:
  .si          = flex-start / text-align left  (padrão para todo conteúdo)
  .si.center   = center (SOMENTE cover, cta, quote, dado)

Itálico serifado: UMA ocorrência por slide, nunca em título.
Labels: só existem se legíveis — mínimo L1 (26px render ≈ 9px phone).
Elementos repetidos (sig, progress): posição fixa — absolute, bottom constante.
"""

# ─── CSS BASE ─────────────────────────────────────────────────────────────────
BASE_CSS = """
:root {
  --ink:        #0e0c0a;
  --paper:      #f4f0e8;
  --gold:       #b8873a;
  --gold-light: #e8d5b0;
  --dark2:      #1a1714;
  --dark3:      #2a2520;
  --blood:      #3d1010;
  --rust:       #6b2d1f;
  --gold-dark:  #8a6228;
  --warm-gray:  #7a7268;
  --muted:      rgba(244,240,232,0.5);

  /* tokens de espaçamento */
  --sp1: 16px;
  --sp2: 24px;
  --sp3: 40px;
  --sp4: 64px;
  --sp5: 96px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html, body {
  width: 1080px;
  height: 1440px;
  overflow: hidden;
  background: var(--ink);
}
.s {
  width: 1080px;
  height: 1440px;
  background: var(--ink);
  color: var(--paper);
  position: relative;
  display: flex;
  flex-direction: column;
  font-family: 'DM Sans', sans-serif;
  overflow: hidden;
}

/* ── TOP BAR ── */
.top-bar {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 6px;
  background: var(--gold);
  z-index: 10;
}

/* ── PADDING INTERNO ── */
/* Padrão: alinhamento esquerdo. .center só em cover / cta / quote / dado */
.si {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  padding: 88px var(--sp5) 200px;   /* 200px bottom reserva espaço p/ elementos fixos */
  position: relative;
  z-index: 2;
  overflow: hidden;
}
.si.center {
  align-items: center;
  text-align: center;
}

/* ── ELEMENTOS FIXOS NO RODAPÉ ── */
/* Sig e progress ficam sempre na mesma posição, independente do conteúdo */
.footer-fixed {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: var(--sp3);
  z-index: 5;
  gap: var(--sp2);
}

/* ── BACKGROUNDS ── */
.bg-img {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  z-index: 0;
}
.bg-img::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(160deg,
    rgba(14,12,10,0.72) 0%,
    rgba(14,12,10,0.55) 45%,
    rgba(14,12,10,0.70) 100%);
}
.bg-grid {
  background-image:
    linear-gradient(rgba(184,135,58,0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(184,135,58,0.035) 1px, transparent 1px);
  background-size: 80px 80px;
}

/* ── SPACERS ── */
.sp  { flex: 1; }
.sp2 { flex: 2; }

/* ── SISTEMA TIPOGRÁFICO ── */

/* T1 — cover headline */
.cover-h {
  font-family: 'Fraunces', serif;
  font-size: 108px;
  font-weight: 900;
  line-height: 0.90;
  letter-spacing: -0.040em;
  color: var(--paper);
  max-width: 860px;
}

/* T2 — hook / cta headline */
h2 {
  font-family: 'Fraunces', serif;
  font-size: 96px;
  font-weight: 700;
  line-height: 0.95;
  letter-spacing: -0.035em;
  color: var(--paper);
  max-width: 860px;
}

/* T3 — corpo / diagnostico headline */
h3 {
  font-family: 'Fraunces', serif;
  font-size: 72px;
  font-weight: 700;
  line-height: 1.05;
  letter-spacing: -0.025em;
  color: var(--paper);
  max-width: 860px;
}

/* B1 — corpo de texto */
.body-l {
  font-family: 'DM Sans', sans-serif;
  font-size: 44px;
  line-height: 1.55;           /* 44 × 1.55 = 68px — espaçamento confortável */
  color: rgba(244,240,232,0.82);
  font-weight: 300;
  letter-spacing: -0.01em;
  max-width: 860px;
  flex-shrink: 1;
  min-height: 0;
}

/* L1 — labels */
.label {
  font-family: 'DM Mono', monospace;
  font-size: 26px;             /* ≈ 9px em celular — mínimo legível */
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: rgba(184,135,58,0.65);
  line-height: 1.4;
}

/* Slide number: variante da label */
.slide-num {
  font-family: 'DM Mono', monospace;
  font-size: 24px;
  letter-spacing: 0.18em;
  color: rgba(244,240,232,0.22);
}

/* Helpers */
.gold    { color: var(--gold); }
.gold-lt { color: var(--gold-light); }
.italic  { font-style: italic; }
.w700    { font-weight: 700; }

/* ── REVEAL BAR ── */
.reveal-bar {
  width: 64px;
  height: 4px;
  background: var(--gold);
  flex-shrink: 0;
}
.reveal-bar-full {
  width: 100%;
  height: 1px;
  background: rgba(184,135,58,0.25);
  flex-shrink: 0;
}

/* ── SUBTÍTULO do cover (único italic serifado neste slide) ── */
.subtitle {
  font-family: 'Fraunces', serif;
  font-style: italic;
  font-size: 48px;
  font-weight: 300;
  color: var(--gold-light);
  line-height: 1.25;
  letter-spacing: -0.015em;
  max-width: 820px;
}

/* ── DESTAQUE (único italic serifado em slides corpo/hook) ── */
.destaque-block {
  font-family: 'Fraunces', serif;
  font-style: italic;
  font-size: 48px;
  font-weight: 400;
  color: var(--gold-light);
  line-height: 1.28;
  letter-spacing: -0.015em;
  padding: var(--sp2) 0 var(--sp2) var(--sp2);
  border-left: 4px solid var(--gold);
  align-self: flex-start;      /* alinha à esquerda com o restante do conteúdo */
  max-width: 820px;
}

/* ── ASSINATURA ── */
.sig {
  display: flex;
  align-items: center;
  gap: 20px;
}
.sig-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--gold);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Fraunces', serif;
  font-size: 26px;
  font-weight: 900;
  color: var(--ink);
  overflow: hidden;
  flex-shrink: 0;
}
.sig-avatar img { width: 100%; height: 100%; object-fit: cover; }
.sig-name {
  font-family: 'Fraunces', serif;
  font-size: 26px;
  font-weight: 700;
  color: var(--paper);
  line-height: 1.2;
}
.sig-handle {
  font-family: 'DM Mono', monospace;
  font-size: 20px;
  color: var(--gold);
  letter-spacing: 0.05em;
  margin-top: 2px;
}

/* ── PROGRESS ── */
.progress {
  display: flex;
  gap: 8px;
  align-items: center;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(244,240,232,0.18);
  flex-shrink: 0;
}
.dot.active {
  background: var(--gold);
  width: 24px;
  border-radius: 4px;
}
.progress-line-wrap {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 2px;
  background: rgba(244,240,232,0.06);
  z-index: 10;
}
.progress-line-fill {
  height: 100%;
  background: var(--gold);
}

/* ── DADO ── */
.dado-numero {
  font-family: 'Fraunces', serif;
  font-size: 220px;
  font-weight: 900;
  line-height: 0.82;
  letter-spacing: -0.06em;
  color: var(--gold);
}

/* ── QUOTE ── */
.quote-mark {
  font-family: 'Fraunces', serif;
  font-size: 160px;
  font-weight: 900;
  color: rgba(184,135,58,0.10);
  line-height: 0.7;
  user-select: none;
  margin-bottom: -16px;
}
.quote-text {
  font-family: 'Fraunces', serif;
  font-style: italic;
  font-size: 64px;
  font-weight: 400;
  line-height: 1.25;
  letter-spacing: -0.02em;
  color: var(--paper);
  max-width: 840px;
}
.quote-attr {
  font-family: 'DM Mono', monospace;
  font-size: 26px;
  color: var(--gold);
  letter-spacing: 0.10em;
  margin-top: var(--sp3);
}

/* ── VERSUS ── */
.versus-wrap {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  align-self: stretch;
}
.versus-col {
  padding: 48px 56px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  text-align: left;
}
.versus-col.nao {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
}
.versus-col.sim {
  background: rgba(184,135,58,0.09);
  border: 1px solid rgba(184,135,58,0.28);
}
.versus-tag {
  font-family: 'DM Mono', monospace;
  font-size: 22px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
}
.versus-col.nao .versus-tag { color: rgba(244,240,232,0.28); }
.versus-col.sim .versus-tag { color: var(--gold); }
.versus-label {
  font-family: 'Fraunces', serif;
  font-size: 56px;
  font-weight: 700;
  line-height: 1.05;
  letter-spacing: -0.02em;
  max-width: 820px;
}
.versus-col.nao .versus-label {
  color: rgba(244,240,232,0.35);
  text-decoration: line-through;
  text-decoration-color: rgba(255,255,255,0.12);
}
.versus-col.sim .versus-label { color: var(--paper); }

/* ── DIAGNÓSTICO ── */
.diag-list {
  display: flex;
  flex-direction: column;
  width: 100%;
  align-self: stretch;
}
.diag-item {
  display: flex;
  align-items: flex-start;
  gap: var(--sp2);
  padding: var(--sp3) 0;
  border-bottom: 1px solid rgba(244,240,232,0.07);
  text-align: left;
  width: 100%;
}
.diag-item:first-child { padding-top: var(--sp2); }
.diag-item:last-child  { border-bottom: none; }
.diag-num {
  font-family: 'DM Mono', monospace;
  font-size: 22px;
  color: var(--gold);
  letter-spacing: 0.12em;
  flex-shrink: 0;
  padding-top: 8px;
  min-width: 36px;
}
.diag-text {
  font-family: 'DM Sans', sans-serif;
  font-size: 42px;
  font-weight: 300;
  line-height: 1.45;           /* 42 × 1.45 = 61px */
  color: rgba(244,240,232,0.85);
  letter-spacing: -0.01em;
  max-width: 820px;
}
/* único italic serifado no slide diagnostico */
.diag-conclusao {
  font-family: 'Fraunces', serif;
  font-style: italic;
  font-size: 46px;
  font-weight: 700;
  color: var(--gold-light);
  line-height: 1.22;
  letter-spacing: -0.015em;
  padding-top: var(--sp3);
  border-top: 2px solid rgba(184,135,58,0.4);
  max-width: 860px;
}

/* ── CTA DIVIDER ── */
.cta-divider {
  width: 100%;
  height: 1px;
  background: rgba(184,135,58,0.22);
}

/* == CONTINUIDADE */
.right-bar {
  position: absolute;
  right: 0;
  top: 80px;
  bottom: 80px;
  width: 4px;
  background: linear-gradient(to bottom, transparent 0%, rgba(184,135,58,0.55) 18%, rgba(184,135,58,0.55) 82%, transparent 100%);
  z-index: 10;
}
.swipe-cue {
  position: absolute;
  bottom: 190px;
  right: 52px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  z-index: 6;
  pointer-events: none;
}
.swipe-cue-label {
  font-family: 'DM Mono', monospace;
  font-size: 18px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(184,135,58,0.40);
  line-height: 1;
}
.swipe-cue-arrow {
  font-size: 40px;
  color: rgba(184,135,58,0.58);
  line-height: 1;
}
"""



# ─── TEMAS ────────────────────────────────────────────────────────────────────

LIGHT = (
    ':root{'
    '--ink:#f5f1e8;--paper:#0e0c0a;--gold:#7a4e18;--gold-light:#5a3812;'
    '--dark2:#ece8de;--dark3:#e2ddd3;--blood:#e4e0d6;'
    '}'
    '.body-l{color:rgba(14,12,10,.75);}'
    '.slide-num{color:rgba(14,12,10,.28);}'
    '.eyebrow{color:rgba(122,78,24,.65);}'
    '.bg-grid{background-image:linear-gradient(rgba(122,78,24,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(122,78,24,.04) 1px,transparent 1px);background-size:80px 80px;}'
    '.diag-item{border-bottom-color:rgba(14,12,10,.07);}'
    '.diag-text{color:rgba(14,12,10,.80);}'
    '.diag-conclusao{border-top-color:rgba(122,78,24,.35);}'
    '.progress-line-wrap{background:rgba(14,12,10,.06);}'
    '.swipe-cue-label{color:rgba(122,78,24,.42);}'
    '.swipe-cue-arrow{color:rgba(122,78,24,.62);}'
    '.right-bar{background:linear-gradient(to bottom,transparent 0%,rgba(122,78,24,.50) 18%,rgba(122,78,24,.50) 82%,transparent 100%);}'
    '.versus-col.nao{background:rgba(0,0,0,.04);border:1px solid rgba(0,0,0,.08);}'
    '.versus-col.nao .versus-tag{color:rgba(14,12,10,.25);}'
    '.versus-col.nao .versus-label{color:rgba(14,12,10,.32);text-decoration-color:rgba(14,12,10,.12);}'
    '.versus-col.sim{background:rgba(122,78,24,.10);border:1px solid rgba(122,78,24,.30);}'
    '.quote-mark{color:rgba(122,78,24,.12);}'
    '.reveal-bar-full{background:rgba(122,78,24,.20);}'
    '.dot{background:rgba(14,12,10,.15);}.dot.active{background:var(--gold);}'
    '.sig-handle{color:var(--gold);}'
    '.cta-divider{background:rgba(122,78,24,.22);}'
    '.destaque-block{border-left-color:var(--gold);color:var(--gold-light);}'
    '.cover-h{color:var(--paper);}h2{color:var(--paper);}h3{color:var(--paper);}'
    '.quote-text{color:var(--paper);}.subtitle{color:var(--gold-light);}'
    '.footer-fixed{border-top-color:rgba(122,78,24,.15);}'
    'html,body,.s{background:var(--paper);}'
)

FERRUGEM = (
    ':root{'
    '--ink:#1a0a04;--paper:#f5e8d5;--gold:#c8683a;--gold-light:#e0a070;'
    '--dark2:#280e06;--dark3:#3e1c0c;--blood:#5c2210;'
    '}'
    '.body-l{color:rgba(245,232,213,.82);}'
    '.slide-num{color:rgba(245,232,213,.22);}'
    '.eyebrow{color:rgba(200,104,58,.70);}'
    '.bg-grid{background-image:linear-gradient(rgba(200,104,58,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(200,104,58,.05) 1px,transparent 1px);background-size:80px 80px;}'
    '.diag-item{border-bottom-color:rgba(245,232,213,.07);}'
    '.diag-text{color:rgba(245,232,213,.85);}'
    '.diag-conclusao{border-top-color:rgba(200,104,58,.40);}'
    '.progress-line-wrap{background:rgba(245,232,213,.06);}'
    '.swipe-cue-label{color:rgba(200,104,58,.45);}'
    '.swipe-cue-arrow{color:rgba(200,104,58,.65);}'
    '.right-bar{background:linear-gradient(to bottom,transparent 0%,rgba(200,104,58,.60) 18%,rgba(200,104,58,.60) 82%,transparent 100%);}'
    '.versus-col.nao{background:rgba(245,232,213,.03);border:1px solid rgba(245,232,213,.07);}'
    '.versus-col.sim{background:rgba(200,104,58,.10);border:1px solid rgba(200,104,58,.30);}'
    '.quote-mark{color:rgba(200,104,58,.12);}'
    '.reveal-bar-full{background:rgba(200,104,58,.25);}'
    '.dot{background:rgba(245,232,213,.18);}.dot.active{background:var(--gold);}'
    '.sig-handle{color:var(--gold);}'
    '.cta-divider{background:rgba(200,104,58,.22);}'
    '.destaque-block{border-left-color:var(--gold);color:var(--gold-light);}'
)

THEME_CSS = {
    "dark":     "",
    "light":    LIGHT,
    "ferrugem": FERRUGEM,
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────
_FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,400&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">'

def _html(body: str, theme: str = 'dark') -> str:
    theme_override = THEME_CSS.get(theme, '')
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">{_FONT_LINK}<style>{BASE_CSS}{theme_override}</style></head><body>{body}</body></html>"""


def _footer(index: int, total: int, avatar_url: str | None = None, show_sig: bool = False, is_last: bool = False) -> str:
    """Rodapé fixo: sig (opcional) + progress dots + barra de progresso.
    Sempre posicionado no mesmo lugar em todos os slides."""
    dots = "".join(
        f'<div class="dot{"  active" if i == index else ""}"></div>'
        for i in range(1, total + 1)
    )
    pct = int(index / total * 100)

    sig_html = ""
    if show_sig:
        inner = f'<img src="{avatar_url}" alt="">' if avatar_url else "J"
        sig_html = f"""
    <div class="sig">
      <div class="sig-avatar">{inner}</div>
      <div>
        <div class="sig-name">Julio Carvalho</div>
        <div class="sig-handle">@j.karv</div>
      </div>
    </div>"""

    return f"""
<div class="footer-fixed">
  {sig_html}
  <div class="progress">{dots}</div>
</div>
<div class="progress-line-wrap">
  <div class="progress-line-fill" style="width:{pct}%"></div>
</div>{_right_bar() if not is_last else ""}{_swipe_cue() if not is_last else ""}"""


def _slide_bg_class(imagem_url: str | None) -> str:
    """Retorna class do slide: bg-grid quando sem imagem, vazio quando tem."""
    return "" if imagem_url else " bg-grid"

def _slide_bg_html(imagem_url: str | None) -> str:
    """Retorna HTML do background image para slides do meio (com overlay)."""
    if not imagem_url:
        return ""
    return f'<div class="bg-img" style="background-image:url(\'{imagem_url}\')"></div>'

def _dark_bg(imagem_url: str | None, theme: str = 'dark') -> str:
    """Fundo do slide — imagem ou fallback gradient temático."""
    if imagem_url:
        return f'<div class="bg-img" style="background-image:url(\'{imagem_url}\')"></div>'
    if theme == 'light':
        return '<div style="position:absolute;inset:0;z-index:0;background:linear-gradient(160deg,#ece8de 0%,#e4e0d5 60%,#dad6cc 100%);"><div style="position:absolute;inset:0;background-image:linear-gradient(rgba(122,78,24,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(122,78,24,.03) 1px,transparent 1px);background-size:60px 60px;"></div></div>'
    if theme == 'ferrugem':
        return '<div style="position:absolute;inset:0;z-index:0;background:var(--blood);"><div style="position:absolute;inset:0;background:radial-gradient(ellipse at 80% 20%,rgba(200,104,58,.20) 0%,transparent 50%),linear-gradient(160deg,#3d1208 0%,#2a0a04 50%,#1a0804 100%);"></div><div style="position:absolute;inset:0;background-image:linear-gradient(rgba(200,104,58,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(200,104,58,.05) 1px,transparent 1px);background-size:60px 60px;"></div></div>'
    return '<div style="position:absolute;inset:0;z-index:0;background:var(--blood);"><div style="position:absolute;inset:0;background:radial-gradient(ellipse at 80% 20%,rgba(184,135,58,.12) 0%,transparent 50%),radial-gradient(ellipse at 20% 80%,rgba(107,45,31,.4) 0%,transparent 50%),linear-gradient(160deg,#2a0a0a 0%,#1a0808 40%,#0e0c0a 100%);"></div><div style="position:absolute;inset:0;background-image:linear-gradient(rgba(184,135,58,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(184,135,58,.04) 1px,transparent 1px);background-size:60px 60px;"></div></div>'



def _right_bar():
    return '<div class="right-bar"></div>'

def _swipe_cue():
    return ('<div class="swipe-cue">' + '<div class="swipe-cue-label">pr&#xF3;ximo</div>' + '<div class="swipe-cue-arrow">&#x2192;</div>' + '</div>')

# ─── COVER ────────────────────────────────────────────────────────────────────
# Centrado: headline curto (≤ 5 palavras) + subtitle (1 italic por slide)
# Sig aparece no cover porque é o cartão de visita do criador
def slide_cover(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = "dark") -> str:
    headline = data.get("headline", "").replace("\n", "<br>")
    subtitle = data.get("subtitle", "")
    eyebrow  = data.get("eyebrow", "")
    index, total = data.get("index", 1), data.get("total", 7)

    eyebrow_html = f'<div class="label" style="margin-bottom:var(--sp4);">{eyebrow}</div>' if eyebrow else f'<div style="height:var(--sp4);"></div>'
    subtitle_html = f'<div style="margin-top:var(--sp3);" class="subtitle">{subtitle}</div>' if subtitle else ""

    return _html(f"""<div class="s">
  <div class="top-bar"></div>
  {_dark_bg(imagem_url, theme)}
  <div class="si center">
    <div class="sp" style="flex:0.8"></div>
    {eyebrow_html}
    <div class="cover-h">{headline}</div>
    <div style="margin-top:var(--sp3);"><div class="reveal-bar" style="margin:0 auto;"></div></div>
    {subtitle_html}
    <div class="sp"></div>
  </div>
  {_footer(index, total, avatar_url, show_sig=True)}
</div>""", theme=theme)


# ─── HOOK ─────────────────────────────────────────────────────────────────────
# Esquerda: headline médio (≤ 7 palavras) + body + 1 destaque italic
def slide_hook(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = "dark") -> str:
    headline = data.get("headline", "").replace("\n", "<br>")
    body_txt = data.get("body", "").replace("\n", "<br>")
    destaque = data.get("destaque", "")
    index, total = data.get("index", 2), data.get("total", 7)

    destaque_html = f"""
    <div style="margin-top:var(--sp4);">
      <div class="destaque-block">{destaque}</div>
    </div>""" if destaque else ""

    bg_cls = _slide_bg_class(imagem_url)
    bg_html = _slide_bg_html(imagem_url)

    return _html(f"""<div class="s{bg_cls}">
  <div class="top-bar"></div>
  {bg_html}
  <div class="si">
    <div class="sp" style="flex:0.5"></div>
    <h2>{headline}</h2>
    <div style="margin-top:var(--sp2);"><div class="reveal-bar"></div></div>
    <div style="margin-top:var(--sp3);" class="body-l">{body_txt}</div>
    {destaque_html}
    <div class="sp"></div>
  </div>
  {_footer(index, total, avatar_url)}
</div>""", theme=theme)


# ─── CORPO ────────────────────────────────────────────────────────────────────
# Esquerda: slide-num (L1) + h3 + linha + body + destaque (opcional)
def slide_corpo(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = "dark") -> str:
    headline = data.get("headline", "").replace("\n", "<br>")
    body_txt = data.get("body", "").replace("\n", "<br>")
    destaque = data.get("destaque", "")
    index, total = data.get("index", 3), data.get("total", 7)

    destaque_html = f'<div style="margin-top:var(--sp3);" class="destaque-block">{destaque}</div>' if destaque else ""

    return _html(f"""<div class="s">
  <div class="top-bar"></div>
  <div class="si">
    <div class="slide-num">{index:02d} — {total:02d}</div>
    <div class="sp" style="flex:0.5;min-height:var(--sp4);flex-shrink:0;"></div>
    <h3>{headline}</h3>
    <div style="margin-top:var(--sp2);"><div class="reveal-bar-full"></div></div>
    <div style="margin-top:var(--sp3);" class="body-l">{body_txt}</div>
    {destaque_html}
    <div class="sp"></div>
  </div>
  {_footer(index, total, avatar_url)}
</div>""", theme=theme)


# ─── DADO ─────────────────────────────────────────────────────────────────────
# Centrado: número enorme + label (L1) + corpo de texto
def slide_dado(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = "dark") -> str:
    numero   = data.get("numero", "—")
    label    = data.get("label", "")
    body_txt = data.get("body", "").replace("\n", "<br>")
    index, total = data.get("index", 4), data.get("total", 7)

    bg_cls = _slide_bg_class(imagem_url)
    bg_html = _slide_bg_html(imagem_url)

    return _html(f"""<div class="s{bg_cls}">
  <div class="top-bar"></div>
  {bg_html}
  <div class="si center">
    <div class="sp" style="flex:0.6"></div>
    <div class="dado-numero">{numero}</div>
    <div style="margin-top:var(--sp2);" class="label">{label}</div>
    <div style="margin-top:var(--sp4);width:56px;height:3px;background:var(--gold);margin-left:auto;margin-right:auto;"></div>
    <div style="margin-top:var(--sp3);" class="body-l" style="text-align:left;">{body_txt}</div>
    <div class="sp" style="flex:0.4"></div>
  </div>
  {_footer(index, total, avatar_url)}
</div>""", theme=theme)


# ─── QUOTE ────────────────────────────────────────────────────────────────────
# Centrado: aspas decorativas + quote (todo italic) + atribuição (L1)
def slide_quote(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = "dark") -> str:
    quote_txt = data.get("quote", "").replace("\n", "<br>")
    attr      = data.get("atribuicao", "Julio Carvalho")
    index, total = data.get("index", 5), data.get("total", 7)

    return _html(f"""<div class="s" style="background:var(--dark2);">
  <div class="top-bar"></div>
  <div class="si center">
    <div class="sp" style="flex:0.5"></div>
    <div class="quote-mark">"</div>
    <div style="margin-top:var(--sp1);" class="quote-text">{quote_txt}</div>
    <div class="quote-attr">— {attr}</div>
    <div class="sp"></div>
  </div>
  {_footer(index, total, avatar_url)}
</div>""", theme=theme)


# ─── VERSUS ───────────────────────────────────────────────────────────────────
# Esquerda: cards empilhados + body explicativo embaixo
def slide_versus(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = "dark") -> str:
    label_nao = data.get("label_nao", "").replace("\n", "<br>")
    label_sim = data.get("label_sim", "").replace("\n", "<br>")
    body_txt  = data.get("body", "").replace("\n", "<br>")
    index, total = data.get("index", 6), data.get("total", 7)

    body_html = f'<div style="margin-top:var(--sp3);" class="body-l">{body_txt}</div>' if body_txt else ""

    bg_cls = _slide_bg_class(imagem_url)
    bg_html = _slide_bg_html(imagem_url)

    return _html(f"""<div class="s{bg_cls}">
  <div class="top-bar"></div>
  {bg_html}
  <div class="si">
    <div class="sp" style="flex:0.3"></div>
    <div class="versus-wrap">
      <div class="versus-col nao">
        <div class="versus-tag">O mercado faz</div>
        <div class="versus-label">{label_nao}</div>
      </div>
      <div class="versus-col sim">
        <div class="versus-tag">A realidade é</div>
        <div class="versus-label">{label_sim}</div>
      </div>
    </div>
    {body_html}
    <div class="sp"></div>
  </div>
  {_footer(index, total, avatar_url)}
</div>""", theme=theme)


# ─── DIAGNÓSTICO ──────────────────────────────────────────────────────────────
# Esquerda: h3 + linha + itens numerados (max 3) + conclusão italic
def slide_diagnostico(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = "dark") -> str:
    headline  = data.get("headline", "").replace("\n", "<br>")
    itens     = data.get("itens", [])[:3]
    conclusao = data.get("conclusao", "").replace("\n", "<br>")
    index, total = data.get("index", 7), data.get("total", 7)

    itens_html = "".join(f"""
    <div class="diag-item">
      <div class="diag-num">{i+1:02d}</div>
      <div class="diag-text">{item}</div>
    </div>""" for i, item in enumerate(itens))

    conclusao_html = f'<div style="margin-top:var(--sp2);" class="diag-conclusao">{conclusao}</div>' if conclusao else ""

    return _html(f"""<div class="s">
  <div class="top-bar"></div>
  <div class="si">
    <div class="sp" style="flex:0.35;min-height:40px;flex-shrink:0;"></div>
    <h3>{headline}</h3>
    <div style="margin-top:var(--sp2);"><div class="reveal-bar-full"></div></div>
    <div class="diag-list">{itens_html}</div>
    {conclusao_html}
    <div class="sp"></div>
  </div>
  {_footer(index, total, avatar_url)}
</div>""", theme=theme)


# ─── CTA ──────────────────────────────────────────────────────────────────────
# Centrado: label (L1) + h2 + sub + divisor + sig (sig aparece aqui também)
def slide_cta(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = "dark") -> str:
    headline = data.get("headline", "").replace("\n", "<br>")
    sub      = data.get("sub", "")
    index, total = data.get("index", 7), data.get("total", 7)

    sub_html = f'<div style="margin-top:var(--sp3);" class="body-l gold-lt">{sub}</div>' if sub else ""

    return _html(f"""<div class="s">
  <div class="top-bar"></div>
  {_dark_bg(imagem_url, theme)}
  <div class="si center">
    <div class="sp"></div>
    <div class="label" style="color:rgba(184,135,58,0.55);">Próximo passo</div>
    <div style="margin-top:var(--sp2);"><div class="reveal-bar" style="margin:0 auto;"></div></div>
    <div style="margin-top:var(--sp3);"><h2>{headline}</h2></div>
    {sub_html}
    <div class="sp" style="flex:0.5"></div>
    <div style="width:100%;height:1px;background:rgba(184,135,58,0.22);"></div>
    <div style="height:var(--sp4);"></div>
  </div>
  {_footer(index, total, avatar_url, show_sig=True, is_last=True)}
</div>""", theme=theme)


# ─── COVER FOTO ──────────────────────────────────────────────────────────────
# Layout premium: foto pessoal à direita, shape dourado, texto à esquerda

def slide_cover_foto(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = 'dark') -> str:
    headline = data.get("headline", "").replace("\n", "<br>")
    subtitle = data.get("subtitle", "")
    eyebrow  = data.get("eyebrow", "")
    cta_text = data.get("cta_text", "")
    foto_url = data.get("foto_url", "")
    index, total = data.get("index", 1), data.get("total", 7)

    cta_html = f"""
    <div style="margin-top:48px;">
      <div style="display:inline-flex;align-items:center;gap:12px;padding:18px 32px;
        border:1px solid rgba(244,240,232,0.25);border-radius:40px;
        font-family:'DM Sans',sans-serif;font-size:28px;color:var(--paper);
        letter-spacing:0.02em;">
        {cta_text} <span style="font-size:24px;">→</span>
      </div>
    </div>""" if cta_text else ""

    # Shape dourado decorativo atrás da foto
    gold_shape = """
    <div style="position:absolute;right:120px;top:80px;bottom:200px;width:320px;
      background:linear-gradient(180deg,var(--gold) 0%,rgba(184,135,58,0.4) 100%);
      z-index:1;transform:skewX(-4deg);"></div>"""

    foto_html = f"""
    <div style="position:absolute;right:0;bottom:0;width:580px;height:100%;z-index:2;
      display:flex;align-items:flex-end;justify-content:center;overflow:hidden;">
      <img src="{foto_url}" alt="" style="height:92%;width:auto;object-fit:cover;
        object-position:center top;filter:brightness(0.95);">
    </div>""" if foto_url else ""

    return _html(f"""<div class="s" style="background:var(--ink);">
  <div class="top-bar"></div>
  {gold_shape}
  {foto_html}
  <div class="si" style="position:relative;z-index:3;">
    <div style="font-family:'Fraunces',serif;font-size:20px;font-weight:700;
      color:var(--paper);letter-spacing:0.08em;">JULIO<span style="color:var(--gold);">CARVALHO</span></div>
    <div class="sp" style="flex:0.6"></div>
    <div style="max-width:520px;">
      <div style="font-family:'DM Sans',sans-serif;font-size:36px;font-weight:300;
        color:rgba(244,240,232,0.75);line-height:1.45;letter-spacing:-0.01em;">{subtitle}</div>
      <div style="margin-top:24px;font-family:'Fraunces',serif;font-size:96px;font-weight:900;
        line-height:0.92;letter-spacing:-0.04em;color:var(--paper);">{headline}</div>
      {cta_html}
    </div>
    <div class="sp"></div>
  </div>
  {_footer(index, total, is_last=False)}
</div>""", theme=theme)


# ─── HOOK FOTO ───────────────────────────────────────────────────────────────
# Layout premium: foto à esquerda menor, texto à direita com bullet points

def slide_hook_foto(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = 'dark') -> str:
    headline = data.get("headline", "").replace("\n", "<br>")
    subtitle = data.get("subtitle", "")
    pontos_nao = data.get("pontos_nao", [])
    ponto_sim  = data.get("ponto_sim", "")
    foto_url   = data.get("foto_url", "")
    index, total = data.get("index", 2), data.get("total", 7)

    # Pontos negativos (X vermelho)
    pontos_html = ""
    for p in pontos_nao:
        pontos_html += f"""
      <div style="display:flex;align-items:center;gap:20px;margin-top:20px;">
        <div style="width:40px;height:40px;border-radius:8px;background:rgba(220,60,60,0.85);
          display:flex;align-items:center;justify-content:center;flex-shrink:0;
          font-family:'DM Sans',sans-serif;font-size:22px;font-weight:600;color:white;">✕</div>
        <div style="font-family:'DM Sans',sans-serif;font-size:34px;font-weight:400;
          color:rgba(244,240,232,0.85);line-height:1.3;">{p}</div>
      </div>"""

    # Ponto positivo (check verde) com destaque
    sim_html = ""
    if ponto_sim:
        sim_html = f"""
      <div style="display:flex;align-items:center;gap:20px;margin-top:36px;
        padding:24px 28px;background:rgba(244,240,232,0.08);
        border:1px solid rgba(244,240,232,0.12);border-radius:12px;">
        <div style="width:44px;height:44px;border-radius:50%;
          background:linear-gradient(135deg,#2ecc71,#27ae60);
          display:flex;align-items:center;justify-content:center;flex-shrink:0;
          font-size:24px;color:white;">✓</div>
        <div style="font-family:'DM Sans',sans-serif;font-size:34px;font-weight:600;
          color:var(--paper);line-height:1.3;">{ponto_sim}</div>
      </div>"""

    # Shape dourado + foto
    gold_shape = """
    <div style="position:absolute;left:80px;top:120px;bottom:240px;width:260px;
      background:linear-gradient(180deg,var(--gold) 0%,rgba(184,135,58,0.3) 100%);
      z-index:1;transform:skewX(-4deg);"></div>"""

    foto_html = f"""
    <div style="position:absolute;left:0;bottom:0;width:480px;height:100%;z-index:2;
      display:flex;align-items:flex-end;justify-content:center;overflow:hidden;">
      <img src="{foto_url}" alt="" style="height:88%;width:auto;object-fit:cover;
        object-position:center top;filter:brightness(0.95);">
    </div>""" if foto_url else ""

    return _html(f"""<div class="s" style="background:var(--ink);">
  <div class="top-bar"></div>
  {gold_shape}
  {foto_html}
  <div class="si" style="position:relative;z-index:3;">
    <div style="font-family:'Fraunces',serif;font-size:20px;font-weight:700;
      color:var(--paper);letter-spacing:0.08em;text-align:right;">JULIO<span style="color:var(--gold);">CARVALHO</span></div>
    <div class="sp" style="flex:0.3"></div>
    <div style="margin-left:auto;max-width:560px;">
      <div style="font-family:'DM Sans',sans-serif;font-size:32px;font-weight:300;
        color:rgba(244,240,232,0.70);line-height:1.45;">{subtitle}</div>
      <div style="margin-top:16px;font-family:'Fraunces',serif;font-size:72px;font-weight:900;
        line-height:0.95;letter-spacing:-0.035em;color:var(--paper);">{headline}</div>
      <div style="margin-top:32px;">{pontos_html}</div>
      {sim_html}
    </div>
    <div class="sp"></div>
  </div>
  {_footer(index, total, is_last=False)}
</div>""", theme=theme)


# ─── DISPATCHER ───────────────────────────────────────────────────────────────
SLIDE_BUILDERS = {
    "cover":       slide_cover,
    "cover_foto":  slide_cover_foto,
    "hook":        slide_hook,
    "hook_foto":   slide_hook_foto,
    "corpo":       slide_corpo,
    "dado":        slide_dado,
    "quote":       slide_quote,
    "versus":      slide_versus,
    "diagnostico": slide_diagnostico,
    "cta":         slide_cta,
}


def build_slide(slide_data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = "dark") -> str:
    tipo = slide_data.get("tipo", "corpo")
    fn   = SLIDE_BUILDERS.get(tipo, slide_corpo)
    return fn(slide_data, imagem_url=imagem_url, avatar_url=avatar_url, theme=theme)


def build_all_slides(carrossel: dict, avatar_url: str | None = None, theme: str = "dark") -> list[str]:
    imagem_url  = carrossel.get("imagem_url")
    slices      = carrossel.get("imagem_slices")
    slides_data = carrossel.get("slides", [])
    result = []
    for i, s in enumerate(slides_data):
        # Usa fatia panorâmica se disponível, senão imagem única
        img = slices[i] if slices and i < len(slices) else imagem_url
        result.append(build_slide(s, imagem_url=img, avatar_url=avatar_url, theme=theme))
    return result
