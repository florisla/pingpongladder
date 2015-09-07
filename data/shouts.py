
from data.datamodel import Player, Shout
from tournament import db

def get_shouts(max_shouts=20):
    return db.session.query(Shout).order_by(Shout.date).order_by(Shout.id).limit(max_shouts).all()

def save_shout(author, shout_message):
    db.session.add(Shout(
        shout = shout_message,
        player = db.session.query(Player).filter(Player.name == author).one(),
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


if __name__ == '__main__':
    #save_shout('Floris', 'test shout')
    #update_shout(2, 'test shout2')
    #delete_shout(2)
    #print(get_shouts())
    pass

