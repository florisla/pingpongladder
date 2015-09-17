
import hashlib

from flask import render_template, g, session, request, flash, redirect, url_for

from application import app
from data.players import get_players
from data.shouts import get_shouts
from data.challenges import get_challenges
from ranking import calculate_ranking


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
        p.name: str(p.absence)
        for p in g.players
        if p.absence is not None
    }
    g.drops = {
        p.name: p.rank_drop_at_game for p in g.players
        if p.rank_drop_at_game is not None
    }

    calculate_ranking()


@app.route('/')
def show_home():
    return render_template(
        'index.html',
        shouts=g.shouts,
        challenged_players=g.challenged_players,
    )


@app.route('/rules')
def show_rules():
    return render_template('show_rules.html')


@app.route('/stats')
def show_stats():
    return render_template('show_stats.html')


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
            flash("You were logged in as '{username}'".format(**session))
            return redirect(url_for('show_home'))
    return render_template('login.html', error=error, users=g.ranking)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_home'))
