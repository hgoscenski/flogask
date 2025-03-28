## Getting Started

```bash
# add the package
uv add 'git+https://github.com/hgoscenski/flogask#subdirectory=flogask'
```

```python
# simplest usage
import os

from flask import Flask
from flogask.log import setup_logging, pre_logging_setup

pre_logging_setup()

def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", False)
    
    logger = setup_logging(app)

    @app.route('/')
    def index():
        logger.info("Hello", test="this")
        return 'Hello, World!'
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
```

Usage with gunicorn is fully demoed in `example/`, of note is a simplified gunicorn config file.

Required fields for flogask to work correctly are

- `access_log_format = gunicorn_access_log_format`
- `logconfig_dict = gunicorn_logconfig_dict`
