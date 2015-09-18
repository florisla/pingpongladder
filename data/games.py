
import pytz

from flask import g

from data.datamodel import Game, Player
from data.database import db


def save_game(challenger, defender, scores, comment, date):
    game = Game(
        challenger=db.session.query(Player).filter(Player.name==challenger).one(),
        defender=db.session.query(Player).filter(Player.name==defender).one(),
        score_challenger_1 = scores[0][0],
        score_defender_1 = scores[0][1],
        score_challenger_2 = scores[1][0],
        score_defender_2 = scores[1][1],
        score_challenger_3 = scores[2][0] if len(scores) == 3 else None,
        score_defender_3 = scores[2][1] if len(scores) == 3 else None,
        game_comment=comment,
        date=date
    )
    db.session.add(game)
    db.session.commit()

    return game


def get_games():
    games = db.session.query(Game).order_by(Game.date.asc()).all()

        # calculate update game dates in local timezonepyth
    for game in games:
        # date from database is in UTC, and we convert it to local timezone
        game.local_date = pytz.utc.localize(game.date).astimezone(g.website_timezone)
        game.local_date_string = game.local_date.strftime("%Y-%m-%d %H")

    return games
