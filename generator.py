"""generator.py — Geração de copy via Claude Code CLI (usa plano Max, sem custo de API)
Fallback automático para API direta se o CLI não estiver disponível."""
import base64
import json
import os
import shutil
import subprocess
import httpx
from dna import SYSTEM_PROMPT

# ─── LOCALIZAR O BINÁRIO DO CLAUDE CODE ──────────────────────────────────────
# Expande PATH para incluir dirs comuns onde o Claude Code é instalado
_extra_paths = ["~/.local/bin", "~/.npm-global/bin", "/usr/local/bin", "/opt/homebrew/bin"]
os.environ["PATH"] = os.environ.get("PATH", "") + ":" + ":".join(
    os.path.expanduser(p) for p in _extra_paths
)

def _find_claude_bin() -> str | None:
    # 1. shutil.which com PATH expandido (funciona independente de versão)
    found = shutil.which("claude")
    if found and os.path.isfile(found) and os.access(found, os.X_OK):
        return found
    # 2. Fallbacks explícitos
    for path in [
        os.path.expanduser("~/.local/bin/claude"),
        "/usr/local/bin/claude",
        "/opt/homebrew/bin/claude",
    ]:
        if path and os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None

CLAUDE_BIN = _find_claude_bin()

# ─── SCHEMA DO CARROSSEL ──────────────────────────────────────────────────────
CAROUSEL_SCHEMA = """Retorne um JSON com exatamente este formato:
{
  "titulo": "título interno do carrossel (para referência)",
  "pilar": "nome do pilar de conteúdo usado",
  "unsplash_query": "query curta em inglês para imagem de fundo dark/editorial (ex: 'dark architecture blueprint minimal')",
  "slides": [
    {
      "tipo": "cover",
      "eyebrow": "frase curta em caps — o gancho do público (máx 5 palavras)",
      "headline": "MÁXIMO 5 PALAVRAS. Sem verbos de apoio. Ex: 'IA não salva sistema ruim.' ou 'O sistema invisível trava tudo.' — impactante, direto, para no scroll",
      "subtitle": "1 frase que vira a chave — a promessa ou tensão central (máx 12 palavras)",
      "index": 1,
      "total": N
    },
    {
      "tipo": "hook",
      "headline": "pergunta ou afirmação que cria tensão",
      "body": "desenvolvimento curto e direto. Use \\n para quebras.",
      "destaque": "frase ou palavra-chave em ouro (a revelação)",
      "index": 2,
      "total": N
    },
    {
      "tipo": "corpo",
      "headline": "subtítulo do ponto",
      "body": "explicação direta. 2-4 linhas. Sem enrolação.",
      "destaque": "palavra ou frase que resume o ponto (opcional)",
      "index": 3,
      "total": N
    },
    {
      "tipo": "dado",
      "numero": "dado ou estatística impactante (ex: '87%' ou '300+')",
      "label": "o que esse número significa",
      "body": "contexto e implicação do dado",
      "index": 4,
      "total": N
    },
    {
      "tipo": "quote",
      "quote": "citação ou afirmação poderosa de Julio",
      "atribuicao": "Julio Carvalho — contexto",
      "index": 5,
      "total": N
    },
    {
      "tipo": "versus",
      "label_nao": "o que o mercado faz / o mito",
      "label_sim": "o que realmente funciona / a verdade",
      "body": "a lógica por trás da distinção",
      "index": 6,
      "total": N
    },
    {
      "tipo": "diagnostico",
      "headline": "o diagnóstico real",
      "itens": ["sintoma/ponto 1", "sintoma/ponto 2", "sintoma/ponto 3"],
      "conclusao": "a causa raiz que o lead ainda não nomeou",
      "index": 7,
      "total": N
    },
    {
      "tipo": "cta",
      "headline": "o convite — uma ação clara",
      "sub": "o próximo passo específico",
      "index": N,
      "total": N
    }
  ]
}
REGRAS:
- Primeiro slide: SEMPRE tipo "cover"
- Último slide: SEMPRE tipo "cta"
- Slides do meio: misture tipos conforme o tema pede
- Index começa em 1, total = número total de slides
- Headline do cover: impactante, pode ter quebra de linha com \\n
- Tom sempre: direto, cirúrgico, fala com o lead
- Retorne APENAS o JSON, sem markdown, sem explicação"""

# ─── GERAÇÃO VIA CLAUDE BRIDGE (HTTP) ────────────────────────────────────────
CLAUDE_BRIDGE_URL = os.environ.get("CLAUDE_BRIDGE_URL", "")

def _gerar_via_bridge(prompt_completo: str) -> dict:
    """Usa o claude-bridge HTTP (servidor) para gerar copy."""
    r = httpx.post(
        CLAUDE_BRIDGE_URL,
        json={"prompt": prompt_completo},
        timeout=180,
    )
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Claude Bridge erro: {data['error']}")
    raw = data.get("text") or data.get("result") or ""
    return _parse_json_response(raw)

# ─── GERAÇÃO VIA CLAUDE CODE CLI ─────────────────────────────────────────────
def _gerar_via_cli(prompt_completo: str) -> dict:
    if not CLAUDE_BIN:
        raise RuntimeError("Claude Code CLI não encontrado.")
    cmd = [
        CLAUDE_BIN, "--print",
        "--model", "sonnet", "-p", prompt_completo,
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120,
        env={**os.environ, "HOME": os.path.expanduser("~")},
    )
    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI erro: {result.stderr[:300]}")
    return _parse_json_response(result.stdout)

def _gerar_via_api(prompt_completo: str) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt_completo}],
    )
    return _parse_json_response(message.content[0].text)

