
import configuration

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

# application with configuration
app = Flask(__name__)
app.config.from_object(configuration)
toolbar = DebugToolbarExtension(app)

