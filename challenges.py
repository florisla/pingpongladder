
from flask import render_template, g, session, abort, request, redirect, url_for, flash

from application import app
from data.challenges import may_challenge, add_challenge, deactivate_challenges
from data.shouts import save_shout
from data.email import send_email


@app.route('/challenges')
def show_challenges():
    return render_template(
        'show_challenges.html',
        challenges=g.challenges,
        players=g.ranking,
        absence=g.absences,
    )


@app.route('/challenges/add', methods=['POST'])
def add_challenge_page():
    if not session.get('logged_in'):
        abort(401)
    if request.form['player1'] not in g.ranking:
        abort(401)
    if request.form['player2'] not in g.ranking:
        abort(401)

    # deny 'serial' challenges (placed too quickly after last played challenge)
    can_challenge = may_challenge(
        request.form['player1'],
        app.config['CHALLENGE_COOLDOWN_DURATION_M'],
        app.config['COOLDOWN_RANDOMIZE_SALT']
    )
    if not can_challenge:
        flash(
            "Serial challenging is not allowed.  You are in a cool-down period "
            "after your last challenge.".format(
                **request.form
            ),
            'error'
        )
        save_shout(
            None,
            "The serial-challenge detection system blocked an attempt by <b>{player}</b>. "
            "Nice try though.".format(
                player=request.form['player1']
            )
        )
        add_challenge(request.form['player1'], request.form['player2'], active=False)
        return redirect(url_for('show_challenges'))

    # deny challenges to anyone who is already in a challenge
    if any(chal for chal in g.challenges if chal.challenger.name == request.form['player1']):
        flash("You already have an open challenge.", 'error')
        return redirect(url_for('show_challenges'))
    if any(chal for chal in g.challenges if chal.defender.name == request.form['player1']):
        flash("You are already challanged.", 'error')
        return redirect(url_for('show_challenges'))
    if any(chal for chal in g.challenges if chal.challenger.name == request.form['player2']):
        flash("Player {player2} already has an open challenge.".format(**request.form), 'error')
        return redirect(url_for('show_challenges'))
    if any(chal for chal in g.challenges if chal.defender.name == request.form['player2']):
        flash("Player {player2} is already challenged.".format(**request.form), 'error')
        return redirect(url_for('show_challenges'))

    add_challenge(request.form['player1'], request.form['player2'])
    flash("Challenge was saved")

    save_shout(None, "<b>{player1}</b> challenged <b>{player2}</b>".format(**request.form))

    send_email(
        request.form['player2'],
        'You have been challenged by {challenger}'.format(challenger=request.form['player1']),
        'Hi {challengee},\n\nPlayer {challenger} has just challenged you on the PingPongLadder.\n\nSee more at {website_url}.\n\n--\nThe PingPongLadder'.format(
            website_url=app.config['WEBSITE_URL'],
            challenger=request.form['player1'],
            challengee=request.form['player2'],
        )
    )

    return redirect(url_for('show_challenges'))


@app.route('/challenges/remove', methods=['POST'])
def remove_challenge():
    if not session.get('logged_in'):
        abort(401)

    deactivate_challenges(session['username'])
    flash("Your current challenge (if any) was removed")

    return redirect(url_for('show_challenges'))
