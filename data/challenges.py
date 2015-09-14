
from datetime import datetime, timedelta
import random

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import func

from data.datamodel import Challenge, Player, Game
from data.database import db

def add_challenge(challenger, defender, active=True):
    db.session.add(Challenge(
        challenger=db.session.query(Player).filter(Player.name == challenger).one(),
        defender=db.session.query(Player).filter(Player.name == defender).one(),
        active=active,
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

def may_challenge(player_name, cool_down_time_range_m, cool_down_random_salt):
    player = db.session.query(Player).filter(Player.name == player_name).one()

    most_recent_challenge_game_date = db.session.\
        query(func.max(Game.date)).\
        filter(Game.challenger == player).\
        first()[0]

    if not most_recent_challenge_game_date:
        return True

    # find for this game date, the 'cooldown' time in minutes
    # this is random out of a range, but a random value which is unique and constant
    # per game date/time (seeded)
    random.seed(cool_down_random_salt + str(most_recent_challenge_game_date))
    cooldown_period_m = random.randint(*cool_down_time_range_m)

    # player may challenge again if more minutes have passed
    # than the cooldown period requires
    lapsed_minits = (datetime.now() - most_recent_challenge_game_date).total_seconds() / 60
    return lapsed_minits > cooldown_period_m
