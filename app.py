import configuration

from flask import Flask

# application with configuration
app = Flask(__name__)
app.config.from_object(configuration)
