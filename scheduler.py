"""
scheduler.py — Agendamento de carrosseis automáticos
Configurável via API. Persiste config no volume.
"""
import json
import threading
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
import pytz

BR_TZ = pytz.timezone("America/Sao_Paulo")

# ─── CONFIG PERSISTENCE ──────────────────────────────────────────────────────
_app_hist = Path("/app/historico")
CONFIG_DIR = _app_hist if _app_hist.exists() else Path.home() / "carousel-api" / "historico"
SCHEDULE_FILE = CONFIG_DIR / "schedule-config.json"

DEFAULT_CONFIG = {
    "ativo": False,
    "jobs": [
        {"hora": "09:00", "estilo": "dark", "visual": "editorial", "slides": 7, "ativo": True},
        {"hora": "13:00", "estilo": "light", "visual": "none", "slides": 7, "ativo": True},
        {"hora": "18:00", "estilo": "ferrugem", "visual": "editorial", "slides": 7, "ativo": True},
    ]
}


def load_config() -> dict:
    if SCHEDULE_FILE.exists():
        try:
            return json.loads(SCHEDULE_FILE.read_text())
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    SCHEDULE_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2))


# ─── SCHEDULER ───────────────────────────────────────────────────────────────
_scheduler: BackgroundScheduler | None = None
_lock = threading.Lock()


