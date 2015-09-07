
from data.datamodel import Player
from tournament import db

def get_players():
    return db.session.query(Player).all()

def set_player_absence(player_name, absence):
    player = db.session.query(Player).filter(Player.name == player_name).one()
    player.absence = absence
    db.session.commit()


if __name__ == '__main__':
    #print([p.tags for p in get_players()])
    #import datetime
    #set_player_absence('Floris', datetime.datetime(year=2015, month=10, day=1))
    pass
