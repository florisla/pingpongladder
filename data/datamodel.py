from sqlalchemy import Column, ForeignKey, Sequence
from sqlalchemy import Boolean, Integer, String, Date, DateTime, LargeBinary, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import func

from data.database import db


class Player(db.Model):

    __tablename__ = 'players'
    id = Column(Integer, Sequence('player_id_seq'), primary_key=True)
    name = Column(String(15), nullable=False)
    full_name = Column(String(25), nullable=False)
    admin = Column(Boolean, default=False, nullable=False)
    initial_rank = Column(Integer, nullable=False)
    rank_drop_at_game = Column(Integer, nullable=True)
    absence = Column(Date, nullable=True)
    email_address = Column(String(25), nullable=True)
    password_salt = Column(LargeBinary(20))
    password_hash = Column(LargeBinary(128))

    def __repr__(self):
        return "Player(name='{player.name}', full_name='{player.full_name}'>".format(
            player=self
        )

    def __str__(self):
        return self.name


class Tag(db.Model):

    __tablename__ = 'tags'
    id = Column(Integer, Sequence('tag_id_seq'), primary_key=True)
    tag = Column(String(15), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)

    player = relationship("Player", backref=backref('tags', order_by=id))

    def __repr__(self):
        return "Tag(tag='{tag.tag}', player_id={tag.player_id}".format(tag=self)

    def __str__(self):
        return "{tag.player.name}: {tag.tag}".format(tag=self)


class Game(db.Model):

    __tablename__ = 'games'
    id = Column(Integer, Sequence('game_id_seq'), primary_key=True)
    date = Column(DateTime, nullable=False, default=func.now())
    challenger_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    defender_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    score_challenger_1 = Column(Integer, nullable=False)
    score_defender_1 = Column(Integer, nullable=False)
    score_challenger_2 = Column(Integer, nullable=False)
    score_defender_2 = Column(Integer, nullable=False)
    score_challenger_3 = Column(Integer, nullable=True)
    score_defender_3 = Column(Integer, nullable=True)
    game_comment = Column(Text, nullable=True)

    challenger = relationship("Player", foreign_keys=[challenger_id], backref=backref('challenge_games', order_by=id))
    defender = relationship("Player", foreign_keys=[defender_id], backref=backref('defense_games', order_by=id))

    def __repr__(self):
        return "Game(challenger='{game.challenger.name}', defender='{game.defender.name}', date='{game.date}'".format(game=self)

    def __str__(self):
        return "{game.challenger.name}-{game.defender.name} ({game.date:%Y-%m-%d})".format(game=self)


class Shout(db.Model):

    __tablename__ = 'shouts'
    id = Column(Integer, Sequence('shout_id_seq'), primary_key=True)
    shout = Column(Text, nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=True)
    date = Column(DateTime, nullable=False, default=func.now())

    player = relationship("Player", backref=backref('shouts', order_by=id))

    def __repr__(self):
        return "Shout(player_id={shout.player_id}, shout='{shout.shout}')".format(shout=self)

    def __str__(self):
        return "{player}: {shout}".format(
            player=self.player.name if self.player else 'system',
            shout=self.shout[0:50],
        )


class Challenge(db.Model):

    __tablename__ = 'challenges'
    id = Column(Integer, Sequence('shout_id_seq'), primary_key=True)
    challenger_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    defender_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    date = Column(DateTime, nullable=False, default=func.now())
    active = Column(Boolean, default=True, nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=True)

    challenger = relationship("Player", foreign_keys=[challenger_id], backref=backref('offensive_challenges', order_by=id))
    defender = relationship("Player", foreign_keys=[defender_id], backref=backref('defensive_challenges', order_by=id))
    game = relationship("Game", backref=backref('challenge', order_by=id))

    def __repr__(self):
        return "Challenge(challenger_id={challenge.challenger_id}, defender_id={challenge.defender_id}, active={challenge.active})".format(challenge=self)

    def __str__(self):
        return "{challenge.challenger.name}-{challenge.defender.name} {challenge.active}".format(challenge=self)


class TableReservation(db.Model):

    __tablename__ = 'reservations'
    id = Column(Integer, Sequence('reservation_id_seq'), primary_key=True)
    reserver_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    date = Column(DateTime, nullable=False, default=func.now())

    reserver = relationship("Player", foreign_keys=[reserver_id], backref=backref('table_reservations', order_by=id))

    def __repr__(self):
        return "TableReservation(reserver_id={reservation.reserver_id})".format(reservation=self)

    def __str__(self):
        return "{reservation.reserver.name} {reservation.date:%Y-%m-%d %H:%M}".format(reservation=self)
