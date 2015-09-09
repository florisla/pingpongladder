
import sqlite3
import datetime
from flask import request, session, g, redirect, url_for, abort, \
                  render_template, flash, json

import hashlib
import random

from app import app
from data.database import db
import data.admin

from data.players import get_players, player_is_admin, set_player_absence
from data.shouts import get_shouts, save_shout
from data.challenges import get_challenges, link_challenge_to_game, deactivate_challenges, add_challenge
from data.tags import add_tag
from data.games import get_games, save_game


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

    return 1 < len([score for score in zip(player1_scores, player2_scores) if score[1] > score[0]])

def calculate_ranking():
    if hasattr(g, 'swaps'):
        return
    g.swaps = []
    # load all games
    g.games = get_games()
    g.positions = {player: [-i - 1] for i,player in enumerate(g.ranking)}
    g.game_details = []

    is_participating = set()

    g.ranking = g.original_ranking[:]

    # for each game, determine the winner and swap ranking with the loser if necessary
    for game in g.games:
        is_participating.add(game.challenger.name)
        is_participating.add(game.defender.name)

        challenger_lost = player2_won([game.score_challenger_1, game.score_challenger_2, game.score_challenger_3], [game.score_defender_1, game.score_defender_2, game.score_defender_3]);
        if challenger_lost:
            game.winner = game.defender.name
            if swap_ranking(game.defender.name, game.challenger.name):
                g.swaps.append((game.defender.name, game.challenger.name))
        else:
            game.winner = game.challenger.name
            if swap_ranking(game.challenger.name, game.defender.name):
                g.swaps.append((game.challenger.name, game.defender.name))

        g.game_details.append(dict(
            challenger=dict(name=game.challenger.name, rank=abs(g.positions[game.challenger.name][-1])),
            challengee=dict(name=game.defender.name, rank=abs(g.positions[game.defender.name][-1])),
            scores=[
                (game.score_challenger_1, game.score_defender_1),
                (game.score_challenger_2, game.score_defender_2),
                (game.score_challenger_3, game.score_defender_3),
            ],
            winner=game.defender.name if challenger_lost else game.challenger.name,
            index=len(g.positions[game.challenger.name]),
            date=str(game.date),
        ))
        game_index = len(g.game_details)

        drops = ((player,drop_at) for player,drop_at in g.drops.items() if drop_at == game_index)
        for player,drop_at in drops:
            # move the quitter to the bottom of the ranking
            g.ranking.remove(player)
            g.ranking.append(player)

        # log all current positions for all players
        for i,player in enumerate(g.ranking):
            if player in is_participating:
                g.positions[player].append(i + 1)
            else:
                g.positions[player].append(-i - 1)

@app.before_request
def before_request():
    if '/static/' in request.url:
        # no need to do dynamic things on non-dynamic resources
        return

    # FIXME: do the sorting according to rank already in get_players!
    g.players = get_players()
    g.ranking = [
        player.name for player in sorted(
            g.players,
            key=lambda player: player.initial_rank
        )
    ]
    g.original_ranking = g.ranking[:]
    g.shouts = get_shouts()
    g.challenges = get_challenges()
    g.challengers = set(challenge.challenger.name for challenge in g.challenges)
    g.defenders = set(challenge.defender.name for challenge in g.challenges)
    g.challenged_players = sorted(g.challengers.union(g.defenders))
    g.absences = {
                 p.name:str(p.absence) for p in g.players
                 if p.absence is not None
    }
    g.drops = {
        p.name:p.rank_drop_at_game for p in g.players
        if p.rank_drop_at_game is not None
    }

    calculate_ranking()

@app.route('/')
def show_home():
    return render_template('index.html',
        shouts=g.shouts,
        challenged_players=g.challenged_players,
    )

@app.route('/ranking')
def show_ranking():
    ranking = [dict(rank=player[0]+1, name=player[1]) for player in enumerate(g.ranking)]
    return render_template(
        'show_ranking.html',
        ranking=ranking,
    )

