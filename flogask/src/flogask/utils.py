import structlog

timestamper = structlog.processors.TimeStamper(fmt="iso")

default_processors = [
    structlog.contextvars.merge_contextvars,  # <--!!!
    # structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.CallsiteParameterAdder(
        [
            structlog.processors.CallsiteParameter.FILENAME,
            structlog.processors.CallsiteParameter.MODULE,
            structlog.processors.CallsiteParameter.FUNC_NAME,
            structlog.processors.CallsiteParameter.LINENO
        ],
    ),
    # timestamper,
    structlog.processors.StackInfoRenderer(),
    # structlog.processors.format_exc_info,
]

pre_chain = [
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.format_exc_info,
    timestamper,
]