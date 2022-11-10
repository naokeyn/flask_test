// テーブルにソート機能を追加
//Parser を定義
$.tablesorter.addParser({
    id: 'jpdays',
    is: function (s) {
        return false;
    },
    format: function (s) {
        days = ["月", "火", "水", "木", "金", "土", "日"]
        maxi = 10

        if (s.includes("集中")) {
            s = "998"
        } else if (s.includes("卒研")) {
            s = "999"
        } else {
            for (let i = 0; i < days.length; i++) {
                for (let j = 0; j < maxi; j++) {
                    if (s.includes(days[i] + j)) {
                        s = String(i * maxi + j)
                        //break
                    }
                }
            }
        }

        return s;
    },
    type: 'string'
});

$(document).ready(function () {
    $('#table').tablesorter({
        headers: {
            // 曜日のソート
            1: { sorter: 'jpdays' }
        }
    });
});
