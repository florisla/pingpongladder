
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from data.datamodel import Player, Challenge, Game, Shout, Tag

def connect():
    old_db = create_engine('sqlite:///../database.db').connect()
    new_engine = create_engine('sqlite:///../data/tournament.db').connect()
    Session = sessionmaker(bind=new_engine)
    new_session = Session()

    return old_db, new_session

def migrate_players(old_db, new_session):
    for name,full_name,initial_rank,absence,rank_drop_at_game,admin in old_db.execute(text('SELECT name,full_name,initial_rank,absence,rank_drop_at_game,admin FROM players')).fetchall():
        player = Player(name=name, full_name=full_name, initial_rank=initial_rank)
        absence = absence.strip()
        if absence != '' and absence != '?':
            player.absence = datetime.strptime(absence, '%Y-%m-%d')
        player.rank_drop_at_game = rank_drop_at_game
        player.admin = admin
        print(player)
        new_session.add(player)

def migrate_challenges(old_db, new_session):
    for player1,player2,date in old_db.execute(text('SELECT player1,player2,date FROM challenges')).fetchall():
        challenge_date=datetime.strptime(date, '%Y-%m-%d %H:%M')
        challenge = Challenge(
            challenger=new_session.query(Player).filter(Player.name == player1).one(),
            defender=new_session.query(Player).filter(Player.name == player2).one(),
            date=challenge_date,
        )
        print(challenge)
        new_session.add(challenge)

def migrate_games(old_db, new_session):
    for date,player1,player2,s11,s21,s12,s22,s13,s23,comment in old_db.execute(text('SELECT date,player1,player2,player1_score1,player2_score1,player1_score2,player2_score2,player1_score3,player2_score3,comment FROM games')).fetchall():
        game = Game(
            challenger=new_session.query(Player).filter(Player.name == player1).one(),
            defender=new_session.query(Player).filter(Player.name == player2).one(),
            score_challenger_1=s11,
            score_defender_1=s21,
            score_challenger_2=s12,
            score_defender_2=s22,
            score_challenger_3=s13,
            score_defender_3=s23,
            date=datetime.strptime(date, '%Y-%m-%d %H:%M'),
            game_comment=comment,
        )
        print(game)
        new_session.add(game)

def migrate_shouts(old_db, new_session):
    for player_name,message,date in old_db.execute(text('SELECT player, shout, date from shouts')).fetchall():
        try:
            player = new_session.query(Player).filter(Player.name == player_name).one()
        except:
            player = None
        shout = Shout(
            shout=message,
            player=player,
            date=datetime.strptime(date, '%Y-%m-%d %H:%M'),
        )
        print(shout)
        new_session.add(shout)

def migrate_tags(old_db, new_session):
    for player_name,tag_text in old_db.execute(text('SELECT player, tag from tags')).fetchall():
        player = new_session.query(Player).filter(Player.name == player_name).one()
        tag = Tag(
            player=new_session.query(Player).filter(Player.name == player_name).one(),
            tag=tag_text
        )
        print(tag)
        new_session.add(tag)


if __name__ == '__main__':
    old,new = connect()
    migrate_players(old, new)
    migrate_challenges(old, new)
    migrate_games(old, new)
    migrate_shouts(old, new)
    migrate_tags(old, new)

    new.commit()

