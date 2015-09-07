
from app import app
from data.database import db
from data.datamodel import Player, Tag, Challenge, Game, Shout

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf import Form as SafeForm

class SafeModelView(ModelView):
    from_base_class = SafeForm

# admin interface
admin = Admin(app)
admin.add_view(SafeModelView(Player, db.session))
admin.add_view(SafeModelView(Tag, db.session))
admin.add_view(SafeModelView(Challenge, db.session))
admin.add_view(SafeModelView(Game, db.session))
admin.add_view(SafeModelView(Shout, db.session))

