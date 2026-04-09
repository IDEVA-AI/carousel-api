"""
visuals.py — Sistema de elementos visuais SVG para slides
Camada decorativa independente do conteúdo. Cada função retorna HTML/SVG
posicionado absolutamente, pronto pra sobrepor ao slide.

Arquitetura pensada pra evoluir:
  - SVG inline (hoje) → animações CSS/SMIL → vídeo (futuro)
  - Cada visual é uma função pura: recebe dados, retorna HTML
  - Composição: múltiplos visuais podem ser empilhados no mesmo slide
"""


# ─── PALETA VISUAL ───────────────────────────────────────────────────────────
# Reutiliza as cores do design system mas em formato direto pra SVG

COLORS = {
    "dark": {
        "stroke": "rgba(184,135,58,0.18)",
        "stroke_accent": "rgba(184,135,58,0.40)",
        "fill": "rgba(184,135,58,0.06)",
        "fill_accent": "rgba(184,135,58,0.12)",
        "dot": "rgba(244,240,232,0.08)",
        "dot_accent": "rgba(184,135,58,0.55)",
        "text": "rgba(244,240,232,0.12)",
    },
    "light": {
        "stroke": "rgba(122,78,24,0.12)",
        "stroke_accent": "rgba(122,78,24,0.30)",
        "fill": "rgba(122,78,24,0.04)",
        "fill_accent": "rgba(122,78,24,0.08)",
        "dot": "rgba(14,12,10,0.06)",
        "dot_accent": "rgba(122,78,24,0.45)",
        "text": "rgba(14,12,10,0.08)",
    },
    "ferrugem": {
        "stroke": "rgba(200,104,58,0.15)",
        "stroke_accent": "rgba(200,104,58,0.35)",
        "fill": "rgba(200,104,58,0.05)",
        "fill_accent": "rgba(200,104,58,0.10)",
        "dot": "rgba(245,232,213,0.06)",
        "dot_accent": "rgba(200,104,58,0.50)",
        "text": "rgba(245,232,213,0.10)",
    },
}

def _c(theme: str) -> dict:
    return COLORS.get(theme, COLORS["dark"])


# ─── LINHAS DE CONSTRUÇÃO ────────────────────────────────────────────────────
# Grid editorial com linhas douradas sutis — sensação de "design de estúdio"

def construction_lines(theme: str = "dark") -> str:
    """Grid de construção com proporção áurea. Para covers e CTAs."""
    c = _c(theme)
    golden = 0.618
    h1 = int(1440 * golden)  # ~890px
    h2 = int(1440 * (1 - golden))  # ~550px
    v1 = int(1080 * golden)  # ~668px

    return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <!-- Proporção áurea horizontal -->
  <line x1="0" y1="{h2}" x2="1080" y2="{h2}" stroke="{c['stroke']}" stroke-width="1"/>
  <line x1="0" y1="{h1}" x2="1080" y2="{h1}" stroke="{c['stroke']}" stroke-width="1" stroke-dasharray="8,16"/>

  <!-- Proporção áurea vertical -->
  <line x1="{v1}" y1="0" x2="{v1}" y2="1440" stroke="{c['stroke']}" stroke-width="1" stroke-dasharray="4,12"/>

  <!-- Marcadores nos cruzamentos -->
  <circle cx="{v1}" cy="{h2}" r="6" fill="none" stroke="{c['stroke_accent']}" stroke-width="1.5"/>
  <circle cx="{v1}" cy="{h2}" r="2" fill="{c['dot_accent']}"/>

  <!-- Marcas de canto — sensação de "crop marks" -->
  <g stroke="{c['stroke_accent']}" stroke-width="1.5">
    <line x1="60" y1="60" x2="60" y2="100"/>
    <line x1="60" y1="60" x2="100" y2="60"/>
    <line x1="1020" y1="60" x2="1020" y2="100"/>
    <line x1="1020" y1="60" x2="980" y2="60"/>
    <line x1="60" y1="1380" x2="60" y2="1340"/>
    <line x1="60" y1="1380" x2="100" y2="1380"/>
    <line x1="1020" y1="1380" x2="1020" y2="1340"/>
    <line x1="1020" y1="1380" x2="980" y2="1380"/>
  </g>
