import structlog

from flogask.utils import pre_chain

alembic_logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": True,
    "propagate": True,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": pre_chain,
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["root"],
    },
    "loggers": {
        "alembic": {
            "level": "INFO"
        },
    },
    "handlers": {
        "root": {
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
        },
    },
}
