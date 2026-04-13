# CONTEXT.md — Carousel API (Julio Carvalho)

## 1. Visão geral

API Python (FastAPI) que automatiza produção de conteúdo para Instagram. Gera carrosseis (1080×1440) e formatos alternativos (tweet 1080×1080, feed single 1080×1440, story 1080×1920) a partir de um tema ou trending topic, usando Claude (CLI/bridge/SDK) ancorado no DNA de marca de Julio Carvalho. Renderiza slides HTML→PNG via Playwright, publica no Instagram Graph API, agenda posts (APScheduler) e roda automações de DM, comentários, lead scoring e analytics. Interface web em `static/index.html` + `static/pages/`.

## 2. Stack & dependências

- **Runtime:** Python 3.10+, venv `.venv/`
- **Web:** FastAPI 0.115, Uvicorn 0.32
- **LLM:** Claude Code CLI (preferencial, plano Max); fallback `CLAUDE_BRIDGE_URL` (HTTP); fallback final `anthropic` SDK 0.40 (`claude-sonnet-4-6`)
- **Render:** Playwright 1.49 Chromium headless, Pillow 11
- **HTTP:** httpx 0.28
- **Trends/Schedule:** pytrends 4.9, APScheduler 3.10 (timezone America/Sao_Paulo)
- **Config:** python-dotenv, pydantic 2.10
- **Infra:** Docker (`mcr.microsoft.com/playwright/python:v1.49.1-noble`), Docker Swarm via `docker-stack.yaml`, Traefik em `carousel.onexos.com.br`, porta interna 8765, volume `carousel-historico`

## 3. Modelos, schemas e persistência

Não há ORM/DB — persistência é 100% JSON em disco (`historico/` ou volume `/app/historico`).

**Pydantic (request models em `server.py`):**
- `GerarRequest { tema:str, slides:int 5-10=7, pilar:str="auto", avatar_url:str?, estilo:str="dark" }`
- `RenderizarRequest { carrossel_json:dict, avatar_url:str?, estilo:str="dark", foto_url:str?, visual:str="none" }`

**Schema do carrossel (JSON, `generator.CAROUSEL_SCHEMA`):**
```
{ titulo, pilar, unsplash_query,
  slides: [ {tipo, index, total, ...campos por tipo} ] }
```
Tipos de slide: `cover`, `hook`, `corpo`, `dado`, `quote`, `versus`, `diagnostico`, `cta` (+ variantes `*_foto`, `*_visual`). Primeiro sempre `cover`, último sempre `cta`.

**Pilares válidos (fixos, `trending.PILARES_VALIDOS`):**
"O Sistema Invisível", "Arquitetura de Decisão", "Diagnóstico Cirúrgico", "Comportamento e Sistema", "Narrativas vs. Realidade".

**Arquivos JSON persistidos em `HISTORICO_DIR`:**
| Arquivo | Conteúdo |
|---|---|
| `{id}/meta.json` + `slide_N.png` | Carrossel salvo (id 8 hex) |
| `base-conteudo.json` | frameworks/cases/dados/opinioes/sintomas |
| `postagens.json` | Últimas 100 postagens (pipeline) |
| `schedule-config.json` | Config do scheduler (jobs cron) |
| `schedule-log.json` | Últimos 50 logs de execução |
| `automation-keywords.json`, `automation-logs.json` | Keywords/logs do comment handler |
| `dm-sequences.json`, `dm-active.json` | Sequências DM e DMs ativas |
| `leads.json` | Lead scoring (SCORE_MAP, THRESHOLD_QUENTE=30) |
| `analytics.json` | Snapshots de métricas IG |

**DNA modular (`dna/*.py`):** `identidade`, `avatar`, `pilares`, `metodo`, `credenciais`, `tom` → concatenados em `BRAND_DNA` e `SYSTEM_PROMPT`. Editáveis via `PUT /api/dna/{modulo}` (reescreve arquivo `.py` + `importlib.reload`).

## 4. Endpoints (FastAPI — `server.py`)

**Core geração:**
- `GET /health` · `GET /pilares`
- `POST /gerar` → gera copy JSON (sem render)
- `POST /renderizar` → monta HTML, Playwright→PNG, salva no histórico, retorna previews base64
- `GET /baixar` → ZIP do último carrossel

**Histórico:**
- `GET /historico` · `GET /historico/{id}` · `GET /historico/{id}/thumb` · `DELETE /historico/{id}`

**Pipeline automático:**
- `POST /pipeline/executar` → trending→copy→render→caption→post→notify
- `POST /pipeline/preview` → etapas 1-5 sem postar

**Formatos alternativos:**
- `POST /api/post/render` (formato: tweet | feed_single | story) · `GET /api/post/formatos`

**Instagram Graph:**
- `GET /api/instagram/profile` · `/media` · `/quota`

**Webhook Meta:**
- `GET /webhook/instagram` (verify) · `POST /webhook/instagram` (events → `process_comment`)

