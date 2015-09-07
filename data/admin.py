
from app import app
from data.database import db
from data.datamodel import Player, Tag, Challenge, Game, Shout

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# admin interface
admin = Admin(app)
admin.add_view(ModelView(Player, db.session))
admin.add_view(ModelView(Tag, db.session))
admin.add_view(ModelView(Challenge, db.session))
admin.add_view(ModelView(Game, db.session))
admin.add_view(ModelView(Shout, db.session))
