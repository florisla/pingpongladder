d3.json("http://florisla.pythonanywhere.com/games/data", function(games) {
    matches_per_date = game_count_per_day(games.game_details);
    challenges_won_per_date = lost_won_per_day(games.game_details);
    games_per_player = games_per_player(games.game_details);
    play_times = games_time_per_day(games.game_details);

    graph_match_rate(matches_per_date);
    graph_lost_won_rate(challenges_won_per_date);
    graph_games_per_player(games_per_player);
    graph_play_times(play_times);
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
            players[details.challenger.name] = {
                challenges:0,
                challengeswon:0,
                defenses:0,
                defenseswon:0
            };
        }
        if (! (details.challengee.name in players)) {
            players[details.challengee.name] = {
                challenges:0,
                challengeswon:0,
                defenses:0,
                defenseswon:0
            };
        }

        players[details.challenger.name].challenges += 1;
        if (details.challenger.name == details.winner) {
            players[details.challenger.name].challengeswon += 1;
        }
        players[details.challengee.name].defenses += 1;
        if (details.challengee.name == details.winner) {
            players[details.challengee.name].defenseswon += 1;
        }

    }
    for (var name in players) {
        player = players[name];
        player.total_games = player.challenges + player.defenses;
    }
    return players;
}

function games_time_per_day (game_details) {
    date_time_format = d3.time.format('%Y-%m-%d %H:%M');
    dates = [];
    for (var game in game_details) {
        date_time = date_time_format.parse(game_details[game].date);
        dates.push(date_time);
    }
    return dates;
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
    var height = 600;
    var margin_horizontal = 40;
    var margin_vertical = 25;
    var total_bar_height = (height - 2*margin_vertical) / games_per_player.length;
    var bar_height = 0.5 * total_bar_height;
    var bar_spacing = 0.4 * total_bar_height;

    var most_played = d3.max(games_per_player, function(d) { return d.value.total_games; } );

    x = d3.scale.linear()
        .domain([0, most_played])
        .range([0,  width - 2*margin_horizontal]);

    svg = d3.select('.gamesperplayer')
        .attr('width', width)
        .attr('height', height);

    g = svg.append('g')
        .attr('transform', 'translate(20,12)');

    legend = svg.append('g')
        .attr('id', 'legend')
        .attr('transform', 'translate(' + (width-100) + ', 180)');

    legend.append('rect')
        .attr('width', 10)
        .attr('height', 10)
        .attr('x', 0)
        .attr('y', 10)
        .attr('fill', 'green');

    legend.append('rect')
        .attr('width', 10)
        .attr('height', 10)
        .attr('x', 0)
        .attr('y', 30)
        .attr('fill', 'indianred');

    legend.append('rect')
        .attr('width', 10)
        .attr('height', 10)
        .attr('x', 0)
        .attr('y', 50)
        .attr('fill', 'lightgreen');

    legend.append('rect')
        .attr('width', 10)
        .attr('height', 10)
        .attr('x', 0)
        .attr('y', 70)
        .attr('fill', 'red');

    legend.append('text')
        .attr('x', 18)
        .attr('y', 17)
        .attr('fill', 'black')
        .attr('font-size', 8)
        .text('Challenges won')

    legend.append('text')
        .attr('x', 18)
        .attr('y', 37)
        .attr('fill', 'black')
        .attr('font-size', 8)
        .text('Challenges lost')

    legend.append('text')
        .attr('x', 18)
        .attr('y', 57)
        .attr('fill', 'black')
        .attr('font-size', 8)
        .text('Defenses won')

    legend.append('text')
        .attr('x', 18)
        .attr('y', 77)
        .attr('fill', 'black')
        .attr('font-size', 8)
        .text('Defenses lost')

    g.selectAll('.challengeswon')
        .data(games_per_player)
        .enter()
        .append('rect')
        .attr('x', 0)
        .attr('y', function(d,i) { return i*total_bar_height; } )
        .attr('width', function(d,i) { return x(d.value.challengeswon); } )
        .attr('height', bar_height)
        .attr('class', 'challenges')
        .attr('id', function(d) { return d.key; } )
        .attr('fill', 'green');

    g.selectAll('.challengeslost')
        .data(games_per_player)
        .enter()
        .append('rect')
        .attr('x', function(d) { return x(d.value.challengeswon); } )
        .attr('y', function(d,i) { return i*total_bar_height; } )
        .attr('width', function(d) { return x(d.value.challenges - d.value.challengeswon); } )
        .attr('height', bar_height)
        .attr('class', 'challenges')
        .attr('id', function(d) { return d.key; } )
        .attr('fill', 'indianred');

    g.selectAll('.challengelostnr')
        .data(games_per_player)
        .enter()
        .append('text')
        .attr('x', function(d) { return -17 + x(d.value.challenges); })
        .attr('y', function(d,i) { return (i+0.45) * total_bar_height; } )
        .text(function(d) { if ((d.value.challenges - d.value.challengeswon) > 0) { return d.value.challenges - d.value.challengeswon; } return ''; } )
        .attr('fill', 'white')
        .attr('font-size', 10);

    g.selectAll('.challengewonnr')
        .data(games_per_player)
        .enter()
        .append('text')
        .attr('x', function(d) { return -17 + x(d.value.challengeswon); })
        .attr('y', function(d,i) { return (i+0.45) * total_bar_height; } )
        .text(function(d) { if (d.value.challenges > 0) { return d.value.challengeswon; } return ''; } )
        .attr('fill', 'white')
        .attr('font-size', 10);

    g.selectAll('.defenseswon')
        .data(games_per_player)
        .enter()
        .append('rect')
        .attr('x', function(d) { return x(d.value.challenges); } )
        .attr('y', function(d,i) { return i*total_bar_height; } )
        .attr('width', function(d) { return x(d.value.defenseswon); } )
        .attr('height', bar_height)
        .attr('fill', 'lightgreen');

    g.selectAll('.defenseslost')
        .data(games_per_player)
        .enter()
        .append('rect')
        .attr('x', function(d) { return x(d.value.challenges) + x(d.value.defenseswon); } )
        .attr('y', function(d,i) { return i*total_bar_height; } )
        .attr('width', function(d) { return x(d.value.defenses - d.value.defenseswon); } )
        .attr('height', bar_height)
        .attr('fill', 'red');

    g.selectAll('.defensewonnr')
        .data(games_per_player)
        .enter()
        .append('text')
        .attr('x', function(d) { return -15 + x(d.value.total_games - d.value.defenses + d.value.defenseswon); })
        .attr('y', function(d,i) { return (i+0.45) * total_bar_height; } )
        .text(function(d) { if (d.value.defenseswon > 0) { return d.value.defenseswon; } return ''; })
        .attr('fill', 'white')
        .attr('font-size', 10);

    g.selectAll('.defenselostnr')
        .data(games_per_player)
        .enter()
        .append('text')
        .attr('x', function(d) { return -15 + x(d.value.total_games); })
        .attr('y', function(d,i) { return (i+0.45) * total_bar_height; } )
        .text(function(d) { if ((d.value.defenses - d.value.defenseswon)> 0) { return d.value.defenses - d.value.defenseswon; } return ''; })
        .attr('fill', 'white')
        .attr('font-size', 10);

    g.selectAll('.playerlabel')
        .data(games_per_player)
        .enter()
        .append('text')
        .attr('x', function(d) { return 5 + x(d.value.total_games); })
        .attr('y', function(d,i) { return (i+0.45) * total_bar_height; } )
        .text(function(d) { return d.key; })
        .attr('fill', 'black')
        .attr('font-size', 10);
}

