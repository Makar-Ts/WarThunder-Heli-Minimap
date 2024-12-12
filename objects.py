# pylint: disable=line-too-long, invalid-name, import-error, multiple-imports, unspecified-encoding, broad-exception-caught, trailing-whitespace, no-name-in-module, unused-import

import math
import time
from PIL import Image, ImageFont, ImageDraw, ImageTk
from geom import segment_square_intersection, rotate_points

import logging
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------- #
#                                    Object                                    #
# ---------------------------------------------------------------------------- #


class Object:
    
    
    # ----------------------------------- Init ----------------------------------- #
    
    def __init__(self, canvas, width=10, height=10, x=0, y=0, color="white"):
        self.canvas = canvas
        
        self.width = width
        self.height = height
        
        self.color = color
        
        self.x = x
        self.y = y
        
        self.id = self.canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.height,
            fill=color
        )
    
    
    # ----------------------------------- Move ----------------------------------- #
    
    def move(self, x, y):
        self.canvas.move(self.id, x - self.x, y - self.y)
        self.x = x
        self.y = y
    
    def coords(self, x, y):
        self.x = x
        self.y = y
        self.canvas.coords(self.id, self.x, self.y, self.x + self.width, self.y + self.height,)



# ---------------------------------------------------------------------------- #
#                                Player's Marker                               #
# ---------------------------------------------------------------------------- #


class Player(Object):
    
    
    # ----------------------------------- Init ----------------------------------- #
    
    def __init__(self, canvas, width=10, height=10, x=0, y=0, rotation=0, color="white"):
        super().__init__(canvas, width, height, x, y, color)
        
        self.rotation = rotation
        
        points = self.calculate_points(x, y, self.width, self.height, rotation)
        self.id = self.canvas.create_polygon(
            points,
            fill=color
        )
        
    
    # ----------------------------------- Move ----------------------------------- #
        
    def move(self, x, y, rotation=0):
        self.canvas.delete(self.id)

        self.rotation = rotation-math.pi/2*3

        self.x = x
        self.y = y

        points = self.calculate_points(x, y, self.width, self.height, self.rotation)

        self.canvas.delete(self.id)
        self.id = self.canvas.create_polygon(points, fill=self.color)
    
    
    # ------------------------------- Calc. Points ------------------------------- #

    def calculate_points(self, x, y, width, height, rotation):
        points = [
            (-width, -height),
            (width, -height),
            (0, height)
        ]

        angle = rotation

        rotated_points = []
        for px, py in points:
            new_x = px * math.cos(angle) - py * math.sin(angle)
            new_y = px * math.sin(angle) + py * math.cos(angle)

            rotated_points.append((new_x + x, new_y + y))

        return [coord for point in rotated_points for coord in point]




# ---------------------------------------------------------------------------- #
#                                 Object Drawer                                #
# ---------------------------------------------------------------------------- #


