"""server.py — FastAPI backend do gerador de carrosseis v2
Fluxo: POST /gerar (copy) → edição → POST /renderizar (PNG + histórico)
"""
import base64
import io
import json
import os
import shutil
import uuid
import zipfile
from datetime import datetime
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from generator import gerar_carrossel_completo, CLAUDE_BIN
from slide_builder import build_all_slides
from renderer import renderizar_e_empacotar

# ─── HISTORICO ────────────────────────────────────────────────────────────────
# Em Docker, usa /app/historico (volume). Local, usa ~/carousel-api/historico
_app_hist = Path("/app/historico")
HISTORICO_DIR = _app_hist if _app_hist.exists() else Path.home() / "carousel-api" / "historico"
HISTORICO_DIR.mkdir(parents=True, exist_ok=True)

# ─── BASE DE CONTEÚDO ─────────────────────────────────────────────────────────
CONTEUDO_FILE = HISTORICO_DIR / "base-conteudo.json"

def _load_conteudo() -> dict:
    if CONTEUDO_FILE.exists():
        return json.loads(CONTEUDO_FILE.read_text())
    # Default structure
    return {
        "frameworks": [],
        "cases": [],
        "dados": [],
        "opinioes": [],
        "sintomas": [],
    }

def _save_conteudo(data: dict):
    CONTEUDO_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))

# ─── APP ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="Gerador de Carrosseis — Julio Carvalho", version="2.0.0")

@app.on_event("startup")
def on_startup():
    from scheduler import start_scheduler
    start_scheduler()

PILARES = [
    "auto",
    "O Sistema Invisível",
    "Arquitetura de Decisão",
    "Diagnóstico Cirúrgico",
    "Comportamento e Sistema",
    "Narrativas vs. Realidade",
]

# ─── MODELS ───────────────────────────────────────────────────────────────────
class GerarRequest(BaseModel):
    tema: str = Field(..., min_length=3)
    slides: int = Field(7, ge=5, le=10)
    pilar: str = Field("auto")
    avatar_url: str | None = None
    estilo: str = Field("dark")

class RenderizarRequest(BaseModel):
    carrossel_json: dict
    avatar_url: str | None = None
    estilo: str = "dark"
    foto_url: str | None = None
    visual: str = "none"

# ─── ENDPOINTS ────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}

@app.get("/pilares")
def listar_pilares():
    return {"pilares": PILARES}

