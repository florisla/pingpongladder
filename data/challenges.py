
from database import Challenge, Player
from data.dbsession import session
from sqlalchemy.orm.exc import NoResultFound

def add_challenge(challenger, defender):
    session.add(Challenge(
        challenger=session.query(Player).filter(Player.name == challenger).one(),
        defender=session.query(Player).filter(Player.name == defender).one(),
    ))
    session.commit()

def get_challenges():
    return session.query(Challenge).filter(Challenge.active == True).order_by(Challenge.date.desc()).all()

def deactivate_challenges(challenger_name):
    challenger = session.query(Player).filter(Player.name == challenger_name).one()
    try:
        challenge = session.query(Challenge).filter(Challenge.challenger == challenger).filter(Challenge.active == True).one()
    except NoResultFound:
        return

    challenge.active = False
    session.commit()

def link_challenge_to_game(game):
    try:
        challenge = session.query(Challenge).filter(Challenge.challenger_id == game.challenger_id).filter(Challenge.defender_id == game.defender_id).filter(Challenge.active == True).one()
    except NoResultFound:
        return
    challenge.game_id = game.id
    challenge.active = False
    session.commit()


if __name__ == '__main__':
    #add_challenge('Floris', 'Lou')
    #from data.database import Game
    #game = session.query(Game).filter(Game.id == 1).one()
    #link_challenge_to_game(game)
    #add_challenge('Lou', 'Floris')
    #deactivate_challenges('Floris')
    #print(get_challenges())
    pass