function graph_play_times(play_times) {

    var width = 500;
    var height = 500;

    date_format = d3.time.format('%Y-%m-%d');

    dates = [];
    for (i in play_times) {
        play_time = play_times[i];
        date = date_format(play_time);

        if (dates.indexOf(date) < 0) {
            dates.push(date);
        }
    }

    x = d3.scale.ordinal()
        .domain(dates)
        .rangeRoundBands([100, width-20]);

    y = d3.scale.linear()
        .domain(d3.extent(play_times, function(d) { e=new Date(d.getTime()); e.setFullYear(1970, 0, 1); return e.getTime(); } ))
        .range([height-20, 0+20]);

    y_axis = d3.svg.axis()
        .scale(y)
        .orient('left');

    svg = d3.select('.playtimes')
        .attr('width', width)
        .attr('height', height);

    var axis_group = svg.append("g")
        .attr('transform', 'translate(30,0)')
        .call(y_axis);

    svg.selectAll('time')
        .data(play_times)
        .enter()
        .append('circle')
        .attr('r', 3)
        .attr('cx', function(d) { return x(date_format(d)); } )
        .attr('cy', function(d) { e=new Date(d.getTime()); e.setFullYear(1970, 0, 1); return y(e.getTime()); } )
        .attr('fill', 'gray')
        .attr('opacity', '0.6')

}