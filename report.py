"""
report.py — Gera reportes diários de atividade no Instagram.
Formato oficial DESAFIO DOMINACAO (d'demarco):
  DIA X · FEED · STORIES · STORYAD · CASE + pontuação automática.
"""
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx

GRAPH = "https://graph.instagram.com/v22.0"
BR_TZ = ZoneInfo("America/Sao_Paulo")
DIAS_SEMANA = {
    0: "segunda", 1: "terça", 2: "quarta", 3: "quinta",
    4: "sexta", 5: "sábado", 6: "domingo",
}

# Pontuação oficial (PDF DESAFIO DOMINACAO)
PONTOS = {
    "feed_primeiro": 10,
    "feed_extra": 2,
    "stories_bloco": 10,         # 4-7 stories no dia
    "story_com_oferta": 2,       # qualquer story com CTA/oferta no bloco
    "storyad": 8,                # por storyad testado
    "case_normal": 15,
    "case_com_venda": 30,
}


def _token() -> str:
    t = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
    if not t:
        raise RuntimeError("INSTAGRAM_ACCESS_TOKEN não configurado")
    return t


def _account_id() -> str:
    a = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
    if not a:
        raise RuntimeError("INSTAGRAM_BUSINESS_ACCOUNT_ID não configurado")
    return a


def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(BR_TZ)


