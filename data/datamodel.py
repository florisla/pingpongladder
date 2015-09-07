from sqlalchemy import Column, ForeignKey, Sequence
from sqlalchemy import Boolean, Integer, String, Date, LargeBinary
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import func

from tournament import db


class Player(db.Model):

    __tablename__ = 'players'
    id = Column(Integer, Sequence('player_id_seq'), primary_key=True)
    name = Column(String(15), nullable=False)
    full_name = Column(String(25), nullable=False)
    admin = Column(Boolean, default=False, nullable=False)
    initial_rank = Column(Integer, nullable=False)
    rank_drop_at_game = Column(Integer, nullable=True)
    absence = Column(Date, nullable=True)
    password_salt = Column(LargeBinary(20))
    password_hash = Column(LargeBinary(128))

    def __repr__(self):
        return "Player(name='{}', full_name='{}'>".format(
            self.name, self.full_name
        )


class Tag(db.Model):

    __tablename__ = 'tags'
    id = Column(Integer, Sequence('tag_id_seq'), primary_key=True)
    tag = Column(String(15), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)

    player = relationship("Player", backref=backref('tags', order_by=id))

    def __repr__(self):
        return "Tag(tag='{}', player_id={}".format(
            self.tag,
            self.player_id,
        )


class Game(db.Model):

    __tablename__ = 'games'
    id = Column(Integer, Sequence('game_id_seq'), primary_key=True)
    date = Column(Date, nullable=False, default=func.now())
    challenger_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    defender_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    score_challenger_1 = Column(Integer, nullable=False)
    score_defender_1 = Column(Integer, nullable=False)
    score_challenger_2 = Column(Integer, nullable=False)
    score_defender_2 = Column(Integer, nullable=False)
    score_challenger_3 = Column(Integer, nullable=True)
    score_defender_3 = Column(Integer, nullable=True)
    game_comment = Column(String(60), nullable=True)

    challenger = relationship("Player", foreign_keys=[challenger_id], backref=backref('challenge_games', order_by=id))
    defender = relationship("Player", foreign_keys=[defender_id], backref=backref('defense_games', order_by=id))

    def __repr__(self):
        return "Game(challenger='{}', defender='{}', date='{}'".format(
            self.challenger.name,
            self.defender.name,
            self.date,
        )


class Shout(db.Model):

    __tablename__ = 'shouts'
    id = Column(Integer, Sequence('shout_id_seq'), primary_key=True)
    shout = Column(String(128), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    date = Column(Date, nullable=False, default=func.now())

    player = relationship("Player", backref=backref('shouts', order_by=id))

    def __repr__(self):
        return "Shout(player_id={}, shout='{}')".format(
            self.player_id,
            self.shout
        )


class Challenge(db.Model):

    __tablename__ = 'challenges'
    id = Column(Integer, Sequence('shout_id_seq'), primary_key=True)
    challenger_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    defender_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    date = Column(Date, nullable=False, default=func.now())
    active = Column(Boolean, default=True, nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=True)

    challenger = relationship("Player", foreign_keys=[challenger_id], backref=backref('offensive_challenges', order_by=id))
    defender = relationship("Player", foreign_keys=[defender_id], backref=backref('defensive_challenges', order_by=id))
    game = relationship("Game", backref=backref('challenge', order_by=id))

    def __repr__(self):
        return "Challenge(challenger_id={}, defender_id={}, active={})".format(
            self.challenger_id,
            self.defender_id,
            self.active
        )

