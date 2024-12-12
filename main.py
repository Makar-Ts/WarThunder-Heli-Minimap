# pylint: undefined-loop-variable, disable=line-too-long, invalid-name, import-error, multiple-imports, unspecified-encoding, broad-exception-caught, trailing-whitespace, no-name-in-module, unused-import

import sys, os
import local.config as clconfig
import time
from tkinter import *
from tkinter import ttk

import thunder_reader
from objects import Player, ObjectDrawer


# ---------------------------------- Logger ---------------------------------- #

import log
import logging
logging.basicConfig(
    level=logging.INFO, 
    filename=os.path.join(
        sys.path[0], 
        "local", 
        "log", 
        f"{time.time()}_log.log"
    ), 
    filemode="w",
    format="%(asctime)s | [%(name)s] %(levelname)s | %(message)s")

logger = log.configure_logger()



# ---------------------------------------------------------------------------- #
#                                    Config                                    #
# ---------------------------------------------------------------------------- #


root=Tk()

config = clconfig.Config((root.winfo_screenwidth(), root.winfo_screenheight()))


# --------------------------------- Constants -------------------------------- #

TRANSPARENT_COLOR = "#"+config.bg_color
ZOOM = config.zoom
UPPER_PADDING = 30



# ---------------------------------------------------------------------------- #
#                                    Window                                    #
# ---------------------------------------------------------------------------- #


logger.info("Setting up the window")

root.title("Map ThunderParcer")

geometry = f"{config.size["x"]}x{config.size["y"]+UPPER_PADDING}+{config.position["x"]}+{config.position["y"]-UPPER_PADDING}"

root.geometry(geometry)
logger.info(f"Geometry {geometry}")

root.overrideredirect(True)
if config.transparent:
    root.attributes("-transparentcolor",TRANSPARENT_COLOR)
root.config(bg=TRANSPARENT_COLOR)



# ---------------------------------------------------------------------------- #
#                                      UI                                      #
# ---------------------------------------------------------------------------- #


# ------------------------------- Close Button ------------------------------- #

logger.info("Setting up \"close\" button")

b=Button(root,text="close",command=lambda:exit(0))
b.place(x=config.size["x"]-40, rely=0, height=UPPER_PADDING, width=40)


# ------------------------------- Map Canvas ------------------------------- #

logger.info("Setting up canvas")

is_canvas_shown=True
canvas_style = ttk.Style()
canvas_style.configure("My.TCanvas",       
                    font="consolas 14",  
                    foreground="#004D40",
                    padding=0,          
                    background=TRANSPARENT_COLOR)


canvas = Canvas(
    root, 
    width=int(config.size["x"])-10, 
    height=int(config.size["y"])-10, 
    border=0,
    borderwidth=1,
    bg=TRANSPARENT_COLOR
)
canvas.place(relx=0, y=UPPER_PADDING)

#map_img = MapImage(
#    canvas, 
#    (
#        int(config["size"]["x"]),
#        int(config["size"]["y"])
#    ),
#    os.path.join(sys.path[0], "local", "map.png")
#)


# ------------------------------- Objects Setup ------------------------------ #

logger.info("Setting up Draw Objects")

player = Player(canvas, 5, 10, 0, 0, 0)
drawer = ObjectDrawer(
    canvas,
    (
        config.size["x"],
        config.size["y"]
    ),
    (
        config.object_size["other"]["x"],
        config.object_size["other"]["y"]
    ),
    (
        config.object_size["ground"]["x"],
        config.object_size["ground"]["y"]
    )
)
drawer.load_font(os.path.join(sys.path[0], "local", "font.ttf"), config.text_size)
drawer.set_zoom(ZOOM)

def change_zoom(zoom):
    ZOOM = zoom
    
    drawer.set_zoom(zoom)


# -------------------------------- Zoom Slider ------------------------------- #

logger.info("Setting up zoom slider")

def zoom_slider(event):  
    change_zoom(slider.get())

slider_style = ttk.Style()
slider_style.configure("background", TRANSPARENT_COLOR)

slider = ttk.Scale(
    root,
    from_=1,
    to=20,
    orient='horizontal',
    command=zoom_slider,
    #style=slider_style
)
slider.set(ZOOM)
slider.place(
    relx=0, 
    rely=0, 
    width=config.size["x"]-80,
    height=UPPER_PADDING
)


