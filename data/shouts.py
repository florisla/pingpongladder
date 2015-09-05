
from data.database import Player, Shout
from data.dbsession import session

def get_shouts(max_shouts=20):
    return session.query(Shout).order_by(Shout.date).order_by(Shout.id).limit(max_shouts).all()

def save_shout(author, shout_message):
    session.add(Shout(
        shout = shout_message,
        player = session.query(Player).filter(Player.name == author).one(),
    ))
    session.commit()

def update_shout(shout_id, shout_message):
    # load shout
    shout = session.query(Shout).filter(Shout.id == shout_id).one()
    shout.shout = shout_message
    session.commit()

def delete_shout(shout_id):
    session.query(Shout).filter(Shout.id == shout_id).delete()
    session.commit()


if __name__ == '__main__':
    #save_shout('Floris', 'test shout')
    #update_shout(2, 'test shout2')
    #delete_shout(2)
    #print(get_shouts())
    pass

