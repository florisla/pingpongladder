
from flask import Flask

import configuration


# application with configuration
app = Flask(__name__)
app.config.from_object(configuration)

if app.config['DEBUG']:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)

