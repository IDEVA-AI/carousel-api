# DESIGN.md — Sistema de Design · Carrossel Julio Carvalho

Documento de referência para o `slide_builder.py`. Toda decisão visual aqui tem uma razão.
Ao editar slides, este arquivo é a fonte da verdade de design.

---

## Princípios

1. **Estrutura antes de decoração.** Layout correto, tipografia certa, hierarquia clara — antes de qualquer elemento visual extra.
2. **Respiro é conteúdo.** Espaço em branco não é vazio; é o que faz o conteúdo respirar e a mensagem aterrissar.
3. **Hierarquia pelo tamanho.** O olho segue o tamanho. Nunca inverta: headline sempre maior que subheadline, subheadline sempre maior que corpo.
4. **Alinhamento à esquerda por padrão.** Slides de conteúdo são alinhados à esquerda. Centro é reservado para cover, cta, quote e dado.
5. **Itálico tem função, não decoração.** Só usar em destaques emocionais, citações e subtítulos de cover/cta.
6. **Labels em caixa alta com tracking.** Eyebrows e rótulos de seção sempre `text-transform: uppercase; letter-spacing: 0.12em`.
7. **Rodapé fixo e independente.** Assinatura e dots nunca competem com o conteúdo — ficam em posição absoluta fora do fluxo.
8. **Uma ideia por slide.** Se precisar de mais de um ponto, é outro slide.

---

## Paleta

| Variável        | Hex       | Uso                                      |
|-----------------|-----------|------------------------------------------|
| `--ink`         | `#0e0c0a` | Fundo principal (quase preto)            |
| `--paper`       | `#f4f0e8` | Texto principal (off-white quente)       |
| `--gold`        | `#b8873a` | Acentos, labels, barra reveal, atribuição|
| `--gold-light`  | `#e8d5b0` | Destaques secundários, dots ativos       |
| `--burgundy`    | `#3d1a0f` | Fundo de cover e cta (tom profundo)      |

---

## Tipografia

### Famílias

| Família    | Variável CSS   | Uso                                      |
|------------|----------------|------------------------------------------|
| Fraunces   | display / serif | Headlines, destaques, quotes            |
| DM Sans    | sans-serif      | Corpo de texto, labels                  |
| DM Mono    | monospace       | Números de slide, atribuições mono      |

Todas carregadas via Google Fonts no `<head>` de cada slide.

### Escala de tipos

| Token   | Classe CSS   | Tamanho  | Peso  | Família   | Uso                          |
|---------|--------------|----------|-------|-----------|------------------------------|
| T1      | `.cover-h`   | 108px    | 900   | Fraunces  | Headline de cover            |
| T2      | `h2`         | 96px     | 900   | Fraunces  | Headline de hook             |
| T3      | `h3`         | 72px     | 700   | Fraunces  | Headline de corpo/diagnóstico|
| B1      | `.body-l`    | 44px     | 400   | DM Sans   | Corpo principal              |
| B2      | `.body-m`    | 36px     | 400   | DM Sans   | Corpo secundário             |
| L1      | `.label`     | 26px     | 500   | DM Sans   | Labels / eyebrows            |
| L2      | `.slide-num` | 22px     | 400   | DM Mono   | Numeração de slides          |

**Regra:** nunca usar negrito no corpo. Negrito só em headlines. Itálico só em destaques e quotes.

---

## Espaçamento

Tokens definidos como variáveis CSS globais:

```css
--sp1: 16px   /* micro — gap entre elementos inline */
--sp2: 24px   /* pequeno — gap padrão entre elementos */
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
┌─────────────────────────────┐
│  top-bar (4px, gold)        │  ← decoração topo
│                             │
│  .si (flex column)          │  ← área de conteúdo
│    spacer (flex proporcional)│
│    conteúdo                 │
│    spacer (flex: 1)         │  ← empurra para cima
│                             │
│  .footer-fixed (absolute)   │  ← fora do fluxo
│    assinatura               │
│    dots de progresso        │
└─────────────────────────────┘
```

### CSS crítico do `.si`

```css
.si {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;   /* esquerda por padrão */
  text-align: left;
  padding: 88px var(--sp5) 200px;
  position: relative;
  z-index: 2;
  overflow: hidden;          /* protege overflow de conteúdo longo */
}

.si.center {
  align-items: center;
  text-align: center;
}
```

### Rodapé fixo

```css
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
```

---

## Alinhamento por tipo de slide

