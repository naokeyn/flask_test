"""
MapDataのkeyが変わった時に対応するDataBaseの建物名も変更する
"""

# DataBase操作
from sqlalchemy import create_engine
import pandas as pd

# 大野様がお創りになられた辞書型を拝領仕る
import MapData

# DataBaseのパス
PATH = "DataBase/db.sqlite3"

# DataBaseエンジン．よくわからん
engine = create_engine("sqlite:///" + PATH)

# DataBaseの読み込み
db = pd.read_sql(con=engine, sql="select * from df")

# DataBaseの建物名を取得
builds = db.loc[:, "building"].tolist()

# MapDataのkeyを取得，並び替え
keys = list(MapData.data.keys())

# DataBaseの建物名とMapDataの建物名を比較
diff_buil = (set(keys) ^ set(builds)) & set(builds)

# Noneを削除
diff_buil = list(diff_buil)
diff_buil.remove("None")

# 書き換える必要がある建物名を出力
# print(diff_buil)

# 修正前後の名称をまとめたファイルを読み込み
mod = pd.read_csv("mod.csv")
before_name = mod.loc[:, "before"].tolist()
after_name  = mod.loc[:, "after"].tolist()

# 確認
assert set(before_name) == set(diff_buil), \
    f"mod.csv の内容とMapData.py の内容が一致しません\n{before_name} : {diff_buil}"

# 置き換え作業
# 全探査でやる
# 改良の余地あり
for i in range(len(db)):
    buid_i = db.loc[i, "building"]
    if buid_i in before_name:
        idx = before_name.index(buid_i)
        db.loc[i, "building"] = after_name[idx]

# 確認
builds = db.loc[:, "building"].tolist()
diff = list( (set(builds) ^ set(keys)) & set(builds) )

assert len(diff) == 1 and diff[0] == "None", f"なんか失敗してね？：{diff}"

# DataBaseの上書き保存
db.to_sql("df", con=engine, if_exists="replace")

