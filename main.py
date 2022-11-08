from flask import Flask, render_template, request
from sqlalchemy import create_engine

import pandas as pd

app = Flask(__name__)

# データベースの読み込み
engine = create_engine("sqlite:///test.sqlite3", encoding="utf-8", echo=False)
data_base = pd.read_sql("select * from df", engine)

# 講義名のリスト
names = data_base["subject_name"].tolist()

# 部分一致のインデックスを返す
# 同じ文字列にも対応させる
def return_index(query):
    global names
    
    index = []
    for i in range(len(names)):
        if query in names[i]:
            index.append(i)
            
    return index    


@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html"), 404

@app.route("/", methods=["GET"])
def Hello():
    return render_template("index.html")
   
@app.route("/result", methods=["POST"])
def result():
    # フォームに入力された文字列を取得
    query = request.form["name"]
    
    # 部分一致のindexを調べる
    index = return_index(query)

    # 一致する講義名がない場合
    if len(index) == 0:
        return render_template("page_not_found.html")
    
    else:
        data = {
            "name": data_base.loc[index, "subject_name"].tolist(),
            "time": data_base.loc[index, "day_period"].tolist(),
            "teac": data_base.loc[index, "teacher"].tolist(),
            "room": data_base.loc[index, "room"].tolist(),
            "length": len(index)
        }
        
        return render_template("result.html", data=data)
    
@app.route("/all", methods=["GET", "POST"])
def show_all():
    lec_list = data_base["subject_name"].tolist()
    per_list = data_base["day_period"].tolist()
    room_list = data_base["room"].tolist()
    length = len(lec_list)
    
    data = {"lec":lec_list, "period":per_list, "room":room_list, "length":length}
    
    return render_template("show_all.html", data=data)
    

# @app.route("/<text>")
# def text(text):
#     return render_template("hello.html", text=text)

if __name__ == "__main__":
    app.run(debug=True)