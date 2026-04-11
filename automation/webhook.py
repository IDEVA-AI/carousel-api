"""
webhook.py — Handler de webhooks do Instagram
Recebe notificações de comentários e mensagens em tempo real.
"""
import hashlib
import hmac
import json
import os
from fastapi import Request, HTTPException

VERIFY_TOKEN = os.environ.get("INSTAGRAM_WEBHOOK_VERIFY_TOKEN", "carousel_julio_2026")
APP_SECRET = os.environ.get("INSTAGRAM_APP_SECRET", "657abf5a1bddd6285c6")


def verify_webhook(mode: str, token: str, challenge: str) -> str:
    """Verificação do webhook (GET) — Meta envia challenge."""
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print(f"[Webhook] Verificação OK")
        return challenge
    raise HTTPException(status_code=403, detail="Verificação falhou")


def validate_signature(payload: bytes, signature: str) -> bool:
    """Valida X-Hub-Signature-256 do payload."""
    if not signature or not APP_SECRET:
        return False
    expected = "sha256=" + hmac.new(
        APP_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


async def handle_webhook(request: Request) -> dict:
    """Processa evento de webhook do Instagram."""
    body = await request.body()

    # Validar signature (opcional em dev, obrigatório em prod)
    signature = request.headers.get("X-Hub-Signature-256", "")
    if APP_SECRET and signature and not validate_signature(body, signature):
        print("[Webhook] Signature inválida")
        raise HTTPException(status_code=403, detail="Signature inválida")

    try:
        data = json.loads(body)
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    print(f"[Webhook] Evento recebido: {json.dumps(data)[:200]}")

    # Processar cada entry
    events = []
    for entry in data.get("entry", []):
        # Comentários
        for change in entry.get("changes", []):
            field = change.get("field", "")
            value = change.get("value", {})

            if field == "comments":
                event = {
                    "type": "comment",
                    "comment_id": value.get("id"),
                    "text": value.get("text", ""),
                    "username": value.get("from", {}).get("username", ""),
                    "user_id": value.get("from", {}).get("id", ""),
                    "media_id": value.get("media", {}).get("id", ""),
                    "timestamp": value.get("timestamp", ""),
                }
                events.append(event)
                print(f"[Webhook] Comentário de @{event['username']}: {event['text'][:60]}")

            elif field == "messages":
                event = {
                    "type": "message",
                    "message_id": value.get("id"),
                    "text": value.get("message", {}).get("text", ""),
                    "sender_id": value.get("sender", {}).get("id", ""),
                    "timestamp": value.get("timestamp", ""),
                }
                events.append(event)
                print(f"[Webhook] DM recebida: {event['text'][:60]}")

    return {"events": events}