</svg>"""


# ─── CROSSHAIR / FOCO ───────────────────────────────────────────────────────
# Elemento de foco visual — "mira" sobre o ponto central do conteúdo

def crosshair(cx: int = 540, cy: int = 600, size: int = 120, theme: str = "dark") -> str:
    """Crosshair decorativo. Posição customizável."""
    c = _c(theme)
    hs = size // 2
    gap = 16

    return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <!-- Linhas do crosshair com gap central -->
  <line x1="{cx - hs}" y1="{cy}" x2="{cx - gap}" y2="{cy}" stroke="{c['stroke_accent']}" stroke-width="1"/>
  <line x1="{cx + gap}" y1="{cy}" x2="{cx + hs}" y2="{cy}" stroke="{c['stroke_accent']}" stroke-width="1"/>
  <line x1="{cx}" y1="{cy - hs}" x2="{cx}" y2="{cy - gap}" stroke="{c['stroke_accent']}" stroke-width="1"/>
  <line x1="{cx}" y1="{cy + gap}" x2="{cx}" y2="{cy + hs}" stroke="{c['stroke_accent']}" stroke-width="1"/>

  <!-- Círculo central -->
  <circle cx="{cx}" cy="{cy}" r="{gap}" fill="none" stroke="{c['stroke_accent']}" stroke-width="1" opacity="0.6"/>
  <circle cx="{cx}" cy="{cy}" r="3" fill="{c['dot_accent']}"/>
</svg>"""


# ─── ACCENT STROKES ──────────────────────────────────────────────────────────
# Linhas dinâmicas que criam movimento e direção visual

def accent_strokes(variant: str = "diagonal", theme: str = "dark") -> str:
    """Linhas de acento. Variantes: diagonal, horizontal, radial."""
    c = _c(theme)

    if variant == "diagonal":
        return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <!-- Diagonais paralelas — movimento descendente -->
  <line x1="780" y1="0" x2="1080" y2="400" stroke="{c['stroke']}" stroke-width="1"/>
  <line x1="830" y1="0" x2="1080" y2="330" stroke="{c['stroke']}" stroke-width="0.5" opacity="0.6"/>
  <line x1="880" y1="0" x2="1080" y2="260" stroke="{c['stroke']}" stroke-width="0.5" opacity="0.3"/>

  <!-- Acento forte inferior -->
  <line x1="0" y1="1100" x2="300" y2="1440" stroke="{c['stroke_accent']}" stroke-width="2"/>
  <line x1="40" y1="1100" x2="340" y2="1440" stroke="{c['stroke']}" stroke-width="0.5"/>
</svg>"""

    if variant == "horizontal":
        return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <!-- Linhas horizontais rítmicas -->
  <line x1="0" y1="340" x2="180" y2="340" stroke="{c['stroke_accent']}" stroke-width="2"/>
  <line x1="0" y1="360" x2="120" y2="360" stroke="{c['stroke']}" stroke-width="1"/>
  <line x1="900" y1="1100" x2="1080" y2="1100" stroke="{c['stroke_accent']}" stroke-width="2"/>
  <line x1="940" y1="1120" x2="1080" y2="1120" stroke="{c['stroke']}" stroke-width="1"/>
</svg>"""

    # radial
    return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <circle cx="540" cy="720" r="300" fill="none" stroke="{c['stroke']}" stroke-width="0.5"/>
  <circle cx="540" cy="720" r="500" fill="none" stroke="{c['stroke']}" stroke-width="0.5" stroke-dasharray="4,8"/>
  <circle cx="540" cy="720" r="200" fill="none" stroke="{c['stroke_accent']}" stroke-width="1" opacity="0.4"/>
</svg>"""


# ─── SHAPE GEOMÉTRICO ────────────────────────────────────────────────────────
# Formas abstratas que reforçam emoção sem explicar

def geometric_shape(variant: str = "triangle", theme: str = "dark") -> str:
    """Shapes geométricos decorativos. Variantes: triangle, diamond, arc."""
    c = _c(theme)

    if variant == "triangle":
        return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <!-- Triângulo grande, rotacionado — tensão visual -->
  <polygon points="820,180 980,520 660,520"
    fill="{c['fill']}" stroke="{c['stroke_accent']}" stroke-width="1.5"
    transform="rotate(15, 820, 350)"/>
  <!-- Eco menor -->
  <polygon points="840,240 920,440 760,440"
    fill="none" stroke="{c['stroke']}" stroke-width="0.5"
    transform="rotate(15, 840, 340)"/>
</svg>"""

    if variant == "diamond":
        return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <rect x="800" y="900" width="160" height="160"
    fill="{c['fill_accent']}" stroke="{c['stroke_accent']}" stroke-width="1.5"
    transform="rotate(45, 880, 980)"/>
  <rect x="820" y="920" width="120" height="120"
    fill="none" stroke="{c['stroke']}" stroke-width="0.5"
    transform="rotate(45, 880, 980)"/>
