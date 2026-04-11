"""
lead_scoring.py — Social selling: scoring de leads por engajamento
"""
import json
from datetime import datetime
from pathlib import Path

_app_hist = Path("/app/historico")
CONFIG_DIR = _app_hist if _app_hist.exists() else Path.home() / "carousel-api" / "historico"
LEADS_FILE = CONFIG_DIR / "leads.json"

SCORE_MAP = {
    "like": 1,
    "comment": 3,
    "comment_keyword": 10,
    "save": 5,
    "dm_received": 15,
    "profile_visit": 2,
    "dm_sent": 0,  # não pontua envio, só recebimento
}

THRESHOLD_QUENTE = 30


def _load_leads() -> dict:
    if LEADS_FILE.exists():
        try:
            return json.loads(LEADS_FILE.read_text())
        except Exception:
            pass
    return {}


def _save_leads(leads: dict):
    LEADS_FILE.write_text(json.dumps(leads, ensure_ascii=False, indent=2))


def record_interaction(user_id: str, username: str, interaction_type: str, score: int | None = None):
    """Registra interação e atualiza score do lead."""
    if not user_id:
        return

    leads = _load_leads()
    points = score if score is not None else SCORE_MAP.get(interaction_type, 1)

    if user_id not in leads:
        leads[user_id] = {
            "username": username,
            "score": 0,
            "interactions": [],
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "status": "frio",
        }

    lead = leads[user_id]
    lead["score"] += points
    lead["last_seen"] = datetime.now().isoformat()
    lead["username"] = username or lead["username"]

    # Atualizar status
    if lead["score"] >= THRESHOLD_QUENTE:
        lead["status"] = "quente"
    elif lead["score"] >= 10:
        lead["status"] = "morno"
    else:
        lead["status"] = "frio"

    # Guardar últimas 20 interações
    lead["interactions"].insert(0, {
        "type": interaction_type,
        "points": points,
        "timestamp": datetime.now().isoformat(),
    })
    lead["interactions"] = lead["interactions"][:20]

    leads[user_id] = lead
    _save_leads(leads)
    print(f"[Lead] @{username}: +{points} ({interaction_type}) → score={lead['score']} ({lead['status']})")


def get_all_leads() -> list[dict]:
    """Retorna todos os leads ordenados por score."""
    leads = _load_leads()
    result = []
    for uid, lead in leads.items():
        result.append({**lead, "user_id": uid})
    return sorted(result, key=lambda x: x["score"], reverse=True)


def get_hot_leads() -> list[dict]:
    """Retorna apenas leads quentes."""
    return [l for l in get_all_leads() if l["status"] == "quente"]
