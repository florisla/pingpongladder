
from datetime import datetime, timedelta

from data.database import db
from data.datamodel import TableReservation, Player


def get_reservations():
    now = datetime.utcnow()
    now_one_hour_ago = now - timedelta(hours=1)
    print(now, now_one_hour_ago)
    reservations =  db.session.query(TableReservation) \
        .filter(TableReservation.date > now_one_hour_ago) \
        .all()

    for reservation in reservations:
        reservation.minutes_ago = int((now - reservation.date).total_seconds() // 60)

    return reservations


def save_reservation(player):
    db.session.add(TableReservation(
        reserver=db.session.query(Player).filter(Player.name == player).one(),
        date=datetime.utcnow(),
    ))
    db.session.commit()
