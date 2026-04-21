# agent/logging_config.py
"""
Zentrale Logging-Konfiguration mit structlog.
Strukturierte, durchsuchbare Logs im JSON-Format.
"""
import logging
import structlog
from typing import Any, MutableMapping

def add_app_context(
    logger: structlog.BoundLogger, method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """
    Fügt jedem Log-Eintrag Anwendungskontext hinzu.
    Dies ist der Ort, um z.B. die App-Version oder Umgebung hinzuzufügen.
    """
    event_dict["app"] = "netzero-ai-agent"
    event_dict["environment"] = "development"  # In Produktion aus .env lesen
    return event_dict


def setup_logging(level: str = "INFO", json_format: bool = False):
    """
    Konfiguriert structlog als primäres Logging-System.

    Args:
        level: Log-Level (DEBUG, INFO, WARNING, ERROR)
        json_format: True für JSON-Ausgabe (Produktion), False für lesbare Konsolenausgabe
    """
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    # Gemeinsame Prozessoren für alle Logs
    shared_processors = [
        structlog.stdlib.add_log_level,      # Fügt 'level' Feld hinzu
        structlog.stdlib.add_logger_name,    # Fügt 'logger' Feld hinzu
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,                         # Fügt 'timestamp' Feld hinzu
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        add_app_context,                     # Unsere eigene Kontext-Anreicherung
    ]

    if json_format:
        # Produktion: JSON-Format für einfache Verarbeitung durch Log-Aggregatoren
        structlog.configure(
            processors=shared_processors + [
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level)),
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Entwicklung: Lesbares Format für die Konsole
        structlog.configure(
            processors=shared_processors + [
                structlog.dev.ConsoleRenderer(colors=True)
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level)),
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """
    Gibt einen konfigurierten Logger zurück.

    Usage:
        logger = get_logger(__name__)
        logger.info("Onboarding gestartet", student_email="max@example.com")
    """
    return structlog.get_logger(name)