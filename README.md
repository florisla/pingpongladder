Pingpong Ladder
===============
Pingpong Ladder is a small web app to keep track of tabletennis scores in a 'ladder competition'.

It is built on Python, Flask, sqlite and d3.js.

Features
========
* Game scores and challenges are logged in the database.
* Nice visualisation of the ladder ranking over time -- scrollable and zoomable.
* Statistics page shows some tournament history charts.
* Shoutbox allows players to chat and discuss mong each other.
* Player can be attributed tags (nicknames) anonymously.
* System publishes messages in the shoutbox: game scores, challenges, player tags.

Limitations
===========
* Players can't register themselves, they are entered manually in the configuration file.
* All users share a single password -- Pingpong Ladder trusts its users.
* There is no real management interface, only a page where you can enter manual SQL queries.

Installation
============
* Install Flask
* Create the sqlite database using schema.sql
* Rename example.configuration.py to configuration.py
* Edit configuration.py and update all relevent settings

Warning
=======
This application, while functional, is not finished yet.

Features and documentation are lacking, but above all - it is INSECURE.
Only use on protected intranets with people you trust.

