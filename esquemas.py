"""
esquemas.py — Diagramas SVG gerados a partir do conteúdo dos slides
Cada função recebe os dados do slide e retorna SVG inline posicionado
como overlay (z-index 1, atrás do texto).

Objetivo: criar percepção de valor visual — "conteúdo de outro nível".
Não é pra explicar, é pra impressionar.
"""
import re
import math
from visuals import COLORS

def _c(theme: str) -> dict:
    return COLORS.get(theme, COLORS["dark"])


# ─── COVER: REDE ABSTRATA ────────────────────────────────────────────────────
# Nós conectados — "mapa de sistema". Posições determinísticas via seed.

def esquema_cover(data: dict, theme: str = "dark") -> str:
    c = _c(theme)
    headline = data.get("headline", "")
    seed = len(headline) % 7 + 3

    # Gerar nós em posições semi-fixas mas variáveis
    nodes = [
        (180, 280), (820, 200), (650, 480),
        (280, 680), (900, 720), (160, 1000),
        (780, 950), (500, 1150),
    ][:seed]

    # Conexões entre nós próximos
    lines = ""
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes):
            if j <= i:
                continue
            dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            if dist < 500:
                lines += f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c["stroke"]}" stroke-width="0.5"/>\n'

    dots = ""
    for i, (x, y) in enumerate(nodes):
        r = 6 if i % 3 == 0 else 4
        fill = c["dot_accent"] if i == 0 else c["dot"]
        dots += f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>\n'
        if i % 2 == 0:
            dots += f'  <circle cx="{x}" cy="{y}" r="{r + 12}" fill="none" stroke="{c["stroke"]}" stroke-width="0.5"/>\n'

    return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
{lines}{dots}</svg>"""


# ─── HOOK: FUNIL ─────────────────────────────────────────────────────────────
# Linhas convergentes — tensão estreitando pro insight.

def esquema_hook(data: dict, theme: str = "dark") -> str:
    c = _c(theme)

    return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <!-- Funil: linhas convergindo -->
  <line x1="760" y1="320" x2="1000" y2="320" stroke="{c['stroke_accent']}" stroke-width="1.5"/>
  <line x1="790" y1="480" x2="1000" y2="480" stroke="{c['stroke_accent']}" stroke-width="1.5"/>
  <line x1="830" y1="640" x2="1000" y2="640" stroke="{c['stroke_accent']}" stroke-width="1"/>

  <!-- Bordas do funil -->
  <line x1="760" y1="320" x2="830" y2="640" stroke="{c['stroke']}" stroke-width="0.5"/>
  <line x1="1000" y1="320" x2="1000" y2="640" stroke="{c['stroke']}" stroke-width="0.5"/>

  <!-- Ponto de convergência -->
  <line x1="830" y1="640" x2="920" y2="780" stroke="{c['stroke_accent']}" stroke-width="1" stroke-dasharray="6,8"/>
  <line x1="1000" y1="640" x2="920" y2="780" stroke="{c['stroke_accent']}" stroke-width="1" stroke-dasharray="6,8"/>
  <circle cx="920" cy="780" r="8" fill="{c['fill_accent']}" stroke="{c['stroke_accent']}" stroke-width="1.5"/>
  <circle cx="920" cy="780" r="3" fill="{c['dot_accent']}"/>

  <!-- Label markers -->
  <circle cx="750" cy="320" r="3" fill="{c['dot_accent']}"/>
  <circle cx="780" cy="480" r="3" fill="{c['dot_accent']}"/>
  <circle cx="820" cy="640" r="3" fill="{c['dot_accent']}"/>
</svg>"""


# ─── CORPO: FRAMEWORK BOX ───────────────────────────────────────────────────
# Retângulo estruturado com divisões internas — "pensamento organizado".

