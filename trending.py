"""
trending.py — Detecção de tendências + geração de temas
Busca trending topics e adapta ao DNA da marca via Claude.
Verifica histórico pra evitar repetição.
"""
import os
import json
from pathlib import Path
import httpx

CLAUDE_BRIDGE_URL = os.environ.get("CLAUDE_BRIDGE_URL", "")

# ─── PILARES VÁLIDOS ─────────────────────────────────────────────────────────
PILARES_VALIDOS = [
    "Diagnostico Cognitivo",
    "Operacao Cognitiva",
    "Conteudo com Profundidade",
    "Transferencia de Criterio",
    "Escala sem Diluir Autoria",
    "Metodo Vivo",
    "Oferta Consultiva",
]

# ─── HISTÓRICO DE TEMAS JÁ USADOS ───────────────────────────────────────────
_app_hist = Path("/app/historico")
_hist_dir = _app_hist if _app_hist.exists() else Path.home() / "carousel-api" / "historico"

def _carregar_temas_usados() -> list[str]:
    """Carrega títulos dos carrosseis já gerados pra evitar repetição."""
    titulos = []
    # Do histórico de carrosseis
    if _hist_dir.exists():
        for d in _hist_dir.iterdir():
            meta = d / "meta.json"
            if meta.exists():
                try:
                    m = json.loads(meta.read_text())
                    titulo = m.get("titulo", "")
                    if titulo:
                        titulos.append(titulo.lower())
                except Exception:
                    pass
    # Do log de postagens
    postagens_file = _hist_dir / "postagens.json"
    if postagens_file.exists():
        try:
            posts = json.loads(postagens_file.read_text())
            for p in posts:
                t = p.get("titulo", "")
                if t:
                    titulos.append(t.lower())
        except Exception:
            pass
    # Do log do scheduler
    log_file = _hist_dir / "schedule-log.json"
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text())
            for l in logs:
                t = l.get("titulo", "")
                if t:
                    titulos.append(t.lower())
        except Exception:
            pass
    return list(set(titulos))


def _tema_ja_usado(tema: str, usados: list[str]) -> bool:
    """Verifica se um tema é parecido demais com algum já usado."""
    tema_lower = tema.lower()
    for usado in usados:
        # Match exato
        if tema_lower == usado:
            return True
        # Palavras em comum > 60%
        palavras_tema = set(tema_lower.split())
        palavras_usado = set(usado.split())
        if len(palavras_tema) > 2 and len(palavras_usado) > 2:
            comum = palavras_tema & palavras_usado
            similaridade = len(comum) / max(len(palavras_tema), len(palavras_usado))
            if similaridade > 0.6:
                return True
    return False


def _validar_pilar(pilar: str) -> str:
    """Valida e corrige o pilar — se nao e dos 7, escolhe o mais proximo."""
    if pilar in PILARES_VALIDOS:
        return pilar
    # Tentar match parcial
    pilar_lower = pilar.lower()
    for p in PILARES_VALIDOS:
        if p.lower() in pilar_lower or pilar_lower in p.lower():
            print(f"[Trending] Pilar corrigido: '{pilar}' → '{p}'")
            return p
    # Match por palavras-chave
    keywords_map = {
        "Diagnostico Cognitivo": ["diagnostico", "sintoma", "problema", "cabeca", "gargalo"],
        "Operacao Cognitiva": ["operacao", "sistema", "vivo", "infraestrutura", "contexto"],
        "Conteudo com Profundidade": ["conteudo", "post", "social", "pauta", "profundidade"],
        "Transferencia de Criterio": ["criterio", "delegar", "equipe", "briefing", "decisao"],
        "Escala sem Diluir Autoria": ["escala", "autoria", "essencia", "marca", "identidade"],
        "Metodo Vivo": ["metodo", "notion", "documento", "conhecimento", "repertorio"],
        "Oferta Consultiva": ["oferta", "diagnostico", "consultoria", "venda", "convite"],
    }
    best_match = PILARES_VALIDOS[0]
    best_score = 0
    for p, keywords in keywords_map.items():
        score = sum(1 for kw in keywords if kw in pilar_lower)
        if score > best_score:
            best_score = score
            best_match = p
    print(f"[Trending] Pilar corrigido: '{pilar}' → '{best_match}'")
    return best_match

