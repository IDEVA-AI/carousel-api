"""
pipeline.py — Orquestra o pipeline completo: trending → copy → render → caption → post → notify
Cada etapa é uma função independente. executar_pipeline() roda tudo em sequência.
"""
import base64
import json
import os
import io
import zipfile
from datetime import datetime
from pathlib import Path

import httpx

CLAUDE_BRIDGE_URL = os.environ.get("CLAUDE_BRIDGE_URL", "")

# ─── AVATAR DO INSTAGRAM ─────────────────────────────────────────────────────
_avatar_cache: str | None = None

def _get_avatar_url() -> str | None:
    """Busca foto de perfil do Instagram e converte pra base64."""
    global _avatar_cache
    if _avatar_cache:
        return _avatar_cache
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
    if not token:
        return None
    try:
        r = httpx.get(
            "https://graph.instagram.com/v22.0/me",
            params={"fields": "profile_picture_url", "access_token": token},
            timeout=10,
        )
        r.raise_for_status()
        pic_url = r.json().get("profile_picture_url")
        if not pic_url:
            return None
        # Baixar e converter pra base64
        img_r = httpx.get(pic_url, timeout=10, follow_redirects=True)
        img_r.raise_for_status()
        b64 = base64.b64encode(img_r.content).decode()
        _avatar_cache = f"data:image/jpeg;base64,{b64}"
        print(f"[Pipeline] Avatar carregado ({len(img_r.content)//1024}KB)")
        return _avatar_cache
    except Exception as e:
        print(f"[Pipeline] Erro ao carregar avatar: {e}")
        return None


# ─── ETAPA 1+2: TRENDING + TEMA ─────────────────────────────────────────────

def etapa_tema() -> dict:
    """Busca trending e gera tema adaptado ao DNA."""
    from trending import buscar_tema
    resultado = buscar_tema()
    print(f"[Pipeline] Tema: {resultado.get('tema_adaptado')} | Pilar: {resultado.get('pilar')}")
    return resultado


# ─── ETAPA 3: GERAR COPY ────────────────────────────────────────────────────

def etapa_copy(tema: str, pilar: str, num_slides: int = 7, estilo: str = "dark") -> dict:
    """Gera JSON do carrossel via Claude."""
    from generator import gerar_carrossel_completo
    carrossel = gerar_carrossel_completo(tema, num_slides, pilar, estilo=estilo)

    # Validar pilar — forçar um dos 5 válidos
    from trending import _validar_pilar
    pilar_gerado = carrossel.get("pilar", "")
    pilar_valido = _validar_pilar(pilar_gerado)
    if pilar_gerado != pilar_valido:
        print(f"[Pipeline] Pilar corrigido pós-geração: '{pilar_gerado}' → '{pilar_valido}'")
        carrossel["pilar"] = pilar_valido

    # Validar slides — garantir que nenhum saiu vazio
    slides = carrossel.get("slides", [])
    for i, s in enumerate(slides):
        tipo = s.get("tipo", "")
        headline = s.get("headline", s.get("quote", ""))
        if not headline and tipo not in ("dado",):
            print(f"[Pipeline] AVISO: Slide {i+1} ({tipo}) sem headline — preenchendo fallback")
            if tipo == "cta":
                s["headline"] = "Quer o diagnóstico?"
                s["sub"] = s.get("sub") or "Chama no DM."
            elif tipo == "cover":
                s["headline"] = carrossel.get("titulo", "Carrossel")
            else:
                s["headline"] = "..."

    print(f"[Pipeline] Copy gerado: {carrossel.get('titulo')} | {len(slides)} slides")
    return carrossel


# ─── ETAPA 4: RENDERIZAR ────────────────────────────────────────────────────

def etapa_render(carrossel: dict, estilo: str = "dark", visual: str = "editorial") -> tuple[list[bytes], list[str]]:
    """Renderiza slides em PNGs. Retorna (pngs_bytes, previews_base64)."""
    from slide_builder import build_all_slides
    from renderer import renderizar_e_empacotar

    avatar = _get_avatar_url()
    slides_html = build_all_slides(carrossel, avatar_url=avatar, theme=estilo, visual=visual)
    zip_bytes, previews = renderizar_e_empacotar(slides_html)

    # Extrair PNGs do ZIP
    pngs = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for name in sorted(zf.namelist()):
            pngs.append(zf.read(name))

    print(f"[Pipeline] Renderizado: {len(pngs)} slides")
    return pngs, previews


# ─── ETAPA 5: GERAR CAPTION ─────────────────────────────────────────────────

