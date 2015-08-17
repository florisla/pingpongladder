# configuration
DATABASE = '/path/to/db/database.db'
DEBUG = True
SECRET_KEY = 'KnofBcdnLGjK5eY5'
ADMINS = ['Trusted_User']

POSSIBLE_PLAYERS = sorted("Dude".split(','))
DENIED = ["Nobody"]
PLAYERS = "A,B,C".split(',')

POSSIBLE_PLAYERS = sorted("D,E".split(','))
DENIED = sorted("F,G".split(','))
ABSENCE = dict(
    C='August 27',
    B='August 17',
)
QUITS = {
    12: ['A']
}
