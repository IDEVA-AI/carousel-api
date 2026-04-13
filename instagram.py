"""
instagram.py — Publicação de carrosseis no Instagram via Graph API
Fluxo: upload imagens → criar carousel container → publicar
"""
import os
import time
import httpx

GRAPH_API = "https://graph.instagram.com/v22.0"
ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
ACCOUNT_ID = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")


def _headers():
    return {"Authorization": f"Bearer {ACCESS_TOKEN}"}


def _check_config():
    if not ACCESS_TOKEN:
        raise RuntimeError("INSTAGRAM_ACCESS_TOKEN não configurado")
    if not ACCOUNT_ID:
        raise RuntimeError("INSTAGRAM_BUSINESS_ACCOUNT_ID não configurado")


# ─── UPLOAD DE IMAGEM ────────────────────────────────────────────────────────

def _create_image_container(image_url: str, is_carousel_item: bool = True) -> str:
    """Cria container de imagem no Instagram. Retorna container ID."""
    params = {
        "image_url": image_url,
        "is_carousel_item": str(is_carousel_item).lower(),
        "access_token": ACCESS_TOKEN,
    }
    r = httpx.post(f"{GRAPH_API}/{ACCOUNT_ID}/media", data=params, timeout=30)
    if r.status_code >= 400:
        print(f"[Instagram] {r.status_code} body: {r.text[:500]}")
        print(f"[Instagram] image_url enviada: {image_url}")
    r.raise_for_status()
    container_id = r.json().get("id")
    if not container_id:
        raise RuntimeError(f"Falha ao criar container: {r.json()}")
    print(f"[Instagram] Container criado: {container_id}")
    return container_id


def _wait_container_ready(container_id: str, max_wait: int = 60) -> bool:
    """Aguarda container ficar pronto (status FINISHED)."""
    for _ in range(max_wait // 3):
        r = httpx.get(
            f"{GRAPH_API}/{container_id}",
            params={"fields": "status_code", "access_token": ACCESS_TOKEN},
            timeout=10,
        )
        status = r.json().get("status_code", "")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            raise RuntimeError(f"Container {container_id} com erro: {r.json()}")
        time.sleep(3)
    raise RuntimeError(f"Container {container_id} timeout após {max_wait}s")


# ─── CRIAR CAROUSEL ─────────────────────────────────────────────────────────

def _create_carousel_container(children_ids: list[str], caption: str) -> str:
    """Cria container de carousel com os filhos. Retorna carousel container ID."""
    params = {
        "media_type": "CAROUSEL",
        "children": ",".join(children_ids),
        "caption": caption,
        "access_token": ACCESS_TOKEN,
    }
    r = httpx.post(f"{GRAPH_API}/{ACCOUNT_ID}/media", data=params, timeout=30)
    r.raise_for_status()
    carousel_id = r.json().get("id")
    if not carousel_id:
        raise RuntimeError(f"Falha ao criar carousel: {r.json()}")
    print(f"[Instagram] Carousel container: {carousel_id}")
    return carousel_id


# ─── PUBLICAR ────────────────────────────────────────────────────────────────

def _publish(container_id: str) -> str:
    """Publica o container. Retorna media ID do post publicado."""
    params = {
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN,
    }
    r = httpx.post(f"{GRAPH_API}/{ACCOUNT_ID}/media_publish", data=params, timeout=30)
    r.raise_for_status()
    media_id = r.json().get("id")
    if not media_id:
        raise RuntimeError(f"Falha ao publicar: {r.json()}")
    print(f"[Instagram] Publicado! Media ID: {media_id}")
    return media_id


# ─── PIPELINE COMPLETO ───────────────────────────────────────────────────────

def postar_carousel(image_urls: list[str], caption: str, max_retries: int = 3) -> dict:
    """
    Posta carousel no Instagram.

    Args:
        image_urls: Lista de URLs públicas das imagens (2-10 imagens)
        caption: Texto do post (legenda + hashtags)
        max_retries: Tentativas em caso de erro

    Returns:
        {"media_id": str, "permalink": str}

    Nota: As imagens precisam ser URLs PÚBLICAS acessíveis pela Meta.
    Base64 não funciona — precisa fazer upload pra um storage público primeiro.
    """
    _check_config()

    if len(image_urls) < 2:
        raise ValueError("Carousel precisa de pelo menos 2 imagens")
    if len(image_urls) > 10:
        raise ValueError("Carousel aceita no máximo 10 imagens")

    for attempt in range(1, max_retries + 1):
        try:
            print(f"[Instagram] Tentativa {attempt}/{max_retries}")

            # 1. Criar containers para cada imagem
            children_ids = []
            for i, url in enumerate(image_urls):
                print(f"[Instagram] Upload imagem {i+1}/{len(image_urls)}...")
                container_id = _create_image_container(url)
                _wait_container_ready(container_id)
                children_ids.append(container_id)

            # 2. Criar carousel container
            carousel_id = _create_carousel_container(children_ids, caption)
            _wait_container_ready(carousel_id)

            # 3. Publicar
            media_id = _publish(carousel_id)

            # 4. Buscar permalink
            permalink = ""
            try:
                r = httpx.get(
                    f"{GRAPH_API}/{media_id}",
                    params={"fields": "permalink", "access_token": ACCESS_TOKEN},
                    timeout=10,
                )
                permalink = r.json().get("permalink", "")
            except Exception:
                pass

            return {"media_id": media_id, "permalink": permalink}

        except Exception as e:
            print(f"[Instagram] Erro na tentativa {attempt}: {e}")
            if attempt == max_retries:
                raise
            time.sleep(5 * attempt)  # backoff

    raise RuntimeError("Todas as tentativas falharam")