def etapa_caption(carrossel: dict) -> dict:
    """Gera legenda + hashtags via Claude."""
    from dna import BRAND_DNA

    titulo = carrossel.get("titulo", "")
    pilar = carrossel.get("pilar", "")
    slides = carrossel.get("slides", [])

    # Resumo dos slides pra contexto
    resumo = "\n".join(
        f"- Slide {s.get('index')}: [{s.get('tipo')}] {s.get('headline', s.get('quote', ''))}"
        for s in slides
    )

    prompt = f"""Você é o social media de Julio Carvalho.

{BRAND_DNA}

CARROSSEL GERADO:
Título: {titulo}
Pilar: {pilar}
Slides:
{resumo}

GERE a legenda do post no Instagram. Regras:
1. Máximo 2200 caracteres (limite do Instagram)
2. Primeira linha: gancho forte que complementa o carrossel (não repita o título)
3. Corpo: 3-5 linhas expandindo o tema — direto, cirúrgico, sem enrolação
4. CTA claro no final (salvar, compartilhar, comentar, ou DM)
5. Quebras de linha com espaço visual (use linhas vazias entre blocos)
6. 15-20 hashtags relevantes no FINAL (separadas por espaço)
7. Tom: mesmo do carrossel — direto, fala com o dono de empresa

Retorne APENAS este JSON:
{{
  "caption": "texto completo da legenda incluindo hashtags",
  "first_comment": "comentário opcional pra fixar (ou vazio)"
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
            result = json.loads(raw)
            print(f"[Pipeline] Caption gerada ({len(result.get('caption', ''))} chars)")
            return result
        except Exception as e:
            print(f"[Pipeline] Erro ao gerar caption: {e}")

    # Fallback simples
    return {
        "caption": f"{titulo}\n\n🔹 {pilar}\n\n#juliocarvalho #sistemas #gestao #ceo #negocios",
        "first_comment": "",
    }


# ─── ETAPA 6: POSTAR NO INSTAGRAM ───────────────────────────────────────────

def etapa_postar(pngs: list[bytes], caption: str, upload_base_url: str = "") -> dict:
    """
    Posta carousel no Instagram.
    Precisa de URLs públicas — faz upload temporário das imagens.
    """
    from instagram import postar_carousel

    # Instagram exige URLs públicas pras imagens.
    # Precisamos servir os PNGs temporariamente via um endpoint público.
    # Usamos o próprio carousel-api pra isso.
    if not upload_base_url:
        upload_base_url = os.environ.get("PUBLIC_BASE_URL", "https://carousel.onexos.com.br")

    # Salvar PNGs temporários e gerar URLs públicas
    temp_dir = Path("/tmp/carousel-temp")
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Instagram carousel só aceita aspect ratio entre 1:1 e 4:5. Nossos slides são 1080x1440 (3:4).
    # Crop centro vertical pra 1080x1350 (4:5) antes do upload.
    from PIL import Image
    import io as _io
    def _crop_para_ig(png: bytes) -> bytes:
        img = Image.open(_io.BytesIO(png))
        if img.size == (1080, 1350):
            return png
        if img.size[0] == 1080 and img.size[1] > 1350:
            top = (img.size[1] - 1350) // 2
            img = img.crop((0, top, 1080, top + 1350))
        buf = _io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=92)
        return buf.getvalue()

    image_urls = []
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    for i, png in enumerate(pngs):
        filename = f"post_{timestamp}_{i+1}.jpg"
        (temp_dir / filename).write_bytes(_crop_para_ig(png))
        image_urls.append(f"{upload_base_url}/api/temp/{filename}")

    print(f"[Pipeline] {len(image_urls)} imagens servidas pra upload")

    # Aguardar URLs ficarem acessíveis
    import time
    time.sleep(2)

    # Postar
    resultado = postar_carousel(image_urls, caption)

    # Limpar temp após postar
    for f in temp_dir.glob(f"post_{timestamp}_*"):
        f.unlink(missing_ok=True)

    return resultado


# ─── ETAPA 7: NOTIFICAR ─────────────────────────────────────────────────────

def etapa_notificar(resultado: dict, tema: str, erro: str | None = None):
    """Notifica via BRAINIAC/WhatsApp."""
    brainiac_url = os.environ.get("BRAINIAC_API_URL", "https://brainiac-api.onexos.com.br")
    whatsapp_number = os.environ.get("NOTIFY_WHATSAPP", "")

    if erro:
        msg = f"❌ Pipeline falhou\nTema: {tema}\nErro: {erro}"
    else:
        permalink = resultado.get("permalink", "post publicado")
        msg = f"✅ Carrossel postado!\nTema: {tema}\n{permalink}"

    print(f"[Pipeline] Notificação: {msg}")

    # Tentar via WhatsApp (BRAINIAC)
    if whatsapp_number:
        try:
            httpx.post(
                f"{brainiac_url}/api/whatsapp/send",
                json={"number": whatsapp_number, "message": msg},
                timeout=10,
            )
        except Exception as e:
            print(f"[Pipeline] Erro ao notificar WhatsApp: {e}")


# ─── REGISTRO DE POSTAGENS ───────────────────────────────────────────────────

_app_hist = Path("/app/historico")
POSTAGENS_DIR = _app_hist if _app_hist.exists() else Path.home() / "carousel-api" / "historico"
POSTAGENS_FILE = POSTAGENS_DIR / "postagens.json"

def _load_postagens() -> list:
    if POSTAGENS_FILE.exists():
        try:
            return json.loads(POSTAGENS_FILE.read_text())
        except Exception:
            pass
    return []

def _salvar_postagem(post: dict):
    posts = _load_postagens()
    posts.insert(0, post)
    posts = posts[:100]  # manter últimas 100
    POSTAGENS_FILE.write_text(json.dumps(posts, ensure_ascii=False, indent=2))
    print(f"[Pipeline] Postagem salva: {post.get('titulo', '')[:40]}")


# ─── PIPELINE COMPLETO ───────────────────────────────────────────────────────

TIPO_INSTRUCOES = {
    "provocacao": "Gere um carrossel de PROVOCAÇÃO. Headline agressiva, tensão imediata, confronta uma crença do lead.",
    "diagnostico": "Gere um carrossel de DIAGNÓSTICO. Liste 3 sintomas e revele a causa raiz que o lead não nomeou.",
    "framework": "Gere um carrossel de FRAMEWORK. Ensine um modelo/método com etapas claras. Use dados da base de frameworks.",
    "dado": "Gere um carrossel centrado em DADO/ESTATÍSTICA. Número impactante como protagonista. Use dados da base.",
    "mito_vs_realidade": "Gere um carrossel MITO vs REALIDADE. Desconstrua uma narrativa que o mercado vende. Use as opiniões fortes da base.",
    "historia": "Gere um carrossel de HISTÓRIA/CASE. Narre um case real (anonimizado) da base de cases.",
    "opiniao": "Gere um carrossel de OPINIÃO FORTE. Posicionamento polêmico dentro do nicho. Use as opiniões da base.",
    "checklist": "Gere um carrossel CHECKLIST/HOW-TO. Lista acionável com passos práticos.",
    "noticia": "Gere um carrossel de NOTÍCIA ADAPTADA. Adapte o trending topic ao universo do Julio.",
    "cta_direto": "Gere um carrossel de CTA DIRETO. Foco em conversão — DM, aplicação, diagnóstico gratuito.",
}

def executar_pipeline(
    num_slides: int = 7,
    estilo: str = "dark",
    visual: str = "editorial",
    tipo_conteudo: str = "auto",
) -> dict:
    """
    Executa o pipeline completo: trending → copy → render → caption → post → notify.
    Retorna status de cada etapa.
    """
    resultado = {
        "timestamp": datetime.now().isoformat(),
        "status": "running",
        "etapas": {},
    }
    tema_info = None
    carrossel = None
    pngs = None

    try:
        # 1+2. Tema
        tema_info = etapa_tema()
        resultado["etapas"]["tema"] = {"ok": True, "data": tema_info}

        tema = tema_info["tema_adaptado"]
        pilar = tema_info.get("pilar", "auto")

        # Injetar instrução do tipo de conteúdo no tema
        tipo_instrucao = TIPO_INSTRUCOES.get(tipo_conteudo, "")
        if tipo_instrucao:
            tema = f"{tema}\n\nINSTRUÇÃO DE TIPO: {tipo_instrucao}"

        # 3. Copy
        carrossel = etapa_copy(tema, pilar, num_slides, estilo)
        resultado["etapas"]["copy"] = {"ok": True, "titulo": carrossel.get("titulo")}

        # 4. Render
        pngs, previews = etapa_render(carrossel, estilo, visual)
        resultado["etapas"]["render"] = {"ok": True, "slides": len(pngs)}

        # 5. Caption
        caption_data = etapa_caption(carrossel)
        caption = caption_data.get("caption", "")
        resultado["etapas"]["caption"] = {"ok": True, "chars": len(caption)}

        # 6. Postar
        post_result = etapa_postar(pngs, caption)
        resultado["etapas"]["post"] = {"ok": True, **post_result}

        resultado["status"] = "success"
        resultado["permalink"] = post_result.get("permalink", "")

        # Salvar na lista de postagens
        _salvar_postagem({
            "timestamp": datetime.now().isoformat(),
            "titulo": carrossel.get("titulo", ""),
            "pilar": carrossel.get("pilar", ""),
            "tema": tema,
            "estilo": estilo,
            "visual": visual,
            "total_slides": len(pngs),
            "media_id": post_result.get("media_id", ""),
            "permalink": post_result.get("permalink", ""),
            "caption": caption[:200],
            "preview": previews[0] if previews else "",
            "status": "publicado",
        })

        # 7. Notificar sucesso
        etapa_notificar(post_result, tema)

    except Exception as e:
        resultado["status"] = "error"
        resultado["error"] = str(e)
        etapa_notificar({}, tema_info.get("tema_adaptado", "?") if tema_info else "?", erro=str(e))

    return resultado
