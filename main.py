# pylint: undefined-loop-variable, disable=line-too-long, invalid-name, import-error, multiple-imports, unspecified-encoding, broad-exception-caught, trailing-whitespace, no-name-in-module, unused-import

import sys, os
import configparser
from tkinter import *
from tkinter import ttk

import thunder_reader
from objects import Player, ObjectDrawer



# ---------------------------------------------------------------------------- #
#                                    Config                                    #
# ---------------------------------------------------------------------------- #


import local.files_check
local.files_check.main(0, "local")

config = configparser.ConfigParser()
config.read(os.path.join(sys.path[0], "local", "config.ini"))

print(f"{config["position"]["x"]} {config["position"]["y"]}  {config["size"]["x"]}x{config["size"]["y"]}")


# --------------------------------- Constants -------------------------------- #

TRANSPARENT_COLOR = "#"+config["settings"]["bg_color"]
ZOOM = int(config["settings"]["zoom"])



# ---------------------------------------------------------------------------- #
#                                    Window                                    #
# ---------------------------------------------------------------------------- #


root=Tk()
root.title("Map ThunderParcer")

root.geometry(f"{config["size"]["x"]}x{int(config["size"]["y"])+20}+{config["position"]["x"]}+{int(config["position"]["y"])-20}")

root.overrideredirect(True)
if int(config["settings"]["trasparent"]):
    root.attributes("-transparentcolor",TRANSPARENT_COLOR)
root.config(bg=TRANSPARENT_COLOR)



# ---------------------------------------------------------------------------- #
#                                      UI                                      #
# ---------------------------------------------------------------------------- #


# ------------------------------- Close Button ------------------------------- #

b=Button(root,text="close",command=lambda:exit(0))
b.place(x=int(config["size"]["x"])-40, rely=0)


# ------------------------------- Map Canvas ------------------------------- #

canvas_style = ttk.Style()
canvas_style.configure("My.TCanvas",       
                    font="consolas 14",  
                    foreground="#004D40",
                    padding=0,          
                    background=TRANSPARENT_COLOR)


canvas = Canvas(
    root, 
    width=int(config["size"]["x"])-10, 
    height=int(config["size"]["y"])-10, 
    border=0,
    borderwidth=1,
    bg=TRANSPARENT_COLOR
)
canvas.place(relx=0, y=20)

#map_img = MapImage(
#    canvas, 
#    (
#        int(config["size"]["x"]),
#        int(config["size"]["y"])
#    ),
#    os.path.join(sys.path[0], "local", "map.png")
#)


# ------------------------------- Objects Setup ------------------------------ #

player = Player(canvas, 5, 10, 0, 0, 0)
drawer = ObjectDrawer(
    canvas,
    (
        int(config["size"]["x"]),
        int(config["size"]["y"])
    ),
    (
        int(config["object_other_size"]["x"]),
        int(config["object_other_size"]["y"])
    ),
    (
        int(config["object_ground_size"]["x"]),
        int(config["object_ground_size"]["y"])
    )
)
drawer.set_zoom(ZOOM)
drawer.load_font(os.path.join(sys.path[0], "local", "font.ttf"), int(config["settings"]["text_size"]))



# ---------------------------------------------------------------------------- #
#                                     Main                                     #
# ---------------------------------------------------------------------------- #


def main(reader):
    
    
    # -------------------------------- Update Data ------------------------------- #
    
    beenReady = reader.isReady
    
    if not reader.update_objects_data():
        canvas.delete("object")
        return canvas.after(3000, main, reader)
    
    
    # ----------------------------- Delete Last Frame ---------------------------- #
    
    canvas.delete("object")
    canvas.delete("text")
    
    
    # ----------------------------- New Frame Prepare ---------------------------- #
    
    #if not beenReady and reader.isReady:
    #    map_img.update_img(reader.get_map_size(), ZOOM)
    
    
    ppos = reader.pabs(reader.objects["player"])
    
    drawer.set_player_pos(ppos)
    
    cx = 0.5*int(config["size"]["x"])
    cy = 0.5*int(config["size"]["y"])
    
    
    # ----------------------------- New Frame Render ----------------------------- #
    
    for i in reader.objects["other"]:
        pos = reader.abs(i["position"])
        
        if i["type"] == "respawn_base_tank":
            drawer.draw_object__respawn_base_tank(pos[0], pos[1], i["color"])
            continue
        elif i["type"] == "respawn_base_fighter":
            drawer.draw_object__respawn_base_fighter(pos[0], pos[1], i["color"])
            continue
        elif i["type"] == "airfield":
            drawer.draw_object__airfield(
                pos[0], pos[1], 
                i["color"], 
                round(
                    reader.player__get_distance(
                            i["position"][0], 
                            i["position"][1]
                        )/1000, 
                    1
                    )
            )
            continue

        if "dir" in i:
            drawer.draw_object__plane(pos[0], pos[1], i["dir"][0], i["dir"][1], i["color"])
        else:
            drawer.draw_object__other(pos[0], pos[1], i["color"])
    
    for i in reader.objects["ground"]:
        pos = reader.abs(i["position"])
        
        drawer.draw_object__ground(pos[0], pos[1], i["color"])
    
    
    # -------------------------------- Finalizing -------------------------------- #
    
    canvas.tag_raise("text")
    player.move(cx, cy, reader.player__heading())
    
    
    canvas.after(50, main, reader)



# ---------------------------------------------------------------------------- #
#                                  Loop Start                                  #
# ---------------------------------------------------------------------------- #

reader = thunder_reader.MapReader()

root.wm_attributes("-topmost", 1)
canvas.after(0, main, reader)
root.mainloop()
