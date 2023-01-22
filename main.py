from flask import Flask, render_template, \
    request, redirect, url_for, Markup
from flask_httpauth import HTTPBasicAuth

from sqlalchemy import create_engine
from bs4 import BeautifulSoup

import pandas as pd

import MapData
from create_map import create_map

app = Flask(__name__)
auth = HTTPBasicAuth()

# id_listの読み込み
with open("id_list.txt", "r") as r:
    id, pw = r.read().split("\n")

id_list = {id: pw}

# データベースの読み込み
engine = create_engine("sqlite:///db.sqlite3", encoding="utf-8", echo=False)
data_base = pd.read_sql("select * from df", engine)

# 教室名 <-> 建物 のDataFrame
room_data = pd.read_sql("select * from room", engine)

# 講義名のリスト
names = data_base["subject_name"].tolist()

# 選択可能な建物のリスト
nodes = list(MapData.data.keys())  # [:3]

# map のデータを reshape
def map_data(start, end):
    global nodes
    
    if (start not in nodes) or (end not in nodes):
        return False
    
    map, d, t, route = create_map(start, end)
    map = map._repr_html_()

    iframe = BeautifulSoup(map, "html.parser")
    iframe = iframe.select_one("iframe")

    route = route.split("\n")
    
    data = {
        "map": Markup(iframe),
        "distance": d,
        "time": t,
        "start": start,
        "end": end,
        "route": route
    }

    return data

# Basic認証
@auth.get_password
def get_pw(id):
    if id in id_list:
        return id_list.get(id)

    return None

@app.errorhandler(400)
def invalid_request(error):
    return render_template("400.html"), 400


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.route("/", methods=["GET"])
@auth.login_required
def index():
    return render_template("index.html")


@app.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "GET":
        return redirect("/")

    else:
        # フォームに入力された文字列を取得
        value = request.form["name"].split(", ")

        # リダイレクトか判定
        if len(value) == 2:
            query, r = value[0], True
        else:
            query, r = value[0], False

        index = [i for i in range(len(data_base))
                 if query in data_base.loc[i, "subject_name"]]

        # 検索結果の上限
        max_hit = 50

        # 一致する講義名がない or queryがNULLのとき
        if len(index) == 0 or query == "":
            return render_template("404.html"), 404

        elif len(index) <= max_hit or r:
            df = data_base.loc[index, :]
            df = df.sort_values("subject_name", ascending=True)

            data = {
                "name": df["subject_name"].tolist(),        # 講義名
                "time": df["day_period"].tolist(),          # 曜日 + 時限
                "tearm": df["tearm"].tolist(),              # 開講ターム
                # "teac": df["teacher"].tolist(),             # 教員名
                "room": df["room"].tolist(),                # 教室
                "buil": df["building"].tolist(),            # 建物名
                "syll": df["link"].tolist(),                # シラバスのリンク
                "length": len(index),                       # データの長さ
                "query": query                              # 検索キーワード
            }

            return render_template("result.html", data=data)

        else:
            data = {
                "length": len(index),
                "query": query
            }

            return render_template("overflow.html", data=data)


@app.route("/all", methods=["GET", "POST"])
@auth.login_required
def show_all():
    df = data_base.copy()
    query = "すべて"

    data = {
        "name": df["subject_name"].tolist(),        # 講義名
        "time": df["day_period"].tolist(),          # 曜日 + 時限
        "tearm": df["tearm"].tolist(),
        # "teac": df["teacher"].tolist(),             # 教員名
        "room": df["room"].tolist(),                # 教室
        "buil": df["building"].tolist(),            # 建物名
        "syll": df["link"].tolist(),                # シラバスのリンク
        "length": len(df),                       # データの長さ
        "query": query                              # 検索キーワード
    }

    return render_template('result.html', data=data)


@app.route("/map", methods=["GET", "POST"])
def map():
    global nodes
    
    if request.method == "GET":
        # クエリパラメータが存在するとき
        if request.args:
            start = request.args.get("start")
            end = request.args.get("end")
        
        # クエリパラメータが存在しないとき
        # デフォルト値を設定
        else:        
            start = "正門"
            end = "大学会館"
        
    # method が post のとき
    else:
        # form の値を取得してみる
        try:
            start = request.form["start"]

        # ダメだったらデフォルト値を入れる
        except:
            start = "正門"

        end = request.form["end"]

        # 建物名が見つからなかったとき
        if end not in nodes:
            return render_template("400.html"), 400

    data = map_data(start, end)
    
    if not data:
        return render_template("400.html"), 400

    return render_template("map.html", data=data, starts=nodes, ends=nodes)


@app.route("/room")
def room():
    msg = request.args.get("msg")
    
    return render_template("room.html", msg=msg)


@app.route("/room-result", methods=["GET", "POST"])
def room_result():
    global room_data
    
    start_room = request.form["start-room"]
    end_room = request.form["end-room"]

    room_list = room_data.loc[:, "room"].tolist()
    buil_list = room_data.loc[:, "building"].tolist()
    
    if (start_room in room_list) and (end_room in room_list):
        start_idx = room_list.index(start_room)
        start = buil_list[start_idx]

        end_idx = room_list.index(end_room)
        end = buil_list[end_idx]
        
    else :
        return redirect(url_for("room", msg='お探しの教室が見つかりませんでした'))
    
    return redirect(url_for('map', start=start, end=end))


if __name__ == "__main__":
    app.run(debug=True)
