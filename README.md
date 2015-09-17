Pingpong Ladder
===============
Pingpong Ladder is a small web app to keep track of tabletennis scores in a 'ladder competition'.

It makes use of Python, Flask, SQLAlchemy, Flask-Admin, and d3.js.  By default,
data is stored in a simple sqlite database.

Features
========
* Game scores and challenges are logged in the database by the players themselves.
* Nice visualisation of the ladder ranking over time -- scrollable and zoomable.
* Statistics page shows some tournament history charts.
* Shoutbox allows players to chat and discuss among each other.
* Player can be attributed tags (nicknames) anonymously.
* System publishes messages in the shoutbox: game scores, challenges, player tags.
* Full database adminstration forms.

Limitations
===========
* Players can't register themselves, they are entered manually in the database.
* All users share a single password -- Pingpong Ladder trusts its users.
* There is no distinction between a 'user' of the site and a tournament 'participant'.
* The code and visualisations are not tested for big numbers (hundreds of players, thousands of
  matches, hundreds of days). So optimizations may be required if that's your use case.

Installation
============
* Install Flask.
* Create an empty sqlite database.
* Rename example.configuration.py to configuration.py .
* Edit configuration.py and update all settings.
* Run tools/createdb.py with ADD_ADMIN=True.
