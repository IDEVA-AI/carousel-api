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

# ─── APP ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="Gerador de Carrosseis — Julio Carvalho", version="2.0.0")

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

# ─── STATIC FILES ─────────────────────────────────────────────────────────────
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8765)), reload=True)