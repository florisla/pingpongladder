d3.json("http://florisla.pythonanywhere.com/games/data", function(games) {
    matches_per_date = game_count_per_day(games.game_details);
    challenges_won_per_date = lost_won_per_day(games.game_details);
    games_per_player = games_per_player(games.game_details);

    graph_match_rate(matches_per_date);
    graph_lost_won_rate(challenges_won_per_date);
    graph_games_per_player(games_per_player);
})

function game_count_per_day(game_details) {
    dates = [];
    for (var game in game_details) {
        date = game_details[game].date.substring(0,10);
        if (! (date in dates)) {
            dates[date] = 1;
        }
        else {
            dates[date] += 1;
        }
    }
    return dates;
}

function lost_won_per_day(game_details) {
    dates = [];
    for (var game in game_details) {
        details = game_details[game];
        date = details.date.substring(0,10);
        if (! (date in dates)) {
            dates[date] = {won:0, lost:0};
        }

        if (details.challenger.name == details.winner) {
            dates[date]['won'] += 1;
        }
        else {
            dates[date]['lost'] += 1;
        }
    }
    return dates;
}

function games_per_player(game_details) {
    players = [];
    for (var game in game_details) {
        details = game_details[game];

        if (! (details.challenger.name in players)) {
            players[details.challenger.name] = {challenges:0, defenses:0};
        }
        if (! (details.challengee.name in players)) {
            players[details.challengee.name] = {challenges:0, defenses:0};
        }

        players[details.challenger.name].challenges += 1;
        players[details.challengee.name].defenses += 1;

    }
    for (var name in players) {
        player = players[name];
        player.total_games = player.challenges + player.defenses;
    }
    return players;
}

function graph_match_rate(match_rate) {

    match_rate = d3.entries(match_rate)

    var width = 500;
    var height = 300;
    var barWidth = 0.65 * width / match_rate.length;
    var barSpacing = 0.15 * width / match_rate.length;
    var marginTop = 20;

    var margin_horizontal = 20;
    var total_bar_width = (width - margin_horizontal*2) / match_rate.length;
    var bar_width = total_bar_width * 0.8;
    var bar_spacing = total_bar_width * 0.2;

    var y = d3.scale.linear()
        .domain([0, d3.max(match_rate, function(datum) { return datum.value; })]).rangeRound([0, height])
        .range([0, height-marginTop]);

    var dateBar = d3.select(".datechart")
        .attr("width", width)
        .attr("height", height);

    dateBar.selectAll('.matchcountbar')
        .data(match_rate)
        .enter()
        .append('rect')
        .attr('x', function(d, i) { return margin_horizontal + total_bar_width * i; } )
        .attr('y', function(d, i) { return height - y(d.value); } )
        .attr('width', barWidth)
        .attr('height', function(d, i) { return y(d.value); } )
        .attr('fill', 'steelblue')

    dateBar.selectAll(".matchcountlabel")
        .data(match_rate)
        .enter()
        .append("svg:text")
        .attr("x", function(d, i) { return -8 + margin_horizontal + total_bar_width/2 + total_bar_width * i; })
        .attr("y", function(d) { return 20 + height - y(d.value); })
        .attr("text-anchor", "middle")
        .text(function(d) { if (d.value <= 1) {return '';} return d.value;} )
        .attr("fill", "white");
}