**Automação:**
- Keywords: `GET/POST /api/automation/keywords`, `GET /api/automation/logs`
- DMs: `GET/POST /api/dm/sequences`, `GET /api/dm/active`, `POST /api/dm/send`
- Leads: `GET /api/leads`, `GET /api/leads/quentes`
- Analytics: `GET /api/analytics`, `POST /api/analytics/snapshot`

**Scheduler:**
- `GET /api/scheduler`, `POST /api/scheduler/config|start|stop`

**DNA:**
- `GET /api/dna`, `PUT /api/dna/{modulo}`

**Base de conteúdo:**
- `GET /api/conteudo`, `POST /api/conteudo/importar`
- `GET/POST/PUT/DELETE /api/conteudo/{tipo}[/{index}]`

**Postagens, temp & privacy:**
- `GET /api/postagens` · `GET /api/temp/{filename}` · `GET /privacy`
- `GET /` → `static/` (SPA)

## 5. Services & regras de negócio

### `generator.py`
- `_find_claude_bin()` detecta CLI no PATH estendido (`~/.local/bin`, `/opt/homebrew/bin`, etc.).
- `gerar_copy()` escolhe backend em ordem: CLI → bridge HTTP → anthropic SDK. Prompt = `SYSTEM_PROMPT + tema + num_slides + pilar + CAROUSEL_SCHEMA`. Modelo: `sonnet` no CLI, `claude-sonnet-4-6` no SDK.
- `buscar_imagem_unsplash()` baixa e embute como `data:` base64 (garante render Playwright).
- `buscar_panoramica_unsplash()` busca landscape, redimensiona a `1080*N × 1440` e fatia em N slides contínuos (Pillow).
- `gerar_carrossel_completo()` injeta `QUERY_SUFFIX` por estilo (`dark`, `light`, `ferrugem`, `misto`, `tricolor`).

### `pipeline.py` — orquestração de 7 etapas
1. `etapa_tema` → `trending.buscar_tema`
2. `etapa_copy` → gera carrossel, **valida pilar** (`_validar_pilar`), **fallback** headline para slides vazios
3. `etapa_render` → avatar IG cache → `build_all_slides` → `renderizar_e_empacotar`
4. `etapa_caption` → Claude gera legenda ≤2200 chars + 15-20 hashtags (bridge HTTP)
5. `etapa_postar` → grava PNGs em `/tmp/carousel-temp`, expõe via `{PUBLIC_BASE_URL}/api/temp/...`, chama `instagram.postar_carousel`, limpa temp
6. `etapa_notificar` → POST pra BRAINIAC WhatsApp API em sucesso ou erro
7. `_salvar_postagem` em `postagens.json` (ring 100)

`TIPO_INSTRUCOES`: 10 moldes de conteúdo (provocacao, diagnostico, framework, dado, mito_vs_realidade, historia, opiniao, checklist, noticia, cta_direto).

### `trending.py`
- `buscar_trending_google()` via pytrends (`pn='brazil'`).
- `adaptar_trending_ao_dna()` — Claude bridge recebe DNA + trending + lista de temas já usados e escolhe/adapta.
- `_carregar_temas_usados()` une títulos de `meta.json`, `postagens.json`, `schedule-log.json`.
- `_tema_ja_usado()` — dedup: match exato OR similaridade Jaccard > 0.6.
- `_validar_pilar()` — força um dos 5 pilares (match exato → substring → keywords).
- `TEMAS_FALLBACK` — 20 temas curados, rotação circular por pilar.
- `buscar_tema()` — Google Trends → adapt → dedup → fallback curado → último recurso repetido.

### `instagram.py` (Graph API v22.0)
Fluxo carousel: `_create_image_container` (1 por imagem) → `_wait_container_ready` (poll status_code até FINISHED/ERROR, timeout 60s) → `_create_carousel_container` → `_publish` → busca `permalink`. Retries com backoff 5×attempt, máx 3. Valida 2-10 imagens.

### `renderer.py`
`render_slides()` roda `asyncio.run` em `ThreadPoolExecutor(max_workers=1)` — isola do event loop FastAPI. Playwright Chromium, viewport 1080×1440, `networkidle` + 800ms para fontes Google. Empacota ZIP em memória + base64 previews.

### `slide_builder.py` / `post_builder.py` / `visuals.py` / `esquemas.py`
Design system fechado: tokens tipográficos T1..T3/B1/L1, paleta `--ink/--paper/--gold`, fontes Fraunces + DM Mono + DM Sans, film grain SVG, vignette. Cada tipo de slide = função que recebe `(data, imagem_url, avatar_url, theme)` e retorna string HTML. `post_builder.FORMAT_BUILDERS` com `tweet` (1080²), `feed_single` (1080×1440), `story` (1080×1920). `visuals.COLORS` por tema. `esquemas.py` gera SVGs decorativos (rede, funil, gauge, flowchart, seta curva).

### `scheduler.py`
`BackgroundScheduler` + `CronTrigger` em BR_TZ. 3 jobs default (09/13/18h, estilos dark/light/ferrugem). `start_scheduler` é idempotente (shutdown+recreate sob `_lock`). Cada job chama `pipeline.executar_pipeline` e loga em `schedule-log.json`.

