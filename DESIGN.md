# DESIGN.md — Sistema de Design · Carrossel Julio Carvalho

Documento de referência para o `slide_builder.py`. Toda decisão visual aqui tem uma razão.
Ao editar slides, este arquivo é a fonte da verdade de design.

---

## Princípios

1. **Estrutura antes de decoração.** Layout correto, tipografia certa, hierarquia clara — antes de qualquer elemento visual extra.
2. **Respiro é conteúdo.** Espaço em branco não é vazio; é o que faz o conteúdo respirar e a mensagem aterrissar.
3. **Hierarquia pelo tamanho.** O olho segue o tamanho. Nunca inverta: headline > subheadline > corpo.
4. **Alinhamento à esquerda por padrão.** Centro é reservado para cover, cta, quote e dado.
5. **Itálico tem função, não decoração.** Só em destaques emocionais, citações e subtítulos.
6. **Labels em caixa alta com tracking.** Eyebrows e rótulos: `text-transform: uppercase; letter-spacing: 0.22em`.
7. **Rodapé fixo e independente.** Assinatura e dots nunca competem com o conteúdo.
8. **Uma ideia por slide.** Se precisar de mais de um ponto, é outro slide.
9. **Nunca sobrescrever layouts existentes.** Novos formatos são criados ao lado, nunca substituem.

---

## Paleta (tema dark — default)

| Variável        | Hex       | Uso                                      |
|-----------------|-----------|------------------------------------------|
| `--ink`         | `#0e0c0a` | Fundo principal (quase preto)            |
| `--paper`       | `#f4f0e8` | Texto principal (off-white quente)       |
| `--gold`        | `#b8873a` | Acentos, labels, barra reveal            |
| `--gold-light`  | `#e8d5b0` | Destaques, subtítulos                    |
| `--dark2`       | `#1a1714` | Fundo alternativo (quote)                |
| `--dark3`       | `#2a2520` | Badges, labels de slide                  |
| `--blood`       | `#3d1010` | Fundo fallback cover/CTA                 |
| `--gold-dark`   | `#8a6228` | Variante gold para sombras               |
| `--warm-gray`   | `#7a7268` | Texto terciário                          |

---

## Temas

