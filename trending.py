"""
trending.py — Detecção de tendências + geração de temas
Busca trending topics e adapta ao DNA da marca via Claude.
"""
import os
import json
import httpx

CLAUDE_BRIDGE_URL = os.environ.get("CLAUDE_BRIDGE_URL", "")

# ─── TEMAS FALLBACK (rotação pelos 5 pilares) ────────────────────────────────
TEMAS_FALLBACK = [
    # Pilar 1: O Sistema Invisível
    "Por que sua empresa para quando você sai de férias",
    "O fluxo invisível que mata sua operação sem você perceber",
    "Sua empresa funciona ou depende de você?",
    "O que acontece quando o dono some por uma semana",
    # Pilar 2: Arquitetura de Decisão
    "Você não delega mal — seu sistema não tem zonas de decisão",
    "Por que toda decisão ainda chega até você",
    "Como o CEO virou gargalo sem perceber",
    "Delegar tarefa vs delegar autoridade — a diferença que trava tudo",
    # Pilar 3: Diagnóstico Cirúrgico
    "3 perguntas que revelam onde o sistema quebrou",
    "Como separar sintoma de causa em 10 minutos",
    "O que todo diagnóstico raso deixa passar",
    "Seu problema não é o que você acha que é",
    # Pilar 4: Comportamento e Sistema
    "Por que pessoas boas não salvam sistemas ruins",
    "Seu melhor funcionário vai embora mas o problema continua",
    "O que o sistema recompensa que você não percebe",
    "A empresa é o espelho do dono — gostando ou não",
    # Pilar 5: Narrativas vs. Realidade
    "Automatizar processo quebrado só escala o erro",
    "O CRM não vai resolver seu problema de vendas",
    "A mentira do crescimento a qualquer custo",
    "Por que mais processo não significa mais resultado",
]

_fallback_index = 0


# ─── GOOGLE TRENDS ───────────────────────────────────────────────────────────

def buscar_trending_google() -> list[str]:
    """Busca trending searches no Google Trends Brasil."""
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl='pt-BR', tz=180)
        trending = pytrends.trending_searches(pn='brazil')
        topics = trending[0].tolist()[:20]
        print(f"[Trending] Google Trends: {len(topics)} tópicos")
        return topics
    except Exception as e:
        print(f"[Trending] Google Trends falhou: {e}")
        return []


# ─── ADAPTAR TRENDING AO DNA ─────────────────────────────────────────────────

def adaptar_trending_ao_dna(trending_topics: list[str]) -> dict:
    """Claude escolhe o melhor trending topic e adapta ao DNA da marca."""
    from dna import BRAND_DNA

    prompt = f"""Você é o estrategista de conteúdo de Julio Carvalho.

{BRAND_DNA}

TRENDING TOPICS DO MOMENTO (Brasil):
{chr(10).join(f"- {t}" for t in trending_topics[:15])}

TAREFA:
1. Escolha o trending topic com MAIOR potencial de engajamento para o público do Julio (CEOs, founders, donos de empresa)
2. ADAPTE o tema para o universo de negócios/sistemas/gestão do Julio
3. Escolha o pilar mais adequado dos 5 pilares acima

Retorne APENAS este JSON:
{{
  "trending_original": "o topic original escolhido",
  "tema_adaptado": "o tema adaptado pro Julio (frase direta, provocativa)",
  "pilar": "nome exato do pilar escolhido",
  "justificativa": "por que esse tema vai engajar (1 frase)"
}}"""

    if CLAUDE_BRIDGE_URL:
        try:
            r = httpx.post(CLAUDE_BRIDGE_URL, json={"prompt": prompt}, timeout=120)
            r.raise_for_status()
            data = r.json()
            raw = data.get("text") or data.get("result") or ""
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()
            return json.loads(raw)
        except Exception as e:
            print(f"[Trending] Claude bridge falhou: {e}")
    return None


# ─── TEMA FALLBACK ───────────────────────────────────────────────────────────

def tema_fallback() -> dict:
    """Retorna próximo tema da lista de fallback (rotação circular)."""
    global _fallback_index
    tema = TEMAS_FALLBACK[_fallback_index % len(TEMAS_FALLBACK)]
    _fallback_index += 1

    # Determinar pilar pelo índice
    pilares = [
        "O Sistema Invisível",
        "Arquitetura de Decisão",
        "Diagnóstico Cirúrgico",
        "Comportamento e Sistema",
        "Narrativas vs. Realidade",
    ]
    pilar = pilares[(_fallback_index - 1) // 4 % 5]

    return {
        "trending_original": None,
        "tema_adaptado": tema,
        "pilar": pilar,
        "justificativa": "Tema curado do banco de conteúdo",
    }


# ─── PIPELINE: BUSCAR TEMA ──────────────────────────────────────────────────

def buscar_tema() -> dict:
    """Pipeline completo: trending → adaptar → fallback."""
    # 1. Tentar Google Trends
    trending = buscar_trending_google()

    # 2. Se achou trending, adaptar ao DNA
    if trending:
        resultado = adaptar_trending_ao_dna(trending)
        if resultado:
            print(f"[Trending] Tema adaptado: {resultado.get('tema_adaptado')}")
            return resultado

    # 3. Fallback: banco de temas curados
    resultado = tema_fallback()
    print(f"[Trending] Fallback: {resultado.get('tema_adaptado')}")
    return resultado