# ----------------------------- Show/Hide button ----------------------------- #

logger.info("Setting up \"show/hide\" button")

def toggle_canvas():
    global is_canvas_shown
    if canvas.winfo_ismapped():
        canvas.place_forget()
        is_canvas_shown=False
        
        slider['state'] = 'disabled'
        
        b2.config(text="show")
        
        logger.info("Canvas hidden. Updating stopped")
    else:
        canvas.place(relx=0, y=UPPER_PADDING)
        is_canvas_shown=True
        
        slider['state'] = 'normal'
        
        b2.config(text="hide")
        
        logger.info("Canvas shown. Updating resumption")

b2=Button(root,text="hide",command=toggle_canvas)
b2.place(x=config.size["x"]-80, rely=0, height=UPPER_PADDING, width=40)



# ---------------------------------------------------------------------------- #
#                                     Main                                     #
# ---------------------------------------------------------------------------- #

is_error_shown=False
def main(reader):
    global is_error_shown
    
    # -------------------------------- Clear Cache ------------------------------- #
    
    if len(drawer.images__text) > config.cache["max_images"]: 
        drawer.clear_cache__text_images() # clearing the cache
    
    # -------------------------------- Update Data ------------------------------- #
    
    beenReady = reader.isReady
    
    if not is_canvas_shown:
        canvas.delete("object")
        canvas.delete("text")
        
        return canvas.after(config.update_time["usual"], main, reader)
    
    if not reader.update_objects_data():
        if not is_error_shown: 
            logger.exception(reader.last_error)
        
        canvas.delete("object")
        canvas.delete("text")
        
        is_error_shown=True
        return canvas.after(config.update_time["not_working"], main, reader)
    
    
    # ----------------------------- Delete Last Frame ---------------------------- #
    
    canvas.delete("object")
    canvas.delete("text")
    
    
    # ----------------------------- New Frame Prepare ---------------------------- #
    
    #if not beenReady and reader.isReady:
    #    map_img.update_img(reader.get_map_size(), ZOOM)
    
    is_error_shown=False
    
    ppos = reader.pabs(reader.objects["player"])
    
    drawer.set_player_pos(ppos)
    
    cx = 0.5*config.size["x"]
    cy = 0.5*config.size["y"]
    
    
    # ----------------------------- New Frame Render ----------------------------- #

    for i in reader.get_mid_spawns(config.cache["use_cached_spawns_positions"]):
        try:
            pos = reader.abs(i["position"])
            
            drawer.draw_object__respawn_base_tank(pos[0], pos[1], i["color"])
        except Exception as e:
            logger.exception(f"Error drawing object {i['name'] if 'name' in i else None if i else None}: {e}")
    
    for i in reader.objects["other"]:
        pos = reader.abs(i["position"])
        
        try:
            if i["type"] == "respawn_base_tank":
                #drawer.draw_object__respawn_base_tank(pos[0], pos[1], i["color"]) replaced with get_mid_spawns
                continue
            
            if i["type"] == "respawn_base_fighter":
                drawer.draw_object__respawn_base_fighter(pos[0], pos[1], i["color"])
                continue
            
            if i["type"] == "airfield":
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
        except Exception as e:
            logger.exception(f"Error drawing object {i['type'] if 'type' in i else None if i else None}: {e}")
    
    for i in reader.objects["ground"]:
        try:
            pos = reader.abs(i["position"])
            
            drawer.draw_object__ground(pos[0], pos[1], i["color"])
        except Exception as e:
            logger.exception(f"Error drawing ground object {i['type'] if 'type' in i else None if i else None}: {e}")
    
    
    # -------------------------------- Finalizing -------------------------------- #
    
    canvas.tag_raise("text")
    canvas.tag_raise("ui__zoom_text")
    player.move(cx, cy, reader.player__heading())
    
    
    canvas.after(config.update_time["usual"], main, reader)



# ---------------------------------------------------------------------------- #
#                                  Loop Start                                  #
# ---------------------------------------------------------------------------- #

logger.info("Starting the main loop")

reader = thunder_reader.MapReader()

root.wm_attributes("-topmost", 1)
canvas.after(0, main, reader)
root.mainloop()
