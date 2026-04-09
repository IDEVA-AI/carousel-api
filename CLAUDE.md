# CLAUDE.md — Gerador de Carrosseis · Julio Carvalho

Este arquivo instrui o Claude Code sobre a arquitetura e convenções deste projeto.

## O que é este projeto

API local que gera carrosseis de Instagram prontos para postar. Recebe um tema, chama o Claude Code CLI para gerar o copy com DNA de marca fixo, busca imagem de fundo no Unsplash, renderiza os slides em HTML via Playwright e devolve PNGs 1080×1440px.

## Stack

- **FastAPI** + **Uvicorn** — servidor HTTP local (porta 8765)
- **Playwright (Chromium)** — screenshot engine headless
- **Claude Code CLI** — geração de copy (usa plano Max, sem custo de API)
- **Unsplash API** — imagens de fundo (opcional, chave no .env)
- **Python 3.10+**, venv em `.venv/`

## Estrutura dos arquivos

```
carousel-api/
├── server.py          # FastAPI app — endpoints /gerar e /baixar
├── generator.py       # Orquestra: chama CLI do Claude + Unsplash
├── slide_builder.py   # Monta HTML de cada tipo de slide (1080×1440px)
├── renderer.py        # Playwright: HTML → PNG, gera ZIP
├── dna.py             # DNA da marca Julio Carvalho (contexto fixo do prompt)
├── static/
│   └── index.html     # Interface web completa (preview + download)
├── requirements.txt
├── .env               # Chaves (não commitar)
└── .env.example
```

## Como rodar

```bash
cd ~/carousel-api
.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8765
# Abrir: http://localhost:8765
```

## Variáveis de ambiente (.env)

| Variável | Obrigatório | Descrição |
|---|---|---|
| `ANTHROPIC_API_KEY` | Não (se CLI disponível) | Fallback caso o CLI não seja encontrado |
| `UNSPLASH_ACCESS_KEY` | Não | Imagens de fundo. Sem ela, cover fica com grid |
| `PORT` | Não | Porta do servidor (default: 8000) |

## Fluxo de geração

```
POST /gerar { tema, slides, pilar, avatar_url }
  └─ generator.py → claude CLI -p "prompt+DNA" --output-format json
  └─ generator.py → Unsplash API (busca imagem pelo unsplash_query do JSON)
  └─ slide_builder.py → build_all_slides() → lista de HTML strings
  └─ renderer.py → Playwright screenshot cada HTML → lista de PNG bytes
  └─ response → { previews: [base64...], titulo, pilar, ... }

GET /baixar
  └─ Renderiza novamente o último carrossel gerado
  └─ response → arquivo .zip com slide_01.png ... slide_N.png
```

## Tipos de slide disponíveis

| tipo | Uso |
|---|---|
| `cover` | Sempre o primeiro. Eyebrow + headline grande + subtitle + assinatura |
| `hook` | Pergunta ou afirmação que cria tensão. Headline h2 + body + destaque |
| `corpo` | Ponto de conteúdo. Slide-num + h3 + body + destaque opcional |
| `dado` | Estatística impactante. Número gigante + label + contexto |
| `quote` | Citação de Julio. Aspas decorativas + texto itálico + atribuição |
| `versus` | Comparação stacked. Mito vs. realidade |
| `diagnostico` | Lista numerada (máx 3 itens) + conclusão. Sempre h3 |
| `cta` | Sempre o último. Convite + próximo passo + assinatura completa |

## Design system dos slides

- **Cores:** `--ink #0e0c0a`, `--paper #f4f0e8`, `--gold #b8873a`, `--gold-light #e8d5b0`
- **Fontes:** Fraunces (display, 900/700), DM Mono (monospace), DM Sans (corpo)
- **Padding:** 88px top, 100px lados, 80px bottom
- **Cover headline:** `.cover-h` — 108px, máx 5 palavras
- **h2:** 112px para slides de impacto (hook)
- **h3:** 84px para slides de conteúdo (corpo, diagnóstico)
- **body-l:** 46px, line-height 1.52 — texto corrido
- **body-m:** 40px — texto secundário

## Convenções importantes

- `slide_builder.py` — cada função recebe `(data, imagem_url, avatar_url)`. Apenas `cover` e `cta` usam `imagem_url`.
- `renderer.py` — usa `ThreadPoolExecutor` para isolar o `asyncio.run()` do event loop do FastAPI. Não remover.
- `generator.py` — `CLAUDE_BIN` é detectado no import. Se não encontrar o CLI, cai para API direta.
- `dna.py` — `SYSTEM_PROMPT` é o contexto completo da marca. Alterar aqui para mudar tom, pilares ou credenciais.

## Tarefas comuns

**Adicionar novo tipo de slide:**
1. Criar função `slide_novo(data, imagem_url, avatar_url)` em `slide_builder.py`
2. Adicionar ao dict `SLIDE_BUILDERS`
3. Adicionar ao schema `CAROUSEL_SCHEMA` em `generator.py`

**Mudar o modelo do Claude:**
Em `generator.py`, na função `_gerar_via_cli()`, alterar `--model sonnet` para `opus` ou `haiku`.

**Trocar porta:**
Editar `.env`: `PORT=XXXX` e reiniciar.

**Atualizar DNA da marca:**
Editar `dna.py` — variável `BRAND_DNA`. O `SYSTEM_PROMPT` é montado automaticamente a partir dela.