@app.route('/ranking/data')
def show_ranking_json():
    return json.jsonify(
        positions=g.positions,
        absences=g.absences,
        challengers=list(g.challengers),
        challengees=list(g.defenders),
    )

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
        games=[g for g in list(reversed(g.games)) if g.challenger.name == player or g.defender.name == player],
        players=g.ranking,
        swaps=g.swaps,
        filtered_player=player,
    )

@app.route('/games/<player>/vs/<other_player>')
def show_games_for_players(player, other_player):
    return render_template(
        'show_games.html',
        games=[g for g in list(reversed(g.games)) if g.challenger.name in[player, other_player] and g.defender.name in [player, other_player]],
        players=g.ranking,
        swaps=g.swaps,
        filtered_player=player,
        filtered_player2=other_player,
    )

@app.route('/games/raw')
def show_game_data_raw():
    return json.jsonify(game_details=g.games)

@app.route('/challenges')
def show_challenges():
    return render_template(
        'show_challenges.html',
        challenges=g.challenges,
        players=g.ranking,
        absence=g.absences,
    )

@app.route('/players')
def show_players():

    sorted_players = sorted(g.players, key=lambda p: p.name)

    return render_template('show_players.html',
        players=sorted_players,
        ranking=g.ranking,
        absence='',
    )

@app.route('/players/data')
def get_players_data():
    players = {name:dict(occupied=(name in g.challenged_players)) for name in g.ranking}
    return json.jsonify(players=players)

@app.route('/rules')
def show_rules():
    return render_template('show_rules.html')

@app.route('/stats')
def show_stats():
    return render_template('show_stats.html')

@app.route('/shoutbox')
def shoutbox():
    get_shouts(2000)
    return render_template(
        'show_shoutbox.html',
        shouts = g.shouts,
    )

@app.route('/player/absence/save', methods=['POST'])
def save_absence():
    if not session.get('logged_in'):
        abort(401)
    if request.form.get('absence') is None:
        abort(401)

    set_player_absence(session['username'], request.form['absence'])
    flash("Absence was saved")
    return redirect(url_for('show_players'))

@app.route('/player/tag/add', methods=['POST'])
def add_tag_to_player():
    if not session.get('logged_in'):
        abort(401)
    if request.form.get('player') is None or len(request.form['player']) == 0:
        abort(401)
    if request.form.get('tag') is None or len(request.form['tag']) == 0:
        abort(401)

    add_tag(request.form['player'], request.form['tag'].lower())
    flash("Tag was saved")

    save_shout(None, "Someone saw it fit to attribute <b>{}</b> with the tag <span class=\"tag\">{}</span>.".format(
        request.form['player'],
        request.form['tag'].lower()
    ))

    return redirect(url_for('show_players'))

@app.route('/game/add', methods=['POST'])
def add_game():
    if not session.get('logged_in'):
        abort(401)

    comment = request.form['comment'] if 'comment' in request.form else ''
    game = save_game(
        request.form['player1'],
        request.form['player2'],
        (
            (request.form['player1_score1'], request.form['player2_score1']),
            (request.form['player1_score2'], request.form['player2_score2']),
            (request.form['player1_score3'], request.form['player2_score3']),
        ),
        comment,
    )
    flash("Game result was saved")
    link_challenge_to_game(game)
    flash("Open challenge (if any) was removed")

    challenger_lost = player2_won([request.form['player1_score1'], request.form['player1_score2'], request.form['player1_score3']], [request.form['player2_score1'], request.form['player2_score2'], request.form['player2_score3']]);
    if challenger_lost:
        winner = game.defender
        shout_message = '<b>{player1}</b> could not win from {nick} <b>{player2}</b> {player1_score1}-{player2_score1} {player1_score2}-{player2_score2} {player1_score3}{dash}{player2_score3}{comment}'
    else:
        winner = game.challenger
        shout_message = '{nick}<b>{player1}</b> beat <b>{player2}</b> {player1_score1}-{player2_score1} {player1_score2}-{player2_score2} {player1_score3}{dash}{player2_score3}{comment}'

    if len(comment) > 0:
        comment = '<div class="gamecomment">{0}</div>'.format(comment)

    # pick one of the winner's nicknames
    nickname = ''
    if any(winner.tags):
        nickname = " '<span class=\"tag\">{}</span>' ".format(
            random.choice(winner.tags).tag
        )

    save_shout(None, shout_message.format(
        player1=request.form['player1'],
        player2=request.form['player2'],
        nick=nickname,
        player1_score1=request.form['player1_score1'],
        player1_score2=request.form['player1_score2'],
        player1_score3=request.form['player1_score3'],
        player2_score1=request.form['player2_score1'],
        player2_score2=request.form['player2_score2'],
        player2_score3=request.form['player2_score3'],
        dash='-' if request.form['player1_score3'] else '',
        comment=comment
    ))

    return redirect(url_for('show_games'))

