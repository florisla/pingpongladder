
import datetime
import random

from flask import render_template, json, g, session, abort, request, flash, redirect, url_for
import bleach

from application import app
from ranking import player2_won
from data.games import save_game
from data.challenges import link_challenge_to_game
from data.shouts import save_shout


@app.route('/games')
def show_games():
    return render_template(
        'show_games.html',
        games=list(reversed(g.games)),
        players=g.ranking,
        swaps=g.swaps,
    )


@app.route('/games/data')
def show_game_data_json():
    return json.jsonify(game_details=g.game_details)


@app.route('/games/<player>')
def show_games_for_player(player):
    return render_template(
        'show_games.html',
        games=[
            game for game
            in list(reversed(g.games))
            if game.challenger.name == player
            or game.defender.name == player
        ],
        players=g.ranking,
        swaps=g.swaps,
        filtered_player=player,
    )


@app.route('/games/<player>/vs/<other_player>')
def show_games_for_players(player, other_player):
    return render_template(
        'show_games.html',
        games=[
            game for game
            in list(reversed(g.games))
            if game.challenger.name in[player, other_player]
            and game.defender.name in [player, other_player]
        ],
        players=g.ranking,
        swaps=g.swaps,
        filtered_player=player,
        filtered_player2=other_player,
    )


@app.route('/game/add', methods=['POST'])
def add_game():
    if not session.get('logged_in'):
        abort(401)
    if request.form['player1'] not in g.ranking:
        abort(401)
    if request.form['player2'] not in g.ranking:
        abort(401)

    scores = (
        (request.form['player1_score1'], request.form['player2_score1']),
        (request.form['player1_score2'], request.form['player2_score2']),
        (request.form['player1_score3'], request.form['player2_score3']),
    )

    for game in scores:
        for score in game:
            if len(score) > 0 and not score.isnumeric():
                abort(401)

    comment = bleach.clean(
        request.form.get('comment', ''),
        tags=app.config['ALLOWED_TAGS']['game_comment'],
        attributes=app.config['ALLOWED_ATTRS']['game_comment'],
    )

    game = save_game(
        request.form['player1'],
        request.form['player2'],
        scores,
        comment,
        date=datetime.datetime.now() - datetime.timedelta(
            hours=app.config.get('GAME_DATE_TIME_OFFSET_H', 0)
        )
    )
    flash("Game result was saved")

    link_challenge_to_game(game)
    flash("Open challenge (if any) was removed")

    challenger_lost = player2_won(
        [scores[0][0], scores[1][0], scores[2][0]],
        [scores[0][1], scores[1][1], scores[2][1]]
    )
    if challenger_lost:
        winner = game.defender
        shout_message = '<b>{player1}</b> could not win from {nick} <b>{player2}</b> {score[0][0]}-{score[0][1]} {score[1][0]}-{score[1][1]} {score[2][0]}{dash}{score[2][1]}{comment}'
    else:
        winner = game.challenger
        shout_message = '{nick}<b>{player1}</b> beat <b>{player2}</b> {score[0][0]}-{score[0][1]} {score[1][0]}-{score[1][1]} {score[2][0]}{dash}{score[2][1]}{comment}'

    if len(comment) > 0:
        comment = '<div class="gamecomment">{comment}</div>'.format(comment=comment)

    # pick one of the winner's nicknames
    nickname = ''
    if any(winner.tags):
        nickname = " '<span class=\"tag\">{random_tag}</span>' ".format(
            random_tag=random.choice(winner.tags).tag
        )

    save_shout(None, shout_message.format(
        player1=request.form['player1'],
        player2=request.form['player2'],
        nick=nickname,
        score=scores,
        dash='-' if request.form['player1_score3'] else '',
        comment=comment
    ))

    return redirect(url_for('show_games'))
