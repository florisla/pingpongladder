
var width = 800;
var height = 500;
var graph_offset_x = 20;
var game_count = 15;
var player_count = 25;
var min_game = 0;

var game_count = 0;
var game_width = 20;

var scales = [];
var scale_index = 0;
var scale_index_unity = 0;
var translation = graph_offset_x;

url = window.location.toString();
skip_pos = url.search("skip=");
if (skip_pos > 0) {
    skip = parseInt(url.substring(skip_pos+5, skip_pos+8));
    min_game = skip;
}

function draw() {
    d3.json("http://florisla.pythonanywhere.com/ranking/data", function(ranks) {
        ranking = ranks;
        draw_ranking();

        d3.json("http://florisla.pythonanywhere.com/games/data", function(games) {
            game_details = games.game_details;
            draw_games();

            setup_scales();
            all_view();
            latest_view();
        });
    });
}

draw();

function setup_scales() {
    if (scales.length == 0) {
        total_width = game_width * game_count + 0;
        full_view_scale = (width-100) / total_width;
        scale = full_view_scale;
        while (scale < 2.4)
        {
            scales.push(scale);
            scale *= 1.2;

            if (scale >= 0.83 && scale <= 1.2 ) {
                scale_index_unity = scales.length;
            }
        }
    }
}

function pan_and_zoom() {
    console.log('centerpoint', (translation + (width-80)/2) * (1/scales[scale_index]));

    group = d3.select('#ranklines');
    group.transition()
        .duration(500)
        .attr('transform', 'translate(' + (translation) + ', 0) scale(' + scales[scale_index] + ',1.0)');
}

function dotranslate(to_right) {
    translation += 150;
    if (to_right) {
        translation -= 300;
    }
    // don't go too far off the left
    translation = Math.min(translation, graph_offset_x);

    // don't go too far off the right
    total_drawn_width = game_count*scales[scale_index]*game_width;
    invisible_width = total_drawn_width - (width - 80);
    translation = Math.max(-invisible_width, translation);

    pan_and_zoom();
}

function zoom(zoom_in) {
    old_scale = scales[scale_index];

    if (zoom_in) {
        if (scale_index < (scales.length -1)) {
            scale_index += 1;
        }
    }
    else if (scale_index > 0) {
        scale_index -= 1;
    }

    pan_and_zoom();
}

function latest_view() {
    scale_index = scale_index_unity;
    total_drawn_width = game_count * game_width * scales[scale_index];
    invisible_width = total_drawn_width - (width - 80);
    translation = - invisible_width;
    pan_and_zoom();
}

function all_view() {
    scale_index = 0;
    translation = graph_offset_x;
    pan_and_zoom();
}

function draw_ranking() {
    var positions = [];
    var players = [];

    for (var player in ranking) {
        ranks = ranking[player];
        player_positions = [];
        player_slack_positions = [];
        for (var i=min_game; i<ranks.length; i++) {
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

    game_count = ranks.length - min_game;
    player_count = positions.length;

    var random_color = d3.scale.category20();
    function bertize(d,i) {
        if ('player' in d) {
            if (d.player=='Bert') {
                return 'deeppink';
            }
        }
        else {
            if (d[1] == 'Bert') {
                return 'deeppink';
            }
        }
        return random_color(i);
    }

    var svg = d3.select("svg")
        .attr("width", width)
        .attr("height", height);

    var ranks = d3.select('svg')
        .append('g')
        .attr('id', 'ranklines');

    var line = d3.svg.line()
        .x(function(d){ return graph_offset_x + (d[0]-min_game) * game_width; })
        .y(function(d){ return 10 + (d[1]-1) * height/player_count; })
        .interpolate('monotone');

    var rank_lines = ranks.selectAll('.rank')
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
       .attr('stroke', bertize)
       .attr("d", function(d) { return line(d.positions); })
       .attr('fill', 'none')
       .attr('stroke-width', '4');

    var slacker_rank_lines = ranks.selectAll('.slackerrank')
       .data(positions)
       .enter()
       .append('path')
       .attr('class', 'slackerrank')
       .attr('stroke-dasharray', ("3, 3"))
       .attr("d", function(d) { return line(d.slacker_positions); })
       .attr('fill', 'none');

    rank_nrs = []
    for (var i=1; i<=player_count; i++) {
        rank_nrs.push(i);
    };

    var player_labels_background = svg
        .append('rect')
        .attr('width', 20)
        .attr('height', height)
        .attr('x', 0)
        .attr('y', 0)
        .attr('fill', 'white')
        .attr('stroke', 'none')
        .attr('opacity', 0.7);

    var rank_nr_labels = svg.selectAll('.ranknr')
        .data(rank_nrs)
        .enter()
        .append('text')
        .attr("x", 2)
        .attr("y", function(d) { return -2 + d * height/player_count; })
        .text(function(d) { return d; });

    var player_labels_background = svg
        .append('rect')
        .attr('width', 75)
        .attr('height', height)
        .attr('x', width-75)
        .attr('y', 0)
        .attr('fill', 'white')
        .attr('stroke', 'none')
        .attr('opacity', 0.7);

    var player_labels = svg.selectAll('.playerlabel')
        .data(players)
        .enter()
        .append('text')
        .attr("x", width-70)
        .attr("y", function(d) { return 14 + (d[0] - 1) * height/player_count; })
        .attr('stroke', bertize)
        .attr('fill', bertize)
        .attr('stroke-width', 1)
        .attr('font-size', 14)
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

    var ranks = d3.select('#ranklines');

    var game_rects = ranks.selectAll('.match')
        .data(game_positions)
        .enter()
        .append("rect")
        .attr("x", function(d) { return 3 + graph_offset_x + (d[0]-1-min_game) * game_width; })
        .attr("y", function(d) { return 9 + d[1] * height/player_count; })
        .attr("width", -6 + game_width)
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
        ranks.append("line")
            .attr('class', 'dateline')
            //.attr('stroke', 'gray')
            .attr("x1", graph_offset_x + (index-1-min_game) * game_width)
            .attr("y1", 8)
            .attr("x2", graph_offset_x + (index-1-min_game) * game_width)
            .attr("y2", height-6);
    }
}
