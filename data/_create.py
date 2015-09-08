
from data.database import db
from data.datamodel import *

if __name__ == '__main__':
    db.create_all()

    db.session.add(Player(
        name='admin',
        full_name='Administrator',
        initial_rank=1,
        admin=True,
    ))
    db.session.commit()

    db.session

