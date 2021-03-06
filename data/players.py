
from sqlalchemy.orm.exc import NoResultFound

from data.datamodel import Player
from data.database import db


def get_players():
    """
    Return all players, sorted by their initial rank (rank 1 first).
    """
    return db.session.query(Player).order_by(Player.initial_rank.asc()).all()

def player_is_admin(player_name):
    try:
        db.session.query(Player).filter(Player.name == player_name).filter(Player.admin == True).one()
    except NoResultFound:
        return False
    return True

def get_player_email(player_name):
    player = db.session.query(Player).filter(Player.name == player_name).one()
    return (player.full_name, player.email_address)

def get_players_email(player_names):
    players = db.session \
        .query(Player) \
        .filter(Player.name.in_(player_names)) \
        .filter(Player.email_address.isnot(None)) \
        .all()
    cc_emails = [(player.full_name, player.email_address) for player in players]
    if len(cc_emails) == 0:
        return None
    return cc_emails

def set_player_absence(player_name, absence):
    player = db.session.query(Player).filter(Player.name == player_name).one()
    player.absence = absence
    db.session.commit()

def get_player_absence(player_name):
    player = db.session.query(Player).filter(Player.name == player_name).one()
    return player.absence
