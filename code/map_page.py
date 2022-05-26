import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from tkinter import font
import pandas as pd
from tkinter import scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import seaborn as sns
import plotly.graph_objects as go
import palettable
from tkwebview2.tkwebview2 import WebView2
from tkinterweb import HtmlFrame
import time
import folium
from PIL import Image, ImageTk
from folium import plugins
import urllib
import math
import threading
import random
import csv
import string
import re

class MapPage:
    def __init__(self, root):
##        self.root = tk.Tk()
        self.root = root
        self.data = pd.read_csv("../data/trace0_new.csv")
        self.add_obj()
        self.show()

    def show(self):
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.mpage = tk.Canvas(self.root)
        self.mpage.grid(row = 0, column = 0,  rowspan = 2, sticky = 'nsew')
##        self.mpage.delete(tk.ALL)
        
        self.map_html = WebView2(self.mpage, width = width-20, height = height-60,)
        self.map_html.load_url("./save_map.html")
        self.mpage.create_window(width/2, height/2,
                                 window = self.map_html)
        
        ttk.Button(self.mpage, text = "后退", width = 8, command = self.go_back).place(
            x = 55, y = 25)

    def go_back(self):
        self.mpage.destroy()
        
    def add_obj(self):
        self.nhMap = self.default_map()
        obs = self.data.groupby(["id","category","standpoint"]).time.count().reset_index()
        f = self.data.groupby("id").x.apply(lambda x: len(set(x))).reset_index()
        obs = obs[obs["id"].apply(lambda x: True if x in f[f.x > 1].id.values else False)]
        features = []
        for i,row in obs.iterrows():
            col = (lambda x: "red" if x == 1 else "blue")(row["standpoint"])
            icon = folium.features.CustomIcon('../graph/{}_{}.png'.format(row["category"], col))
            points = []
            tem = self.data[(self.data["id"] == row["id"]) & (self.data["category"] == row[
                "category"]) & (self.data["standpoint"] == row["standpoint"])]
            if len(set(tem.x)) > 1:
                for j,sub in tem.iterrows():
                    time = sub["time"]
                    tooltip = row["category"]
                    coordinates = [sub["x"], sub["y"]]
                    points.append({"time":time, "tooltip":tooltip, "coordinates":coordinates})
                [features.append(
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": point["coordinates"],
                        },
                        "properties": {
                            "time": point["time"],
                            "popup": point["tooltip"],
                            "tooltip": point["tooltip"],
                            "id": '{}_{}'.format(row["category"], col),
                            "icon": "marker",
                            "iconstyle": {
                                "iconUrl": icon.options["iconUrl"],
                                "iconSize": [30, 30],
                            },
                        },
                    })
                    for point in points]
        a = plugins.TimestampedGeoJson(
            {"type": "FeatureCollection", "features": features},
            period="PT1M",
            add_last_point = False,
            auto_play = False,
            loop = False,
            max_speed = 2,
            loop_button = False,
            date_options="YYYY-MM-DD HH:MM",
            time_slider_drag_update=True,
            duration = "PT1S",
        )
        a.add_to(self.nhMap)
        self.nhMap.save("./save_map.html")
            
    def default_map(self):
##        f = folium.Figure(width=1200, height=600)
        m = folium.Map(
##            width = 1600, height = 600, 
            location=[14.388572, 114.007092],
            zoom_start=5, max_bounds=True,
##            control_scale = True,
##            prefer_canvas = True,
            tiles = "https://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}",
            attr='default'
            )
