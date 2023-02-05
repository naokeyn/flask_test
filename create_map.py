import os                   # ファイルパスの指定に使用
import sys                  # プログラム強制終了に使用（try部分）
import time                 # 実行時間計算に使用
from pathlib import Path    # 格納パスの作成に使用
from sre_parse import expand_template

import folium               # 主にマップのピン配置
import osmnx as ox          # 主に最短経路検索
import networkx as nx       # 距離計算
import numpy as np

import math
import MapData              # 緯度経度およびURL格納データ


# 出発場所や到着場所の設定
start_name = "西門"
end_name = "図書館"


def create_map(start_name, end_name):
    try:
        start_data = MapData.data[start_name][0]
        start_lat, start_long = start_data[0], start_data[1]
        end_data = MapData.data[end_name][0]
        end_lat, end_long = end_data[0], end_data[1]

        if start_name in MapData.exception_name:
            start_lat, start_long = 35.86094, 139.60693
        elif end_name in MapData.exception_name:
            end_lat, end_long = 35.86094, 139.60693

    except KeyError:
        print("辞書リストに存在しない名前が指定されています\n",
              "MapData.pyを確認してください")
        sys.exit()
    except:
        print("取得段階で何らかのエラーが発生しました\n",
              "頑張って確認してね☆")
        sys.exit()

    # 地図読み込み中心位置および出力ファイルパス
    center_point = (35.8622, 139.6076)
    outdir_path = Path("static/map_ctrl")
    os.makedirs(outdir_path, exist_ok=True)

    # 道路ネットワーク取得（ファイルが既にあれば再利用）
    graphml_outfile = outdir_path / "road_network.graphml"

    if os.path.isfile(graphml_outfile) is False:
        G = ox.graph_from_point(center_point, dist=450,
                                network_type="walk")    # 歩行可能な道路グラフネットワークを取得
        # 取得データを再利用目的でGraphml形式にて保存
        ox.save_graphml(G, filepath=graphml_outfile)
    else:
        # 前回取得の道路グラフネットワークを再利用
        G = ox.load_graphml(graphml_outfile)

    # 道路ネットワークを可視化（マップはOpenStreetMap）
    map = ox.plot_graph_folium(G, color="gray", tiles="OpenStreetMap")

    # 最短経路の探索
    start_point = (start_lat, start_long)
    end_point = (end_lat, end_long)
    start_node = ox.nearest_nodes(G, start_long, start_lat)
    end_node = ox.nearest_nodes(G, end_long, end_lat)
    shortest_path = ox.shortest_path(G, start_node, end_node)

    direction, distance = np.empty(0), np.empty(0)
    distance_new, direction_new = [0], np.empty(0)

    for i in range(1, len(shortest_path)):
        if i < len(shortest_path)-1:
            lat_0, long_0 = G.nodes(data=True)[
                shortest_path[i-1]]["y"], G.nodes(data=True)[shortest_path[i-1]]["x"]
            lat_1, long_1 = G.nodes(data=True)[shortest_path[i]]["y"], G.nodes(
                data=True)[shortest_path[i]]["x"]
            lat_2, long_2 = G.nodes(data=True)[
                shortest_path[i+1]]["y"], G.nodes(data=True)[shortest_path[i+1]]["x"]
            #vec0 , vec1 = [lat_1-lat_0, long_1-long_0, 0]  , [lat_2-lat_1, long_2-long_1, 0]
            vec0, vec1 = [long_1-long_0, lat_1-lat_0,
                          0], [long_2-long_1, lat_2-lat_1, 0]

            absvec0, absvec1 = np.linalg.norm(vec0), np.linalg.norm(vec1)
            inner = np.inner(vec0, vec1)
            cos_theta = inner / (absvec0 * absvec1)
            theta = math.degrees(math.acos(cos_theta))

            cross = np.cross(vec0, vec1)

            if theta > 45:
                if cross[2] < 0:
                    # print("右折")
                    direction = np.append(direction, "右折")
                elif cross[2] > 0:
                    # print("左折")
                    direction = np.append(direction, "左折")
            else:
                # print("直進")
                direction = np.append(direction, "直進")

        distance = np.append(distance, nx.shortest_path_length(
            G, shortest_path[i-1], shortest_path[i], weight='length'))

    if len(shortest_path) == 2:
        direction = np.append(direction, "直進")
    else:
        direction = np.insert(direction, 0, "直進")

    i, j, k = 0, 0, 0
    while i < len(distance):
        if direction[i] == "直進":
            distance_new[j] += distance[i]
            # print("case:1")
        else:
            distance_new = np.append(distance_new, distance[i])
            j += 1
            # print("case:2")
        i += 1
    direction_new = direction[~(direction == "直進")]

    return_str = ""
    while True:
        return_str += "↓\n"\
            + "↓約" + str(int(round(distance_new[k], -1))) + "m直進する\n"\
            + "↓\n"
        if k == len(distance_new)-1:
            break
        return_str += direction_new[k] + "\n"
        k += 1
    return_str = return_str.rstrip()

    # 最短経路探索結果の可視化
    new_map = ox.plot_route_folium(
        G, shortest_path, route_map=map, color="blue", tiles="OpenStreetMap")
    start_point = (start_data[0], start_data[1])
    end_point = (end_data[0], end_data[1])

    # 出発地点および到着地点のマーカーおよびポップアップ設定
    # 変更前のリンク指定：<a href="https://maps.google.com/maps?q=&layer=c&cbll=' + str(MapData.data[start_name][1][0]) + ',' + str(MapData.data[start_name][1][1]) + '&cbp=11,0,0,0,0"  target="_blank">' + start_name + '（Googleストリートビュー）
    folium.Marker(start_point,
                  popup='<h4><a href="https://www.google.com/maps/@?api=1&map_action=pano&parameters&viewpoint=' +
                  str(MapData.data[start_name][1][0]) + ',' + str(MapData.data[start_name]
                                                                  [1][1]) + '"  target="_blank">' + start_name + '（Googleストリートビュー）'
                  '<br/><br/><img width="320" height="240" src=static/map_ctrl/' +
                  MapData.data[start_name][2] + '></h4></a>',
                  tooltip="出発地点：" + start_name, icon=folium.Icon(color="green", icon="glyphicon glyphicon-flag")).add_to(new_map)

    folium.Marker(end_point,
                  popup='<h4><a href="https://www.google.com/maps/@?api=1&map_action=pano&parameters&viewpoint=' +
                  str(MapData.data[end_name][1][0]) + ',' + str(MapData.data[end_name]
                                                                [1][1]) + '" target="_blank">' + end_name + '（Googleストリートビュー）'
                  '<br/><br/><img width="320" height="240" src=static/map_ctrl/' +
                  MapData.data[end_name][2] + '></h4></a>',
                  tooltip="到着地点：" + end_name,  icon=folium.Icon(color="red", icon="glyphicon glyphicon-flag")).add_to(new_map)

    d = round(nx.shortest_path_length(
        G, start_node, end_node, weight='length'))
    t = round(nx.shortest_path_length(
        G, start_node, end_node, weight='length') / 82.5)

    return new_map, d, t, return_str
