from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date, LargeBinary, Sequence
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///tournament.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Player(Base):

    __tablename__ = 'players'
    id = Column(Integer, Sequence('player_id_seq'), primary_key=True)
    name = Column(String(15), nullable=False)
    full_name = Column(String(25), nullable=False)
    admin = Column(Integer, default=0, nullable=False)
    initial_rank = Column(Integer)
    rank_drop_at_game = Column(Integer)
    absence = Column(Date)
    password_salt = Column(String(20))
    password_hash = Column(LargeBinary(128))

    def __repr__(self):
        return "Player(name='{}', full_name='{}'>".format(
            self.name, self.full_name
        )

class Tag(Base):

    __tablename__ = 'tags'
    id = Column(Integer, Sequence('player_id_seq'), primary_key=True)
    tag = Column(String(15), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'))
    player = relationship("Player", backref=backref('tags', order_by=id))

    def __repr__(self):
        return "Tag(tag='{}', player_id={}".format(
            self.tag,
            self.player_id,
        )


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
