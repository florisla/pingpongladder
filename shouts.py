
from flask import render_template, session, request, flash, abort, redirect, url_for
import bleach

from application import app
from data.shouts import get_shouts, save_shout


@app.route('/shoutbox')
def shoutbox():
    all_shouts = get_shouts(2000)
    return render_template(
        'show_shoutbox.html',
        shouts=all_shouts,
    )


@app.route('/shoutbox/shout', methods=['POST'])
def add_shout():
    if not session.get('logged_in'):
        abort(401)

    shout = bleach.clean(
        request.form['shout'],
        tags=app.config['ALLOWED_TAGS']['shout_message'],
        attributes=app.config['ALLOWED_ATTRS']['shout_message'],
    )

    save_shout(session['username'], shout)
    flash('Your shout is heard.')
    return redirect(url_for('show_home'))
