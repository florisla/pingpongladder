
from datetime import datetime

from flask import render_template, session, request, abort, redirect, url_for, g, json, flash
import bleach

from application import app
from data.players import get_player_absence, set_player_absence
from data.tags import add_tag
from data.shouts import save_shout


@app.route('/players')
def show_players():

    sorted_players = sorted(g.players, key=lambda p: p.name)

    return render_template(
        'show_players.html',
        players=sorted_players,
        ranking=g.ranking,
        absence=get_player_absence(session['username']) if session.get('logged_in') else ''
    )


@app.route('/players/data')
def get_players_data():
    players = {name: dict(occupied=(name in g.challenged_players)) for name in g.ranking}
    return json.jsonify(players=players)


@app.route('/player/absence/save', methods=['POST'])
def save_absence():
    if not session.get('logged_in'):
        abort(401)
    if request.form.get('absence') is None:
        abort(401)

    if len(request.form['absence'].strip()) == 0:
        # absence date is being cleared
        absence_date = None
    else:
        # try to parse the date
        try:
            absence_date = datetime.strptime(
                request.form['absence'].strip(),
                '%Y-%m-%d'
            )
        except ValueError:
            flash('Date was not in the correct format', 'error')
            return redirect(url_for('show_players'))

    set_player_absence(session['username'], absence_date)
    flash("Absence was saved")
    return redirect(url_for('show_players'))


@app.route('/player/tag/add', methods=['POST'])
def add_tag_to_player():
    if not session.get('logged_in'):
        abort(401)
    if request.form.get('player') is None or len(request.form['player']) == 0:
        abort(401)
    if request.form.get('tag') is None or len(request.form['tag'].strip()) == 0:
        flash('Please enter a valid tag', 'error')
        return redirect(url_for('show_players'))

    tag = bleach.clean(
        request.form['tag'].lower(),
        tags=app.config['ALLOWED_TAGS']['tag'],
        attributes=app.config['ALLOWED_ATTRS']['tag'],
    )

    add_tag(request.form['player'], tag)
    flash("Tag was saved")

    save_shout(None, "Someone saw it fit to attribute <b>{player}</b> with the tag <span class=\"tag\">{tag}</span>.".format(
        tag=tag,
        player=request.form['player'],
    ))

    return redirect(url_for('show_players'))
