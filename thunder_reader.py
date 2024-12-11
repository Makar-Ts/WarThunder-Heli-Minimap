# pylint: unsubscriptable-object, disable=line-too-long, invalid-name, import-error, multiple-imports, unspecified-encoding, broad-exception-caught, trailing-whitespace, no-name-in-module, unused-import

import os
import sys
from urllib.request import urlopen
import json
import time
import math

import logging
logger = logging.getLogger(__name__)



# ---------------------------------------------------------------------------- #
#                                   Constants                                  #
# ---------------------------------------------------------------------------- #


THUNDER_OBJECTS_PATH = "http://127.0.0.1:8111/map_obj.json"
THUNDER_MAP_INFO_PATH = "http://127.0.0.1:8111/map_info.json"
THUNDER_MAP_IMG = "http://localhost:8111/map.img"

OUR_COLOR = '#174DFF'



# ---------------------------------------------------------------------------- #
#                                   MapReader                                  #
# ---------------------------------------------------------------------------- #


# ----------------------------------- Utils ---------------------------------- #

def get_type(obj):
    return obj["icon"] if obj["icon"] != 'none' else obj['type']


# ----------------------------------- Class ---------------------------------- #

class MapReader:
    
    
    # ----------------------------------- Init ----------------------------------- #
    
    def __init__(self):
        self._map_data = None
        
        self.objects = {
            "ground": [],
            "other": [],
            "player": None
        }
        
        self.isReady = False
        self.last_error = None
        
        self.update_objects_data()

    def map_init(self):
        data = json.loads(urlopen(THUNDER_MAP_INFO_PATH).read())
        
        self._map_data = data
        
        img = urlopen(THUNDER_MAP_IMG).read()
        with open(os.path.join(sys.path[0], "local", "map.png"), 'wb') as f:
            f.write(img)
        
        self._map_size = [
            self._map_data["map_max"][0] - self._map_data["map_min"][0],
            self._map_data["map_max"][1] - self._map_data["map_min"][1]
        ]
        
        logger.info("Map initialization complete")

    
    # ---------------------------------- Update ---------------------------------- #
    
    def update_objects_data(self):
        try:
            if not self.isReady:
                self.map_init()

            self._objects_data = json.loads(urlopen(THUNDER_OBJECTS_PATH).read())
            
            self.objects = {
                "ground": [],
                "other": [],
                "player": None
            }
            
            for i in self._objects_data:
                if i['icon'] == "Player":
                    self.objects["player"] = (
                        i['x']*self._map_size[0], 
                        i['y']*self._map_size[1], 
                        i['dx'], 
                        i['dy'])
                    continue
                
                if i['type'] == "ground_model":
                    self.objects["ground"].append({
                        "type": get_type(i), 
                        "position":(
                            i['x']*self._map_size[0], 
                            i['y']*self._map_size[1]
                        ),
                        "color": i['color']})
                else:
                    data = {}
                    
                    if 'x' in i:
                        data = {
                            "type": get_type(i), 
                            "position":(
                                i['x']*self._map_size[0], 
                                i['y']*self._map_size[1]
                            ),
                            "color": i['color']}
                    else:
                        data = {
                            "type": get_type(i), 
                            "position":(
                                i['sx']*self._map_size[0], 
                                i['sy']*self._map_size[1]
                            ),
                            "color": i['color']}
                    
                    if 'dx' in i:
                        data["dir"] = (
                            i["dx"],
                            i["dy"]
                        )
                    
                    self.objects["other"].append(data)
            
            if not self.objects["player"]:
                self.last_error = "Player not found"
                self.isReady = False
                
                return None
            
            self.isReady = True
            return True
        except Exception as e:
            self.last_error = e
            self.isReady = False
            
            return None
    
    
    # ------------------------------- Get Variables ------------------------------ #
    
    def get_map_size(self):
        return self._map_size
    
    def player__get_distance(self, x, y):
        if not self.objects["player"]:
            return 0
        
        ppos = self.objects["player"]
        
        length = ((x-ppos[0])**2+(y-ppos[1])**2)**0.5
        
        return length
    
    def player__get_heading(self, x, y):
        if not self.objects["player"]:
            return 0
        
        ppos = self.objects["player"]
        
        length = self.player__get_distance(x, y)
        player_dir = (ppos[2]**2 + ppos[3]**2)**0.5
        if length*player_dir == 0: 
            heading = 0
        else:                      
            heading = ((x-ppos[0])*ppos[2]+(y-ppos[1])*ppos[3])/(length*player_dir)
        
        return heading
    
    def player__heading(self):
        return math.atan2(self.objects["player"][3], self.objects["player"][2])
    
    def get_mid_spawns(self):
        if not self.objects["other"]:
            return []
        
        spawns = {}
        
        for sp in self.objects["other"]:
            if not sp["type"] == "respawn_base_tank":
                continue
            
            name = f"{math.floor(sp["position"][0]/250)}x{math.floor(sp["position"][1]/200)}_{sp["color"]}"
            
            if name in spawns:
                spawns[name]["pos_sum"][0] += sp["position"][0]
                spawns[name]["pos_sum"][1] += sp["position"][1]
                spawns[name]["count"] += 1
            else:
                spawns[name] = {
                    "pos_sum": [sp["position"][0], sp["position"][1]],
                    "count": 1
                }
            
        mid_spawns = []
        for name, spawn in spawns.items():
            name, color = name.split("_")
            
            mid_spawns.append({
                "name": name,
                "color": color,
                "position": (
                    spawn["pos_sum"][0]/spawn["count"],
                    spawn["pos_sum"][1]/spawn["count"]
                )
            })
            
        return mid_spawns
    
    
    # ----------------------- Convert To Absolute Position ----------------------- #
    
    def pabs(self, pos):
        return (
            pos[0]/self._map_size[0], 
            pos[1]/self._map_size[1],
            pos[2],
            pos[3]
        )
    
    def abs(self, pos):
        return (
            pos[0]/self._map_size[0],
            pos[1]/self._map_size[1]
        )