| Tipo         | Classe `.si`      | Justificativa                            |
|--------------|-------------------|------------------------------------------|
| `cover`      | `.si.center`      | Impacto visual, leitura rápida           |
| `hook`       | `.si` (esquerda)  | Narrativa, leitura linear                |
| `corpo`      | `.si` (esquerda)  | Conteúdo educacional, leitura linear     |
| `dado`       | `.si.center`      | Número gigante centraliza naturalmente   |
| `quote`      | `.si.center`      | Citação clama por centralidade           |
| `versus`     | `.si` (esquerda)  | Comparação em stacked blocks             |
| `diagnostico`| `.si` (esquerda)  | Lista numerada lê melhor à esquerda      |
| `cta`        | `.si.center`      | CTA pede atenção focal                   |

---

## Centralização vertical (flex spacers)

Problema: conteúdo curto fica colado ao topo; conteúdo longo extravasa.
Solução: flex spacers proporcionais — não `justify-content: center` (que não controla overflow).

```python
# Antes do conteúdo (empurra para baixo)
<div class="sp" style="flex:0.35; min-height:40px; flex-shrink:0;"></div>

# Depois do conteúdo (preenche o restante)
<div class="sp" style="flex:1;"></div>
```

**Valores por tipo:**

| Tipo         | Spacer superior | min-height |
|--------------|-----------------|------------|
| `corpo`      | `flex: 0.5`     | `64px`     |
| `diagnostico`| `flex: 0.35`    | `40px`     |
| `hook`       | sem spacer      | —          |
| `cover/cta`  | `.si.center` + `justify-content: center` | — |

---

## Controle de overflow

O `.body-l` (corpo principal) pode crescer demais em slides com muito texto:

```css
.body-l {
  flex-shrink: 1;
  min-height: 0;
}
```

Isso permite que o flex container comprima o corpo antes de extravazar o footer.
O `overflow: hidden` no `.si` corta qualquer extravazamento residual.

---

## Elementos recorrentes

### Barra reveal

```html
<div class="reveal-bar-full"></div>
```
```css
.reveal-bar-full {
  width: 64px;
  height: 4px;
  background: var(--gold);
}
```
Usada depois do headline em slides de corpo e diagnóstico.

### Destaque (blockquote visual)

```html
<div class="destaque">Texto do destaque.</div>
```
```css
.destaque {
  border-left: 4px solid var(--gold);
  padding-left: var(--sp2);
  font-style: italic;
  font-family: 'Fraunces', serif;
  color: var(--gold-light);
  font-size: 38px;
  line-height: 1.4;
}
```

### Dots de progresso

Gerados pelo helper `_footer()`. Dot ativo = cor gold, inativos = opacidade 30%.

```python
dots = ""
for i in range(1, total + 1):
    active = "background:var(--gold);" if i == index else "opacity:0.3;"
    dots += f'<div style="width:8px;height:8px;border-radius:50%;background:var(--paper);{active}"></div>'
```

---

## Tipos de slide — referência rápida

### `cover`
- `.si.center`
- Label eyebrow em ouro → headline grande → barra → subtítulo itálico
- Fundo: `--burgundy` ou imagem
- Footer: assinatura + dots

### `hook`
- `.si` (esquerda)
- h2 grande → barra → corpo em parágrafos → destaque opcional
- Fundo: ink

### `corpo`
- `.si` (esquerda)
- Slide-num → spacer → h3 → barra → body-l → destaque opcional → spacer
- Numerado: `02 — 07`

### `dado`
- `.si.center`
- Número gigante (120px+) → label descritivo → separador → contexto

### `quote`
- `.si.center`
- Aspas decorativas (SVG ou `❝`) → texto itálico grande → atribuição mono ouro

### `versus`
- `.si` (esquerda)
- Dois blocos stacked: "O mercado faz" vs "A realidade é"

### `diagnostico`
- `.si` (esquerda)
- h3 → barra → lista `.diag-list` (máx 3 itens numerados 01/02/03) → conclusão itálica

### `cta`
- `.si.center`
- Label "PRÓXIMO PASSO" → h2 → body → assinatura completa + dots

---

## Dimensões finais

| Propriedade  | Valor        |
|--------------|--------------|
| Largura      | 1080px       |
| Altura       | 1440px       |
| Proporção    | 3:4 (vertical Instagram) |
| Formato      | PNG          |
| Renderização | Playwright (Chromium headless) |
