
d3.json("http://florisla.pythonanywhere.com/ranking/data", function(ranks) {
    ranking = ranks;
    draw_ranking();

    d3.json("http://florisla.pythonanywhere.com/games/data", function(games) {
        game_details = games.game_details;
        draw_games();
    });
});


var width = 800;
var height = 500;
var graph_offset_x = 20;
var game_count = 15;
var player_count = 25;


function draw_ranking() {
    var positions = [];
    var players = [];

    for (var player in ranking) {
        ranks = ranking[player];
        player_positions = [];
        player_slack_positions = [];
        for (var i=0; i<ranks.length; i++) {
            position = [i, Math.abs(ranks[i]) ];
            player_positions.push(position);

            if (ranks[i] < 0) {
                player_slack_positions.push(position);
            }
        };

        player_ranks = {};
        player_ranks['player'] = player;
        player_ranks['positions'] = player_positions;
        player_ranks['slacker_positions'] = player_slack_positions;
        positions.push(player_ranks);

        if (player_positions.length > 0) {
            players.push([player_positions[player_positions.length-1][1], player]);
        }
        else {
            // player has not yet played, has no ranking in player_positions
            // lookup original ranking in ranking array
            rank = Math.abs(ranking[player][0]);
            players.push([rank, player])
        }
    };

    game_count = ranks.length;
    player_count = positions.length;

    var color = d3.scale.category20();

    var svg = d3.select("svg")
        .attr("width", width)
        .attr("height", height);

    var line = d3.svg.line()
        .x(function(d){ return graph_offset_x + d[0] * (width-100)/game_count; })
        .y(function(d){ return 10 + (d[1]-1) * height/player_count; })
        .interpolate('monotone');

    var rank_lines = svg.selectAll('.rank')
       .data(positions)
       .enter()
       .append('path')
       .on('mouseover', function(d) {
           d3.select(this).style({'stroke-width':7});
        })
       .on('mouseout', function(d) {
           d3.select(this).style({'stroke-width':4});
        })
       .attr('class', 'rank')
       .attr('stroke', function(d,i) { return color(i); })
       .attr("d", function(d) { return line(d.positions); });

    var slacker_rank_lines = svg.selectAll('.slackerrank')
       .data(positions)
       .enter()
       .append('path')
       .attr('class', 'slackerrank')
       .attr('stroke-dasharray', ("3, 3"))
       .attr("d", function(d) { return line(d.slacker_positions); });

    rank_nrs = []
    for (var i=1; i<=player_count; i++) {
        rank_nrs.push(i);
    };

    var rank_nr_labels = svg.selectAll('.ranknr')
        .data(rank_nrs)
        .enter()
        .append('text')
        .attr("x", 2)
        .attr("y", function(d) { return -2 + d * height/player_count; })
        .text(function(d) { return d; });

    var player_labels = svg.selectAll('.ranknr')
        .data(players)
        .enter()
        .append('text')
        .attr("x", width-85)
        .attr("y", function(d) { return 14 + (d[0] - 1) * height/player_count; })
        .attr('stroke', function(d,i) { return color(i); })
        .attr('stroke-width', 1)
        .attr('font-size', 14)
        .attr('fill', function(d,i) { return color(i); })
        .text(function(d) { return d[1]; });
}

function draw_games() {
    game_positions = [];
    last_date = '';
    date_indices = [];

    for (var i in game_details) {
        game_detail = game_details[i];
        day = game_detail.date.substring(0,10);
        if (day != last_date) {
            last_date = day;
            if (game_detail.index > 1) {
                date_indices.push(game_detail.index);
            }
        }

        if (game_detail.winner == game_detail.challenger.name) {
            continue;
        }

        game_positions.push([
            // game index
            game_detail.index,
            // lowest player rank
            Math.min(game_detail.challenger.rank, game_detail.challengee.rank) - 1,
            // rank difference
            Math.abs(game_detail.challenger.rank - game_detail.challengee.rank)
        ]);
    }

    var svg = d3.select("svg");
    var game_rects = svg.selectAll('.match')
        .data(game_positions)
        .enter()
        .append("rect")
        .attr("x", function(d) { return 3 + graph_offset_x + (d[0]-1) * (width-100)/game_count; })
        .attr("y", function(d) { return 9 + d[1] * height/player_count; })
        .attr("width", -6 + (width-100)/game_count)
        .attr("height", function(d) { return 2 + d[2] * height/player_count; })
        .attr('class', 'game');

    /*
    var date_lines = svg.selectAll('.gameline')
        .data(date_indices)
        .enter()
        .append("line")
        .attr('x1', 10)
        .attr('x2', 100)
        .attr('y1', 0)
        .attr('y2', 100)
        */

    for (var di in date_indices) {
        index = date_indices[di];

        svg.append("line")
            .attr('class', 'dateline')
            //.attr('stroke', 'gray')
            .attr("x1", graph_offset_x + (index-1) * (width-100)/game_count)
            .attr("y1", 8)
            .attr("x2", graph_offset_x + (index-1) * (width-100)/game_count)
            .attr("y2", height-6);
    }
}
