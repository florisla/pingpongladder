
import sqlite3
import datetime
from flask import Flask, request, session, g, redirect, url_for, abort, \
                  render_template, flash, json

import configuration
import hashlib

app = Flask(__name__)
app.config.from_object(configuration)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

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
    player2_won = 0
    if player1_scores[0] < player2_scores[0]:
        player2_won += 1
    if player1_scores[1] < player2_scores[1]:
        player2_won += 1
    if player1_scores[2] < player2_scores[2]:
        player2_won += 1

    return player2_won > 1

def get_shouts():
    cur = g.db.execute('select player, shout, date from shouts order by date desc, id desc')
    g.shouts = [dict(zip(['player', 'shout', 'date'], row)) for row in cur.fetchall()]

def calculate_ranking():
    if hasattr(g, 'swaps'):
        return
    g.swaps = []
    # load all games
    cur = g.db.execute('select date, player1, player2, player1_score1, player2_score1, player1_score2, player2_score2, player1_score3, player2_score3 from games order by date asc')
    g.games = [dict(zip(['date', 'player1', 'player2', 'player1_score1', 'player2_score1', 'player1_score2', 'player2_score2', 'player1_score3', 'player2_score3'], row)) for row in cur.fetchall() if row[1] != '']
    g.positions = {player: [-i - 1] for i,player in enumerate(g.ranking)}
    g.game_details = []

    is_participating = set()

    g.ranking = g.original_ranking[:]
    cur = g.db.execute('select date, player1, player2, player1_score1, player2_score1, player1_score2, player2_score2, player1_score3, player2_score3 from games order by date asc')
    # for each game, determine the winner and swap ranking with the loser if necessary

    for match_date, player1, player2, player1_score1, player2_score1, player1_score2, player2_score2, player1_score3, player2_score3 in cur.fetchall():
        if player1 in [None, ''] or player2 in [None, '']:
            # invalid row in the database; ignore
            continue

        is_participating.add(player1)
        is_participating.add(player2)

        challenger_won = player2_won([player1_score1, player1_score2, player1_score3], [player2_score1, player2_score2, player2_score3]);
        if challenger_won:
            if swap_ranking(player2, player1):
                g.swaps.append((player2, player1))
        else:
            if swap_ranking(player1, player2):
                g.swaps.append((player1, player2))

        g.game_details.append(dict(
            challenger=dict(name=player1, rank=abs(g.positions[player1][-1])),
            challengee=dict(name=player2, rank=abs(g.positions[player2][-1])),
            scores=[(player1_score1, player2_score1), (player1_score2, player2_score2), (player1_score3, player2_score3)],
            winner=player2 if challenger_won else player1,
            index=len(g.positions[player1]),
            date=match_date,
        ))

        # log all current positions for all players
        for i,player in enumerate(g.ranking):
            if player in is_participating:
                g.positions[player].append(i + 1)
            else:
                g.positions[player].append(-i - 1)

@app.before_request
def before_request():
    g.db = connect_db()
    g.ranking = app.config['PLAYERS'][:]
    g.original_ranking = app.config['PLAYERS'][:]
    try:
        calculate_ranking()
        get_shouts()
    except Exception as e:
        flash(e)

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_home():
    return render_template('index.html', shouts=g.shouts[:20])

@app.route('/ranking')
def show_ranking():
    ranking = [dict(rank=player[0]+1, name=player[1]) for player in enumerate(g.ranking)]
    return render_template(
        'show_ranking.html',
        ranking=ranking,
    )

@app.route('/ranking/data')
def show_ranking_json():
    return json.jsonify(g.positions)

@app.route('/games')
def show_games():

    return render_template(
        'show_games.html',
        games=g.games,
        players=app.config['PLAYERS'],
        swaps=g.swaps,
    )

@app.route('/games/data')
def show_game_data_json():
    return json.jsonify(game_details=g.game_details)

@app.route('/games/raw')
def show_game_data_raw():
    return json.jsonify(game_details=g.games)

@app.route('/players')
def show_players():
    players = [dict(name=player) for player in sorted(app.config['PLAYERS'])]
    possible_players = [dict(name=player) for player in sorted(app.config['POSSIBLE_PLAYERS'])]

    return render_template(
        'show_players.html',
        players=players,
        possible_players=possible_players,
    )

@app.route('/rules')
def show_rules():
    return render_template('show_rules.html')

@app.route('/news')
def show_news():
    return render_template('show_news.html')

@app.route('/shoutbox')
def shoutbox():

    return render_template(
        'show_shoutbox.html',
        shouts = g.shouts,
    )

@app.route('/game/add', methods=['POST'])
def add_game():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into games (date, player1, player2, player1_score1, player2_score1, player1_score2, player2_score2, player1_score3, player2_score3) values (?,?,?,?,?,?,?,?,?)', [
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            request.form['player1'],
            request.form['player2'],
            request.form['player1_score1'],
            request.form['player2_score1'],
            request.form['player1_score2'],
            request.form['player2_score2'],
            request.form['player1_score3'],
            request.form['player2_score3'],
    ])
    g.db.commit()
    flash("Game result was saved")
    return redirect(url_for('show_games'))

@app.route('/shoutbox/shout', methods=['POST'])
def add_shout():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into shouts (player, shout, date) values (?,?,?)', [
            session['username'],
            request.form['shout'],
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    ])
    g.db.commit()
    flash('Your shout is heard.')
    return redirect(url_for('show_home'))

@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None
    if request.method == 'POST':
        hasher = hashlib.sha512()
        salted_password = "4DnhISbPs8oXbAjT" + request.form['password']
        hasher.update(salted_password.encode('utf-8'))
        password_hash = hasher.digest()
        expected_password_hash = b'O\x9e\xba\xa5\x8cgH\x1bO\xaa\xe7\x93\x84\x85\xe1\xbd\x1d\x87\xfa\x1a\x08z$\xc8\xfd+T\xdeM\xf6\xa9\xb4\xc5`\xa4\x1d\x9d\xd6\xa5\xdc\x01\xcc\xc1J\xb4\x81\xc1\xab\x0b\x0fO\xccf\x16^\xb0\x0f\x91\xfc\xc1`\xbd\x02]'

        if request.form['username'] not in app.config['PLAYERS']:
            error = 'Invalid username'
        elif password_hash != expected_password_hash:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            flash("You were logged in as '{}'".format(session['username']))
            return redirect(url_for('show_home'))
    users = app.config['PLAYERS']
    return render_template('login.html', error=error, users=users)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_home'))

@app.route('/internal/manage')
def manage():
    if not session.get('logged_in'):
        abort(401)

    if not session['username'] in app.config['ADMINS']:
        abort(401)

    cur = g.db.execute('select id, date, player1, player2, player1_score1, player2_score1, player1_score2, player2_score2, player1_score3, player2_score3 from games order by date asc')
    games = [dict(zip(['id', 'date', 'player1', 'player2', 'player1_score1', 'player2_score1', 'player1_score2', 'player2_score2', 'player1_score3', 'player2_score3'], row)) for row in cur.fetchall() if row[1] != '']

    cur = g.db.execute('select id, player, shout, date from shouts order by date desc')
    shouts = [dict(zip(['id', 'player', 'shout', 'date'], row)) for row in cur.fetchall()]

    return render_template('manage.html', games=games, shouts=shouts)

@app.route('/internal/manage', methods=['POST'])
def manage_query():
    if not session.get('logged_in'):
        abort(401)

    if not session['username'] in app.config['ADMINS']:
        abort(401)

    g.db.execute(request.form['query'])
    g.db.commit()

    flash('Query is executed')
    return redirect(url_for('manage'))
