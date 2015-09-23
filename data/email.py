
from flask_mail import Mail, Message

from application import app
from data.players import get_player_email

def send_email(player_name, title, body_text):
    player_full_name, email_address = get_player_email(player_name)
    if email_address is None:
        return False

    with app.app_context():
        mailer = Mail(app)
        message = Message(title, recipients=[(player_full_name, email_address)])
        message.body = body_text
        mailer.send(message)

    return True