</svg>"""

    # arc
    return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <path d="M 900 200 A 400 400 0 0 1 900 1000"
    fill="none" stroke="{c['stroke_accent']}" stroke-width="2"/>
  <path d="M 920 280 A 340 340 0 0 1 920 940"
    fill="none" stroke="{c['stroke']}" stroke-width="0.5"/>
</svg>"""


# ─── BRACKETS / MARCADORES ───────────────────────────────────────────────────
# Colchetes e marcadores que "enquadram" o conteúdo

def brackets(y_start: int = 300, y_end: int = 900, theme: str = "dark") -> str:
    """Colchetes laterais que enquadram a zona de conteúdo."""
    c = _c(theme)
    bw = 20  # largura do bracket

    return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <!-- Bracket esquerdo -->
  <path d="M {68+bw} {y_start} L 68 {y_start} L 68 {y_end} L {68+bw} {y_end}"
    fill="none" stroke="{c['stroke_accent']}" stroke-width="1.5"/>

  <!-- Bracket direito -->
  <path d="M {1012-bw} {y_start} L 1012 {y_start} L 1012 {y_end} L {1012-bw} {y_end}"
    fill="none" stroke="{c['stroke_accent']}" stroke-width="1.5"/>

  <!-- Marcadores de medida -->
  <line x1="68" y1="{y_start - 20}" x2="68" y2="{y_start - 8}" stroke="{c['stroke']}" stroke-width="0.5"/>
  <line x1="1012" y1="{y_start - 20}" x2="1012" y2="{y_start - 8}" stroke="{c['stroke']}" stroke-width="0.5"/>
</svg>"""


# ─── NÚMERO EDITORIAL ────────────────────────────────────────────────────────
# Número gigante de fundo — reforça hierarquia e ritmo

def bg_number(number: str = "01", theme: str = "dark") -> str:
    """Número grande semi-transparente no fundo."""
    c = _c(theme)

    return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <text x="880" y="350" text-anchor="end"
    font-family="'Fraunces', serif" font-size="380" font-weight="900"
    fill="{c['text']}" letter-spacing="-0.05em">{number}</text>
</svg>"""


# ─── CONTINUIDADE ENTRE SLIDES ───────────────────────────────────────────────
# Elementos que "sangram" entre slides vizinhos.
# Borda direita do slide N conecta com borda esquerda do slide N+1.
# Cada função retorna (saída_direita, entrada_esquerda) — par de SVGs.

def continuity_circle(cy: int = 720, r: int = 200, theme: str = "dark") -> tuple[str, str]:
    """Círculo partido: metade direita no slide atual, metade esquerda no próximo."""
    c = _c(theme)

    right_half = f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <circle cx="1080" cy="{cy}" r="{r}" fill="none" stroke="{c['stroke_accent']}" stroke-width="1.5"/>
  <circle cx="1080" cy="{cy}" r="{r - 40}" fill="none" stroke="{c['stroke']}" stroke-width="0.5" stroke-dasharray="6,10"/>
  <circle cx="1080" cy="{cy}" r="4" fill="{c['dot_accent']}"/>
</svg>"""

    left_half = f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <circle cx="0" cy="{cy}" r="{r}" fill="none" stroke="{c['stroke_accent']}" stroke-width="1.5"/>
  <circle cx="0" cy="{cy}" r="{r - 40}" fill="none" stroke="{c['stroke']}" stroke-width="0.5" stroke-dasharray="6,10"/>
  <circle cx="0" cy="{cy}" r="4" fill="{c['dot_accent']}"/>
</svg>"""

    return right_half, left_half


def continuity_line(y1: int = 400, y2: int = 1000, theme: str = "dark") -> tuple[str, str]:
    """Linha diagonal que sai do slide atual e entra no próximo."""
    c = _c(theme)

    right_exit = f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <line x1="700" y1="{y1}" x2="1080" y2="{y2}" stroke="{c['stroke_accent']}" stroke-width="1.5"/>
  <line x1="720" y1="{y1}" x2="1080" y2="{y2 - 20}" stroke="{c['stroke']}" stroke-width="0.5"/>
</svg>"""

    left_enter = f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <line x1="0" y1="{y2}" x2="380" y2="{y1 + 200}" stroke="{c['stroke_accent']}" stroke-width="1.5"/>
  <line x1="0" y1="{y2 - 20}" x2="360" y2="{y1 + 200}" stroke="{c['stroke']}" stroke-width="0.5"/>
</svg>"""

    return right_exit, left_enter


