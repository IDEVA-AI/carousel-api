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


# ─── POST ÚNICO (single image) ──────────────────────────────────────────────

def postar_imagem(image_url: str, caption: str = "", max_retries: int = 3) -> dict:
    """
    Posta uma única imagem no feed do Instagram (não carousel).

    Args:
        image_url: URL pública da imagem (jpg/png, 1080x1080 ou 1080x1350 ou 1080x1440)
        caption: Texto + hashtags
        max_retries: Tentativas em caso de erro

    Returns:
        {"media_id": str, "permalink": str}
    """
    _check_config()

    for attempt in range(1, max_retries + 1):
        try:
            print(f"[Instagram/Imagem] Tentativa {attempt}/{max_retries}")

            r = httpx.post(
                f"{GRAPH_API}/{ACCOUNT_ID}/media",
                data={
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": ACCESS_TOKEN,
                },
                timeout=30,
            )
            if r.status_code >= 400:
                print(f"[Instagram/Imagem] {r.status_code} body: {r.text[:500]}")
            r.raise_for_status()
            container_id = r.json().get("id")
            if not container_id:
                raise RuntimeError(f"Falha ao criar container: {r.json()}")
            print(f"[Instagram/Imagem] Container criado: {container_id}")

            _wait_container_ready(container_id)
            media_id = _publish(container_id)

            permalink = ""
            try:
                rp = httpx.get(
                    f"{GRAPH_API}/{media_id}",
                    params={"fields": "permalink", "access_token": ACCESS_TOKEN},
                    timeout=10,
                )
                permalink = rp.json().get("permalink", "")
            except Exception:
                pass

            return {"media_id": media_id, "permalink": permalink}

        except Exception as e:
            print(f"[Instagram/Imagem] Erro na tentativa {attempt}: {e}")
            if attempt == max_retries:
                raise
            time.sleep(5 * attempt)

    raise RuntimeError("Todas as tentativas falharam")


# ─── REELS ──────────────────────────────────────────────────────────────────

def postar_reel(
    video_url: str,
    caption: str = "",
    cover_url: str | None = None,
    share_to_feed: bool = True,
    max_retries: int = 3,
) -> dict:
    """
    Posta um Reel no Instagram.

    Args:
        video_url: URL pública do MP4 (9:16, até 90s, H.264, AAC)
        caption: Texto + hashtags
        cover_url: URL pública da thumbnail (opcional)
        share_to_feed: Se True, aparece também no grid do feed
        max_retries: Tentativas em caso de erro

    Returns:
        {"media_id": str, "permalink": str}
    """
    _check_config()

    params: dict[str, str] = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": "true" if share_to_feed else "false",
        "access_token": ACCESS_TOKEN,
    }
    if cover_url:
        params["cover_url"] = cover_url

    for attempt in range(1, max_retries + 1):
        try:
            print(f"[Instagram/Reel] Tentativa {attempt}/{max_retries}")

            r = httpx.post(f"{GRAPH_API}/{ACCOUNT_ID}/media", data=params, timeout=30)
            if r.status_code >= 400:
                print(f"[Instagram/Reel] {r.status_code} body: {r.text[:500]}")
            r.raise_for_status()
            container_id = r.json().get("id")
            if not container_id:
                raise RuntimeError(f"Falha ao criar container reel: {r.json()}")
            print(f"[Instagram/Reel] Container criado: {container_id}")

            # Reels precisam transcode — aguarda mais
            _wait_container_ready(container_id, max_wait=300)
            media_id = _publish(container_id)

            permalink = ""
            try:
                rp = httpx.get(
                    f"{GRAPH_API}/{media_id}",
                    params={"fields": "permalink", "access_token": ACCESS_TOKEN},
                    timeout=10,
                )
                permalink = rp.json().get("permalink", "")
            except Exception:
                pass

            return {"media_id": media_id, "permalink": permalink}

        except Exception as e:
            print(f"[Instagram/Reel] Erro na tentativa {attempt}: {e}")
            if attempt == max_retries:
                raise
            time.sleep(5 * attempt)

    raise RuntimeError("Todas as tentativas falharam")


# ─── STORIES ────────────────────────────────────────────────────────────────

def postar_story(
    image_url: str | None = None,
    video_url: str | None = None,
    max_retries: int = 3,
) -> dict:
    """
    Posta um story no Instagram (imagem 1080x1920 ou vídeo MP4 9:16, até 60s).

    Args:
        image_url: URL pública da imagem (use isto OU video_url, não os dois)
        video_url: URL pública do vídeo MP4
        max_retries: Tentativas em caso de erro

    Returns:
        {"media_id": str, "permalink": str}

    Nota: Stories não aceitam caption nem hashtags clicáveis via API.
    """
    _check_config()

    if not image_url and not video_url:
        raise ValueError("Forneça image_url ou video_url")
    if image_url and video_url:
        raise ValueError("Forneça apenas image_url OU video_url, não ambos")

    params: dict[str, str] = {
        "media_type": "STORIES",
        "access_token": ACCESS_TOKEN,
    }
    if image_url:
        params["image_url"] = image_url
    else:
        params["video_url"] = video_url  # type: ignore[assignment]

    for attempt in range(1, max_retries + 1):
        try:
            print(f"[Instagram/Story] Tentativa {attempt}/{max_retries}")

            r = httpx.post(f"{GRAPH_API}/{ACCOUNT_ID}/media", data=params, timeout=30)
            if r.status_code >= 400:
                print(f"[Instagram/Story] {r.status_code} body: {r.text[:500]}")
            r.raise_for_status()
            container_id = r.json().get("id")
            if not container_id:
                raise RuntimeError(f"Falha ao criar container story: {r.json()}")
            print(f"[Instagram/Story] Container criado: {container_id}")

            # Vídeo pode demorar mais que imagem
            wait_timeout = 180 if video_url else 60
            _wait_container_ready(container_id, max_wait=wait_timeout)

            media_id = _publish(container_id)

            permalink = ""
            try:
                rp = httpx.get(
                    f"{GRAPH_API}/{media_id}",
                    params={"fields": "permalink", "access_token": ACCESS_TOKEN},
                    timeout=10,
                )
                permalink = rp.json().get("permalink", "")
            except Exception:
                pass

            return {"media_id": media_id, "permalink": permalink}

        except Exception as e:
            print(f"[Instagram/Story] Erro na tentativa {attempt}: {e}")
            if attempt == max_retries:
                raise
            time.sleep(5 * attempt)

    raise RuntimeError("Todas as tentativas falharam")