def _fetch_feed(limit: int = 50) -> list[dict]:
    r = httpx.get(
        f"{GRAPH}/{_account_id()}/media",
        params={
            "fields": "id,media_type,media_product_type,timestamp,permalink,caption,like_count,comments_count",
            "limit": limit,
            "access_token": _token(),
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json().get("data", [])


def _fetch_stories() -> list[dict]:
    r = httpx.get(
        f"{GRAPH}/{_account_id()}/stories",
        params={
            "fields": "id,media_type,timestamp,permalink",
            "access_token": _token(),
        },
        timeout=15,
    )
    if r.status_code >= 400:
        return []
    return r.json().get("data", [])


def _classify_feed_post(m: dict) -> str:
    """Tag do tipo de post (carrossel, reel, single, vídeo)."""
    mtype = m.get("media_type", "")
    mpt = m.get("media_product_type", "")
    if mpt == "REELS" or (mtype == "VIDEO" and "reel" in m.get("permalink", "")):
        return "REEL"
    if mtype == "CAROUSEL_ALBUM":
        return "CARROSSEL"
    if mtype == "VIDEO":
        return "VÍDEO"
    return "SINGLE"


def _short_caption(c: str | None, n: int = 80) -> str:
    if not c:
        return ""
    c = c.replace("\n", " ").strip()
    return c[:n] + ("…" if len(c) > n else "")


def _calcular_pontos(feed_count: int, stories_count: int, story_com_oferta: bool,
                     storyad_count: int, case: dict | None) -> dict:
    """
    Pontuação oficial DESAFIO DOMINACAO.
    Retorna breakdown + total.
    """
    breakdown = []
    total = 0

    # Feed: 10 pelo 1º + 2 por cada extra (até 4 contam)
    if feed_count >= 1:
        total += PONTOS["feed_primeiro"]
        breakdown.append(f"+{PONTOS['feed_primeiro']} · 1º post feed")
        extras = min(feed_count - 1, 3)  # máx 4 posts no total
        if extras > 0:
            pts = extras * PONTOS["feed_extra"]
            total += pts
            breakdown.append(f"+{pts} · {extras} post(s) extra(s)")

    # Stories: bloco 4-7
    if 4 <= stories_count <= 7:
        total += PONTOS["stories_bloco"]
        breakdown.append(f"+{PONTOS['stories_bloco']} · bloco de stories ({stories_count})")
    elif stories_count >= 1:
        breakdown.append(f"+0 · {stories_count} story(s) — fora do bloco 4-7")

    # Story com oferta
    if story_com_oferta and stories_count >= 4:
        total += PONTOS["story_com_oferta"]
        breakdown.append(f"+{PONTOS['story_com_oferta']} · story com oferta")

    # StoryAds
    if storyad_count > 0:
        pts = storyad_count * PONTOS["storyad"]
        total += pts
        breakdown.append(f"+{pts} · {storyad_count} storyad(s)")

    # Case
    if case:
        com_venda = case.get("venda") or case.get("valor")
        pts = PONTOS["case_com_venda"] if com_venda else PONTOS["case_normal"]
        total += pts
        rotulo = "case com venda" if com_venda else "case normal"
        breakdown.append(f"+{pts} · {rotulo}")

    return {"total": total, "breakdown": breakdown}


def gerar_report(
    data_alvo: str | None = None,
    dia: int | None = None,
    comentarios: str = "",
    stories_labels: list[str] | None = None,
    descricoes_feed: list[str] | None = None,
    story_com_oferta: bool = False,
    storyad: int | None = None,
    storyad_detalhe: dict | None = None,
    case: dict | None = None,
) -> dict:
    """
    Gera report do dia no formato oficial DESAFIO DOMINACAO.

    Args:
        data_alvo: ISO date (YYYY-MM-DD). Default = hoje BR.
        dia: número do dia do desafio (1-30).
        comentarios: texto livre dos comentários (opcional).
        stories_labels: rótulos cronológicos pros stories (ex: "BASTIDOR", "ENQUETE", "CAIXINHA").
        descricoes_feed: descrições curtas paralelas aos posts do feed (ex: "Polarização — Você não é desorganizado").
        story_com_oferta: True se algum story do bloco teve CTA/oferta (+2 pts).
        storyad: quantidade de storyads testados no dia.
        storyad_detalhe: {"formato": "foto|vídeo", "gancho": "..."} (opcional).
        case: {"descricao": "...", "venda": bool, "valor": float, "link": "..."} (opcional).
    """
    if data_alvo:
        d = datetime.fromisoformat(data_alvo).date()
    else:
        d = datetime.now(BR_TZ).date()

    inicio = datetime.combine(d, datetime.min.time(), tzinfo=BR_TZ)
    fim = inicio + timedelta(days=1)

    # Feed do dia
    feed_all = _fetch_feed()
    feed_dia = []
    for m in feed_all:
        ts = _parse_iso(m["timestamp"])
        if inicio <= ts < fim:
            feed_dia.append({
                **m,
                "tag": _classify_feed_post(m),
                "ts_br": ts.strftime("%H:%M"),
                "caption_short": _short_caption(m.get("caption")),
            })
    feed_dia.sort(key=lambda x: x["timestamp"])

    # Stories do dia
    stories_all = _fetch_stories()
    stories_dia = []
    for s in stories_all:
        ts = _parse_iso(s["timestamp"])
        if inicio <= ts < fim:
            stories_dia.append({
                **s,
                "ts_br": ts.strftime("%H:%M"),
            })
    stories_dia.sort(key=lambda x: x["timestamp"])

    # Labels customizados
    if stories_labels:
        for i, s in enumerate(stories_dia):
            if i < len(stories_labels):
                s["label"] = stories_labels[i]
    if descricoes_feed:
        for i, m in enumerate(feed_dia):
            if i < len(descricoes_feed):
                m["descricao"] = descricoes_feed[i]

    storyad_count = storyad if storyad is not None else 0

    # Pontuação
    pontos = _calcular_pontos(
        feed_count=len(feed_dia),
        stories_count=len(stories_dia),
        story_com_oferta=story_com_oferta,
        storyad_count=storyad_count,
        case=case,
    )

    # ─── Texto formato DOUG (mentor d'demarco) ───
    linhas = []
    dia_semana = DIAS_SEMANA[d.weekday()]
    data_fmt = d.strftime("%d/%m/%Y")
    header = f"REPORTE · DIA {dia} · {data_fmt} · {dia_semana}" if dia else f"REPORTE · {data_fmt} · {dia_semana}"
    linhas.append(header)

    # FEED
    linhas.append(f"→ FEED · {len(feed_dia)} {'post publicado' if len(feed_dia) == 1 else 'posts publicados'}")
    for i, m in enumerate(feed_dia, 1):
        desc = m.get("descricao") or m["caption_short"] or m["tag"].lower()
        # Doug usa "URL (tipo - descrição curta)" em uma linha só
        linhas.append(f"{i}. {m['permalink']} ({desc})")

    # STORIES
    linhas.append(f"→ STORIES · {len(stories_dia)} stories no dia")
    for s in stories_dia:
        label = s.get("label") or {"IMAGE": "imagem", "VIDEO": "vídeo"}.get(s["media_type"], s["media_type"].lower())
        linhas.append(label)

    # STORYAD
    if storyad_count == 0:
        linhas.append("→ STORYAD · ZERO hoje")
    else:
        det = ""
        if storyad_detalhe:
            f = storyad_detalhe.get("formato", "")
            g = storyad_detalhe.get("gancho", "")
            partes = [p for p in [f, g] if p]
            if partes:
                det = f" ({', '.join(partes)})"
        linhas.append(f"→ STORYAD · {storyad_count} no dia{det}")

    # CASE (Doug só inclui se houver — sem linha "sem case")
    if case:
        desc = case.get("descricao", "vitória do dia")
        if case.get("venda") or case.get("valor"):
            valor = case.get("valor")
            valor_str = f" — R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if valor else ""
            linhas.append(f"→ CASE com venda · {desc}{valor_str}")
            if case.get("link"):
                linhas.append(f"Link: {case['link']}")
        else:
            linhas.append(f"→ CASE · {desc}")

    # Comentários
    if comentarios:
        linhas.append(f"Comentários: {comentarios}")

    texto = "\n".join(linhas)

    return {
        "data": d.isoformat(),
        "dia_semana": DIAS_SEMANA[d.weekday()],
        "dia_desafio": dia,
        "feed": feed_dia,
        "stories": stories_dia,
        "storyad": storyad_count,
        "case": case,
        "pontuacao": pontos,
        "totais": {
            "feed": len(feed_dia),
            "reels": sum(1 for m in feed_dia if m["tag"] == "REEL"),
            "carrosseis": sum(1 for m in feed_dia if m["tag"] == "CARROSSEL"),
            "singles": sum(1 for m in feed_dia if m["tag"] == "SINGLE"),
            "videos": sum(1 for m in feed_dia if m["tag"] == "VÍDEO"),
            "stories": len(stories_dia),
        },
        "texto": texto,
    }
