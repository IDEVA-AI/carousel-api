# Gerador de Carrosseis — Julio Carvalho

API local que transforma um tema em carrossel de Instagram pronto para postar. Gera o copy com IA usando seu DNA de marca, busca imagem de fundo no Unsplash e renderiza os slides em PNG 1080×1440px.

---

## Requisitos

- macOS com Python 3.10+
- Claude Code instalado e autenticado (`claude --version`)
- Conexão com internet (para fontes Google e Unsplash)

---

## Instalação (primeira vez)

```bash
cd ~/carousel-api
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
cp .env.example .env
```

Edite o `.env` e preencha as chaves:

```bash
nano .env
```

```env
# Obrigatório apenas se o Claude Code CLI não estiver instalado
ANTHROPIC_API_KEY=sk-ant-...

# Opcional — imagens de fundo via Unsplash (gratuito: 50 req/hora)
# Cadastro em: https://unsplash.com/developers
UNSPLASH_ACCESS_KEY=...
```

---

## Iniciar o servidor

```bash
cd ~/carousel-api
.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8765
```

Abra no navegador: **http://localhost:8765**

---

## Como usar a interface

1. **Tema** — descreva o assunto do carrossel em linguagem natural
2. **Pilar** — escolha um dos 5 pilares de conteúdo ou deixe em "Auto-detectar"
3. **Slides** — ajuste de 5 a 10 slides com o slider
4. **Avatar** — clique no círculo para carregar sua foto (aparece em todos os slides)
5. Clique em **→ Gerar Carrossel**

Após a geração (~30–60s):
- Visualize os slides em preview
- Clique em qualquer slide para abrir em tela cheia
- Clique em **↓ Baixar ZIP** para obter os PNGs finais em 1080×1440px

---

## API

### `POST /gerar`

Gera o carrossel e retorna previews em base64.

```json
{
  "tema": "Por que delegar não funciona na maioria das empresas",
  "slides": 7,
  "pilar": "auto",
  "avatar_url": null
}
```

Resposta:
```json
{
  "titulo": "Delegação não é o problema",
  "pilar": "Arquitetura de Decisão",
  "total_slides": 7,
  "previews": ["data:image/png;base64,..."],
  "unsplash_query": "dark architecture minimal",
  "imagem_url": "https://images.unsplash.com/..."
}
```

### `GET /baixar`

Retorna o ZIP com os PNGs do último carrossel gerado.

### `GET /health`

```json
{ "status": "ok", "version": "1.0.0" }
```

### `GET /pilares`

Lista os 5 pilares de conteúdo disponíveis.

---

## Tipos de slide

| Tipo | Descrição |
|---|---|
| `cover` | Capa — eyebrow, headline de impacto, subtitle, assinatura |
| `hook` | Abertura — tensão ou pergunta que para o scroll |
| `corpo` | Conteúdo — ponto específico com destaque opcional |
| `dado` | Estatística — número gigante com contexto |
| `quote` | Citação — frase poderosa em itálico |
| `versus` | Comparação — mito vs. realidade (layout stacked) |
| `diagnostico` | Diagnóstico — lista numerada (máx 3 itens) + conclusão |
| `cta` | CTA final — convite + próximo passo + assinatura completa |

---

## Custo

O gerador usa o **Claude Code CLI** internamente, que consome sua sessão autenticada do Claude Code. Se você tem um plano **Claude Code Max**, as gerações entram nesse plano — sem custo adicional de API.

Se o CLI não for encontrado, o sistema cai para a **API Anthropic direta** (requer `ANTHROPIC_API_KEY`). Custo aproximado: **~R$0,10 por carrossel** com Claude Sonnet.

Imagens do Unsplash são gratuitas (plano Developer: 50 requisições/hora).

---

## Estrutura do projeto

```
carousel-api/
├── server.py          # FastAPI — endpoints e servidor
├── generator.py       # Claude CLI + Unsplash
├── slide_builder.py   # Templates HTML dos 8 tipos de slide
├── renderer.py        # Playwright: HTML → PNG → ZIP
├── dna.py             # DNA da marca (contexto fixo do prompt)
├── static/
│   └── index.html     # Interface web
├── CLAUDE.md          # Instruções para o Claude Code
├── requirements.txt
├── .env.example
└── .env               # Suas chaves (não versionar)
```

---

## Personalização

**Mudar DNA da marca:** edite `dna.py` → variável `BRAND_DNA`.

**Mudar modelo:** em `generator.py` → `_gerar_via_cli()` → flag `--model sonnet` (opções: `haiku`, `sonnet`, `opus`).

**Mudar porta:** edite `.env` → `PORT=XXXX`.

**Adicionar tipo de slide:** crie a função em `slide_builder.py`, registre em `SLIDE_BUILDERS` e adicione ao schema em `generator.py`.
