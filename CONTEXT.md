# CONTEXT.md — Carousel API (Julio Carvalho)

## 1. Visão geral

API local/containerizada em Python que gera carrosseis (e outros formatos) para Instagram. Recebe um tema, chama o Claude (CLI ou bridge HTTP) com o DNA de marca, busca imagem no Unsplash, renderiza slides HTML→PNG via Playwright e devolve imagens prontas. Inclui pipeline de temas com dedup + validação de pilares, agendador (APScheduler), integração com Instagram Graph API e automações (webhooks, DMs, comentários, analytics).

## 2. Stack & dependências

- **Runtime:** Python 3.10+, venv em `.venv/`
- **Web:** FastAPI 0.115 + Uvicorn 0.32
- **LLM:** Claude Code CLI (preferencial) ou `anthropic` SDK 0.40 (fallback). Em Docker, usa `CLAUDE_BRIDGE_URL` (HTTP bridge).
- **Render:** Playwright 1.49 (Chromium headless) + Pillow 11
- **HTTP:** httpx 0.28
- **Scheduler/Trends:** APScheduler 3.10, pytrends 4.9
- **Config:** python-dotenv, pydantic 2.10

Container: `mcr.microsoft.com/playwright/python:v1.49.1-noble`. Deploy via Docker Swarm (`docker-stack.yaml`) atrás de Traefik em `carousel.onexos.com.br`, porta interna 8765, volume `carousel-historico`.

## 10. Estrutura de diretórios

```
carousel-api/
├── server.py              # FastAPI app (endpoints)
├── generator.py           # Orquestra LLM (CLI/bridge/SDK) + Unsplash
├── pipeline.py            # Pipeline de temas: dedup + validação pilares
├── post_builder.py        # Monta posts multi-formato
├── slide_builder.py       # HTML dos slides (1080×1440)
├── renderer.py            # Playwright HTML→PNG + ZIP
├── scheduler.py           # APScheduler (agendamentos)
├── trending.py            # pytrends / temas em alta
├── instagram.py           # Instagram Graph API (publicação)
├── visuals.py             # Helpers visuais
├── esquemas.py            # Schemas Pydantic / JSON
├── dna/                   # DNA modular da marca
│   ├── identidade.py, avatar.py, credenciais.py,
│   ├── metodo.py, pilares.py, tom.py
├── automation/            # Webhook, DMs, comentários, lead scoring, analytics
├── base-conteudo/         # Base editorial (skills, micro-nicho, frameworks, cases…)
├── static/                # index.html + pages + fotos (preview web)
├── historico/             # Carrosseis gerados (persistido em volume)
├── requirements.txt
├── Dockerfile, docker-stack.yaml, start.sh, setup.sh
├── .env / .env.example
├── CLAUDE.md, DESIGN.md, README.md
└── .venv/
```

Módulos legados/backup: `dna_old.py.bak`, `slide_builder.py.bak`, `_backup_pre_temas/`.