### `automation/`
- `webhook.py` — verify_token + HMAC-SHA256 (`X-Hub-Signature-256`) com `INSTAGRAM_APP_SECRET`.
- `comment_handler.py` — matching por keywords → auto-reply + dispara DM via Graph API.
- `dm_sequences.py` — envio em threads, delays configuráveis.
- `lead_scoring.py` — SCORE_MAP (like=1, comment=3, comment_keyword=10, save=5, dm_received=15, profile_visit=2); lead vira quente em score ≥ 30.
- `analytics.py` — coleta métricas `like_count/comments_count` de `/me/media` e snapshota.

## 6. Regras absolutas do DNA (`dna/__init__.py` · SYSTEM_PROMPT)

1. Falar com o lead, nunca descrever o slide.
2. Tom direto/cirúrgico, sem enrolação.
3. Headlines criam tensão ou nomeiam o não-nomeado.
4. Proibido: "Neste slide", "Aqui vemos", "Como vimos", "Em resumo".
5. Retornar **apenas** JSON válido.
6. Somente os 5 pilares fixos — nunca inventar.
7. Adaptar tema fora de escopo ao universo gestão/sistemas.
8. Público fixo: CEO/founder R$5M-R$100M.
9. Usar frases-âncora do avatar.
10. Referenciar Método Arquiteto quando pertinente.
11. Cases/dados reais onde pedir autoridade.
12. Opiniões fortes = referência de intensidade.

## 7. Middlewares & configuração

- `fastapi.staticfiles.StaticFiles` montado em `/` (SPA) — **último** no server.py.
- `on_event("startup")` chama `scheduler.start_scheduler()`.
- Não há CORS/auth middlewares explícitos — API exposta via Traefik; auth do Instagram é por token em env.
- Validação de webhook: HMAC do Meta via `INSTAGRAM_APP_SECRET`.
- Detecção de ambiente Docker vs local: `Path("/app/historico").exists()` decide raiz de persistência em todos os módulos.

## 8. Variáveis de ambiente

| Var | Uso | Obrig. |
|---|---|---|
| `ANTHROPIC_API_KEY` | Fallback SDK direto | Não (se CLI/bridge) |
| `CLAUDE_BRIDGE_URL` | HTTP bridge (Docker) | Não |
| `UNSPLASH_ACCESS_KEY` | Imagens de fundo | Não |
| `INSTAGRAM_ACCESS_TOKEN` | Graph API | Sim p/ pipeline |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Graph API | Sim p/ pipeline |
| `INSTAGRAM_WEBHOOK_VERIFY_TOKEN` | Webhook Meta | Se usar webhook |
| `INSTAGRAM_APP_SECRET` | HMAC webhook | Se usar webhook |
| `PUBLIC_BASE_URL` | URL pública p/ Meta baixar imgs | Sim p/ pipeline |
| `BRAINIAC_API_URL`, `NOTIFY_WHATSAPP` | Notificação | Não |
| `PORT` | default 8765 (Docker) / 8000 (.env.example) | Não |

## 9. Testes

Sem suíte de testes no repo (sem `tests/`, `pytest.ini` ou `conftest.py`). Validação é manual via `GET /health`, `/pilares` e a UI em `static/`. `start.sh` faz pré-check de CLI/API key antes de subir Uvicorn com `--reload`.

## 10. Estrutura de diretórios

```
carousel-api/
├── server.py              # FastAPI app (endpoints)
├── generator.py           # LLM (CLI/bridge/SDK) + Unsplash + panorama
├── pipeline.py            # 7 etapas: tema→copy→render→caption→post→notify
├── trending.py            # pytrends + dedup + validação pilares
├── post_builder.py        # Formatos: tweet, feed_single, story
├── slide_builder.py       # HTML slides 1080×1440 (design system fechado)
├── visuals.py             # Paletas + SVG decorativos
├── esquemas.py            # Diagramas SVG (rede, funil, gauge, flow)
├── renderer.py            # Playwright HTML→PNG + ZIP (ThreadPoolExecutor)
├── scheduler.py           # APScheduler BR_TZ + logs
├── instagram.py           # Graph API v22.0 (carousel publish)
├── dna/                   # DNA modular: identidade, avatar, pilares, metodo, credenciais, tom
├── automation/
│   ├── webhook.py         # Verify + HMAC Meta
│   ├── comment_handler.py # Keywords → reply → DM
│   ├── dm_sequences.py    # Sequências threadsafe
│   ├── lead_scoring.py    # Score + quente (≥30)
│   └── analytics.py       # Snapshots métricas IG
├── base-conteudo/         # Base editorial (frameworks, cases, dados, opiniões, sintomas)
├── static/                # index.html + pages + fotos
├── historico/             # JSONs + PNGs (volume em Docker)
├── requirements.txt
├── Dockerfile, docker-stack.yaml, start.sh, setup.sh
├── .env / .env.example
├── CLAUDE.md, DESIGN.md, README.md, CONTEXT.md
└── .venv/
```

Legado: `dna_old.py.bak`, `slide_builder.py.bak`, `_backup_pre_temas/`.
