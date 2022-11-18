from flask import Flask, render_template, request, redirect, Markup
from sqlalchemy import create_engine

import pandas as pd
import numpy as np

from bs4 import BeautifulSoup

import MapData
from create_map import create_map

app = Flask(__name__)

# データベースの読み込み
engine = create_engine("sqlite:///test.sqlite3", encoding="utf-8", echo=False)
data_base = pd.read_sql("select * from df", engine)

# 講義名のリスト
names = data_base["subject_name"].tolist()

# ゴールとなる建物名のリスト
buildings = list(MapData.data.keys())[3:]


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
        query = request.form["name"]

        index = [i for i in range(len(data_base))
                 if query in data_base.loc[i, "subject_name"]]

        # 一致する講義名がない or queryがNULLのとき
        if len(index) == 0 or query == "":
            return render_template("page_not_found.html")

        else:
            df = data_base.loc[index, :]
            df = df.sort_values("subject_name", ascending=True)

            data = {
                "name": df["subject_name"].tolist(),
                "time": df["day_period"].tolist(),
                "teac": df["teacher"].tolist(),
                "room": df["room"].tolist(),
                "length": len(index)
            }

            return render_template("result.html", data=data)


@app.route("/all", methods=["GET", "POST"])
def show_all():
    df = data_base.sort_values("subject_name", ascending=True)

    data = {
        "lec": df["subject_name"].tolist(),
        "period": df["day_period"].tolist(),
        "room": df["room"].tolist(),
        "length": len(df)
    }

    return render_template("show_all.html", data=data)


@app.route("/map")
def map():
    global buildings
    start = "正門"
    idx = np.random.randint(len(buildings))
    end = buildings[idx]

    map, d, t = create_map(start, end)
    map = map._repr_html_()
    
    iframe = BeautifulSoup(map, "html.parser")
    iframe = iframe.select_one("iframe")
    
    data = {
        "map": Markup(iframe),
        "distance": d,
        "time": t
    }

    return render_template("map.html", data=data)

# @app.route("/<text>")
# def text(text):
#     return render_template("hello.html", text=text)


if __name__ == "__main__":
    app.run(debug=True)
