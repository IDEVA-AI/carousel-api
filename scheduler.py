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


def _run_job(estilo: str, visual: str, slides: int):
    """Executa o pipeline num thread separado."""
    from pipeline import executar_pipeline
    print(f"[Scheduler] Executando job: estilo={estilo}, visual={visual}, slides={slides}")
    try:
        resultado = executar_pipeline(num_slides=slides, estilo=estilo, visual=visual)
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
                args=[job.get("estilo", "dark"), job.get("visual", "editorial"), job.get("slides", 7)],
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
