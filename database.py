from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Sequence
from sqlalchemy import Boolean, Integer, String, Date, LargeBinary
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
    date = Column(Date, nullable=False)
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
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    date = Column(Date, nullable=False)

    player = relationship("Player", backref=backref('shouts', order_by=id))


class Challenge(Base):

    __tablename__ = 'challenges'
    id = Column(Integer, Sequence('shout_id_seq'), primary_key=True)
    challenger_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    defender_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    date = Column(Date, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    challenger = relationship("Player", foreign_keys=[challenger_id], backref=backref('offensive_challenges', order_by=id))
    defender = relationship("Player", foreign_keys=[defender_id], backref=backref('defensive_challenges', order_by=id))


if True:
    Base.metadata.create_all(engine)

if False:
    # add a single player
    player = Player(name='Floris', full_name='Floris Lambrechts')
    player.tags = [
        Tag(tag='ok'),
        Tag(tag='player'),
        Tag(tag='pingpong'),
    ]
    print(player.name, player.full_name, player.id)
    session.add(player)
    session.commit()

if True:
    # add a single player with integrated tags
    player = Player(name='Lou', full_name='Lou Vervecken', tags=[
        Tag(tag='voorstopper'),
    ])
    session.add(player)
    session.commit()

if False:
    # add multiple players
    session.add_all([
        Player(name='Floris', full_name='Floris Lambrechts', initial_rank=3),
        Player(name='Lou', full_name='Lou Vervecken', initial_rank=5),
        Player(name='Roel', full_name='Roel Aerts', initial_rank=9),
    ])
    print(session.new)
    session.commit()

if True:
    # query with filter_by
    our_user = session.query(Player).filter_by(name='Floris').first()
    print(our_user, our_user.id)

if True:
    # query on class
    for player in session.query(Player).order_by(Player.id):
         print(player.name, player.full_name, player.id)

if True:
    # query on entities
    for name,id in session.query(Player.name, Player.id):
        print(name, id)

if True:
    # multiple filter()
    for player in session.query(Player) \
            .filter(Player.name=='Floris') \
            .filter(Player.full_name=='Floris Lambrechts'):
        print(player)

if True:
    # query with IN
    for player in session.query(Player) \
            .filter(Player.name.in_(['Lou', 'Floris'])):
        print(player)
