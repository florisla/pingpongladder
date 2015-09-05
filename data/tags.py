
from data.database import Player, Tag
from data.dbsession import session

def add_tag(player, tag):
    session.add(Tag(
        tag=tag,
        player=session.query(Player).filter(Player.name == player).one(),
    ))
    session.commit()

def get_tags(player):
    tags = session.query(Player).filter(Player.name == player).first().tags
    print(tags)
    return [t.tag for t in tags]


if __name__ == '__main__':
    #add_tag('Floris', 'henauwhater')
    #print(get_tags('Floris'))
    pass

