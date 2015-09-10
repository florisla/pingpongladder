
from data.datamodel import Player, Shout
from data.database import db

def get_shouts(max_shouts=20):
    return db.session.query(Shout).order_by(Shout.date.desc()).order_by(Shout.id.desc()).limit(max_shouts).all()

def save_shout(author, shout_message):
    player = None
    if author is not None:
        player = db.session.query(Player).filter(Player.name == author).one()

    db.session.add(Shout(
        shout=shout_message,
        player=player,
    ))
    db.session.commit()

def update_shout(shout_id, shout_message):
    # load shout
    shout = db.session.query(Shout).filter(Shout.id == shout_id).one()
    shout.shout = shout_message
    db.session.commit()

def delete_shout(shout_id):
    db.session.query(Shout).filter(Shout.id == shout_id).delete()
    db.session.commit()