# ─── TEMAS FALLBACK (rotacao pelos 7 pilares) ────────────────────────────────
TEMAS_FALLBACK = [
    # Pilar 1: Diagnostico Cognitivo
    "Sua cabeca virou o gargalo mais caro do negocio",
    "Voce nao e centralizadora, sua inteligencia ainda nao virou sistema",
    "O problema nao e falta de equipe, e falta de contexto vivo",
    # Pilar 2: Operacao Cognitiva
    "Sua operacao pode pensar junto com voce",
    "O proximo nivel da sua autoridade e virar infraestrutura",
    "Como tirar criterio da cabeca e colocar na rotina",
    # Pilar 3: Conteudo com Profundidade
    "Seu conteudo fica generico quando sai da sua mao?",
    "Voce nao precisa de mais uma social media",
    "Conteudo bom nasce da logica, nao da pauta",
    # Pilar 4: Transferencia de Criterio
    "Delegar sem criterio cria outro tipo de prisao",
    "Sua equipe nao precisa copiar voce, precisa acessar seus criterios",
    "Briefing nao substitui raciocinio",
    # Pilar 5: Escala sem Diluir Autoria
    "Escalar nao precisa custar a alma da sua marca",
    "Sua mente nao precisa ser engessada para ser compartilhada",
    "Multiplicar presenca sem perder identidade",
    # Pilar 6: Metodo Vivo
    "O Notion nao resolve uma mente nao traduzida",
    "Seu metodo nao esta desorganizado, ele esta vivo",
    "Documento morto nao carrega nuance",
    # Pilar 7: Oferta Consultiva
    "Transforme sua cabeca no sistema operacional da marca",
    "Mapeamos sua logica autoral e traduzimos em operacao",
    "Uma estrutura para conteudo, vendas, equipe e entrega pensarem com voce",
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

    temas_usados = _carregar_temas_usados()
    usados_str = "\n".join(f"- {t}" for t in temas_usados[-20:]) if temas_usados else "(nenhum ainda)"

    prompt = f"""Você é o estrategista de conteúdo de Julio Carvalho.

{BRAND_DNA}

TRENDING TOPICS DO MOMENTO (Brasil):
{chr(10).join(f"- {t}" for t in trending_topics[:15])}

TEMAS JÁ USADOS RECENTEMENTE (NÃO REPITA nenhum desses, nem parecidos):
{usados_str}

PILARES VALIDOS (use EXATAMENTE um desses nomes):
- Diagnostico Cognitivo
- Operacao Cognitiva
- Conteudo com Profundidade
- Transferencia de Criterio
- Escala sem Diluir Autoria
- Metodo Vivo
- Oferta Consultiva

TAREFA:
1. Escolha o trending topic com MAIOR potencial de engajamento para experts e mentoras autorais
2. ADAPTE o tema pro universo de operacao cognitiva, conteudo, vendas, equipe, entrega e escala sem diluir essencia
3. O tema DEVE ser DIFERENTE de todos os já usados acima
4. Use EXATAMENTE um dos 7 pilares listados

Retorne APENAS este JSON:
{{
  "trending_original": "o topic original escolhido",
  "tema_adaptado": "o tema adaptado pro Julio (frase direta, provocativa, DIFERENTE dos já usados)",
  "pilar": "EXATAMENTE um dos 7 pilares acima",
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
    pilares = PILARES_VALIDOS
    pilar = pilares[(_fallback_index - 1) // 3 % len(pilares)]

    return {
        "trending_original": None,
        "tema_adaptado": tema,
        "pilar": pilar,
        "justificativa": "Tema curado do banco de conteúdo",
    }


# ─── PIPELINE: BUSCAR TEMA ──────────────────────────────────────────────────

def buscar_tema() -> dict:
    """Pipeline completo: trending → adaptar → validar → fallback."""
    temas_usados = _carregar_temas_usados()
    print(f"[Trending] {len(temas_usados)} temas já usados no histórico")

    # 1. Tentar Google Trends
    trending = buscar_trending_google()

    # 2. Se achou trending, adaptar ao DNA
    if trending:
        resultado = adaptar_trending_ao_dna(trending)
        if resultado:
            tema = resultado.get("tema_adaptado", "")
            # Validar pilar
            resultado["pilar"] = _validar_pilar(resultado.get("pilar", ""))
            # Verificar repetição
            if _tema_ja_usado(tema, temas_usados):
                print(f"[Trending] Tema repetido, descartando: {tema}")
            else:
                print(f"[Trending] Tema adaptado: {tema}")
                return resultado

    # 3. Fallback: banco de temas curados (evitar repetidos)
    for _ in range(len(TEMAS_FALLBACK)):
        resultado = tema_fallback()
        tema = resultado.get("tema_adaptado", "")
        resultado["pilar"] = _validar_pilar(resultado.get("pilar", ""))
        if not _tema_ja_usado(tema, temas_usados):
            print(f"[Trending] Fallback: {tema}")
            return resultado
        print(f"[Trending] Fallback repetido, pulando: {tema}")

    # 4. Se tudo repetiu, usar o fallback mesmo (melhor que nada)
    resultado = tema_fallback()
    resultado["pilar"] = _validar_pilar(resultado.get("pilar", ""))
    print(f"[Trending] Todos repetidos, usando: {resultado.get('tema_adaptado')}")
    return resultado
