
from flask import g, render_template, json
import pytz

from data.games import get_games
from application import app


@app.route('/ranking')
def show_ranking():
    ranking = [dict(rank=player[0]+1, name=player[1]) for player in enumerate(g.ranking)]
    return render_template(
        'show_ranking.html',
        ranking=ranking,
    )


@app.route('/ranking/data')
def show_ranking_data():
    return json.jsonify(
        positions=g.positions,
        absences=g.absences,
        challengers=list(g.challengers),
        challengees=list(g.defenders),
    )


def swap_ranking(winner, loser):
    """
    Indexes are high-ranked first, so 1 is 'higher' on the ranking than 11.
    """
    won, lost = g.ranking.index(winner), g.ranking.index(loser)

    if won <= lost:
        # winner is already higher ranked (lower rank number)
        # so no swap is necessary
        return 0

    g.ranking[won], g.ranking[lost] = g.ranking[lost], g.ranking[won]
    return 1


def player2_won(player1_scores, player2_scores):
    if isinstance(player1_scores[0], str):
        player1_scores = [int(score) if len(score) > 0 else 0 for score in player1_scores]
        player2_scores = [int(score) if len(score) > 0 else 0 for score in player2_scores]
    if player1_scores[2] is None:
        player1_scores[2] = 0
        player2_scores[2] = 0

    won_games = len(
        [score for score in zip(player1_scores, player2_scores) if score[1] > score[0]]
    )
    return won_games > 1


def calculate_ranking():
    if hasattr(g, 'swaps'):
        return
    g.swaps = []
    # load all games
    g.games = get_games()
    g.positions = {player: [-i - 1] for i, player in enumerate(g.ranking)}
    g.game_details = []

    is_participating = set()

    g.ranking = g.original_ranking[:]

    # for each game, determine the winner and swap ranking with the loser if necessary
    for game in g.games:
        is_participating.add(game.challenger.name)
        is_participating.add(game.defender.name)

        challenger_lost = player2_won(
            [game.score_challenger_1, game.score_challenger_2, game.score_challenger_3],
            [game.score_defender_1, game.score_defender_2, game.score_defender_3]
        )
        if challenger_lost:
            game.winner = game.defender.name
            if swap_ranking(game.defender.name, game.challenger.name):
                g.swaps.append((game.defender.name, game.challenger.name))
        else:
            game.winner = game.challenger.name
            if swap_ranking(game.challenger.name, game.defender.name):
                g.swaps.append((game.challenger.name, game.defender.name))

        # convert
        g.game_details.append(dict(
            challenger=dict(
                name=game.challenger.name, rank=abs(g.positions[game.challenger.name][-1])
            ),
            challengee=dict(
                name=game.defender.name, rank=abs(g.positions[game.defender.name][-1])
            ),
            scores=[
                (game.score_challenger_1, game.score_defender_1),
                (game.score_challenger_2, game.score_defender_2),
                (game.score_challenger_3, game.score_defender_3),
            ],
            winner=game.defender.name if challenger_lost else game.challenger.name,
            index=len(g.positions[game.challenger.name]),
            date=game.local_date.strftime("%Y-%m-%d %H:%M:%S"),
        ))
        game_index = len(g.game_details)

        drops = (
            (player, drop_at)
            for player, drop_at in g.drops.items()
            if drop_at == game_index
        )
        for player, drop_at in drops:
            # move the quitter to the bottom of the ranking
            g.ranking.remove(player)
            g.ranking.append(player)

        # log all current positions for all players
        for i, player in enumerate(g.ranking):
            if player in is_participating:
                g.positions[player].append(i + 1)
            else:
                g.positions[player].append(-i - 1)