### Dark (default)
- Fundo: `--ink` (#0e0c0a)
- Texto: `--paper` (#f4f0e8)
- Acentos: `--gold` (#b8873a)
- Unsplash query suffix: `dark moody editorial`

### Light
- Fundo: `#f5f1e8` (creme quente)
- Texto: `#0e0c0a` (preto)
- Acentos: `#7a4e18` (marrom dourado)
- Unsplash query suffix: `minimal white bright clean`
- Overlay de imagem: 72-82% branco (imagem vira textura sutil)
- Grain: `mix-blend-mode: multiply` (sutil, não escurece)

### Ferrugem
- Fundo: `#1a0a04` (marrom escuro profundo)
- Texto: `#f5e8d5` (creme quente)
- Acentos: `#c8683a` (cobre/ferrugem)
- Unsplash query suffix: `warm rust texture industrial`
- Radial gradient quente no fundo

### Misto
- **Cover/CTA**: sempre dark com imagem Unsplash
- **Quote**: sempre light
- **Slides do meio**: alternam dark/light (índice ímpar=dark, par=light)
- Cria ritmo visual de pulsação editorial ao swipear
- Unsplash query: dark (cover/CTA são sempre escuros)

---

## Estética Cinematográfica

Três camadas visuais aplicadas a todos os slides via pseudo-elements do `.s`:

### Film Grain (`::before`)
```css
.s::before {
  opacity: 0.28;
  background-image: url("data:image/svg+xml,...feTurbulence...");
  background-size: 128px 128px;
  mix-blend-mode: overlay;
  z-index: 8;
}
```
Textura granulada sutil. No tema light usa `mix-blend-mode: multiply` com `opacity: 0.12`.

### Vignette (`::after`)
```css
.s::after {
  background: radial-gradient(
    ellipse at center,
    transparent 40%,
    rgba(14,12,10,0.35) 100%
  );
  z-index: 7;
}
```
Escurecimento natural nas bordas. No light: `rgba(245,241,232,0.30)`.

### Color Grading (`.bg-img`)
```css
.bg-img {
  filter: saturate(0.7) contrast(1.1) brightness(0.95);
}
.bg-img::before {
  background: linear-gradient(180deg,
    rgba(184,135,58,0.06) 0%,
    rgba(107,45,31,0.10) 100%);
  mix-blend-mode: color;
}
```
Dessaturação + tint quente nas sombras. No light: `brightness(1.3)`, `saturate(0.5)`.

---

## Tipografia

### Famílias

| Família    | Uso                                      |
|------------|------------------------------------------|
| Fraunces   | Headlines, destaques, quotes, subtítulos |
| DM Sans    | Corpo de texto                           |
| DM Mono    | Labels, eyebrows, numeração, atribuições |

Carregadas via `<link>` tag do Google Fonts no `<head>` de cada slide.

### Escala de tipos

| Token | Classe CSS     | Tamanho | Peso | Família   | Uso                            |
|-------|----------------|---------|------|-----------|--------------------------------|
| T1    | `.cover-h`     | 108px   | 900  | Fraunces  | Headline de cover              |
| T2    | `h2`           | 96px    | 700  | Fraunces  | Headline de hook / CTA         |
| T3    | `h3`           | 72px    | 700  | Fraunces  | Headline de corpo / diagnóstico|
| B1    | `.body-l`      | 44px    | 300  | DM Sans   | Corpo principal                |
| S1    | `.subtitle`    | 48px    | 300i | Fraunces  | Subtítulo do cover (itálico)   |
| D1    | `.destaque-block` | 48px | 400i | Fraunces  | Destaque com barra lateral     |
| L1    | `.label`       | 26px    | 500  | DM Mono   | Labels / eyebrows              |
| L2    | `.slide-num`   | 24px    | 400  | DM Mono   | Numeração de slides            |
| N1    | `.dado-numero` | 220px   | 900  | Fraunces  | Número gigante (slide dado)    |
| Q1    | `.quote-text`  | 64px    | 400i | Fraunces  | Citação (itálico)              |
| V1    | `.versus-label`| 56px    | 700  | Fraunces  | Labels do versus               |

**Regras:**
- Negrito só em headlines (700/900). Corpo sempre 300.
- Itálico só em: subtítulo do cover, destaque, quote, conclusão do diagnóstico.
- `max-width: 860px` em todos os blocos de texto pra evitar linhas muito longas.

---

## Espaçamento

Tokens CSS globais:

```css
--sp1: 16px   /* micro — gap entre elementos inline */
--sp2: 24px   /* pequeno — gap padrão */
--sp3: 40px   /* médio — separação entre blocos */
--sp4: 64px   /* grande — separação entre seções */
--sp5: 96px   /* padding lateral dos slides */
```

### Padding do slide

```css
padding: 88px var(--sp5) 200px;
/* top: 88px | lados: 96px | bottom: 200px (reserva para footer fixo) */
```

---

## Layout base

### Estrutura do slide

```
┌─────────────────────────────────┐
│  top-bar (6px, gold, z:10)      │
│                                 │
│  ::before (grain, z:8)          │  ← camadas
│  ::after  (vignette, z:7)       │     cinematográficas
│                                 │
│  bg-img / bg-grid (z:0)        │  ← fundo
│                                 │
│  .si (flex column, z:2)        │  ← conteúdo
│    spacer (flex proporcional)   │
│    conteúdo                     │
│    spacer (flex: 1)             │
│                                 │
│  .footer-fixed (absolute, z:5) │  ← fora do fluxo
│    assinatura (opcional)        │
│    dots de progresso            │
│  progress-line-wrap (z:10)      │
│  right-bar + swipe-cue          │
└─────────────────────────────────┘
```

### Z-index stack

| Z-index | Elemento        |
|---------|-----------------|
| 0       | bg-img / bg-grid|
| 1       | bg-img::before (color grading) |
| 2       | .si (conteúdo)  |
| 5       | .footer-fixed   |
| 7       | vignette        |
| 8       | film grain      |
| 10      | top-bar, progress-line, right-bar |

---

## Backgrounds

### Com imagem (cover, CTA)
- `_dark_bg()` retorna `<div class="bg-img">` com overlay gradient
- Dark: 50-68% opacidade escura
- Light: 72-82% opacidade clara + `brightness(1.3)`
- Ferrugem: radial gradient quente + grid sutil

### Sem imagem (slides do meio)
- `.bg-grid`: grid sutil 80×80px em dourado 3.5% opacidade
- Fundo: `var(--ink)` (dark) ou `#f5f1e8` (light)

### Fallback sem Unsplash (cover/CTA)
- Dark: gradient radial com tons de sangue/dourado + grid
- Light: gradient linear creme + grid
- Ferrugem: `var(--blood)` + radial gradient cobre

---

## Alinhamento por tipo de slide

| Tipo           | Classe `.si` | Fundo       | Justificativa                |
|----------------|-------------|-------------|-------------------------------|
| `cover`        | `.center`   | bg-img      | Impacto visual, leitura rápida|
| `cover_foto`   | esquerda    | ink + foto  | Foto à direita, texto esquerda|
| `hook`         | esquerda    | bg-grid     | Narrativa, leitura linear     |
| `hook_foto`    | direita     | ink + foto  | Foto à esquerda, texto direita|
| `corpo`        | esquerda    | ink         | Conteúdo educacional          |
| `dado`         | `.center`   | bg-grid     | Número gigante centralizado   |
| `quote`        | `.center`   | `--dark2`   | Citação pede centralidade     |
| `versus`       | esquerda    | bg-grid     | Cards empilhados              |
| `diagnostico`  | esquerda    | ink         | Lista numerada à esquerda     |
| `cta`          | `.center`   | bg-img      | CTA pede atenção focal        |

---

## Tipos de slide

### `cover` — Abertura com impacto
- Eyebrow (L1) → headline grande (T1) → reveal-bar → subtítulo itálico (S1)
- Footer: assinatura + dots
- Fundo: imagem Unsplash com overlay cinematográfico

### `cover_foto` — Abertura com foto pessoal
- Shape dourado decorativo + foto pessoal à direita
- Texto à esquerda: subtítulo + headline (96px) + CTA pill button
- Logo "JULIO**CARVALHO**" no topo
- Requer: foto PNG sem fundo (recorte profissional)

### `hook` — Tensão narrativa
- h2 grande (T2) → reveal-bar → corpo (B1) → destaque com barra dourada (D1)
- Fundo: bg-grid

### `hook_foto` — Tensão com foto pessoal
- Foto à esquerda + shape dourado
- Texto à direita: subtítulo + headline + pontos negativos (X) + ponto positivo (check)

### `corpo` — Ponto de conteúdo
- Slide-num (L2) → spacer → h3 (T3) → reveal-bar-full → body-l (B1) → destaque
- Numerado: `03 — 07`

### `dado` — Estatística impactante
- Número gigante (N1, 220px) → label (L1) → separador → contexto (B1)
- Centralizado

### `quote` — Citação do Julio
- Aspas decorativas (160px, 10% opacidade) → texto itálico (Q1) → atribuição mono
- Fundo: `--dark2`

### `versus` — Comparação
- Dois cards empilhados: "O mercado faz" (riscado, opaco) vs "A realidade é" (destaque, borda dourada)
- Body explicativo embaixo

### `diagnostico` — Lista diagnóstica
- h3 → reveal-bar → lista (máx 3 itens numerados 01/02/03) → conclusão itálica
- Headline auto-reduz pra 64px quando >40 caracteres

### `cta` — Fechamento e chamada
- Label "PRÓXIMO PASSO" → reveal-bar → h2 → body → assinatura + dots
- Fundo: imagem Unsplash (mesma do cover)

---

## Unsplash — Busca de imagens

### Fluxo
1. Claude gera `unsplash_query` no JSON do carrossel
2. `generator.py` adiciona sufixo conforme tema (`QUERY_SUFFIX`)
3. Busca via API Unsplash (orientation: portrait, per_page: 3)
4. Baixa imagem e embute como base64 (garante render no Playwright)

### Sufixos por tema
| Tema     | Sufixo                             |
|----------|------------------------------------|
| dark     | `dark moody editorial`             |
| light    | `minimal white bright clean`       |
| ferrugem | `warm rust texture industrial`     |
| misto    | `dark moody editorial`             |

### Overlay da imagem
| Tema     | Opacidade | Filtro                                |
|----------|-----------|---------------------------------------|
| dark     | 50-68%    | `saturate(0.7) contrast(1.1) brightness(0.95)` |
| light    | 72-82%    | `saturate(0.5) contrast(0.9) brightness(1.3)`  |
| ferrugem | 60-75%    | radial gradient cobre                  |

---

## Elementos recorrentes

### Barra reveal
```css
.reveal-bar { width: 64px; height: 4px; background: var(--gold); }
.reveal-bar-full { width: 100%; height: 1px; background: rgba(184,135,58,0.25); }
```

### Destaque (blockquote visual)
```css
.destaque-block {
  border-left: 4px solid var(--gold);
  padding-left: var(--sp2);
  font-style: italic;
  font-family: 'Fraunces', serif;
  font-size: 48px;
  color: var(--gold-light);
}
```

### Dots de progresso
- Dot inativo: 10×10px, 20% opacidade
- Dot ativo: 32×10px (pill), cor gold
- Progress line: 2px full-width, fill proporcional ao index

### Continuidade visual
- **Right bar**: barra dourada 4px na borda direita (exceto último slide)
- **Swipe cue**: "PRÓXIMO →" no canto inferior direito (exceto último slide)

---

## Dimensões finais

| Propriedade  | Valor              |
|--------------|--------------------|
| Largura      | 1080px             |
| Altura       | 1440px             |
| Proporção    | 3:4 (Instagram)    |
| Formato      | PNG                |
| Renderização | Playwright Chromium|
| Fontes       | Google Fonts (link)|