class ObjectDrawer:
    
    
    # ----------------------------------- Init ----------------------------------- #
    
    def __init__(self, canvas, size, object_size__other, object_size__ground):
        logger.info("ObjectDrawer init started")
        
        self.canvas = canvas
        self.size = size
        
        self.cx = 0.5*self.size[0]
        self.cy = 0.5*self.size[1]
        
        self.os_other = object_size__other
        self.gs_other = object_size__ground
        
        self.images__text = {} # caching distance text
        
        self.zoom = 1
        
        self.ppos = (0, 0)
        
        self.font_mult = 1
        self.font_path = None
        self.font = None
        
        logger.info("ObjectDrawer init complete")
    
    
    # --------------------------------- Set Vars --------------------------------- #
    
    def set_zoom(self, zoom):
        self.zoom = zoom
        
        self.draw_ui__zoom_text()
    
    def set_player_pos(self, pos):
        self.ppos = (
            pos[0]*self.size[0],
            pos[1]*self.size[1]
        )
    
    def set_size(self, size):
        self.size = size
    
    def load_font(self, path, font_size_multiplier):
        logger.info("Loading font")
        
        self.font_mult = font_size_multiplier
        self.font_path = path
        
        self.update_font()
        
        logger.info("Font loaded")
        
    def update_font(self):
        if not self.font_path:
            logger.exception("No font path. Cannot update font")
            return
        
        self.font = ImageFont.truetype(self.font_path, round(self.os_other[0]*self.font_mult))
        
        logger.info("Font update complete")
    
    
    
    
    # ---------------------------------------------------------------------------- #
    #                                     Draw                                     #
    # ---------------------------------------------------------------------------- #
    
    
    # ----------------------------------- Text ----------------------------------- #
    
    def draw_ui__zoom_text(self):
        self.canvas.delete("ui__zoom_text")
        
        self.canvas.create_image( 
            (5, 5), 
            image=self.generate_text(f"{round(self.zoom, 2)}x", "white"),
            tags="ui__zoom_text",
            anchor="nw"
        )
    
    
    # ---------------------------------- Simple ---------------------------------- #
    
    def draw_object__other(self, x, y, color):
        self.canvas.create_oval(
            self.cx + (self.ppos[0] - x*self.size[0] - self.os_other[0])*self.zoom, 
            self.cy + (self.ppos[1] - y*self.size[1] - self.os_other[1])*self.zoom,
            self.cx + (self.ppos[0] - x*self.size[0] + self.os_other[0])*self.zoom, 
            self.cy + (self.ppos[1] - y*self.size[1] + self.os_other[1])*self.zoom,
            fill=color,
            outline=color,
            tags="object"
        )
    
    def draw_object__ground(self, x, y, color):
        self.canvas.create_rectangle(
            self.cx + (self.ppos[0] - x*self.size[0] - self.gs_other[0])*self.zoom, 
            self.cy + (self.ppos[1] - y*self.size[1] - self.gs_other[1])*self.zoom,
            self.cx + (self.ppos[0] - x*self.size[0] + self.gs_other[0])*self.zoom, 
            self.cy + (self.ppos[1] - y*self.size[1] + self.gs_other[1])*self.zoom,
            fill=color,
            outline="black",
            tags="object"
        )
    
    
    # ----------------------------------- Utils ---------------------------------- #
    
    def generate_text(self, text, color):
        identifier = f"{text}_{color}"
        if identifier not in self.images__text:
            img = (Image.new(
                "RGBA", 
                (
                    round(self.os_other[0]*len(text)*self.font_mult//2), 
                    round(self.os_other[0]*self.font_mult)
                ), 
                (255, 255, 255, 0))
            )
            draw = ImageDraw.Draw(img)
            draw.fontmode = "1"
            draw.text(
                (0, 0), 
                text, 
                font=self.font, 
                fill=color
            )
            
            
            self.images__text[identifier] = ImageTk.PhotoImage(img)
        
        return self.images__text[identifier]
    
    def clear_cache__text_images(self):
        t = time.localtime()
        logger.info(f"Image Cache cleared (cleared {len(self.images__text)} imgs)")
        self.images__text = {}
        
        self.draw_ui__zoom_text()
    
    def draw_object__by_points(self, x, y, points, color, outline=None):
        res = []
        
        if not outline:
            outline = color
        
        is_outside = True
        
        for i, p in enumerate(points):
            xy = i%2
            
            c = self.cx if xy == 0 else self.cy
            r = x if xy == 0 else y
            
            pos = c + (self.ppos[xy] - r*self.size[xy] + p)*self.zoom
            
            if xy == 1:
                is_outside = is_outside and (
                    0 > pos or pos > self.size[1]
                        or
                    0 > res[-1] or res[-1] > self.size[0]
                    )
            
            res.append(pos)
        
        if is_outside:
            return False
        
        self.canvas.create_polygon(
            res,
            fill=color,
            outline=outline,
            tags="object"
        )
        
        return True
    
    
    # ------------------------------- Respawn Bases ------------------------------ #
    
    def draw_object__plane(self, x, y, dx, dy, color):
        points = [
            [- self.gs_other[0], - self.gs_other[1]*2],
            [self.gs_other[0], - self.gs_other[1]*2],
            [0, self.gs_other[1]*2]
        ]
        
        p = rotate_points(points, math.atan2(dx, dy))
        
        self.draw_object__by_points(x, y, p, color, "black")
    
    
    def draw_object__respawn_base_tank(self, x, y, color):
        points = [
            - self.os_other[0],
            - self.os_other[1],
            + self.os_other[0],
            - self.os_other[1],
            + self.os_other[0]*0.5,
            0,
            + self.os_other[0],
            + self.os_other[1],
            - self.os_other[0],
            + self.os_other[1],
            - self.os_other[0]*0.5,
            0
        ]
        
        self.draw_object__by_points(x, y, points, color)
    
    
    def draw_object__respawn_base_fighter(self, x, y, color):
        points = [
            - self.os_other[0],
            0,
            0,
            + self.os_other[1],
            + self.os_other[0],
            0,
            0,
            - self.os_other[1]
        ]
        
        self.draw_object__by_points(x, y, points, color)
    
    
    # --------------------------------- Airfield --------------------------------- #
    
    def draw_object__airfield(self, x, y, color, distance_from_player):
        points = [
            - self.os_other[0],
            - self.os_other[1],
            + self.os_other[0],
            - self.os_other[1],
            + self.os_other[0]*0.5,
            + self.os_other[1],
            - self.os_other[0]*0.5,
            + self.os_other[1],
        ]
        
        text_pos = [
            self.cx + (self.ppos[0] - x*self.size[0])*self.zoom,
            self.cy + (self.ppos[1] - y*self.size[1] - self.os_other[1])*self.zoom
        ]
        anchor='s' # n e s w
        
        if not self.draw_object__by_points(x, y, points, color):
            anchor = ""
            text_pos = segment_square_intersection(
                ((int(self.cx), int(self.cy)), (int(text_pos[0]), int(text_pos[1]))), 
                ((0, 0), (self.size[0], self.size[1]))
            )[0]
            
            if text_pos == []: 
                return
            
            if text_pos[1]//10 == self.size[1]//10:
                anchor += "s"
            elif text_pos[1]//10 == 0:
                anchor += "n"
            
            if text_pos[0]//10 == self.size[0]//10:
                anchor += "e"
            elif text_pos[0]//10 == 0:
                anchor += "w"
        else:
            color = "white"
        
        self.canvas.create_image( 
            text_pos, 
            image=self.generate_text(f"{distance_from_player}km", color),
            tags="text",
            anchor=anchor
        )


#idk how to do this
#NOT WORKING
class MapImage:
    def __init__(self, canvas, size, image_path):
        self.canvas = canvas
        self.size = size
        self.image_path = image_path
        
        self.map_size = [1, 1]
        
        self.cx = 0.5*self.size[0]
        self.cy = 0.5*self.size[1]
        
        self.x = 0
        self.y = 0
        
        self.image_file = None
        self.tk_image = None
        
        self.image_id = None
        
    def update_img(self, map_size, zoom):
        self.image_file = Image.open(self.image_path)
        print("Map loaded")
        #self.image_file.resize((int(map_size[0]*zoom), int(map_size[1]*zoom)))
        
        #self.map_size = map_size
        
        self.tk_image = ImageTk.PhotoImage(self.image_file)
        
        self.image_id = self.canvas.create_image(0, 0, image=self.tk_image)
        self.canvas.scale(
            self.image_id, 
            0, 
            0, 
            (map_size[0]/self.image_file.size[0])*zoom, 
            (map_size[1]/self.image_file.size[1])*zoom
        )
        print("Map updated")
    
    def move(self, ppos):
        self.x = self.cx + ppos[0]*self.size[0]
        self.y = self.cy + ppos[1]*self.size[1]
        
        self.canvas.coords(self.image_id, self.x, self.y)