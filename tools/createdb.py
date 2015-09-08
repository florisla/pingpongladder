
from data.database import db
from data.datamodel import *

ADD_ADMIN = False

if __name__ == '__main__':
    db.create_all()

    if ADD_ADMIN:
        db.session.add(Player(
            name='admin',
            full_name='Administrator',
            initial_rank=1,
            admin=True,
        ))
    db.session.commit()