def esquema_corpo(data: dict, theme: str = "dark") -> str:
    c = _c(theme)
    body = data.get("body", "")
    sections = max(2, min(4, body.count("\n") + 1))

    box_x, box_y = 720, 280
    box_w, box_h = 300, 400
    section_h = box_h // sections

    dividers = ""
    connectors = ""
    for i in range(1, sections):
        y = box_y + i * section_h
        dividers += f'  <line x1="{box_x}" y1="{y}" x2="{box_x + box_w}" y2="{y}" stroke="{c["stroke"]}" stroke-width="0.5"/>\n'
        # Conector esquerdo
        connectors += f'  <circle cx="{box_x}" cy="{y}" r="4" fill="{c["fill_accent"]}" stroke="{c["stroke_accent"]}" stroke-width="1"/>\n'

    # Números de seção
    nums = ""
    for i in range(sections):
        y = box_y + i * section_h + section_h // 2 + 6
        nums += f'  <text x="{box_x + 24}" y="{y}" font-family="\'DM Mono\', monospace" font-size="18" fill="{c["stroke_accent"]}" letter-spacing="0.1em">{i+1:02d}</text>\n'

    return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <!-- Framework box -->
  <rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" rx="4"
    fill="{c['fill']}" stroke="{c['stroke_accent']}" stroke-width="1"/>
{dividers}{connectors}{nums}
  <!-- Conector de entrada -->
  <line x1="{box_x - 40}" y1="{box_y + box_h // 2}" x2="{box_x}" y2="{box_y + box_h // 2}"
    stroke="{c['stroke_accent']}" stroke-width="1" stroke-dasharray="4,6"/>
  <circle cx="{box_x - 40}" cy="{box_y + box_h // 2}" r="3" fill="{c['dot_accent']}"/>
</svg>"""


# ─── DADO: GAUGE / ARCO DE PROGRESSO ─────────────────────────────────────────
# Arco circular mostrando a proporção. Atrás do número principal.

def _parse_numero(numero: str) -> float | None:
    """Extrai valor numérico 0-100 de strings como '74%', '3x', '87%'."""
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*%', numero)
    if m:
        return min(100, float(m.group(1).replace(',', '.')))
    m = re.search(r'(\d+(?:[.,]\d+)?)', numero)
    if m:
        val = float(m.group(1).replace(',', '.'))
        if val <= 100:
            return val
    return None


def esquema_dado(data: dict, theme: str = "dark") -> str:
    c = _c(theme)
    numero = data.get("numero", "")
    pct = _parse_numero(numero)

    cx, cy, r = 540, 480, 240

    if pct is not None:
        # Arco de progresso (270° = 100%)
        angle = (pct / 100) * 270
        start_angle = 135  # começa embaixo-esquerda
        end_angle = start_angle + angle

        def polar(a, radius):
            rad = math.radians(a)
            return cx + radius * math.cos(rad), cy + radius * math.sin(rad)

        sx, sy = polar(start_angle, r)
        ex, ey = polar(end_angle, r)
        large = 1 if angle > 180 else 0

        # Trilha de fundo (arco completo 270°)
        bsx, bsy = polar(start_angle, r)
        bex, bey = polar(start_angle + 270, r)

        return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <!-- Trilha de fundo -->
  <path d="M {bsx:.0f} {bsy:.0f} A {r} {r} 0 1 1 {bex:.0f} {bey:.0f}"
    fill="none" stroke="{c['stroke']}" stroke-width="3" stroke-linecap="round"/>
  <!-- Arco preenchido -->
  <path d="M {sx:.0f} {sy:.0f} A {r} {r} 0 {large} 1 {ex:.0f} {ey:.0f}"
    fill="none" stroke="{c['stroke_accent']}" stroke-width="5" stroke-linecap="round"/>
  <!-- Ponto final -->
  <circle cx="{ex:.0f}" cy="{ey:.0f}" r="6" fill="{c['dot_accent']}"/>
  <!-- Tick marks -->
  <circle cx="{bsx:.0f}" cy="{bsy:.0f}" r="3" fill="{c['dot']}"/>
</svg>"""
    else:
        # Sem percentual: círculos concêntricos
        return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{c['stroke']}" stroke-width="1"/>
  <circle cx="{cx}" cy="{cy}" r="{r - 50}" fill="none" stroke="{c['stroke']}" stroke-width="0.5" stroke-dasharray="6,10"/>
  <circle cx="{cx}" cy="{cy}" r="{r - 100}" fill="none" stroke="{c['stroke_accent']}" stroke-width="1.5"/>
  <circle cx="{cx}" cy="{cy}" r="4" fill="{c['dot_accent']}"/>
