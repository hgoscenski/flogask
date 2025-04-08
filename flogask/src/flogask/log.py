import logging
import sys 
import json
import re

from flask import app, request, g
from flask.logging import default_handler
import uuid

import structlog

from flogask.utils import default_processors

def pre_logging_setup():
    logging.basicConfig(
        format="%(message)s", stream=sys.stdout, level=logging.DEBUG
    )

    logging.getLogger('werkzeug').disabled = True
    logging.getLogger('gunicorn').disabled = True
    logging.getLogger("wsgi").disabled = True

def setup_logging(consoleLogs: bool = False):
    root_logger = logging.getLogger()

    logger = structlog.get_logger()

    processors = default_processors

    if consoleLogs:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        processors.append(structlog.processors.JSONRenderer())


    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    handler = logging.StreamHandler()
    root_logger.addHandler(handler)
    
    return logger

def setup_flask_logging(app: app):
    logger = setup_logging(app.config['DEBUG'])

    app.logger.removeHandler(default_handler)

    @app.before_request
    def logger_setup():
        if rid := request.headers.get("x-request-id"):
            request_id = rid
        else:
            request_id = str(uuid.uuid4())

        g.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            view=request.path,
            request_id=request_id,
            peer=request.access_route[0],
        )
        logger.info("received request")

    @app.after_request
    def add_request_id(response):
        response.headers['x-request-id'] = g.request_id
        return response

    # take care of flask run server logs
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: logger.info("starting flask server", debug=x[0], flask_app=x[1])

    return logger