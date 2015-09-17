
from application import app
from data.database import db
from data.datamodel import Player, Tag, Challenge, Game, Shout

from flask import redirect, request, url_for, session

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf import Form as SafeForm

from data.players import player_is_admin


class SafeModelView(ModelView):

    """
    A simple ModelView derivative which enforces authentication + permission.

    In addition, use Flask-WTF for CSRF attach prevention,
    """

    # derive from flask_wtf.Form to prevent CSRF attacks
    from_base_class = SafeForm

    def is_accessible(self):
        # admin interface is only accessible if user is logged and is an administrator
        return session.get('logged_in') and player_is_admin(session['username'])

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

# admin interface
admin = Admin(app)
admin.add_view(SafeModelView(Player, db.session))
admin.add_view(SafeModelView(Tag, db.session))
admin.add_view(SafeModelView(Challenge, db.session))
admin.add_view(SafeModelView(Game, db.session))
admin.add_view(SafeModelView(Shout, db.session))
