
from application import app

# import all modules containing flask app.routes
import admin
import pages
import shouts
import ranking
import challenges
import players
import games


if __name__ == '__main__':
    # run the PingPongLadder app
    app.run()