</svg>"""


# ─── VERSUS: COMPARAÇÃO VISUAL ──────────────────────────────────────────────
# Dois retângulos — vazio (errado) vs preenchido (certo). Peso visual diferente.

def esquema_versus(data: dict, theme: str = "dark") -> str:
    c = _c(theme)

    return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <!-- Bloco "errado" — vazio, riscado -->
  <rect x="740" y="220" width="240" height="160" rx="4"
    fill="none" stroke="{c['stroke']}" stroke-width="1"/>
  <line x1="740" y1="220" x2="980" y2="380"
    stroke="{c['stroke']}" stroke-width="0.5" opacity="0.5"/>

  <!-- Bloco "certo" — preenchido, destaque -->
  <rect x="740" y="440" width="240" height="160" rx="4"
    fill="{c['fill_accent']}" stroke="{c['stroke_accent']}" stroke-width="2"/>

  <!-- Conector -->
  <line x1="860" y1="380" x2="860" y2="440"
    stroke="{c['stroke_accent']}" stroke-width="1" stroke-dasharray="4,6"/>

  <!-- Ícone X no errado -->
  <line x1="845" y1="285" x2="875" y2="315" stroke="{c['stroke']}" stroke-width="1.5"/>
  <line x1="875" y1="285" x2="845" y2="315" stroke="{c['stroke']}" stroke-width="1.5"/>

  <!-- Ícone check no certo -->
  <polyline points="845,520 858,533 878,505" fill="none" stroke="{c['stroke_accent']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""


# ─── DIAGNOSTICO: FLOWCHART VERTICAL ─────────────────────────────────────────
# Nós numerados fluindo pra baixo → diamante de conclusão.

def esquema_diagnostico(data: dict, theme: str = "dark") -> str:
    c = _c(theme)
    itens = data.get("itens", [])[:3]
    n = max(1, len(itens))

    cx = 880
    start_y = 260
    node_h = 70
    gap = 50
    node_w = 200

    nodes = ""
    arrows = ""
    for i in range(n):
        y = start_y + i * (node_h + gap)

        # Nó retangular arredondado
        nodes += f"""  <rect x="{cx - node_w//2}" y="{y}" width="{node_w}" height="{node_h}" rx="6"
    fill="{c['fill']}" stroke="{c['stroke_accent']}" stroke-width="1"/>
  <text x="{cx - node_w//2 + 16}" y="{y + node_h//2 + 6}" font-family="'DM Mono', monospace" font-size="20"
    fill="{c['stroke_accent']}" letter-spacing="0.08em">{i+1:02d}</text>\n"""

        # Seta pra próximo nó
        if i < n - 1:
            ay = y + node_h
            arrows += f"""  <line x1="{cx}" y1="{ay}" x2="{cx}" y2="{ay + gap}" stroke="{c['stroke_accent']}" stroke-width="1"/>
  <polygon points="{cx-5},{ay + gap - 8} {cx+5},{ay + gap - 8} {cx},{ay + gap}" fill="{c['stroke_accent']}"/>\n"""

    # Diamante de conclusão
    dy = start_y + n * (node_h + gap)
    ds = 40  # half-size
    nodes += f"""  <polygon points="{cx},{dy} {cx+ds},{dy+ds} {cx},{dy+2*ds} {cx-ds},{dy+ds}"
    fill="{c['fill_accent']}" stroke="{c['stroke_accent']}" stroke-width="1.5"/>
  <circle cx="{cx}" cy="{dy+ds}" r="4" fill="{c['dot_accent']}"/>\n"""

    # Seta pro diamante
    ay = start_y + (n - 1) * (node_h + gap) + node_h
    arrows += f"""  <line x1="{cx}" y1="{ay}" x2="{cx}" y2="{dy}" stroke="{c['stroke_accent']}" stroke-width="1"/>
  <polygon points="{cx-5},{dy-8} {cx+5},{dy-8} {cx},{dy}" fill="{c['stroke_accent']}"/>\n"""

    return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
{nodes}{arrows}</svg>"""


# ─── CTA: SETA CURVA ─────────────────────────────────────────────────────────
# Caminho curvo apontando pra frente — "avance, tome ação".

def esquema_cta(data: dict, theme: str = "dark") -> str:
    c = _c(theme)

    return f"""<svg class="vis" viewBox="0 0 1080 1440" xmlns="http://www.w3.org/2000/svg">
  <!-- Caminho curvo -->
  <path d="M 200 1050 Q 540 900 880 1050"
    fill="none" stroke="{c['stroke_accent']}" stroke-width="2" stroke-linecap="round"/>
  <path d="M 220 1070 Q 540 930 860 1070"
    fill="none" stroke="{c['stroke']}" stroke-width="0.5"/>

  <!-- Ponta da seta -->
  <polygon points="880,1050 860,1035 860,1065" fill="{c['stroke_accent']}"/>

  <!-- Dots decorativos no caminho -->
  <circle cx="350" cy="990" r="3" fill="{c['dot_accent']}"/>
  <circle cx="540" cy="960" r="4" fill="{c['dot_accent']}"/>
  <circle cx="730" cy="990" r="3" fill="{c['dot_accent']}"/>
</svg>"""
