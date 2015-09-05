
from data.datamodel import Game, Player
from data.dbsession import session

def save_game(challenger, defender, scores, comment):
    session.add(
        Game(
            challenger=session.query(Player).filter(Player.name==challenger).one(),
            defender=session.query(Player).filter(Player.name==defender).one(),
            score_challenger_1 = scores[0][0],
            score_defender_1 = scores[0][1],
            score_challenger_2 = scores[1][0],
            score_defender_2 = scores[1][1],
            score_challenger_3 = scores[2][0] if len(scores) == 3 else None,
            score_defender_3 = scores[2][1] if len(scores) == 3 else None,
            game_comment=comment,
        )
    )
    session.commit()

def get_games():
    return session.query(Game).order_by(Game.date.desc()).all()


if __name__ == '__main__':
    save_game('Floris', 'Lou', ((11,7), (11,9)), 'good game')
    #print(get_games())
    pass
