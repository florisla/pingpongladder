
from database import Challenge, Player
from database import session
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

# disable challenge for a game

if __name__ == '__main__':
    #add_challenge('Floris', 'Lou')
    #add_challenge('Lou', 'Floris')
    deactivate_challenges('Floris')
    #print(get_challenges())

