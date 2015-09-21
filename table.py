
from flask import render_template, flash, session, abort, redirect, url_for

from application import app
from data.reservations import get_reservations, save_reservation


@app.route('/table')
def show_reservations():
    reservations = get_reservations()
    return render_template(
        'show_reservations.html',
        reservations=reservations,
    )


@app.route('/table/reserve', methods=['POST'])
def save_table_reservation():
    if not session['logged_in']:
        abort(401)

    save_reservation(session['username'])
    flash('Reservation was saved')

    return redirect(url_for('show_reservations'))

