
from data.datamodel import Player, Tag
from data.database import db

def add_tag(player, tag):
    db.session.add(Tag(
        tag=tag,
        player=db.session.query(Player).filter(Player.name == player).one(),
    ))
    db.session.commit()

def get_tags(player):
    tags = db.session.query(Player).filter(Player.name == player).first().tags
    print(tags)
    return [t.tag for t in tags]
