// 全角英数字を半角に変換
let han_to_zen = (str) => {
    return str.replace(/[Ａ-Ｚａ-ｚ０-９]/g, function (s) {
        return String.fromCharCode(s.charCodeAt(0) - 0xFEE0)
    })
}

// テーブルにソート機能を追加

// 曜日 + 時限 を4桁の整数で置き換える
// 例 : 月1~3 -> "0130"，火2,木2 -> 1232
// 集中 -> 9999, 卒研 -> 9998
$.tablesorter.addParser({
    id: 'jpdays',
    is: function (s) {
        return false;
    },

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

        return s
    },
    type: 'string'
});

// tearm のソート
// 第1~2 → 夏季 → 第3~4 冬季 → 通年
// 4桁の数字に変換
$.tablesorter.addParser({
    id: 'tearm',
    is: function (s) {
        return false;
    },

    format: function (s) {
        const tearms = {
            "夏季集中": "2300",
            "冬季集中": "4500",
            "通年": "5000",
            "通年集中": "6000"
        }
        const tearms_len = 4

        for (let i = 0; i < tearms_len; i++) {
            let tearm = Object.keys(tearms)[i]
            if (s === tearm) {
                s = tearms[tearm]
                return s
            }
        }

        const remove_char = ["第", "・"]

        for (let i = 0; i < remove_char.length; i++) {
            s = s.replace(remove_char[i], "")
        }

        s = String(han_to_zen(s) + "000").slice(0, 4)

        return s
    },
    type: 'string'
});

$(document).ready(function () {
    $('#table').tablesorter({
        headers: {
            1: { sorter: 'tearm' },
            2: { sorter: 'jpdays' } // 曜日のソート
        }
    });
});
