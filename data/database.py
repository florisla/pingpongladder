from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Sequence
from sqlalchemy import Boolean, Integer, String, Date, LargeBinary
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///tournament.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Player(Base):

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

class Tag(Base):

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


class Game(Base):

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


class Shout(Base):

    __tablename__ = 'shouts'
    id = Column(Integer, Sequence('shout_id_seq'), primary_key=True)
    shout = Column(String(128), nullable=False)
    session.commit()
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    date = Column(Date, nullable=False, default=func.now())

    player = relationship("Player", backref=backref('shouts', order_by=id))

    def __repr__(self):
        return "Shout(player_id={}, shout='{}')".format(
            self.player_id,
            self.shout
        )


class Challenge(Base):

    __tablename__ = 'challenges'
    id = Column(Integer, Sequence('shout_id_seq'), primary_key=True)
    challenger_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    defender_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    date = Column(Date, nullable=False, default=func.now())
    active = Column(Boolean, default=True, nullable=False)

    challenger = relationship("Player", foreign_keys=[challenger_id], backref=backref('offensive_challenges', order_by=id))
    defender = relationship("Player", foreign_keys=[defender_id], backref=backref('defensive_challenges', order_by=id))

    def __repr__(self):
        return "Challenge(challenger_id={}, defender_id={}, active={})".format(
            self.challenger_id,
            self.defender_id,
            self.active
        )

def create():
    Base.metadata.create_all(engine)

def add_players():
    session.add_all([
        Player(name='Lou', full_name='Lou Vervecken', initial_rank=13, tags=[
            Tag(tag='voorstopper'),
        ]),
        Player(name='Floris', full_name='Floris Lambrechts', initial_rank=5, tags=[
            Tag(tag='midvoor'),
        ]),
    ])
    session.commit()

def add_games():
    import datetime
    players = ['Lou', 'Floris']

    session.add(
        Game(
            challenger=session.query(Player).filter(Player.name==players[0]).one(),
            defender=session.query(Player).filter(Player.name==players[1]).one(),
            score_challenger_1 = 10,
            score_defender_1 = 12,
            score_challenger_2 = 14,
            score_defender_2 = 16,
            game_comment='test',
        )
    )
    session.commit()

def query_filter_by():
    our_user = session.query(Player).filter_by(name='Floris').first()
    print(our_user, our_user.id)

def query_on_class() :
    for player in session.query(Player).order_by(Player.id):
         print(player.name, player.full_name, player.id)

def query_on_entities():
    for name,id in session.query(Player.name, Player.id):
        print(name, id)

def multiple_filter():
    for player in session.query(Player) \
            .filter(Player.name=='Floris') \
            .filter(Player.full_name=='Floris Lambrechts'):
        print(player)

def filter_with_in():
    for player in session.query(Player) \
            .filter(Player.name.in_(['Lou', 'Floris'])):
        print(player)

# execute admin query

# FIXME globalize session

if __name__ == '__main__':
    # create()
    # add_players()
    add_games()
    # query_filter_by()
    # query_on_class()
    # query_on_entities()
    # multiple_filter()
    # query_with_in
    pass

