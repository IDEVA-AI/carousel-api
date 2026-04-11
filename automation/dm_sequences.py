"""
dm_sequences.py — Sequências de DM automáticas (mini-funil)
Envia mensagens em sequência com delays configuráveis.
"""
import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path

import httpx

GRAPH_API = "https://graph.instagram.com/v22.0"
ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")

_app_hist = Path("/app/historico")
CONFIG_DIR = _app_hist if _app_hist.exists() else Path.home() / "carousel-api" / "historico"
SEQUENCES_FILE = CONFIG_DIR / "dm-sequences.json"
ACTIVE_DMS_FILE = CONFIG_DIR / "dm-active.json"


# ─── SEQUENCES CONFIG ────────────────────────────────────────────────────────

def load_sequences() -> list[dict]:
    if SEQUENCES_FILE.exists():
        try:
            return json.loads(SEQUENCES_FILE.read_text())
        except Exception:
            pass
    return [
        {
            "id": "diagnostico_gratis",
            "nome": "Diagnóstico Gratuito",
            "trigger_keyword": "SISTEMA",
            "ativo": True,
            "steps": [
                {"delay_minutes": 0, "message": "Oi! Vi que você se interessou pelo conteúdo sobre sistema. 🔥\n\nVou te fazer uma pergunta rápida: sua empresa funciona sem você ou depende de você pra tudo?"},
                {"delay_minutes": 1440, "message": "E aí, pensou na pergunta?\n\nSe a resposta é 'depende de mim' — isso não é falta de time bom. É falta de arquitetura.\n\nQuer que eu te mostre onde o sistema trava? Tenho uma sessão gratuita de diagnóstico."},
                {"delay_minutes": 4320, "message": "Última mensagem sobre isso: tenho 3 vagas essa semana pra sessão de diagnóstico gratuita.\n\nEm 15 min eu mostro onde a arquitetura da sua empresa está travando o crescimento.\n\nQuer agendar?"},
            ],
        },
        {
            "id": "aplicacao",
            "nome": "Aplicação Direta",
            "trigger_keyword": "QUERO",
            "ativo": True,
            "steps": [
                {"delay_minutes": 0, "message": "Show! Fico feliz que tenha se identificado. 💪\n\nMe conta rapidinho: qual o faturamento da sua empresa e qual a maior dor hoje?"},
            ],
        },
        {
            "id": "link_bio",
            "nome": "Link da Bio",
            "trigger_keyword": "LINK",
            "ativo": True,
            "steps": [
                {"delay_minutes": 0, "message": "Aqui está: https://juliocarvalho.in/aplicacao\n\nQualquer dúvida, me manda aqui mesmo. 👊"},
            ],
        },
    ]


def save_sequences(sequences: list[dict]):
    SEQUENCES_FILE.write_text(json.dumps(sequences, ensure_ascii=False, indent=2))


# ─── SEND DM ─────────────────────────────────────────────────────────────────

def send_dm(user_id: str, message: str) -> bool:
    """Envia DM para um usuário via Instagram API."""
    if not ACCESS_TOKEN:
        print("[DM] Token não configurado")
        return False
    try:
        r = httpx.post(
            f"{GRAPH_API}/me/messages",
            json={
                "recipient": {"id": user_id},
                "message": {"text": message},
            },
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            timeout=15,
        )
        if r.status_code == 200:
            print(f"[DM] Enviada pra {user_id}: {message[:40]}...")
            return True
        else:
            print(f"[DM] Erro {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"[DM] Erro ao enviar: {e}")
        return False


# ─── TRIGGER SEQUENCE ─────────────────────────────────────────────────────────

def trigger_sequence(user_id: str, username: str, sequence_id: str):
    """Dispara uma sequência de DM pra um usuário."""
    sequences = load_sequences()
    seq = next((s for s in sequences if s["id"] == sequence_id and s.get("ativo")), None)
    if not seq:
        print(f"[DM] Sequência '{sequence_id}' não encontrada ou inativa")
        return

    steps = seq.get("steps", [])
    if not steps:
        return

    print(f"[DM] Disparando sequência '{sequence_id}' pra @{username} ({len(steps)} steps)")

    # Salvar DM ativa
    _save_active_dm(user_id, username, sequence_id, steps)

    # Executar em thread separado pra não bloquear
    thread = threading.Thread(
        target=_execute_sequence,
        args=(user_id, username, steps),
        daemon=True,
    )
    thread.start()


def _execute_sequence(user_id: str, username: str, steps: list[dict]):
    """Executa steps com delays."""
    for i, step in enumerate(steps):
        delay = step.get("delay_minutes", 0)
        message = step.get("message", "")

        if not message:
            continue

        # Personalizar mensagem
        message = message.replace("{nome}", username.replace("_", " ").title())

        if delay > 0 and i > 0:
            print(f"[DM] Aguardando {delay}min pra step {i+1}...")
            time.sleep(delay * 60)

        send_dm(user_id, message)

    print(f"[DM] Sequência completa pra @{username}")


# ─── ACTIVE DMS TRACKING ─────────────────────────────────────────────────────

def _save_active_dm(user_id: str, username: str, sequence_id: str, steps: list):
    active = load_active_dms()
    active.insert(0, {
        "user_id": user_id,
        "username": username,
        "sequence_id": sequence_id,
        "total_steps": len(steps),
        "started_at": datetime.now().isoformat(),
    })
    active = active[:100]
    ACTIVE_DMS_FILE.write_text(json.dumps(active, ensure_ascii=False, indent=2))


def load_active_dms() -> list:
    if ACTIVE_DMS_FILE.exists():
        try:
            return json.loads(ACTIVE_DMS_FILE.read_text())
        except Exception:
            pass
    return []