def _run_job(estilo: str, visual: str, slides: int, tipo_conteudo: str = "auto"):
    """Executa o pipeline num thread separado."""
    from pipeline import executar_pipeline
    print(f"[Scheduler] Executando job: estilo={estilo}, visual={visual}, tipo={tipo_conteudo}")
    try:
        resultado = executar_pipeline(num_slides=slides, estilo=estilo, visual=visual, tipo_conteudo=tipo_conteudo)
        status = resultado.get("status", "?")
        print(f"[Scheduler] Job concluído: {status}")

        # Salvar log do job
        log_file = CONFIG_DIR / "schedule-log.json"
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except Exception:
                pass
        logs.insert(0, {
            "timestamp": datetime.now().isoformat(),
            "estilo": estilo,
            "visual": visual,
            "slides": slides,
            "status": status,
            "titulo": resultado.get("etapas", {}).get("copy", {}).get("titulo", ""),
            "error": resultado.get("error", ""),
        })
        logs = logs[:50]  # manter últimos 50
        log_file.write_text(json.dumps(logs, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"[Scheduler] Erro no job: {e}")


def start_scheduler():
    """Inicia ou reinicia o scheduler com a config atual."""
    global _scheduler
    with _lock:
        if _scheduler:
            _scheduler.shutdown(wait=False)

        config = load_config()
        if not config.get("ativo"):
            print("[Scheduler] Desativado")
            _scheduler = None
            return

        _scheduler = BackgroundScheduler()

        for i, job in enumerate(config.get("jobs", [])):
            if not job.get("ativo"):
                continue
            hora = job.get("hora", "09:00")
            h, m = hora.split(":")
            trigger = CronTrigger(hour=int(h), minute=int(m), timezone=BR_TZ)
            _scheduler.add_job(
                _run_job,
                trigger=trigger,
                args=[job.get("estilo", "dark"), job.get("visual", "editorial"), job.get("slides", 7), job.get("tipo_conteudo", "auto")],
                id=f"carousel_job_{i}",
                replace_existing=True,
            )
            print(f"[Scheduler] Job {i+1} agendado: {hora} ({job.get('estilo')})")

        _scheduler.start()
        print(f"[Scheduler] Iniciado com {len([j for j in config.get('jobs', []) if j.get('ativo')])} jobs ativos")


def stop_scheduler():
    """Para o scheduler."""
    global _scheduler
    with _lock:
        if _scheduler:
            _scheduler.shutdown(wait=False)
            _scheduler = None
            print("[Scheduler] Parado")


def agendar_post(carrossel: dict, quando_iso: str, estilo: str = "dark", visual: str = "editorial") -> dict:
    """Agenda um carrossel já gerado para ser postado num horário específico."""
    global _scheduler
    with _lock:
        if not _scheduler or not _scheduler.running:
            _scheduler = BackgroundScheduler()
            _scheduler.start()

        from datetime import datetime as _dt
        quando = _dt.fromisoformat(quando_iso)
        if quando.tzinfo is None:
            quando = BR_TZ.localize(quando)

        job_id = f"post_{int(quando.timestamp())}_{abs(hash(str(carrossel)[:80])) % 10000}"
        _scheduler.add_job(
            _post_agendado,
            trigger=DateTrigger(run_date=quando),
            args=[carrossel, estilo, visual],
            id=job_id,
            replace_existing=True,
        )

        # Persiste na lista de agendados
        agendados_file = CONFIG_DIR / "posts-agendados.json"
        agendados = []
        if agendados_file.exists():
            try: agendados = json.loads(agendados_file.read_text())
            except Exception: pass
        agendados.append({
            "job_id": job_id,
            "quando": quando.isoformat(),
            "titulo": carrossel.get("titulo", ""),
            "pilar": carrossel.get("pilar", ""),
            "estilo": estilo,
            "visual": visual,
            "total_slides": len(carrossel.get("slides", [])),
            "criado_em": datetime.now().isoformat(),
            "status": "agendado",
        })
        agendados_file.write_text(json.dumps(agendados, ensure_ascii=False, indent=2))
        print(f"[Scheduler] Post agendado para {quando.isoformat()} — {carrossel.get('titulo', '')[:40]}")
        return {"job_id": job_id, "quando": quando.isoformat()}


def _post_agendado(carrossel: dict, estilo: str, visual: str):
    """Executa etapas 4-7 do pipeline com um carrossel já gerado."""
    from pipeline import etapa_render, etapa_caption, etapa_postar, etapa_notificar, _salvar_postagem
    try:
        pngs, previews = etapa_render(carrossel, estilo, visual)
        caption_data = etapa_caption(carrossel)
        caption = caption_data.get("caption", "")
        post_result = etapa_postar(pngs, caption)
        _salvar_postagem({
            "timestamp": datetime.now().isoformat(),
            "titulo": carrossel.get("titulo", ""),
            "pilar": carrossel.get("pilar", ""),
            "estilo": estilo, "visual": visual,
            "total_slides": len(pngs),
            "media_id": post_result.get("media_id", ""),
            "permalink": post_result.get("permalink", ""),
            "caption": caption[:200],
            "preview": previews[0] if previews else "",
            "status": "publicado",
        })
        etapa_notificar(post_result, carrossel.get("titulo", "?"))
    except Exception as e:
        print(f"[Scheduler] Falha em post agendado: {e}")
        etapa_notificar({}, carrossel.get("titulo", "?"), erro=str(e))


def listar_agendados() -> list:
    f = CONFIG_DIR / "posts-agendados.json"
    if not f.exists(): return []
    try:
        from datetime import datetime as _dt
        ags = json.loads(f.read_text())
        agora = _dt.now(BR_TZ)
        # Marca os que já passaram
        for a in ags:
            try:
                q = _dt.fromisoformat(a["quando"])
                if q.tzinfo is None: q = BR_TZ.localize(q)
                if a.get("status") == "agendado" and q < agora:
                    a["status"] = "expirado"
            except Exception: pass
        return ags
    except Exception:
        return []


def get_status() -> dict:
    """Retorna status do scheduler."""
    config = load_config()

    # Log recente
    log_file = CONFIG_DIR / "schedule-log.json"
    logs = []
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text())[:10]
        except Exception:
            pass

    return {
        "ativo": config.get("ativo", False),
        "jobs": config.get("jobs", []),
        "logs": logs,
        "scheduler_running": _scheduler is not None and _scheduler.running if _scheduler else False,
    }