@app.route('/challenges/add', methods=['POST'])
def add_challenge_page():
    if not session.get('logged_in'):
        abort(401)

    # do not log a challenge to anyone who is the source or target
    # of another challenge

    if any(chal for chal in g.challenges if chal.challenger.name == request.form['player1']):
        flash("You already have an open challenge.", 'error')
        return redirect(url_for('show_challenges'))
    if any(chal for chal in g.challenges if chal.defender.name == request.form['player1']):
        flash("You are already challanged.", 'error')
        return redirect(url_for('show_challenges'))
    if any(chal for chal in g.challenges if chal.challenger.name == request.form['player2']):
        flash("Player {} already has an open challenge.".format(request.form['player2']), 'error')
        return redirect(url_for('show_challenges'))
    if any(chal for chal in g.challenges if chal.defender.name == request.form['player2']):
        flash("Player {} is already challenged.".format(request.form['player2']), 'error')
        return redirect(url_for('show_challenges'))

    add_challenge(request.form['player1'], request.form['player2'])
    flash("Challenge was saved")

    save_shout(None, "<b>{0}</b> challenged <b>{1}</b>".format(
        request.form['player1'],
        request.form['player2']
    ))

    return redirect(url_for('show_challenges'))

@app.route('/challenges/remove', methods=['POST'])
def remove_challenge():
    if not session.get('logged_in'):
        abort(401)

    deactivate_challenges(session['username'])
    flash("Your current challenge (if any) was removed")
    return redirect(url_for('show_challenges'))

@app.route('/shoutbox/shout', methods=['POST'])
def add_shout():
    if not session.get('logged_in'):
        abort(401)

    save_shout(session['username'], request.form['shout'])
    flash('Your shout is heard.')
    return redirect(url_for('show_home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        hasher = hashlib.sha512()
        salted_password = app.config['PASSWORD_SALT'] + request.form['password'].encode('utf-8')
        hasher.update(salted_password)
        password_hash = hasher.digest()
        expected_password_hash = b'O\x9e\xba\xa5\x8cgH\x1bO\xaa\xe7\x93\x84\x85\xe1\xbd\x1d\x87\xfa\x1a\x08z$\xc8\xfd+T\xdeM\xf6\xa9\xb4\xc5`\xa4\x1d\x9d\xd6\xa5\xdc\x01\xcc\xc1J\xb4\x81\xc1\xab\x0b\x0fO\xccf\x16^\xb0\x0f\x91\xfc\xc1`\xbd\x02]'

        if request.form['username'] not in g.ranking:
            error = 'Invalid username'
        elif password_hash != app.config['PASSWORD_HASH']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            flash("You were logged in as '{}'".format(session['username']))
            return redirect(url_for('show_home'))
    return render_template('login.html', error=error, users=g.ranking)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_home'))


if __name__ == '__main__':
    app.run()

