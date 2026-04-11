"""
analytics.py — Métricas de performance dos posts
"""
import json
import os
from datetime import datetime
from pathlib import Path

import httpx

GRAPH_API = "https://graph.instagram.com/v22.0"
ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")

_app_hist = Path("/app/historico")
CONFIG_DIR = _app_hist if _app_hist.exists() else Path.home() / "carousel-api" / "historico"
ANALYTICS_FILE = CONFIG_DIR / "analytics.json"


def fetch_post_metrics(limit: int = 20) -> list[dict]:
    """Busca métricas dos últimos posts do Instagram."""
    if not ACCESS_TOKEN:
        return []
    try:
        r = httpx.get(
            f"{GRAPH_API}/me/media",
            params={
                "fields": "id,caption,media_type,timestamp,like_count,comments_count,permalink",
                "limit": limit,
                "access_token": ACCESS_TOKEN,
            },
            timeout=15,
        )
        r.raise_for_status()
        posts = r.json().get("data", [])

        metrics = []
        for post in posts:
            metrics.append({
                "id": post.get("id"),
                "caption": (post.get("caption", "") or "")[:100],
                "type": post.get("media_type", ""),
                "timestamp": post.get("timestamp", ""),
                "likes": post.get("like_count", 0),
                "comments": post.get("comments_count", 0),
                "engagement": (post.get("like_count", 0) + post.get("comments_count", 0)),
                "permalink": post.get("permalink", ""),
            })

        return metrics
    except Exception as e:
        print(f"[Analytics] Erro: {e}")
        return []


def fetch_profile_metrics() -> dict:
    """Busca métricas do perfil."""
    if not ACCESS_TOKEN:
        return {}
    try:
        r = httpx.get(
            f"{GRAPH_API}/me",
            params={
                "fields": "followers_count,follows_count,media_count",
                "access_token": ACCESS_TOKEN,
            },
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        return {
            "followers": data.get("followers_count", 0),
            "following": data.get("follows_count", 0),
            "posts": data.get("media_count", 0),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"[Analytics] Erro perfil: {e}")
        return {}


def save_snapshot():
    """Salva snapshot diário de métricas."""
    snapshots = []
    if ANALYTICS_FILE.exists():
        try:
            snapshots = json.loads(ANALYTICS_FILE.read_text())
        except Exception:
            pass

    profile = fetch_profile_metrics()
    posts = fetch_post_metrics(10)

    snapshot = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "profile": profile,
        "top_posts": sorted(posts, key=lambda x: x["engagement"], reverse=True)[:5],
        "avg_engagement": sum(p["engagement"] for p in posts) / len(posts) if posts else 0,
    }

    # Evitar duplicata do mesmo dia
    snapshots = [s for s in snapshots if s.get("date") != snapshot["date"]]
    snapshots.insert(0, snapshot)
    snapshots = snapshots[:90]  # 90 dias de histórico

    ANALYTICS_FILE.write_text(json.dumps(snapshots, ensure_ascii=False, indent=2))
    return snapshot


def get_analytics() -> dict:
    """Retorna analytics completo."""
    snapshots = []
    if ANALYTICS_FILE.exists():
        try:
            snapshots = json.loads(ANALYTICS_FILE.read_text())
        except Exception:
            pass

    posts = fetch_post_metrics(20)
    profile = fetch_profile_metrics()

    return {
        "profile": profile,
        "posts": posts,
        "history": snapshots[:30],
        "avg_engagement": sum(p["engagement"] for p in posts) / len(posts) if posts else 0,
    }