@app.post("/gerar")
async def gerar(req: GerarRequest):
    """Etapa 1: gera o copy (JSON) sem renderizar."""
    if not CLAUDE_BIN and not os.environ.get("CLAUDE_BRIDGE_URL") and not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="Claude Code CLI não encontrado e ANTHROPIC_API_KEY não configurada."
        )
    try:
        carrossel = gerar_carrossel_completo(req.tema, req.slides, req.pilar, estilo=req.estilo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar copy: {str(e)}")

    return {
        "titulo": carrossel.get("titulo", req.tema),
        "pilar": carrossel.get("pilar", req.pilar),
        "total_slides": len(carrossel.get("slides", [])),
        "unsplash_query": carrossel.get("unsplash_query", ""),
        "imagem_url": carrossel.get("imagem_url"),
        "carrossel_json": carrossel,
    }

@app.post("/renderizar")
async def renderizar(req: RenderizarRequest):
    """Etapa 2: renderiza o JSON, salva no histórico, retorna previews."""
    carrossel = req.carrossel_json

    try:
        # Injetar foto_url nos slides que já são cover_foto/hook_foto
        if req.foto_url:
            for s in carrossel.get("slides", []):
                if s.get("tipo") in ("cover_foto", "hook_foto"):
                    s["foto_url"] = req.foto_url

        # Visual "esquema": converter tipos pra versões visuais
        if req.visual == "esquema":
            visual_map = {"hook": "hook_visual", "dado": "dado_visual", "versus": "versus_visual", "diagnostico": "diagnostico_visual"}
            for s in carrossel.get("slides", []):
                original = s.get("tipo", "")
                if original in visual_map:
                    s["tipo"] = visual_map[original]

        slides_html = build_all_slides(carrossel, avatar_url=req.avatar_url, theme=req.estilo, visual=req.visual)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao montar slides: {str(e)}")

    try:
        zip_bytes, previews = renderizar_e_empacotar(slides_html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao renderizar: {str(e)}")

    # Salvar no histórico
    carousel_id = uuid.uuid4().hex[:8]
    hist_dir = HISTORICO_DIR / carousel_id
    hist_dir.mkdir(parents=True, exist_ok=True)

    titulo = carrossel.get("titulo", "Carrossel")
    pilar  = carrossel.get("pilar", "")

    meta = {
        "id": carousel_id,
        "titulo": titulo,
        "pilar": pilar,
        "timestamp": datetime.now().isoformat(),
        "total_slides": len(slides_html),
        "estilo": req.estilo,
        "carrossel_json": carrossel,
    }
    (hist_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))

    # Extrair PNGs do ZIP e salvar
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for i, name in enumerate(sorted(zf.namelist()), 1):
            (hist_dir / f"slide_{i}.png").write_bytes(zf.read(name))

    # Cache para /baixar
    _cache["ultimo"] = {"slides_html": slides_html, "titulo": titulo, "id": carousel_id}

    return {
        "id": carousel_id,
        "titulo": titulo,
        "pilar": pilar,
        "total_slides": len(slides_html),
        "previews": previews,
    }

@app.get("/historico")
def listar_historico():
    """Lista todos os carrosseis salvos, do mais recente ao mais antigo."""
    itens = []
    if not HISTORICO_DIR.exists():
        return {"historico": []}

    for hist_dir in sorted(HISTORICO_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        meta_file = hist_dir / "meta.json"
        if not meta_file.exists():
            continue
        try:
            meta = json.loads(meta_file.read_text())
            thumb = None
            slide1 = hist_dir / "slide_1.png"
            if slide1.exists():
                thumb = f"/historico/{meta['id']}/thumb"
            itens.append({
                "id":           meta["id"],
                "titulo":       meta.get("titulo", ""),
                "pilar":        meta.get("pilar", ""),
                "timestamp":    meta.get("timestamp", ""),
                "total_slides": meta.get("total_slides", 0),
                "thumbnail":    thumb,
            })
        except Exception:
            continue
    return {"historico": itens}

@app.get("/historico/{carousel_id}")
def get_historico(carousel_id: str):
    """Retorna um carrossel do histórico com todos os previews."""
    hist_dir = HISTORICO_DIR / carousel_id
    meta_file = hist_dir / "meta.json"
    if not meta_file.exists():
        raise HTTPException(status_code=404, detail="Carrossel não encontrado")

    meta = json.loads(meta_file.read_text())
    previews = []
    i = 1
    while True:
        png = hist_dir / f"slide_{i}.png"
        if not png.exists():
            break
        previews.append("data:image/png;base64," + base64.b64encode(png.read_bytes()).decode())
        i += 1

    return {**meta, "previews": previews}

@app.get("/historico/{carousel_id}/thumb")
def get_thumb(carousel_id: str):
    """Retorna o slide_1.png como imagem para thumbnail."""
    hist_dir = HISTORICO_DIR / carousel_id
    slide1 = hist_dir / "slide_1.png"
    if not slide1.exists():
        raise HTTPException(status_code=404, detail="Thumbnail não encontrada")
    return StreamingResponse(
        io.BytesIO(slide1.read_bytes()),
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400"},
    )

@app.delete("/historico/{carousel_id}")
def deletar_historico(carousel_id: str):
    hist_dir = HISTORICO_DIR / carousel_id
    if not hist_dir.exists():
        raise HTTPException(status_code=404, detail="Carrossel não encontrado")
    shutil.rmtree(hist_dir)
    return {"ok": True}

@app.get("/baixar")
def baixar_zip():
    cached = _cache.get("ultimo")
    if not cached:
        raise HTTPException(status_code=404, detail="Nenhum carrossel gerado ainda.")
    zip_bytes, _ = renderizar_e_empacotar(cached["slides_html"], prefixo="julio_carvalho")
    import unicodedata
    safe_title = unicodedata.normalize("NFKD", cached["titulo"]).encode("ascii", "ignore").decode()
    filename = safe_title.lower().replace(" ", "_")[:40] + ".zip"
    return StreamingResponse(
        io.BytesIO(zip_bytes), media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

_cache: dict = {}

# ─── PIPELINE AUTOMÁTICO ─────────────────────────────────────────────────────

@app.post("/pipeline/executar")
async def pipeline_executar():
    """Executa pipeline completo: trending → copy → render → caption → post → notify."""
    from pipeline import executar_pipeline
    try:
        resultado = executar_pipeline()
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline falhou: {str(e)}")

@app.post("/pipeline/preview")
async def pipeline_preview():
    """Executa etapas 1-5 sem postar — retorna preview do carrossel + caption."""
    from pipeline import etapa_tema, etapa_copy, etapa_render, etapa_caption
    try:
        tema_info = etapa_tema()
        tema = tema_info["tema_adaptado"]
        pilar = tema_info.get("pilar", "auto")

        carrossel = etapa_copy(tema, pilar)
        pngs, previews = etapa_render(carrossel)
        caption_data = etapa_caption(carrossel)

        return {
            "tema": tema_info,
            "titulo": carrossel.get("titulo"),
            "pilar": carrossel.get("pilar"),
            "total_slides": len(previews),
            "previews": previews,
            "caption": caption_data.get("caption", ""),
            "carrossel_json": carrossel,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview falhou: {str(e)}")

# ─── INSTAGRAM INFO ──────────────────────────────────────────────────────────

@app.get("/api/instagram/profile")
def instagram_profile():
    """Retorna perfil do Instagram conectado."""
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
    if not token:
        raise HTTPException(status_code=400, detail="Instagram não conectado")
    try:
        r = httpx.get(
            "https://graph.instagram.com/v22.0/me",
            params={"fields": "id,username,account_type,media_count,profile_picture_url,biography,followers_count,follows_count,website", "access_token": token},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/instagram/media")
def instagram_media(limit: int = 10):
    """Retorna posts recentes do Instagram."""
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
    if not token:
        raise HTTPException(status_code=400, detail="Instagram não conectado")
    try:
        r = httpx.get(
            "https://graph.instagram.com/v22.0/me/media",
            params={"fields": "id,caption,media_type,timestamp,like_count,comments_count,permalink,thumbnail_url,media_url", "limit": limit, "access_token": token},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/instagram/quota")
def instagram_quota():
    """Retorna quota de publicação do Instagram."""
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
    account_id = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
    if not token or not account_id:
        raise HTTPException(status_code=400, detail="Instagram não conectado")
    try:
        r = httpx.get(
            f"https://graph.instagram.com/v22.0/{account_id}/content_publishing_limit",
            params={"fields": "config,quota_usage", "access_token": token},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json().get("data", [{}])
        return data[0] if data else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── BASE DE CONTEÚDO API ─────────────────────────────────────────────────────

# ─── AUTOMATION: WEBHOOK ──────────────────────────────────────────────────────

@app.get("/webhook/instagram")
async def webhook_verify(request: Request):
    """Verificação do webhook pelo Meta."""
    from automation.webhook import verify_webhook
    params = request.query_params
    result = verify_webhook(
        params.get("hub.mode", ""),
        params.get("hub.verify_token", ""),
        params.get("hub.challenge", ""),
    )
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(result)

@app.post("/webhook/instagram")
async def webhook_receive(request: Request):
    """Recebe eventos de webhook do Instagram."""
    from automation.webhook import handle_webhook
    from automation.comment_handler import process_comment
    result = await handle_webhook(request)
    # Processar cada evento de comentário
    for event in result.get("events", []):
        if event["type"] == "comment":
            process_comment(event)
    return {"ok": True}

# ─── AUTOMATION: KEYWORDS ────────────────────────────────────────────────────

@app.get("/api/automation/keywords")
def get_keywords():
    from automation.comment_handler import load_keywords
    return {"keywords": load_keywords()}

@app.post("/api/automation/keywords")
def set_keywords(payload: dict):
    from automation.comment_handler import save_keywords
    save_keywords(payload.get("keywords", []))
    return {"ok": True}

@app.get("/api/automation/logs")
def get_automation_logs():
    from automation.comment_handler import load_logs
    return {"logs": load_logs()}

# ─── AUTOMATION: DM SEQUENCES ────────────────────────────────────────────────

@app.get("/api/dm/sequences")
def get_dm_sequences():
    from automation.dm_sequences import load_sequences
    return {"sequences": load_sequences()}

@app.post("/api/dm/sequences")
def set_dm_sequences(payload: dict):
    from automation.dm_sequences import save_sequences
    save_sequences(payload.get("sequences", []))
    return {"ok": True}

@app.get("/api/dm/active")
def get_active_dms():
    from automation.dm_sequences import load_active_dms
    return {"active": load_active_dms()}

@app.post("/api/dm/send")
def send_dm_manual(payload: dict):
    from automation.dm_sequences import send_dm
    ok = send_dm(payload.get("user_id", ""), payload.get("message", ""))
    return {"ok": ok}

# ─── AUTOMATION: LEADS ────────────────────────────────────────────────────────

@app.get("/api/leads")
def get_leads():
    from automation.lead_scoring import get_all_leads
    return {"leads": get_all_leads()}

@app.get("/api/leads/quentes")
def get_hot_leads():
    from automation.lead_scoring import get_hot_leads
    return {"leads": get_hot_leads()}

# ─── AUTOMATION: ANALYTICS ────────────────────────────────────────────────────

@app.get("/api/analytics")
def get_analytics():
    from automation.analytics import get_analytics
    return get_analytics()

@app.post("/api/analytics/snapshot")
def take_snapshot():
    from automation.analytics import save_snapshot
    return save_snapshot()

# ─── POSTAGENS API ───────────────────────────────────────────────────────────

@app.get("/api/postagens")
def get_postagens():
    from pipeline import _load_postagens
    return {"postagens": _load_postagens()}

# ─── SCHEDULER API ───────────────────────────────────────────────────────────

@app.get("/api/scheduler")
def scheduler_status():
    from scheduler import get_status
    return get_status()

@app.post("/api/scheduler/config")
def scheduler_update(config: dict):
    from scheduler import save_config, start_scheduler
    save_config(config)
    start_scheduler()
    return {"ok": True}

@app.post("/api/scheduler/start")
def scheduler_start():
    from scheduler import load_config, save_config, start_scheduler
    config = load_config()
    config["ativo"] = True
    save_config(config)
    start_scheduler()
    return {"ok": True}

@app.post("/api/scheduler/stop")
def scheduler_stop():
    from scheduler import load_config, save_config, stop_scheduler
    config = load_config()
    config["ativo"] = False
    save_config(config)
    stop_scheduler()
    return {"ok": True}

# ─── DNA API ─────────────────────────────────────────────────────────────────

@app.get("/api/dna")
def get_dna():
    """Retorna todos os módulos do DNA."""
    from dna.identidade import IDENTIDADE
    from dna.avatar import AVATAR
    from dna.pilares import PILARES
    from dna.metodo import METODO
    from dna.credenciais import CREDENCIAIS
    from dna.tom import TOM
    return {
        "identidade": IDENTIDADE.strip(),
        "avatar": AVATAR.strip(),
        "pilares": PILARES.strip(),
        "metodo": METODO.strip(),
        "credenciais": CREDENCIAIS.strip(),
        "tom": TOM.strip(),
    }

# ─── BASE DE CONTEÚDO API ─────────────────────────────────────────────────────

@app.get("/api/conteudo")
def get_conteudo():
    return _load_conteudo()

@app.post("/api/conteudo/importar")
def importar_conteudo(payload: dict):
    """Importa base completa (substitui tudo)."""
    _save_conteudo(payload)
    totals = {k: len(v) for k, v in payload.items() if isinstance(v, list)}
    return {"ok": True, "totals": totals}

@app.get("/api/conteudo/{tipo}")
def get_conteudo_tipo(tipo: str):
    data = _load_conteudo()
    if tipo not in data:
        raise HTTPException(status_code=404, detail=f"Tipo '{tipo}' nao encontrado")
    return {"tipo": tipo, "items": data[tipo]}

@app.post("/api/conteudo/{tipo}")
def add_conteudo_item(tipo: str, item: dict):
    data = _load_conteudo()
    if tipo not in data:
        data[tipo] = []
    data[tipo].append(item)
    _save_conteudo(data)
    return {"ok": True, "total": len(data[tipo])}

@app.put("/api/conteudo/{tipo}/{index}")
def update_conteudo_item(tipo: str, index: int, item: dict):
    data = _load_conteudo()
    if tipo not in data or index >= len(data[tipo]):
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    data[tipo][index] = item
    _save_conteudo(data)
    return {"ok": True}

@app.delete("/api/conteudo/{tipo}/{index}")
def delete_conteudo_item(tipo: str, index: int):
    data = _load_conteudo()
    if tipo not in data or index >= len(data[tipo]):
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    data[tipo].pop(index)
    _save_conteudo(data)
    return {"ok": True, "total": len(data[tipo])}

# ─── TEMP IMAGE SERVING (para Instagram upload) ─────────────────────────────
TEMP_DIR = Path("/tmp/carousel-temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

from fastapi.responses import FileResponse

@app.get("/api/temp/{filename}")
def serve_temp(filename: str):
    """Serve imagem temporária pra upload no Instagram."""
    filepath = TEMP_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Arquivo nao encontrado")
    return FileResponse(filepath, media_type="image/png")

# ─── STATIC FILES ─────────────────────────────────────────────────────────────
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8765)), reload=True)