function graph_lost_won_rate(dates) {

    var dates = d3.entries(dates);

    var width = 500;
    var height = 300;
    var margin_horizontal = 20;
    var margin_vertical = 25;

    var total_bar_width = (width - margin_horizontal*2) / dates.length;
    var bar_width = total_bar_width * 0.8;
    var bar_spacing = total_bar_width * 0.2;

    var most_won = d3.max(dates, function(d) { return d.value.won; } );
    var most_lost = d3.max(dates, function(d) { return d.value.lost; } );
    var most_games = d3.max([most_won, most_lost]);

    y = d3.scale.linear()
        .domain([0, most_games])
        .range([0, height/2 - margin_vertical]);

    svg = d3.select('.challengerate')
        .attr('width', width)
        .attr('height', height)

    svg.selectAll('.wonrect')
        .data(dates)
        .enter()
        .append('rect')
        .attr('width', bar_width)
        .attr('height', function(d) { return y(d.value.won); } )
        .attr('fill', 'green')
        .attr('x', function(d,i) { return margin_horizontal + i * total_bar_width; } )
        .attr('y', function(d) { return margin_vertical + y(most_games) - y(d.value.won); } );

    svg.selectAll('.wonnr')
        .data(dates)
        .enter()
        .append('text')
        .attr('x', function(d,i) { return margin_horizontal + bar_width/2 + i * total_bar_width; } )
        .attr('y', function(d) { return margin_vertical + 15 + y(most_games) - y(d.value.won); } )
        .text(function(d) { if (d.value.lost <= 1) {return '';} return d.value.won; } )
        .attr('fill', 'white')
        .attr('text-anchor', 'middle');

    svg.selectAll('.lostrect')
        .data(dates)
        .enter()
        .append('rect')
        .attr('width', bar_width)
        .attr('height', function(d) { return y(d.value.lost); } )
        .attr('fill', 'red')
        .attr('x', function(d,i) { return margin_horizontal + i * total_bar_width; } )
        .attr('y', height/2);

    svg.selectAll('.lostnr')
        .data(dates)
        .enter()
        .append('text')
        .attr('x', function(d,i) { return margin_horizontal + bar_width/2 + i * total_bar_width; } )
        .attr('y', function(d) { return height/2 -2 + y(d.value.lost); } )
        .text(function(d) { if (d.value.lost <= 1) {return '';} return d.value.lost; } )
        .attr('fill', 'white')
        .attr('text-anchor', 'middle');

    svg.selectAll('.percentage')
        .data(dates)
        .enter()
        .append('text')
        .attr('x', function(d,i) { return margin_horizontal + bar_width/2 + i * total_bar_width; } )
        .attr('y', 18)
        .text(function(d) { return Math.round(100*d.value.won/(d.value.won+d.value.lost)) + '%'; } )
        .attr('fill', 'black')
        .attr('text-anchor', 'middle');
}

function graph_games_per_player(games_per_player) {

    games_per_player = d3.entries(games_per_player);
    games_per_player =  games_per_player.sort(function(a,b) {
        if (a.value.total_games < b.value.total_games) {
            return -1;
        }
        if (a.value.total_games > b.value.total_games) {
            return 1;
        }
        return 0;
    });

    var width = 500;
    var height = 500;
    var margin_horizontal = 40;
    var margin_vertical = 25;
    var total_bar_height = (height - 2*margin_vertical) / games_per_player.length;
    var bar_height = 0.7 * total_bar_height;
    var bar_spacing = 0.3 * total_bar_height;

    var most_played = d3.max(games_per_player, function(d) { return d.value.total_games; } );

    x = d3.scale.linear()
        .domain([0, most_played])
        .range([0,  width - 2*margin_horizontal]);

    svg = d3.select('.gamesperplayer')
        .attr('width', width)
        .attr('height', height);

    g = svg.append('g')
        .attr('transform', 'translate(20,12)');

    g.selectAll('.challenges')
        .data(games_per_player)
        .enter()
        .append('rect')
        .attr('x', 0)
        .attr('y', function(d,i) { return i*total_bar_height; } )
        .attr('width', function(d,i) { return x(d.value.challenges); } )
        .attr('height', bar_height)
        .attr('class', 'challenges')
        .attr('id', function(d) { return d.key; } )
        .attr('fill', 'purple');

    g.selectAll('.challenge')
        .data(games_per_player)
        .enter()
        .append('rect')
        .attr('x', function(d) { return x(d.value.challenges); } )
        .attr('y', function(d,i) { return i*total_bar_height; } )
        .attr('width', function(d,i) { return x(d.value.defenses); } )
        .attr('height', bar_height)
        .attr('fill', 'steelblue');

    g.selectAll('.challengenr')
        .data(games_per_player)
        .enter()
        .append('text')
        .attr('x', function(d) { return -17 + x(d.value.challenges); })
        .attr('y', function(d,i) { return (i+0.6) * total_bar_height; } )
        .text(function(d) { return d.value.challenges; })
        .attr('fill', 'white')
        .attr('font-size', 10);

    g.selectAll('.defense')
        .data(games_per_player)
        .enter()
        .append('rect')
        .attr('x', function(d) { return x(d.value.challenges); } )
        .attr('y', function(d,i) { return i*total_bar_height; } )
        .attr('width', function(d,i) { return x(d.value.defenses); } )
        .attr('height', bar_height)
        .attr('fill', 'steelblue');

    g.selectAll('.defensenr')
        .data(games_per_player)
        .enter()
        .append('text')
        .attr('x', function(d) { return -15 + x(d.value.total_games); })
        .attr('y', function(d,i) { return (i+0.6) * total_bar_height; } )
        .text(function(d) { return d.value.defenses; })
        .attr('fill', 'white')
        .attr('font-size', 10);

    g.selectAll('.playerlabel')
        .data(games_per_player)
        .enter()
        .append('text')
        .attr('x', function(d) { return 5 + x(d.value.total_games); })
        .attr('y', function(d,i) { return (i+0.6) * total_bar_height; } )
        .text(function(d) { return d.key; })
        .attr('fill', 'black')
        .attr('font-size', 10);
}