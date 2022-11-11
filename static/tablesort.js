// テーブルにソート機能を追加
//Parser を定義
$.tablesorter.addParser({
    id: 'jpdays',
    is: function (s) {
        return false;
    },

    // 曜日 + 時限 を4桁の整数で置き換える
    // 例 : 月1~3 -> "0130"，火2,木2 -> 1232
    // 集中 -> 9999, 卒研 -> 9998
    format: function (s) {
        const days = ["月", "火", "水", "木", "金", "土", "日"]
        const remove_char = [",", "(", ")", "〜"]

        // 不要な文字を消去
        for (let i = 0; i < remove_char.length; i++) {
            s = s.replace(remove_char[i], "")
        }

        // 数字に置き換え
        if (s.includes("集中")) {
            s = "9999"
        } else if (s.includes("卒研")) {
            s = "9998"
        } else {
            for (let i = 0; i < days.length; i++) {
                // 正規表現で全置換
                var day = new RegExp(days[i], 'gu')
                s = s.replace(day, i)
            }
        }

        // 4桁に整える
        s = String(s + "00").slice(0, 4)

        return s;
    },
    type: 'string'
});

$(document).ready(function () {
    $('#table').tablesorter({
        headers: {
            1: { sorter: 'jpdays' } // 曜日のソート
        }
    });
});
