function filter_games() {
    var select = document.getElementById('filter-player');
    var player = select.options[select.selectedIndex].value;
    var new_url = '';

    if (player == "(anyone)") {
        new_url = '/games';
    }
    else {
        var select2 = document.getElementById('filter-player2');
        if (select2) {
            var player2 = select2.options[select2.selectedIndex].value;
            if (player2 == "(anyone)") {
                new_url = "/games/" + encodeURI(player);
            }
            else {
                new_url = "/games/" + encodeURI(player) + "/vs/" + encodeURI(player2);
            }
        }
        else {
            new_url = "/games/" + encodeURI(player);
        }
    }

    window.location = new_url;
    return false;
}