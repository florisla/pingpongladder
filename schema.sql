
drop table if exists players;
create table players (
    id integer primary key autoincrement,
    name text not null,
    full_name text not null,
    initial_rank integer not null,
    absence text,
    rank_drop_at_game integer,
    admin integer not null default 0
);


drop table if exists games;
create table games (
    id integer primary key autoincrement,
    date text not null,
    player1 text not null,
    player2 text not null,
    player1_score1 integer not null,
    player2_score1 integer not null,
    player1_score2 integer not null,
    player2_score2 integer not null,
    player1_score3 integer not null,
    player2_score3 integer not null,
    comment text not null
);


drop table if exists challenges;
create table challenges (
    id integer primary key autoincrement,
    player1 text not null,
    player2 text not null,
    date text not null,
    comment text not null
);


drop table if exists shouts;
create table shouts (
    id integer primary key autoincrement,
    player text not null,
    shout text not null,
    date text not null
);


drop table if exists tags;
create table tags (
    id integer primary key autoincrement,
    player text not null,
    tag text not null
);
