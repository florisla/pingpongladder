function filter_games() {
    var select = document.getElementById('filter-player');
    var player = select.options[select.selectedIndex].value;

    if (player == "(anyone)") {
        window.location = '/games';
        return false;
    }

    var select2 = document.getElementById('filter-player2');
    if (select2) {
        var player2 = select2.options[select2.selectedIndex].value;
        if (player2 == "(anyone)") {
            window.location = "/games/" + player;
            return false;
        }

        window.location = "/games/" + player + "/vs/" + player2;
        return false;
    }
    else {
        window.location = "/games/" + player;
    }

    return false;
}