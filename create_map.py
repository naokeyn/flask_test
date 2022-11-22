import os                   # ファイルパスの指定に使用
import sys                  # プログラム強制終了に使用（try部分）
from pathlib import Path    # 格納パスの作成に使用

import folium               # 主にマップのピン配置
import osmnx as ox          # 主に最短経路検索
import networkx as nx       # 距離計算
import MapData              # 緯度経度およびURL格納データ

def create_map(start_name, end_name):

    try:
        start_data = MapData.data[start_name][0]
        start_lat, start_long = start_data[0], start_data[1]
        end_data = MapData.data[end_name][0]
        end_lat, end_long = end_data[0], end_data[1]
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
    outdir_path = Path("static/map_ctrl") ##("sakuraku_saitama_saitama_Japan")
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
    '''
    scipyのscipy.spatial.cKDTree.queryによる最近傍点検索を実行する
    cf. "venv\Lib\site-packages\osmnx\distance.py" , line 206
    '''
    shortest_path = ox.shortest_path(G, start_node, end_node)

    # 最短経路探索結果の可視化
    new_map = ox.plot_route_folium(
        G, shortest_path, route_map=map, color="blue", tiles="OpenStreetMap")

    # 出発地点および到着地点のマーカーおよびポップアップ設定
    folium.Marker(start_point,
                  popup='<h4><a href="https://maps.google.com/maps?q=&layer=c&cbll=' + str(MapData.data[start_name][1][0]) + ',' + str(
                      MapData.data[start_name][1][1]) + '&cbp=11,0,0,0,0" target="_blank">' + start_name + '（Googleストリートビュー）'
                  '<br/><br/><img width="320" height="240" src=../static/map_ctrl/' +
                  MapData.data[start_name][2] + '></h4></a>',
                  tooltip="出発地点：" + start_name, icon=folium.Icon(color="green", icon="glyphicon glyphicon-flag")).add_to(new_map)

    folium.Marker(end_point, popup='<h4><a href="https://maps.google.com/maps?q=&layer=c&cbll=' + str(MapData.data[end_name][1][0]) + ',' + str(MapData.data[end_name][1][1]) + '&cbp=11,0,0,0,0" target="_blank">' + end_name + '（Googleストリートビュー）'
                  '<br/><br/><img width="320" height="240" src=../static/map_ctrl/' +
                  MapData.data[end_name][2] + '></h4></a>',
                  tooltip="到着地点：" + end_name,  icon=folium.Icon(color="red", icon="glyphicon glyphicon-flag")).add_to(new_map)

    # 経路案内マップの出力
    folium_path_outfile = "templates/road_network.html"
    # new_map.save(outfile=str(folium_path_outfile))

    distance = str(round(nx.shortest_path_length(
        G, start_node, end_node, weight='length')))
    minutes = str(round(nx.shortest_path_length(
        G, start_node, end_node, weight='length') / 85.2))

    return new_map, distance, minutes