##
##        twhxLayer = folium.FeatureGroup(name = "台湾海峡")
##        dsqdLayer = folium.FeatureGroup(name = "东沙群岛")
##        xsqdLayer = folium.FeatureGroup(name = "西沙群岛")
##        zsqdLayer = folium.FeatureGroup(name = "中沙群岛")
##        nsqdLayer = folium.FeatureGroup(name = "南沙群岛")
##        hydLayer = folium.FeatureGroup(name = "黄岩岛")
##        twhxLayer.add_to(m)
##        dsqdLayer.add_to(m)
##        xsqdLayer.add_to(m)
##        zsqdLayer.add_to(m)
##        nsqdLayer.add_to(m)
##        hydLayer.add_to(m)
##
##        twhx = [(121.570148, 25.283938),(119.889239, 25.591495),(119.702472, 25.303804),(119.592609,25.144784),
##                (119.131183,25.005472),(118.69173,24.566605),(117.988605,24.106142),(117.439288,23.55341),
##                (117.340411,23.452661),(116.802081,23.190354),(120.713214,21.901765),(120.229816,22.572928),
##                (120.021075,23.069116),(120.141925,23.694328),(120.141925,23.794892),(120.471515,24.256477),
##                (120.894488,24.806179),(121.042804,25.040315),(121.26253,25.134838)]
##        dsqd = [(116.019274,21.222248),(116.16759,21.171033),(116.387316,20.899297),(116.815783,20.817166),
##                 (116.958605,20.791491),(116.997057,20.699025),(116.986071,20.570506),(116.887194,20.513923),
##                 (116.70592,20.529357),(116.398303,20.791491),(116.074206,20.90956),(115.898425,20.878768),
##                 (115.865466,21.022408),(115.865466,21.109551)]
##        xsqd = [(111.448962,17.203182),(112.305895,17.082452),(112.976061,16.819727),(113.00902,16.714535),
##                (112.701403,16.018825),(112.36632,15.654183),(111.146838,15.717646),(111.405016,16.440764),
##                (111.39403,17.061448),]
##        zsqd = [(114.146105,16.214084),(114.711901,16.27737),(114.733874,16.287915),(115.030505,16.050501),
##                (114.84923,15.770517),(114.673449,15.537783),(114.299914,15.341871),(113.964831,15.325979),
##                (113.624255,15.537783),(113.827502,15.717646),(113.904406,15.960738)]
##        hyd = [(117.7661,15.384246),(117.941882,15.235896),(117.90343,15.013175),(117.57384,14.991952),
##               (117.535388,15.214695)]
##        nsqd = [(109.246203,7.263784),(109.828478,8.047743),(110.949084,8.460897),(111.344592,8.656449),
##                (111.388537,9.383425),(112.465197,9.795071),(113.058459,9.968245),(114.398791,11.748456),
##                (115.695178,11.522485),(116.650988,11.791478),(117.870471,11.264009),(118.013293,10.800328),
##                (117.551867,9.870846),(116.848742,8.917026),(115.530383,8.167384),(115.206286,7.39999),
##                (114.733874,6.756741),(113.800036,6.412955),(113.212267,4.822173),(112.349841,3.611493),
##                (111.740099,3.699205),(111.784045,6.669453)]
##        folium.Polygon([(i[1], i[0]) for i in twhx],
##                       color = "gray",
##                       weight = 1,
##                       popup = "台湾海峡",
##                       tooltip = '台湾海峡',
##                       fill = True,
##                       fill_color = "red",
##                       fill_opacity = 0.1).add_to(twhxLayer)
##        folium.Polygon([(i[1], i[0]) for i in dsqd],
##                       color = "gray",
##                       weight = 1,
##                       popup = "东沙群岛",
##                       tooltip = '东沙群岛',
##                       fill = True,
##                       fill_color = "red",
##                       fill_opacity = 0.1).add_to(dsqdLayer)
##        folium.Polygon([(i[1], i[0]) for i in xsqd],
##                       color = "gray",
##                       weight = 1,
##                       popup = "西沙群岛",
##                       tooltip = "西沙群岛",
##                       fill = True,
##                       fill_color = "red",
##                       fill_opacity = 0.1).add_to(xsqdLayer)
##        folium.Polygon([(i[1], i[0]) for i in zsqd],
##                       color = "gray",
##                       weight = 1,
##                       popup = "中沙群岛",
##                       tooltip = "中沙群岛",
##                       fill = True,
##                       fill_color = "red",
##                       fill_opacity = 0.1).add_to(zsqdLayer)
##        folium.Polygon([(i[1], i[0]) for i in hyd],
##                       color = "gray",
##                       weight = 1,
##                       popup = "黄岩岛",
##                       tooltip = "黄岩岛",
##                       fill = True,
##                       fill_color = "red",
##                       fill_opacity = 0.1).add_to(hydLayer)
##        folium.Polygon([(i[1], i[0]) for i in nsqd],
##                       color = "gray",
##                       weight = 1,
##                       popup = "南沙群岛",
##                       tooltip = "南沙群岛",
##                       fill = True,
##                       fill_color = "red",
##                       fill_opacity = 0.1).add_to(dsqdLayer)
        folium.LayerControl().add_to(m)

##        plugins.ScrollZoomToggler().add_to(m)
        return m

    def main_loop(self):
        self.root.mainloop()
