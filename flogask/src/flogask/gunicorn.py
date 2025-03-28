import re
import json

import structlog

from flogask.log import timestamper

gunicorn_access_log_format = '%({x-forwarded-for}i)s %(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" "%({x-request-id}o)s"'

PARTS = [
    r'(?P<xff>\S+)',  # host %h
    r'(?P<host>\S+)',  # host %h
    r'\S+',  # indent %l (unused)
    r'(?P<user>\S+)',  # user %u
    r'\[(?P<time>.+)\]',  # time %t
    r'"(?P<request>.+)"',  # request "%r"
    r'(?P<status>[0-9]+)',  # status %>s
    r'(?P<size>\S+)',  # size %b (careful, can be '-')
    r'"(?P<referer>.*)"',  # referer "%{Referer}i"
    r'"(?P<agent>.*)"',  # user agent "%{User-agent}i"
    r'"(?P<request_id>.*)"',  # user agent "%{User-agent}i"
]

PATTERN = re.compile(r'\s+'.join(PARTS) + r'\s*\Z')

def combined_logformat(logger, name, event_dict):
    if event_dict.get('logger') == "gunicorn.access":
        message = event_dict['event']

        m = PATTERN.match(message)
        if m:
            res = m.groupdict()

            if res["xff"] != "-":
                res["host"] = res.pop("xff")
            else:
                res.pop("xff")

            if res["request"]:
                try:
                    request_bits = res["request"].split(" ")
                    res["method"] = request_bits[0]
                    res["path"] = request_bits[1]
                    res["http"] = request_bits[2]
                except:
                    pass

            if res["user"] == "-":
                res["user"] = None

            res["status"] = int(res["status"])

            if res["size"] == "-":
                res["size"] = 0
            else:
                res["size"] = int(res["size"])

            if res["referer"] == "-":
                res["referer"] = None

            event_dict.update(res)
            event_dict.pop("event")
    else:
        message = event_dict['event']
        try:
            parsed = json.loads(message)
            event_dict.pop("event")
            event_dict.update(parsed)
        except:
            pass

    return event_dict

# --- Structlog logging initialisation code
pre_chain = [
    # Add the log level and a timestamp to the event_dict if the log entry
    # is not from structlog.
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.format_exc_info,
    timestamper,
    combined_logformat # This does the magic!
]

gunicorn_logconfig_dict = {
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
        "botocore": {
            "level": "INFO"
        },
        "gunicorn": {
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
