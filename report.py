"""
report.py — Gera reportes diários de atividade no Instagram.
Formato espelha template do mentor: FEED + STORIES + STORYAD + comentários.
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
    """Retorna tag legível do tipo de post."""
    mtype = m.get("media_type", "")
    mpt = m.get("media_product_type", "")
    if mpt == "REELS" or (mtype == "VIDEO" and "reel" in m.get("permalink", "")):
        return "reel"
    if mtype == "CAROUSEL_ALBUM":
        return "carrossel"
    if mtype == "VIDEO":
        return "vídeo"
    return "imagem"


def _short_caption(c: str | None, n: int = 60) -> str:
    if not c:
        return ""
    c = c.replace("\n", " ").strip()
    return c[:n] + ("…" if len(c) > n else "")


def gerar_report(
    data_alvo: str | None = None,
    dia: int | None = None,
    comentarios: str = "",
    stories_labels: list[str] | None = None,
    storyad: int | None = None,
) -> dict:
    """
    Gera report do dia em formato JSON + texto pronto pra copiar.

    Args:
        data_alvo: ISO date (YYYY-MM-DD). Default = hoje BR.
        dia: número do dia do desafio (ex: DIA 1, DIA 2). Se None, omite.
        comentarios: texto livre dos comentários (você escreve).
        stories_labels: lista opcional de rótulos pros stories ("bastidor", "caixinha"...) — ordem cronológica.
        storyad: número de story ads no dia (default 0; Graph API não retorna).
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

    # Stories ativos — só pega os do dia alvo (stories somem após 24h)
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

    # Aplica labels manuais se fornecidos
    if stories_labels:
        for i, s in enumerate(stories_dia):
            if i < len(stories_labels):
                s["label"] = stories_labels[i]

    storyad_count = storyad if storyad is not None else 0

    # Monta texto formato mentor
    dia_semana = DIAS_SEMANA[d.weekday()]
    data_fmt = d.strftime("%d/%m/%Y")
    header = f"REPORTE · DIA {dia} · {data_fmt} · {dia_semana}" if dia else f"REPORTE · {data_fmt} · {dia_semana}"

    linhas = [header, ""]

    # FEED
    linhas.append(f"→ FEED · {len(feed_dia)} {'post' if len(feed_dia) == 1 else 'posts'} publicados")
    for i, m in enumerate(feed_dia, 1):
        cap = m["caption_short"]
        suffix = f" — {cap}" if cap else ""
        linhas.append(f"{i}. {m['permalink']} ({m['tag']}){suffix}")
    linhas.append("")

    # STORIES
    linhas.append(f"→ STORIES · {len(stories_dia)} stories no dia")
    for i, s in enumerate(stories_dia, 1):
        label = s.get("label") or {"IMAGE": "imagem", "VIDEO": "vídeo"}.get(s["media_type"], s["media_type"].lower())
        linhas.append(f"{i}. {label}")
    linhas.append("")

    # STORYAD
    if storyad_count == 0:
        linhas.append("→ STORYAD · ZERO hoje")
    else:
        linhas.append(f"→ STORYAD · {storyad_count} no dia")
    linhas.append("")

    # Comentários
    linhas.append("Comentários:")
    if comentarios:
        linhas.append(comentarios)

    texto = "\n".join(linhas)

    return {
        "data": d.isoformat(),
        "dia_semana": dia_semana,
        "dia_desafio": dia,
        "feed": feed_dia,
        "stories": stories_dia,
        "storyad": storyad_count,
        "totais": {
            "feed": len(feed_dia),
            "reels": sum(1 for m in feed_dia if m["tag"] == "reel"),
            "carrosseis": sum(1 for m in feed_dia if m["tag"] == "carrossel"),
            "imagens": sum(1 for m in feed_dia if m["tag"] == "imagem"),
            "videos": sum(1 for m in feed_dia if m["tag"] == "vídeo"),
            "stories": len(stories_dia),
        },
        "texto": texto,
    }
