# configuration
WEBSITE_URL = 'http://pingpong.example.com'
DATABASE = '/path/to/db/database.db'
DEBUG = True
SECRET_KEY = 'KnofBcdnLGjK5eY5'
PASSWORD_SALT = b'\xe7\xca\xf1u\r\n\xdb\xfcx\x16`0\xce\x02N\xf1\x97\xeb\xbd\xcf'
PASSWORD_HASH = b'\x1c\xc10\x82\x06\xfb\x1aW\xe8\xbf/\xbb\x0eR\x0e\xbc\xbe\x1a\x91\xbdG\xf2\xa6\xfb\xeduw\x01-Z8+\xd6\x08:\xc8\xa3\x1c\xe1\x1c\xfc\xcfRJ\xf2eTJ\xbbL\xe8(\xc4.\x8c\x99\xdfj\x01\x92\x80\x1f59'
CHALLENGE_COOLDOWN_DURATION_M = (120, 180)
COOLDOWN_RANDOMIZE_SALT = "shoutnotbeguessed"
# pick one from the tz database: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
WEBSITE_TIMEZONE = 'Etc/UTC'

ALLOWED_TAGS = dict(
    tag=[],
    shout_message=['a', 'b', 'em', 'i', 'div', 'strong', 'img', 'h2', 'br', 'p'],
    game_comment=['b', 'em', 'i', 'strong'],
)

ALLOWED_ATTRS = dict(
    tag={},
    shout_message={
        '*': ['class'],
        'a': ['href', 'rel'],
        'img': ['src', 'alt'],
    },
    game_comment={},
)

MAIL_SERVER = 'smtp.example.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_DEBUG = False
MAIL_USERNAME = 'usrnm'
MAIL_PASSWORD = 'pwd'
MAIL_DEFAULT_SENDER = 'pingpongladder@example.com'
MAIL_SUPPRESS_SEND = True

# example password is not shared; generate new salt and hash like this:
#   import os
#   import hashlib
#   salt = os.urandom(20)
#   password = 'mypassword'.encode('utf-8')
#   hasher = hashlib.sha512()
#   hasher.update(salt + password)
#   hash = hasher.digest()
#   print("Salt: {0}\nHash: {1}".format(salt, hash))

