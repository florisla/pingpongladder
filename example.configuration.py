# configuration
DATABASE = '/path/to/db/database.db'
DEBUG = True
SECRET_KEY = 'KnofBcdnLGjK5eY5'
PASSWORD_SALT = b'\xe7\xca\xf1u\r\n\xdb\xfcx\x16`0\xce\x02N\xf1\x97\xeb\xbd\xcf'
PASSWORD_HASH = b'\x1c\xc10\x82\x06\xfb\x1aW\xe8\xbf/\xbb\x0eR\x0e\xbc\xbe\x1a\x91\xbdG\xf2\xa6\xfb\xeduw\x01-Z8+\xd6\x08:\xc8\xa3\x1c\xe1\x1c\xfc\xcfRJ\xf2eTJ\xbbL\xe8(\xc4.\x8c\x99\xdfj\x01\x92\x80\x1f59'
CHALLENGE_COOLDOWN_DURATION_H = 1.3

# example password is not shared; generate new salt and hash like this:
#   import os
#   import hashlib
#   salt = os.urandom(20)
#   password = 'mypassword'.encode('utf-8')
#   hasher = hashlib.sha512()
#   hasher.update(salt + password)
#   hash = hasher.digest()
#   print("Salt: {0}\nHash: {1}".format(salt, hash))

