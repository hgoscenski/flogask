import structlog

timestamper = structlog.processors.TimeStamper(fmt="iso")
