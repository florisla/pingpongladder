
from data.database import Player
from data.dbsession import session

def get_players():
    return session.query(Player).all()

def set_player_absence(player_name, absence):
    player = session.query(Player).filter(Player.name == player_name).one()
    player.absence = absence
    session.commit()


if __name__ == '__main__':
    #print([p.tags for p in get_players()])
    #import datetime
    #set_player_absence('Floris', datetime.datetime(year=2015, month=10, day=1))
    pass
