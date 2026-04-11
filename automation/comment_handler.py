"""
comment_handler.py — Processa comentários: keyword detection, auto-reply, dispara DM
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
KEYWORDS_FILE = CONFIG_DIR / "automation-keywords.json"
LOGS_FILE = CONFIG_DIR / "automation-logs.json"


# ─── KEYWORDS ────────────────────────────────────────────────────────────────

def load_keywords() -> list[dict]:
    """Carrega keywords configuradas."""
    if KEYWORDS_FILE.exists():
        try:
            return json.loads(KEYWORDS_FILE.read_text())
        except Exception:
            pass
    return [
        {
            "keyword": "SISTEMA",
            "reply": "Acabei de te mandar no DM! Confere lá 👆",
            "dm_sequence": "diagnostico_gratis",
            "ativo": True,
        },
        {
            "keyword": "QUERO",
            "reply": "Olha o DM! Te mandei o próximo passo 🔥",
            "dm_sequence": "aplicacao",
            "ativo": True,
        },
        {
            "keyword": "LINK",
            "reply": "Mandei no seu DM! Confere lá ✉️",
            "dm_sequence": "link_bio",
            "ativo": True,
        },
    ]


def save_keywords(keywords: list[dict]):
    KEYWORDS_FILE.write_text(json.dumps(keywords, ensure_ascii=False, indent=2))


# ─── LOGS ────────────────────────────────────────────────────────────────────

def _log_action(action: dict):
    logs = []
    if LOGS_FILE.exists():
        try:
            logs = json.loads(LOGS_FILE.read_text())
        except Exception:
            pass
    logs.insert(0, {**action, "timestamp": datetime.now().isoformat()})
    logs = logs[:200]
    LOGS_FILE.write_text(json.dumps(logs, ensure_ascii=False, indent=2))


def load_logs() -> list:
    if LOGS_FILE.exists():
        try:
            return json.loads(LOGS_FILE.read_text())
        except Exception:
            pass
    return []


# ─── COMMENT PROCESSING ─────────────────────────────────────────────────────

def process_comment(event: dict) -> dict | None:
    """Processa um comentário: detecta keyword, responde, dispara DM."""
    text = event.get("text", "").strip().upper()
    username = event.get("username", "")
    comment_id = event.get("comment_id", "")
    user_id = event.get("user_id", "")

    if not text or not comment_id:
        return None

    keywords = load_keywords()
    matched = None

    for kw in keywords:
        if not kw.get("ativo"):
            continue
        if kw["keyword"].upper() in text:
            matched = kw
            break

    if not matched:
        _log_action({
            "type": "comment_no_match",
            "username": username,
            "text": event.get("text", ""),
        })
        return None

    print(f"[Comment] Keyword '{matched['keyword']}' detectada de @{username}")

    result = {
        "keyword": matched["keyword"],
        "username": username,
        "comment_id": comment_id,
        "reply_sent": False,
        "dm_sent": False,
    }

    # 1. Auto-reply no comentário
    reply_text = matched.get("reply", "")
    if reply_text and comment_id:
        try:
            r = httpx.post(
                f"{GRAPH_API}/{comment_id}/replies",
                data={"message": reply_text, "access_token": ACCESS_TOKEN},
                timeout=10,
            )
            result["reply_sent"] = r.status_code == 200
            print(f"[Comment] Reply enviado: {r.status_code}")
        except Exception as e:
            print(f"[Comment] Erro no reply: {e}")

    # 2. Disparar DM
    if user_id and matched.get("dm_sequence"):
        from .dm_sequences import trigger_sequence
        try:
            trigger_sequence(user_id, username, matched["dm_sequence"])
            result["dm_sent"] = True
        except Exception as e:
            print(f"[Comment] Erro ao disparar DM: {e}")

    _log_action({
        "type": "comment_keyword_match",
        "username": username,
        "keyword": matched["keyword"],
        "text": event.get("text", ""),
        "reply_sent": result["reply_sent"],
        "dm_sent": result["dm_sent"],
    })

    # 3. Atualizar lead scoring
    from .lead_scoring import record_interaction
    record_interaction(user_id, username, "comment_keyword", score=10)

    return result


def reply_to_comment(comment_id: str, message: str) -> bool:
    """Responde a um comentário específico."""
    try:
        r = httpx.post(
            f"{GRAPH_API}/{comment_id}/replies",
            data={"message": message, "access_token": ACCESS_TOKEN},
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False
