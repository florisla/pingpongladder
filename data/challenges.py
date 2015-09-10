
import datetime

from data.datamodel import Challenge, Player, Game
from sqlalchemy.orm.exc import NoResultFound
from data.database import db

def add_challenge(challenger, defender):
    db.session.add(Challenge(
        challenger=db.session.query(Player).filter(Player.name == challenger).one(),
        defender=db.session.query(Player).filter(Player.name == defender).one(),
    ))
    db.session.commit()

def get_challenges():
    return db.session.query(Challenge).filter(Challenge.active == True).order_by(Challenge.date.desc()).all()

def deactivate_challenges(challenger_name):
    challenger = db.session.query(Player).filter(Player.name == challenger_name).one()
    try:
        challenge = db.session.query(Challenge).filter(Challenge.challenger == challenger).filter(Challenge.active == True).one()
    except NoResultFound:
        return

    challenge.active = False
    db.session.commit()

def link_challenge_to_game(game):
    try:
        challenge = db.session.query(Challenge).filter(Challenge.challenger_id == game.challenger_id).filter(Challenge.defender_id == game.defender_id).filter(Challenge.active == True).one()
    except NoResultFound:
        return
    challenge.game_id = game.id
    challenge.active = False
    db.session.commit()

def may_challenge(player_name, cool_down_time_h):
    player = db.session.query(Player).filter(Player.name == player_name).one()

    recently_played_challenges = db.session \
        .query(Game) \
        .filter(Game.challenger == player) \
        .filter(Game.date > datetime.datetime.now() - datetime.timedelta(hours=cool_down_time_h)) \
        .all()
    return not any(recently_played_challenges)


if __name__ == '__main__':
    #add_challenge('Floris', 'Lou')
    #from data.database import Game
    #game = db.session.query(Game).filter(Game.id == 1).one()
    #link_challenge_to_game(game)
    #add_challenge('Lou', 'Floris')
    #deactivate_challenges('Floris')
    #print(get_challenges())
    pass

