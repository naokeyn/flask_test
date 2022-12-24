from flask import Flask, render_template, request, redirect, Markup
from sqlalchemy import create_engine

import pandas as pd
import numpy as np

from bs4 import BeautifulSoup

import MapData
from create_map import create_map

app = Flask(__name__)

# データベースの読み込み
engine = create_engine("sqlite:///db.sqlite3", encoding="utf-8", echo=False)
data_base = pd.read_sql("select * from df", engine)

# 講義名のリスト
names = data_base["subject_name"].tolist()

# 選択可能な建物のリスト
nodes = list(MapData.data.keys()) # [:3]


@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html"), 404


@app.route("/", methods=["GET"])
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
            return render_template("page_not_found.html")

        elif len(index) <= max_hit or r:
            df = data_base.loc[index, :]
            df = df.sort_values("subject_name", ascending=True)

            data = {
                "name": df["subject_name"].tolist(),        # 講義名
                "time": df["day_period"].tolist(),          # 曜日 + 時限
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
def show_all():
    df = data_base.copy()
    query = "すべて"
    
    data = {
            "name": df["subject_name"].tolist(),        # 講義名
            "time": df["day_period"].tolist(),          # 曜日 + 時限
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
        start = "正門"
        end = "大学会館"
    
    else:
        try:
            start = request.form["start"]
        except:
            start = "正門"
            
        end = request.form["end"]
        
        # 建物名が見つからなかったとき
        if end not in nodes:
            return 404
    
    # idx = np.random.randint(len(ends))
    # end = ends[idx]

    map, d, t = create_map(start, end)
    map = map._repr_html_()

    iframe = BeautifulSoup(map, "html.parser")
    iframe = iframe.select_one("iframe")

    data = {
        "map": Markup(iframe),
        "distance": d,
        "time": t,
        "start": start,
        "end": end
    }

    return render_template("map.html", data=data, starts=nodes, ends=nodes)

# @app.route("/<text>")
# def text(text):
#     return render_template("hello.html", text=text)


if __name__ == "__main__":
    app.run(debug=True)
