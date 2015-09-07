
import sqlite3
import datetime
from flask import Flask, request, session, g, redirect, url_for, abort, \
                  render_template, flash, json

from flask.ext.sqlalchemy import SQLAlchemy

import configuration
import hashlib
import random

app = Flask(__name__)
app.config.from_object(configuration)
db = SQLAlchemy(app)




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
    if isinstance(player1_scores[0], str):
        player1_scores = [int(score) if len(score) > 0 else 0 for score in player1_scores]
        player2_scores = [int(score) if len(score) > 0 else 0 for score in player2_scores]

    return 1 < len([score for score in zip(player1_scores, player2_scores) if score[1] > score[0]])

def get_shouts(max_nr=20):
    cur = g.db.execute('select player, shout, date, id from shouts order by date desc, id desc LIMIT ?', [max_nr])
    g.shouts = [dict(zip(['player', 'shout', 'date', 'id'], row)) for row in cur.fetchall()]

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

        challenger_lost = player2_won([player1_score1, player1_score2, player1_score3], [player2_score1, player2_score2, player2_score3]);
        if challenger_lost:
            if swap_ranking(player2, player1):
                g.swaps.append((player2, player1))
        else:
            if swap_ranking(player1, player2):
                g.swaps.append((player1, player2))

        g.game_details.append(dict(
            challenger=dict(name=player1, rank=abs(g.positions[player1][-1])),
            challengee=dict(name=player2, rank=abs(g.positions[player2][-1])),
            scores=[(player1_score1, player2_score1), (player1_score2, player2_score2), (player1_score3, player2_score3)],
            winner=player2 if challenger_lost else player1,
            index=len(g.positions[player1]),
            date=match_date,
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

def get_challenges():
    cur = g.db.execute('select  player1, player2, date, comment from challenges order by date asc')
    challenges = [dict(zip(['player1', 'player2', 'date', 'comment'], row)) for row in cur.fetchall()]
    return challenges

def get_players():
    cur = g.db.execute('select  name, full_name, initial_rank, absence, rank_drop_at_game, admin from players order by initial_rank ASC;')
    player_list = [dict(zip(['name', 'full_name', 'initial_rank', 'absence', 'rank_drop_at_game', 'admin'], row)) for row in cur.fetchall()]
    players = {p['name']:p for p in player_list}
    return players

@app.before_request
def before_request():
    g.db = connect_db()
    g.players = get_players()
    g.ranking = [
        player['name'] for player in sorted(
            g.players.values(),
            key=lambda p: p['initial_rank']
        )
    ]
    g.original_ranking = g.ranking[:]
    g.challenges = get_challenges()
    g.challengers = set(ch['player1'] for ch in g.challenges)
    g.challengees = set(ch['player2'] for ch in g.challenges)
    g.challenged_players = sorted(g.challengers.union(g.challengees))
    g.absences = {
                 name:details['absence'] for name,details in g.players.items()
                 if details['absence'] is not None
                 and len(details['absence']) > 0
    }
    g.drops = {
        name:details['rank_drop_at_game'] for name,details in g.players.items()
        if details['rank_drop_at_game'] is not None
    }
    g.admins = [player['name'] for player in g.players.values() if player['admin'] == 1]

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
    return render_template('index.html',
        shouts=g.shouts,
        challenged_players=g.challenged_players,
        admin_links=(session.get('logged_in') and session['username'] in g.admins),
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
        challengees=list(g.challengees),
    )

@app.route('/games')
def show_games():

    return render_template(
        'show_games.html',
        games=list(reversed(g.games)),
        players=g.ranking,
        swaps=g.swaps,
    )

@app.route('/challenges')
def show_challenges():
    return render_template(
        'show_challenges.html',
        challenges=g.challenges,
        players=g.ranking,
        absence=g.absences,
    )

@app.route('/games/data')
def show_game_data_json():
    return json.jsonify(game_details=g.game_details)

@app.route('/games/raw')
def show_game_data_raw():
    return json.jsonify(game_details=g.games)

@app.route('/players')
def show_players():

    tags = {player:[] for player in g.ranking}
    cur = g.db.execute('select player, tag from tags order by id desc')
    for player,tag in cur.fetchall():
        tags[player].append(tag)

    players = [
        dict(
            name=player,
            full_name=g.players[player]['full_name'],
            tags=tags[player]
        )
        for player
        in sorted(g.ranking)
    ]

    return render_template('show_players.html',
        players=players,
        ranking=g.ranking,
        absence='' if not session['logged_in'] else g.players[session['username']]['absence'],
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
        admin_links=(session.get('logged_in') and session['username'] in g.admins),
    )

@app.route('/player/absence/save', methods=['POST'])
def save_absence():
    if not session.get('logged_in'):
        abort(401)
    if request.form.get('absence') is None:
        abort(401)

    g.db.execute('update players set absence=? where name=?;', [
        request.form['absence'],
        session['username'],
    ])
    g.db.commit()
    flash("Absence was saved")
    return redirect(url_for('show_players'))

@app.route('/player/tag/add', methods=['POST'])
def add_tag():
    if not session.get('logged_in'):
        abort(401)
    if request.form.get('player') is None or len(request.form['player']) == 0:
        abort(401)
    if request.form.get('tag') is None or len(request.form['tag']) == 0:
        abort(401)

    g.db.execute('insert into tags (player, tag) values (?,?);', [
            request.form['player'],
            request.form['tag'].lower(),
    ])
    g.db.commit()
    flash("Tag was saved")

    save_shout('Ladder', "Someone saw it fit to attribute <b>{}</b> with the tag <span class=\"tag\">{}</span>.".format(
        request.form['player'],
        request.form['tag'].lower()
    ))

    return redirect(url_for('show_players'))

@app.route('/game/add', methods=['POST'])
def add_game():
    if not session.get('logged_in'):
        abort(401)

    comment = request.form['comment'] if 'comment' in request.form else ''

    g.db.execute('insert into games (date, player1, player2, player1_score1, player2_score1, player1_score2, player2_score2, player1_score3, player2_score3, comment) values (?,?,?,?,?,?,?,?,?,?);', [
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            request.form['player1'],
            request.form['player2'],
            request.form['player1_score1'],
            request.form['player2_score1'],
            request.form['player1_score2'],
            request.form['player2_score2'],
            request.form['player1_score3'],
            request.form['player2_score3'],
            comment,
    ])
    g.db.commit()
    flash("Game result was saved")

    g.db.execute('delete from challenges where player1=? and player2=?;', [
            request.form['player1'],
            request.form['player2'],
    ])
    g.db.commit()
    flash("Open challenge (if any) was removed")

    challenger_lost = player2_won([request.form['player1_score1'], request.form['player1_score2'], request.form['player1_score3']], [request.form['player2_score1'], request.form['player2_score2'], request.form['player2_score3']]);
    if challenger_lost:
        winner = request.form['player2']
        shout_message = '<b>{player1}</b> could not win from {nick} <b>{player2}</b> {player1_score1}-{player2_score1} {player1_score2}-{player2_score2} {player1_score3}{dash}{player2_score3}{comment}'
    else:
        winner = request.form['player1']
        shout_message = '{nick}<b>{player1}</b> beat <b>{player2}</b> {player1_score1}-{player2_score1} {player1_score2}-{player2_score2} {player1_score3}{dash}{player2_score3}{comment}'

    if len(comment) > 0:
        comment = '<div class="gamecomment">{0}</div>'.format(comment)

    # find winner's nickname in the tags table
    cur = g.db.execute("select tag from tags where player =?", [winner])
    tags = [row[0] for row in cur.fetchall()]

    nickname = ''
    if any(tags):
        nickname = " '<span class=\"tag\">{}</span>' ".format(
            random.choice(tags)
        )

    save_shout('Ladder', shout_message.format(
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
def add_challenge():
    if not session.get('logged_in'):
        abort(401)

    # do not log a challenge to anyone who is the source or target
    # of another challenge

    if any(chal for chal in g.challenges if chal['player1'] == request.form['player1']):
        flash("You already have an open challenge.", 'error')
        return redirect(url_for('show_challenges'))
    if any(chal for chal in g.challenges if chal['player2'] == request.form['player1']):
        flash("You are already challanged.", 'error')
        return redirect(url_for('show_challenges'))
    if any(chal for chal in g.challenges if chal['player1'] == request.form['player2']):
        flash("Player {} already has an open challenge.".format(request.form['player2']), 'error')
        return redirect(url_for('show_challenges'))
    if any(chal for chal in g.challenges if chal['player2'] == request.form['player2']):
        flash("Player {} is already challenged.".format(request.form['player2']), 'error')
        return redirect(url_for('show_challenges'))

    g.db.execute('insert into challenges (date, player1, player2, comment) values (?,?,?,?)', [
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            request.form['player1'],
            request.form['player2'],
            request.form['comment'],
    ])
    g.db.commit()
    flash("Challenge was saved")

    save_shout('Ladder', "<b>{0}</b> challenged <b>{1}</b>".format(
        request.form['player1'],
        request.form['player2']
    ))

    return redirect(url_for('show_challenges'))

@app.route('/challenges/remove', methods=['POST'])
def remove_challenge():
    if not session.get('logged_in'):
        abort(401)

    g.db.execute('delete from challenges where player1=?', [
        session['username']
    ])
    g.db.commit()
    flash("Your current challenge (if any) was removed")

    return redirect(url_for('show_challenges'))

@app.route('/shoutbox/shout', methods=['POST'])
def add_shout():
    if not session.get('logged_in'):
        abort(401)

    save_shout(session['username'], request.form['shout'])
    flash('Your shout is heard.')
    return redirect(url_for('show_home'))

@app.route('/shoutbox/edit/<int:shout_id>', methods=['GET', 'POST'])
def edit_shout(shout_id):
    if not session.get('logged_in'):
        abort(401)
    if not session['username'] in g.admins:
        abort(401)

    if request.method == 'GET':
        shout = next(iter(s for s in g.shouts if s['id']==shout_id))
        return render_template('edit-shout.html', shout=shout)
    if request.method == 'POST':
        g.db.execute('update shouts set shout=? where id=?;', [
            request.form['shout'],
            shout_id,
        ])
        g.db.commit()
        flash('Shout has been updated.')
        return redirect(url_for('shoutbox'))

    abort(401)

@app.route('/shoutbox/delete/<int:shout_id>', methods=['POST'])
def remove_shout(shout_id):
    if not session.get('logged_in'):
        abort(401)
    if not session['username'] in g.admins:
        abort(401)

    g.db.execute('delete from shouts where id=?;', [
        shout_id,
    ])
    g.db.commit()
    flash('Shout has been deleted.')
    return redirect(url_for('shoutbox'))

def save_shout(player, shout):
    g.db.execute('insert into shouts (player, shout, date) values (?,?,?)', [
        player,
        shout,
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    ])
    g.db.commit()

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

@app.route('/internal/manage/<item_type>', methods=['GET', 'POST'])
def manage(item_type):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if not session['username'] in g.admins:
        abort(401)

    item_details = dict(
        games = dict(
            title = 'Games',
            query = 'select id, date, player1, player2, player1_score1, player2_score1, player1_score2, player2_score2, player1_score3, player2_score3 from games order by date desc',
            columns = ['id', 'date', 'player1', 'player2', 'player1_score1', 'player2_score1', 'player1_score2', 'player2_score2', 'player1_score3', 'player2_score3'],
        ),
        challenges = dict(
            title = 'Challenges',
            query = 'select id, date, player1, player2, comment from challenges order by date desc',
            columns = ['id', 'date', 'player1', 'player2', 'comment'],

        ),
        shouts = dict(
            title = 'Shouts',
            query = 'select id, player, shout, date from shouts order by date desc',
            columns = ['id', 'player', 'shout', 'date'],

        ),
        players = dict(
            title = 'Players',
            query = 'select id, name, full_name, initial_rank, absence, rank_drop_at_game, admin from players order by id desc',
            columns = ['id', 'name', 'full_name', 'initial_rank', 'absence', 'rank_drop_at_game', 'admin'],

        ),
        tags = dict(
            title = 'Tags',
            query = 'select id, player, tag from tags order by id desc',
            columns = ['id', 'player', 'tag'],
        ),
    )

    if item_type not in item_details:
        abort(401)

    if request.method == 'POST':
        try:
            cur = g.db.execute(request.form['query'])
            items = [dict(zip(range(100), r)) for r in cur.fetchall()]
            g.db.commit()
            flash('Query is executed')
        except Exception as e:
            flash(e)

    elif request.method == 'GET':
        cur = g.db.execute(item_details[item_type]['query'])
        items = [dict(zip(item_details[item_type]['columns'], row)) for row in cur.fetchall()]

    return render_template(
        'manage.html',
        title=item_details[item_type]['title'],
        items=items,
        item_type = item_type,
    )


if __name__ == '__main__':
    app.run()

