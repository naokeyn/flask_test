// 目的地と出発地の入れ替え
let change = () => {

    const start = document.getElementById("start")
    const end = document.getElementById("end")

    let start_value = start.value
    let end_value = end.value

    start.value = end_value
    end.value = start_value

}

$(function () {
    $("#start").autocomplete({
        source: function (request, response) {
            
            var list = [];
            list = room_name.filter(function (rm) {
                return (
                    rm.label.indexOf(request.term) === 0 ||
                    rm.hira.indexOf(request.term) === 0
                );
            });
            response(list);
        }
    });
});

$(function () {
    $("#end").autocomplete({
        source: function (request, response) {
            var list = [];
            list = room_name.filter(function (rm) {
                return (
                    rm.label.indexOf(request.term) === 0 ||
                    rm.hira.indexOf(request.term) === 0
                );
            });
            response(list);
        }
    });
});