def continuity_arc(cy: int = 800, r: int = 350, theme: str = "dark") -> tuple[str, str]:
    """Arco grande que sangra entre slides."""
    c = _c(theme)

    right_exit = f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <path d="M 1080 {cy - r} A {r} {r} 0 0 0 1080 {cy + r}"
    fill="none" stroke="{c['stroke_accent']}" stroke-width="2" transform="translate(-80,0)"/>
  <path d="M 1080 {cy - r + 30} A {r - 30} {r - 30} 0 0 0 1080 {cy + r - 30}"
    fill="none" stroke="{c['stroke']}" stroke-width="0.5" stroke-dasharray="4,8" transform="translate(-80,0)"/>
</svg>"""

    left_enter = f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <path d="M 0 {cy - r} A {r} {r} 0 0 1 0 {cy + r}"
    fill="none" stroke="{c['stroke_accent']}" stroke-width="2" transform="translate(80,0)"/>
  <path d="M 0 {cy - r + 30} A {r - 30} {r - 30} 0 0 1 0 {cy + r - 30}"
    fill="none" stroke="{c['stroke']}" stroke-width="0.5" stroke-dasharray="4,8" transform="translate(80,0)"/>
</svg>"""

    return right_exit, left_enter


def continuity_bracket(y_start: int = 300, y_end: int = 1100, theme: str = "dark") -> tuple[str, str]:
    """Bracket/colchete que abre num slide e fecha no próximo."""
    c = _c(theme)

    right_open = f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <path d="M 1040 {y_start} L 1060 {y_start} L 1060 {y_end} L 1040 {y_end}"
    fill="none" stroke="{c['stroke_accent']}" stroke-width="1.5"/>
  <line x1="1060" y1="{(y_start+y_end)//2}" x2="1080" y2="{(y_start+y_end)//2}"
    stroke="{c['stroke_accent']}" stroke-width="1"/>
</svg>"""

    left_close = f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <path d="M 40 {y_start} L 20 {y_start} L 20 {y_end} L 40 {y_end}"
    fill="none" stroke="{c['stroke_accent']}" stroke-width="1.5"/>
  <line x1="0" y1="{(y_start+y_end)//2}" x2="20" y2="{(y_start+y_end)//2}"
    stroke="{c['stroke_accent']}" stroke-width="1"/>
</svg>"""

    return right_open, left_close


# Sequência de continuidades — alterna entre tipos pra cada transição
CONTINUITY_SEQUENCE = [
    lambda t: continuity_line(350, 950, t),
    lambda t: continuity_circle(650, 220, t),
    lambda t: continuity_arc(750, 300, t),
    lambda t: continuity_bracket(280, 1050, t),
    lambda t: continuity_line(500, 1100, t),
    lambda t: continuity_circle(500, 180, t),
    lambda t: continuity_arc(600, 250, t),
]


# ─── COMPOSIÇÕES (combinações prontas) ───────────────────────────────────────

def cover_visuals(theme: str = "dark") -> str:
    """Composição visual para cover: construction lines + crop marks + diagonais."""
    return (
        construction_lines(theme)
        + accent_strokes("diagonal", theme)
    )


def hook_visuals(index: int = 2, theme: str = "dark") -> str:
    """Composição visual para hook: número editorial + brackets."""
    return (
        bg_number(f"{index:02d}", theme)
        + accent_strokes("horizontal", theme)
    )


def corpo_visuals(index: int = 3, theme: str = "dark") -> str:
    """Composição visual para corpo: número + shape geométrico."""
    shapes = ["triangle", "diamond", "arc"]
    shape = shapes[(index - 1) % len(shapes)]
    return (
        bg_number(f"{index:02d}", theme)
        + geometric_shape(shape, theme)
    )


def dado_visuals(theme: str = "dark") -> str:
    """Composição visual para dado: radial + crosshair."""
    return (
        accent_strokes("radial", theme)
        + crosshair(540, 500, 160, theme)
    )


def cta_visuals(theme: str = "dark") -> str:
    """Composição visual para CTA: construction lines + arco."""
    return (
        construction_lines(theme)
        + geometric_shape("arc", theme)
    )


# ─── CSS para a camada visual ────────────────────────────────────────────────

VISUALS_CSS = """
.vis {
  position: absolute;
  inset: 0;
  width: 1080px;
  height: 1440px;
  z-index: 1;
  pointer-events: none;
}
"""
