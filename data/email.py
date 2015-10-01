
from flask_mail import Mail, Message

from application import app
from data.players import get_player_email, get_players_email

def send_email(player_name, title, body_text, cc=None):
    player_full_name, email_address = get_player_email(player_name)

    if cc:
        cc = get_players_email(cc)

    if email_address is None:
        return False

    with app.app_context():
        mailer = Mail(app)
        message = Message(title, recipients=[(player_full_name, email_address)])
        message.body = body_text
        if cc:
            message.cc = cc
            message.reply_to = cc[0]
        mailer.send(message)

    return True
