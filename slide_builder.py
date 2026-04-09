"""
slide_builder.py — Converte dados de slide em HTML renderizável (1080x1440px)
Redesign v2: breathing room generoso, hierarquia clara, ritmo tipográfico consistente.
"""

# ─── CSS BASE ─────────────────────────────────────────────────────────────────

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,400&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --ink:        #0e0c0a;
  --paper:      #f4f0e8;
  --gold:       #b8873a;
  --gold-light: #e8d5b0;
  --dark2:      #1a1714;
  --dark3:      #2a2520;
  --muted:      rgba(244,240,232,0.5);
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

/* ── PADDING INTERNO — generoso e consistente ── */
.si {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 88px 100px 80px;
  position: relative;
  z-index: 2;
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
    rgba(14,12,10,0.94) 0%,
    rgba(14,12,10,0.80) 45%,
    rgba(14,12,10,0.90) 100%);
}

.bg-grid {
  background-image:
    linear-gradient(rgba(184,135,58,0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(184,135,58,0.035) 1px, transparent 1px);
  background-size: 80px 80px;
}

/* ── ESPACADORES ── */
.sp   { flex: 1; }
.sp2  { flex: 2; }
.sp3  { flex: 3; }

/* ── EYEBROW ── */
.eyebrow {
  font-family: 'DM Mono', monospace;
  font-size: 18px;
  letter-spacing: 0.30em;
  text-transform: uppercase;
  color: rgba(184,135,58,0.65);
  line-height: 1.4;
}

/* ── SLIDE NUMBER ── */
.slide-num {
  font-family: 'DM Mono', monospace;
  font-size: 16px;
  letter-spacing: 0.20em;
  color: rgba(244,240,232,0.22);
}

/* ── TIPOGRAFIA ── */
/* cover usa tamanho proprio — comporta headlines de até 5 palavras */
.cover-h {
  font-family: 'Fraunces', serif;
  font-size: 108px;
  font-weight: 900;
  line-height: 0.90;
  letter-spacing: -0.040em;
  color: var(--paper);
}

h2 {
  font-family: 'Fraunces', serif;
  font-size: 112px;
  font-weight: 700;
  line-height: 0.91;
  letter-spacing: -0.038em;
  color: var(--paper);
}

h3 {
  font-family: 'Fraunces', serif;
  font-size: 84px;
  font-weight: 700;
  line-height: 1.02;
  letter-spacing: -0.028em;
  color: var(--paper);
}

.body-l {
  font-family: 'DM Sans', sans-serif;
  font-size: 46px;
  line-height: 1.52;
  color: rgba(244,240,232,0.78);
  font-weight: 300;
  letter-spacing: -0.01em;
}

.body-m {
  font-family: 'DM Sans', sans-serif;
  font-size: 40px;
  line-height: 1.55;
  color: rgba(244,240,232,0.75);
  font-weight: 300;
  letter-spacing: -0.01em;
}

.gold      { color: var(--gold); }
.gold-lt   { color: var(--gold-light); }
.italic    { font-style: italic; }
.w700      { font-weight: 700; }

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

/* ── SUBTÍTULO do cover ── */
.subtitle {
  font-family: 'Fraunces', serif;
  font-style: italic;
  font-size: 52px;
  font-weight: 300;
  color: var(--gold-light);
  line-height: 1.22;
  letter-spacing: -0.015em;
}

/* ── DESTAQUE inline ── */
.destaque-block {
  font-family: 'Fraunces', serif;
  font-style: italic;
  font-size: 50px;
  font-weight: 400;
  color: var(--gold-light);
  line-height: 1.25;
  letter-spacing: -0.015em;
  padding-left: 28px;
  border-left: 4px solid var(--gold);
}

/* ── ASSINATURA ── */
.sig {
  display: flex;
  align-items: center;
  gap: 22px;
}
.sig-avatar {
  width: 68px;
  height: 68px;
  border-radius: 50%;
  background: var(--gold);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Fraunces', serif;
  font-size: 28px;
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
  margin-top: 3px;
}

/* ── PROGRESS ── */
.progress {
  display: flex;
  gap: 8px;
  align-items: center;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(244,240,232,0.20);
  flex-shrink: 0;
}
.dot.active {
  background: var(--gold);
  width: 32px;
  border-radius: 5px;
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
  font-size: 240px;
  font-weight: 900;
  line-height: 0.82;
  letter-spacing: -0.06em;
  color: var(--gold);
}
.dado-label {
  font-family: 'DM Mono', monospace;
  font-size: 24px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(184,135,58,0.65);
  margin-top: 20px;
}

/* ── QUOTE ── */
.quote-mark {
  font-family: 'Fraunces', serif;
  font-size: 160px;
  font-weight: 900;
  color: rgba(184,135,58,0.10);
  line-height: 0.7;
  user-select: none;
  margin-bottom: -24px;
}
.quote-text {
  font-family: 'Fraunces', serif;
  font-style: italic;
  font-size: 68px;
  font-weight: 400;
  line-height: 1.22;
  letter-spacing: -0.02em;
  color: var(--paper);
}
.quote-attr {
  font-family: 'DM Mono', monospace;
  font-size: 20px;
  color: var(--gold);
  letter-spacing: 0.10em;
  margin-top: 48px;
}

/* ── VERSUS ── */
.versus-wrap {
  display: flex;
  flex-direction: column;
  gap: 28px;
  width: 100%;
}
.versus-col {
  padding: 52px 56px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.versus-col.nao {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
}
.versus-col.sim {
  background: rgba(184,135,58,0.09);
  border: 2px solid rgba(184,135,58,0.40);
}
.versus-tag {
  font-family: 'DM Mono', monospace;
  font-size: 16px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
}
.versus-col.nao .versus-tag { color: rgba(244,240,232,0.30); }
.versus-col.sim .versus-tag { color: var(--gold); }
.versus-label {
  font-family: 'Fraunces', serif;
  font-size: 56px;
  font-weight: 700;
  line-height: 1.10;
  letter-spacing: -0.02em;
}
.versus-col.nao .versus-label {
  color: rgba(244,240,232,0.38);
  text-decoration: line-through;
  text-decoration-thickness: 3px;
  text-decoration-color: rgba(255,255,255,0.22);
}
.versus-col.sim .versus-label { color: var(--paper); }

/* ── DIAGNÓSTICO ── */
.diag-list { display: flex; flex-direction: column; }
.diag-item {
  display: flex;
  align-items: flex-start;
  gap: 32px;
  padding: 44px 0;
  border-bottom: 1px solid rgba(244,240,232,0.07);
}
.diag-item:first-child { padding-top: 32px; }
.diag-item:last-child  { border-bottom: none; }
.diag-num {
  font-family: 'DM Mono', monospace;
  font-size: 18px;
  color: var(--gold);
  letter-spacing: 0.12em;
  flex-shrink: 0;
  padding-top: 6px;
  min-width: 36px;
}
.diag-text {
  font-family: 'DM Sans', sans-serif;
  font-size: 42px;
  font-weight: 300;
  line-height: 1.40;
  color: rgba(244,240,232,0.85);
  letter-spacing: -0.01em;
}
.diag-conclusao {
  font-family: 'Fraunces', serif;
  font-style: italic;
  font-size: 46px;
  font-weight: 700;
  color: var(--gold-light);
  line-height: 1.22;
  letter-spacing: -0.015em;
  padding-top: 36px;
  border-top: 2px solid rgba(184,135,58,0.4);
}

/* ── CTA ── */
.cta-divider {
  width: 100%;
  height: 1px;
  background: rgba(184,135,58,0.22);
}
.cta-label {
  font-family: 'DM Mono', monospace;
  font-size: 17px;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: rgba(184,135,58,0.55);
}

/* ── CONTINUIDADE — direção visual para o próximo slide ── */
.right-bar {
  position: absolute;
  right: 0;
  top: 80px;
  bottom: 80px;
  width: 4px;
  background: linear-gradient(
    to bottom,
    transparent 0%,
    rgba(184,135,58,0.55) 18%,
    rgba(184,135,58,0.55) 82%,
    transparent 100%
  );
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
    '--gold-dark:#5a3812;--warm-gray:#5a5248;'
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
    '.dot{background:rgba(14,12,10,.15);}'
    '.dot.active{background:var(--gold);}'
    '.sig-handle{color:var(--gold);}'
    '.cta-divider{background:rgba(122,78,24,.22);}'
    '.destaque-block{border-left-color:var(--gold);color:var(--gold-light);}'
    '.cover-h{color:var(--paper);}'
    'h2{color:var(--paper);}h3{color:var(--paper);}'
    '.quote-text{color:var(--paper);}'
    '.versus-label{color:var(--paper);}'
    '.subtitle{color:var(--gold-light);}'
)

FERRUGEM = (
    ':root{'
    '--ink:#1a0a04;--paper:#f5e8d5;--gold:#c8683a;--gold-light:#e0a070;'
    '--dark2:#280e06;--dark3:#3e1c0c;--blood:#5c2210;'
    '--gold-dark:#a0501e;--warm-gray:#8a6050;'
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
    '.dot{background:rgba(245,232,213,.18);}'
    '.dot.active{background:var(--gold);}'
    '.sig-handle{color:var(--gold);}'
    '.cta-divider{background:rgba(200,104,58,.22);}'
    '.destaque-block{border-left-color:var(--gold);color:var(--gold-light);}'
)

THEME_CSS = {
    'dark':     '',
    'light':    LIGHT,
    'ferrugem': FERRUGEM,
}


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _html(body: str, theme: str = 'dark') -> str:
    theme_override = THEME_CSS.get(theme, '')
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>{BASE_CSS}{theme_override}</style>
</head>
<body>{body}</body>
</html>"""


def _dark_bg(imagem_url: str | None, theme: str = 'dark') -> str:
    """Fundo do slide — imagem ou fallback gradient temático."""
    if imagem_url:
        return f'<div class="bg-img" style="background-image:url(\'{imagem_url}\')"></div>'
    if theme == 'light':
        return '<div style="position:absolute;inset:0;z-index:0;background:linear-gradient(160deg,#ece8de 0%,#e4e0d5 60%,#dad6cc 100%);"><div style="position:absolute;inset:0;background-image:linear-gradient(rgba(122,78,24,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(122,78,24,.03) 1px,transparent 1px);background-size:60px 60px;"></div></div>'
    if theme == 'ferrugem':
        return '<div style="position:absolute;inset:0;z-index:0;background:var(--blood);"><div style="position:absolute;inset:0;background:radial-gradient(ellipse at 80% 20%,rgba(200,104,58,.20) 0%,transparent 50%),linear-gradient(160deg,#3d1208 0%,#2a0a04 50%,#1a0804 100%);"></div><div style="position:absolute;inset:0;background-image:linear-gradient(rgba(200,104,58,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(200,104,58,.05) 1px,transparent 1px);background-size:60px 60px;"></div></div>'
    return '<div style="position:absolute;inset:0;z-index:0;background:var(--blood);"><div style="position:absolute;inset:0;background:radial-gradient(ellipse at 80% 20%,rgba(184,135,58,.12) 0%,transparent 50%),radial-gradient(ellipse at 20% 80%,rgba(107,45,31,.4) 0%,transparent 50%),linear-gradient(160deg,#2a0a0a 0%,#1a0808 40%,#0e0c0a 100%);"></div><div style="position:absolute;inset:0;background-image:linear-gradient(rgba(184,135,58,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(184,135,58,.04) 1px,transparent 1px);background-size:60px 60px;"></div></div>'


def _right_bar() -> str:
    return '<div class="right-bar"></div>'


def _swipe_cue() -> str:
    return (
        '<div class="swipe-cue">'
        '<div class="swipe-cue-label">pr&#xF3;ximo</div>'
        '<div class="swipe-cue-arrow">&#x2192;</div>'
        '</div>'
    )


def _dots(index: int, total: int, is_last: bool = False) -> str:
    dots = "".join(
        f'<div class="dot{"  active" if i == index else ""}"></div>'
        for i in range(1, total + 1)
    )
    pct = int(index / total * 100)
    continuidade = "" if is_last else f"{_right_bar()}{_swipe_cue()}"
    return f"""<div class="progress">{dots}</div>
<div class="progress-line-wrap">
  <div class="progress-line-fill" style="width:{pct}%"></div>
</div>{continuidade}"""


def _sig(avatar_url: str | None = None) -> str:
    inner = f'<img src="{avatar_url}" alt="">' if avatar_url else "J"
    return f"""<div class="sig">
  <div class="sig-avatar">{inner}</div>
  <div>
    <div class="sig-name">Julio Carvalho</div>
    <div class="sig-handle">@j.karv</div>
  </div>
</div>"""


# ─── COVER ────────────────────────────────────────────────────────────────────
# Estrutura: eyebrow → [espaço] → h1 → reveal-bar → subtitle → [espaço menor] → sig → dots

def slide_cover(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = 'dark') -> str:
    headline = data.get("headline", "").replace("\n", "<br>")
    subtitle = data.get("subtitle", "")
    eyebrow  = data.get("eyebrow", "")
    index, total = data.get("index", 1), data.get("total", 7)

    bg = _dark_bg(imagem_url, theme)

    return _html(f"""<div class="s">
  <div class="top-bar"></div>
  {bg}
  <div class="si">
    <div class="eyebrow">{eyebrow}</div>
    <div style="height:64px;flex-shrink:0;"></div>
    <div class="cover-h">{headline}</div>
    <div style="margin-top:48px;">
      <div class="reveal-bar"></div>
      <div style="margin-top:32px;" class="subtitle">{subtitle}</div>
    </div>
    <div class="sp"></div>
    <div class="reveal-bar-full"></div>
    <div style="margin-top:40px;">{_sig(avatar_url)}</div>
    <div style="margin-top:32px;">{_dots(index, total)}</div>
  </div>
</div>""", theme=theme)


# ─── HOOK ─────────────────────────────────────────────────────────────────────
# Estrutura: [espaço] → h2 grande → [24px gap] → body → reveal-bar + destaque → [espaço] → dots

def slide_hook(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = 'dark') -> str:
    headline = data.get("headline", "").replace("\n", "<br>")
    body_txt = data.get("body", "").replace("\n", "<br>")
    destaque = data.get("destaque", "")
    index, total = data.get("index", 2), data.get("total", 7)

    destaque_html = f"""
    <div style="margin-top:48px;">
      <div class="reveal-bar"></div>
      <div style="margin-top:28px;" class="destaque-block">{destaque}</div>
    </div>""" if destaque else ""

    return _html(f"""<div class="s bg-grid">
  <div class="top-bar"></div>
  <div class="si">
    <div class="sp"></div>
    <h2>{headline}</h2>
    <div style="margin-top:40px;" class="body-l">{body_txt}</div>
    {destaque_html}
    <div class="sp"></div>
    {_dots(index, total)}
  </div>
</div>""", theme=theme)


# ─── CORPO ────────────────────────────────────────────────────────────────────
# Estrutura: slide-num → [espaço] → h3 → line → body → destaque (opcional) → [espaço] → dots

def slide_corpo(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = 'dark') -> str:
    headline = data.get("headline", "").replace("\n", "<br>")
    body_txt = data.get("body", "").replace("\n", "<br>")
    destaque = data.get("destaque", "")
    index, total = data.get("index", 3), data.get("total", 7)

    destaque_html = f'<div style="margin-top:44px;" class="destaque-block">{destaque}</div>' if destaque else ""

    return _html(f"""<div class="s">
  <div class="top-bar"></div>
  <div class="si">
    <div class="slide-num">{index:02d} — {total:02d}</div>
    <div class="sp" style="flex:0.6"></div>
    <h3>{headline}</h3>
    <div style="margin-top:36px;" class="reveal-bar-full"></div>
    <div style="margin-top:40px;" class="body-l">{body_txt}</div>
    {destaque_html}
    <div class="sp"></div>
    {_dots(index, total)}
  </div>
</div>""", theme=theme)


# ─── DADO ─────────────────────────────────────────────────────────────────────
# Estrutura: [espaço] → número enorme → label → divider → body → [espaço] → dots

def slide_dado(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = 'dark') -> str:
    numero   = data.get("numero", "—")
    label    = data.get("label", "")
    body_txt = data.get("body", "").replace("\n", "<br>")
    index, total = data.get("index", 4), data.get("total", 7)

    return _html(f"""<div class="s bg-grid">
  <div class="top-bar"></div>
  <div class="si">
    <div class="sp"></div>
    <div class="dado-numero">{numero}</div>
    <div class="dado-label">{label}</div>
    <div style="margin-top:52px;width:56px;height:3px;background:var(--gold)"></div>
    <div style="margin-top:36px;" class="body-l">{body_txt}</div>
    <div class="sp" style="flex:0.6"></div>
    {_dots(index, total)}
  </div>
</div>""", theme=theme)


# ─── QUOTE ────────────────────────────────────────────────────────────────────
# Estrutura: [espaço] → aspas decorativas → quote text → atribuição → [espaço] → dots

def slide_quote(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = 'dark') -> str:
    quote_txt = data.get("quote", "").replace("\n", "<br>")
    attr      = data.get("atribuicao", "Julio Carvalho")
    index, total = data.get("index", 5), data.get("total", 7)

    return _html(f"""<div class="s" style="background:var(--dark2);">
  <div class="top-bar"></div>
  <div class="si">
    <div class="sp" style="flex:0.5"></div>
    <div class="quote-mark">"</div>
    <div style="margin-top:8px;" class="quote-text">{quote_txt}</div>
    <div class="quote-attr">— {attr}</div>
    <div class="sp"></div>
    {_dots(index, total)}
  </div>
</div>""", theme=theme)


# ─── VERSUS ───────────────────────────────────────────────────────────────────
# Layout vertical (stacked) — mais respiro do que lado a lado

def slide_versus(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = 'dark') -> str:
    label_nao = data.get("label_nao", "").replace("\n", "<br>")
    label_sim = data.get("label_sim", "").replace("\n", "<br>")
    body_txt  = data.get("body", "").replace("\n", "<br>")
    index, total = data.get("index", 6), data.get("total", 7)

    body_html = f'<div style="margin-top:52px;" class="body-m">{body_txt}</div>' if body_txt else ""

    return _html(f"""<div class="s bg-grid">
  <div class="top-bar"></div>
  <div class="si">
    <div class="sp"></div>
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
    {_dots(index, total)}
  </div>
</div>""", theme=theme)


# ─── DIAGNÓSTICO ──────────────────────────────────────────────────────────────
# Estrutura: headline → itens numerados (max 3) → linha + conclusão → dots

def slide_diagnostico(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = 'dark') -> str:
    headline  = data.get("headline", "").replace("\n", "<br>")
    itens     = data.get("itens", [])[:3]          # máximo 3 para não afogar
    conclusao = data.get("conclusao", "").replace("\n", "<br>")
    index, total = data.get("index", 7), data.get("total", 7)

    # Reduz font se headline longo (>40 chars)
    h_style = 'style="font-size:64px;line-height:1.08;"' if len(headline) > 40 else ''

    itens_html = "".join(f"""
    <div class="diag-item">
      <div class="diag-num">{i+1:02d}</div>
      <div class="diag-text">{item}</div>
    </div>""" for i, item in enumerate(itens))

    return _html(f"""<div class="s">
  <div class="top-bar"></div>
  <div class="si">
    <h3 {h_style}>{headline}</h3>
    <div style="margin-top:12px;" class="reveal-bar-full"></div>
    <div class="diag-list">{itens_html}</div>
    <div style="margin-top:16px;" class="diag-conclusao">{conclusao}</div>
    <div class="sp"></div>
    {_dots(index, total)}
  </div>
</div>""", theme=theme)


# ─── CTA ──────────────────────────────────────────────────────────────────────
# Estrutura: [espaço] → label → reveal-bar → h2 → sub → [espaço] → divider → sig → dots

def slide_cta(data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = 'dark') -> str:
    headline = data.get("headline", "").replace("\n", "<br>")
    sub      = data.get("sub", "")
    index, total = data.get("index", 7), data.get("total", 7)

    bg = _dark_bg(imagem_url, theme)

    return _html(f"""<div class="s">
  <div class="top-bar"></div>
  {bg}
  <div class="si">
    <div class="sp"></div>
    <div class="cta-label">Próximo passo</div>
    <div style="margin-top:28px;" class="reveal-bar"></div>
    <div style="margin-top:44px;"><h2>{headline}</h2></div>
    <div style="margin-top:44px;" class="body-l gold-lt">{sub}</div>
    <div class="sp" style="flex:0.5"></div>
    <div class="cta-divider"></div>
    <div style="margin-top:40px;">{_sig(avatar_url)}</div>
    <div style="margin-top:36px;">{_dots(index, total, is_last=True)}</div>
  </div>
</div>""", theme=theme)


# ─── DISPATCHER ───────────────────────────────────────────────────────────────

SLIDE_BUILDERS = {
    "cover":       slide_cover,
    "hook":        slide_hook,
    "corpo":       slide_corpo,
    "dado":        slide_dado,
    "quote":       slide_quote,
    "versus":      slide_versus,
    "diagnostico": slide_diagnostico,
    "cta":         slide_cta,
}


def build_slide(slide_data: dict, imagem_url: str | None = None, avatar_url: str | None = None, theme: str = 'dark') -> str:
    tipo = slide_data.get("tipo", "corpo")
    fn   = SLIDE_BUILDERS.get(tipo, slide_corpo)
    return fn(slide_data, imagem_url=imagem_url, avatar_url=avatar_url, theme=theme)


def build_all_slides(carrossel: dict, avatar_url: str | None = None, theme: str = 'dark') -> list[str]:
    imagem_url  = carrossel.get("imagem_url")
    slides_data = carrossel.get("slides", [])
    return [build_slide(s, imagem_url=imagem_url, avatar_url=avatar_url, theme=theme) for s in slides_data]
