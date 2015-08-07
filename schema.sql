drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  text text not null
);

drop table if exists players;
create table players (
    id integer primary key autoincrement,
    name text not null
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
    player2_score3 integer not null
);