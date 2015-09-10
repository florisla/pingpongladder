
from data.datamodel import Player
from data.database import db

def get_players():
    return db.session.query(Player).all()

def player_is_admin(player_name):
    try:
        db.session.query(Player).filter(Player.name == player_name).filter(Player.admin == True).one()
    except:
        return False
    return True

def set_player_absence(player_name, absence):
    player = db.session.query(Player).filter(Player.name == player_name).one()
    player.absence = absence
    db.session.commit()

def get_player_absence(player_name):
    player = db.session.query(Player).filter(Player.name == player_name).one()
    return player.absence