def _parse_json_response(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    return json.loads(raw)

def gerar_copy(tema: str, num_slides: int = 7, pilar: str = "auto") -> dict:
    pilar_instrucao = f"\nUSE OBRIGATORIAMENTE o pilar: {pilar}\n" if pilar != "auto" else ""
    if CLAUDE_BIN:
        prompt_completo = f"{SYSTEM_PROMPT}\n\n---\n\nTema do carrossel: {tema}\nNúmero de slides: {num_slides}\n{pilar_instrucao}\n{CAROUSEL_SCHEMA}"
        modo = "Claude Code CLI (plano Max)"
    else:
        prompt_completo = f"Tema do carrossel: {tema}\nNúmero de slides: {num_slides}\n{pilar_instrucao}\n{CAROUSEL_SCHEMA}"
        modo = "API direta"
    print(f"[Generator] Modo: {modo}")
    print(f"[Generator] Tema: '{tema}' | {num_slides} slides")
    if CLAUDE_BIN:
        return _gerar_via_cli(prompt_completo)
    elif CLAUDE_BRIDGE_URL:
        return _gerar_via_bridge(prompt_completo)
    else:
        return _gerar_via_api(prompt_completo)

# ─── PANORÂMICA: IMAGEM CONTÍNUA FATIADA ─────────────────────────────────────
def buscar_panoramica_unsplash(query: str, num_slides: int = 7) -> list[str] | None:
    """Busca imagem landscape no Unsplash, redimensiona e fatia em N pedaços."""
    key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
    if not key:
        return None
    try:
        r = httpx.get(
            "https://api.unsplash.com/search/photos",
            params={"query": query, "per_page": 5, "orientation": "landscape"},
            headers={"Authorization": f"Client-ID {key}"},
            timeout=10,
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            return None
        # Pega a maior resolução disponível
        url = results[0]["urls"].get("raw", results[0]["urls"]["regular"])
        # Pedir dimensão específica via Unsplash API (largura total do panorama)
        total_w = 1080 * num_slides
        url = f"{url}&w={total_w}&h=1440&fit=crop&crop=center"
    except Exception as e:
        print(f"[Panorama] Erro na busca: {e}")
        return None

    try:
        from PIL import Image
        import io as _io

        img_r = httpx.get(url, timeout=30, follow_redirects=True)
        img_r.raise_for_status()
        img = Image.open(_io.BytesIO(img_r.content))

        # Redimensionar pra cobrir total_w × 1440
        target_w = 1080 * num_slides
        target_h = 1440
        # Calcular crop proporcional
        img_ratio = img.width / img.height
        target_ratio = target_w / target_h
        if img_ratio > target_ratio:
            # Imagem mais larga — crop horizontal
            new_h = img.height
            new_w = int(new_h * target_ratio)
            left = (img.width - new_w) // 2
            img = img.crop((left, 0, left + new_w, new_h))
        else:
            # Imagem mais alta — crop vertical
            new_w = img.width
            new_h = int(new_w / target_ratio)
            top = (img.height - new_h) // 2
            img = img.crop((0, top, new_w, top + new_h))

        img = img.resize((target_w, target_h), Image.LANCZOS)

        # Fatiar em N pedaços
        slices = []
        for i in range(num_slides):
            x = i * 1080
            slide_img = img.crop((x, 0, x + 1080, 1440))
            buf = _io.BytesIO()
            slide_img.save(buf, format="JPEG", quality=85)
            b64 = base64.b64encode(buf.getvalue()).decode()
            slices.append(f"data:image/jpeg;base64,{b64}")

        print(f"[Panorama] OK — {num_slides} fatias de {img.width}x{img.height}")
        return slices
    except Exception as e:
        print(f"[Panorama] Erro ao processar: {e}")
        return None


# ─── BUSCA DE IMAGEM (UNSPLASH) — com embed base64 ───────────────────────────
def buscar_imagem_unsplash(query: str) -> str | None:
    key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
    if not key:
        return None
    try:
        r = httpx.get(
            "https://api.unsplash.com/search/photos",
            params={"query": query, "per_page": 3, "orientation": "portrait"},
            headers={"Authorization": f"Client-ID {key}"},
            timeout=10,
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            return None
        url = results[0]["urls"]["regular"]
    except Exception as e:
        print(f"[Unsplash] Erro na busca: {e}")
        return None

    # Baixa a imagem e embute como base64 para garantir render no Playwright
    try:
        img_r = httpx.get(url, timeout=20, follow_redirects=True)
        img_r.raise_for_status()
        b64 = base64.b64encode(img_r.content).decode()
        mime = img_r.headers.get("content-type", "image/jpeg").split(";")[0]
        print(f"[Unsplash] Imagem embarcada ({len(img_r.content)//1024}KB)")
        return f"data:{mime};base64,{b64}"
    except Exception as e:
        print(f"[Unsplash] Fallback URL externa: {e}")
        return url

# ─── PIPELINE COMPLETO ────────────────────────────────────────────────────────
QUERY_SUFFIX = {
    "dark":     " dark moody editorial",
    "light":    " minimal white bright clean",
    "ferrugem": " warm rust texture industrial",
    "misto":    " dark moody editorial",
    "tricolor": " dark moody editorial",
}

def gerar_carrossel_completo(tema: str, num_slides: int = 7, pilar: str = "auto", estilo: str = "dark") -> dict:
    dados = gerar_copy(tema, num_slides, pilar)
    query = dados.get("unsplash_query", tema)
    # Adaptar query ao estilo visual
    query = query + QUERY_SUFFIX.get(estilo, "")
    print(f"[Unsplash] Query adaptada ({estilo}): {query}")

    imagem_url = buscar_imagem_unsplash(query)
    if imagem_url:
        print(f"[Unsplash] OK ({imagem_url[:60]}...)")
    dados["imagem_url"] = imagem_url
    return dados