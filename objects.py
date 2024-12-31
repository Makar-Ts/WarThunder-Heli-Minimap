# pylint: disable=line-too-long, invalid-name, import-error, multiple-imports, unspecified-encoding, broad-exception-caught, trailing-whitespace, no-name-in-module, unused-import

import math
import sys
import time
from PIL import Image, ImageFont, ImageDraw, ImageTk, ImageOps
from geom import segment_square_intersection, rotate_points

import gc

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
    
    def __init__(self, canvas, size, object_size__other, object_size__ground, is_zoom_affect_sprites=True):
        logger.info("ObjectDrawer init started")
        
        self.canvas = canvas
        self.size = size
        
        self.cx = 0.5*self.size[0]
        self.cy = 0.5*self.size[1]
        
        self.os_other = object_size__other
        self.gs_other = object_size__ground
        
        self.images__text = {} # caching distance text
        
        self.zoom = 1
        self.zoom_affect_sprites = is_zoom_affect_sprites
        
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
    
    def draw_ui__length_text(self, mwidth, mheight):
        self.canvas.delete("ui__length_text")
        
        length = round((self.dy(0) - self.dy(self.size[1]))*mheight/1000, 1)
        
        self.canvas.create_image(
            (5, self.size[0] - self.os_other[0]*self.font_mult - 10),
            image=self.generate_text(f"{length}km", "white", 270),
            tags="ui__length_text",
            anchor="sw"
        )
        
        length2 = round((self.dx(0) - self.dx(self.size[0]))*mwidth/1000, 1)
        
        self.canvas.create_image(
            (self.os_other[0]*self.font_mult, self.size[0] - 10),
            image=self.generate_text(f"{length2}km", "white"),
            tags="ui__length_text",
            anchor="sw"
        )
    
    
    # ---------------------------------- Convert --------------------------------- #
    
    def rx(self, x, offset=0):
        if self.zoom_affect_sprites:
            return self.cx + (self.ppos[0] - x*self.size[0] + offset)*self.zoom
        
        return self.cx + (self.ppos[0] - x*self.size[0])*self.zoom + offset
    
    def ry(self, y, offset=0):
        if self.zoom_affect_sprites:
            return self.cy + (self.ppos[1] - y*self.size[1] + offset)*self.zoom
        
        return self.cy + (self.ppos[1] - y*self.size[1])*self.zoom + offset
    
    def dx(self, x, offset=0):
        if self.zoom_affect_sprites:
            return ((x - self.cx) / self.zoom - self.ppos[0] - offset) / (-self.size[0])
    
        return ((x - self.cx - offset) / self.zoom - self.ppos[0]) / (-self.size[0])
    
    def dy(self, y, offset=0):
        if self.zoom_affect_sprites:
            return ((y - self.cy) / self.zoom - self.ppos[1] - offset) / (-self.size[1])
    
        return ((y - self.cy - offset) / self.zoom - self.ppos[1]) / (-self.size[1])
    
    # ---------------------------------- Simple ---------------------------------- #
    
    def draw_object__other(self, x, y, color):
        self.canvas.create_oval(
            self.rx(x, -self.os_other[0]), 
            self.ry(y, -self.os_other[1]),
            self.rx(x, self.os_other[0]), 
            self.ry(y, self.os_other[1]),
            fill=color,
            outline=color,
            tags="object"
        )

    def draw_object__ground(self, x, y, color):
        self.canvas.create_rectangle(
            self.rx(x, -self.gs_other[0]), 
            self.ry(y, -self.gs_other[1]),
            self.rx(x, self.gs_other[0]), 
            self.ry(y, self.gs_other[1]),
            fill=color,
            outline="black",
            tags="object"
        )
    
    
    # ----------------------------------- Utils ---------------------------------- #
    
    def generate_text(self, text, color, rotate=None):
        identifier = f"{text}_{color}"
        
        if rotate:
            identifier += f"_r{rotate}"
        
        if identifier not in self.images__text:
            size = [
                round(self.os_other[0]*len(text)*self.font_mult//2), 
                round(self.os_other[0]*self.font_mult)
            ]
            
            img = (Image.new(
                "RGBA", 
                tuple(size),
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
            
            if rotate:
                img = img.rotate(rotate, expand=True)
            
            self.images__text[identifier] = ImageTk.PhotoImage(img)
        
        return self.images__text[identifier]
    
    def clear_cache__text_images(self):
        t = time.time()
        logger.info(f"Image Cache clear started")
        
        ln = len(self.images__text)
        bt = sys.getsizeof(self.images__text)
        k = list(self.images__text.keys())
        
        for key in k:
            del self.images__text[key]
        
        self.images__text = {}
        del k
        
        gc.collect()
        self.draw_ui__zoom_text()
        
        logger.info(f"Cleared {ln} imgs ({round(bt/1024, 3)}Kb). Time: {round((time.time() - t) * 1000, 4)} miliseconds")
    
    def draw_object__by_points(self, x, y, points, color, outline=None, tags=["object"]):
        res = []
        
        if not outline:
            outline = color
        
        is_outside = True
        
        for i, p in enumerate(points):
            xy = i % 2
            
            pos = self.rx(x, p) if xy == 0 else self.ry(y, p)
            
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
            tags=tags
        )
        
        return True
    
    def draw_object__multiple_points(self, x, y, objects, color, outline=None, tags=["object"]):
        if not outline:
            outline = color
        
        is_visible = False
        
        for obj in objects:
            v = self.draw_object__by_points(
                x, 
                y,
                obj, 
                color, 
                outline, 
                tags
            )
            
            is_visible = is_visible or v

        return is_visible
    
    def draw_object__line(self, x1, y1, x2, y2, color, width=None, tags=["object"], offset=[0, 0, 0, 0]):
        if not width:
            width = self.os_other[0]
        
        self.canvas.create_line(
            self.rx(x1, offset[0]), 
            self.ry(y1, offset[1]),
            self.rx(x2, offset[2]),
            self.ry(y2, offset[3]),
            width=width, 
            fill=color,
            tags=tags
        )
    
        
    # ------------------------------- Respawn Bases ------------------------------ #
    
    def draw_object__plane(self, x, y, dx, dy, color):
        points = [
            [- self.gs_other[0], - self.gs_other[1]*2],
            [self.gs_other[0], - self.gs_other[1]*2],
            [0, self.gs_other[1]*2]
        ]
        
        p = rotate_points(points, math.atan2(dx, dy)-math.pi/2*3)
        
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
            self.rx(x),
            self.ry(y, -self.os_other[1])
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


class SpotsManager:
    def __init__(self, drawer: ObjectDrawer):
        self.drawer = drawer
        self.spots = []
        
        self.drawer.canvas.bind("<Button-1>", self.on_click_1)
        self.drawer.canvas.bind("<Button-3>", self.on_click_0)
    
    def add_spot(self, rx, ry):
        self.spots.append((self.drawer.dx(rx), self.drawer.dy(ry)))
    
    def remove_spot(self, rx, ry):
        nearest = [None, 0]
        
        dx = self.drawer.dx(rx)
        dy = self.drawer.dy(ry)
        for i, (x, y) in enumerate(self.spots):
            dist = math.sqrt((dx - x)**2 + (dy - y)**2)
            
            if nearest[0] is None or dist < nearest[1]:
                nearest = [i, dist]
        
        if nearest[0] is not None:
            self.spots.pop(nearest[0])
    
    def on_click_1(self, event):
        self.add_spot(event.x, event.y)
    
    def on_click_0(self, event):
        self.remove_spot(event.x, event.y)
    
    def draw_spots(self, map_size):
        points = [
            [
                + self.drawer.os_other[0],
                + self.drawer.os_other[1]*2,
                - self.drawer.os_other[0],
                + self.drawer.os_other[1]*2,
                - self.drawer.os_other[0],
                + self.drawer.os_other[1]*1.5,
                + self.drawer.os_other[0],
                + self.drawer.os_other[1]*1.5,
            ],
            [
                + self.drawer.os_other[0],
                - self.drawer.os_other[1]*2,
                - self.drawer.os_other[0],
                - self.drawer.os_other[1]*2,
                - self.drawer.os_other[0],
                - self.drawer.os_other[1]*1.5,
                + self.drawer.os_other[0],
                - self.drawer.os_other[1]*1.5,
            ],
            [
                + self.drawer.os_other[0]*2,
                - self.drawer.os_other[1],
                + self.drawer.os_other[0]*2,
                + self.drawer.os_other[1],
                + self.drawer.os_other[0]*1.5,
                + self.drawer.os_other[1],
                + self.drawer.os_other[0]*1.5,
                - self.drawer.os_other[1],
            ],
            [
                - self.drawer.os_other[0]*2,
                - self.drawer.os_other[1],
                - self.drawer.os_other[0]*2,
                + self.drawer.os_other[1],
                - self.drawer.os_other[0]*1.5,
                + self.drawer.os_other[1],
                - self.drawer.os_other[0]*1.5,
                - self.drawer.os_other[1],
            ]
        ]
        
        pad = max(self.drawer.os_other)*4
        
        self.drawer.canvas.delete("spot")
        
        for i, pos in enumerate(self.spots):
            self.drawer.draw_object__multiple_points(
                pos[0],
                pos[1],
                points,
                "lime",
                tags=["spot"]
            )
            
            
            next_index = (i+1)%len(self.spots)
            
            if len(self.spots) == 1:
                nxt_pos_x = self.drawer.ppos[0]/self.drawer.size[0]
                nxt_pos_y = self.drawer.ppos[1]/self.drawer.size[1]
            else:
                nxt_pos_x = self.spots[next_index][0]
                nxt_pos_y = self.spots[next_index][1]
            
            angle = math.atan2(
                pos[0]-nxt_pos_x,
                pos[1]-nxt_pos_y
            )
            
            
            length = round(
                math.sqrt(
                    ((pos[0]-nxt_pos_x)*map_size[0])**2 + 
                    ((pos[1]-nxt_pos_y)*map_size[1])**2
                )/1000
            , 1)
            
            mid_x = (pos[0] + nxt_pos_x) / 2
            mid_y = (pos[1] + nxt_pos_y) / 2
            
            mid_rx = self.drawer.rx(mid_x)
            mid_ry = self.drawer.ry(mid_y)
            
            text = f"{length}km"
            self.drawer.canvas.create_image(
                (mid_rx, mid_ry),
                image=self.drawer.generate_text(text, "white"),
                tags="spot"
            )
            
            pad2 = self.drawer.os_other[0]*len(text)*self.drawer.font_mult//4
            
            pad2_x = math.sin(angle)*pad2
            pad2_y = math.cos(angle)*pad2
            
            pad_x = math.sin(angle)*pad
            pad_y = math.cos(angle)*pad
            
            self.drawer.draw_object__line(
                pos[0],
                pos[1],
                mid_x,
                mid_y,
                "lime",
                tags=["spot"],
                offset=[pad_x, pad_y, -pad2_x, -pad2_y]
            )
            
            self.drawer.draw_object__line(
                mid_x,
                mid_y,
                nxt_pos_x,
                nxt_pos_y,
                "lime",
                tags=["spot"],
                offset=[pad2_x, pad2_y, -pad_x, -pad_y]
            )


# I still dont understand how to do this
class MapDrawer:
    def __init__(self, drawer, map_path):
        self.drawer = drawer
        
        self.map_path = map_path
        
        self.map_size = (2048, 2048)
        self.tile_size = (0, 0)
        
        self.tiles = []
        self.tiles_ids = []
    
    def load_map(self, map_size):
        with Image.open(self.map_path) as img:
            input_image = ImageOps.flip(ImageOps.mirror(img))

            self.map_size = (
                map_size[0] * self.drawer.zoom,
                map_size[1] * self.drawer.zoom
            )
            
            image_width, image_height = input_image.size
            
            tile_width = image_width // 32
            tile_height = image_height // 32
            
            resize = (
                self.map_size[0] // image_width,
                self.map_size[1] // image_height
            )
            
            self.tile_size = (
                tile_width*resize[0],
                tile_height*resize[1]
            )
            
            self.tiles = []
            for y in range(0, image_height, tile_height):
                tiles = []
                
                for x in range(0, image_width, tile_width):
                    left = x
                    upper = y
                    right = x + tile_width
                    lower = y + tile_height

                    tile = input_image\
                        .crop((left, upper, right, lower))\
                        .resize(
                            (
                                math.ceil(self.tile_size[0]), 
                                math.ceil(self.tile_size[1])
                            )
                        )
                    
                    tiles.append(ImageTk.PhotoImage(tile))
                
                self.tiles.append(tiles)
    
    def draw_map(self):
        self.drawer.canvas.delete("map")
        
        zero = (
            self.drawer.rx(-1),
            self.drawer.ry(-1)
        )

        for y, row in enumerate(self.tiles):
            ids = []
            
            for x, tile in enumerate(row):
                ids.append(
                    self.drawer.canvas.create_image(
                        (
                            zero[0] - x*self.tile_size[0], 
                            zero[1] - y*self.tile_size[1]
                        ),
                        image=tile,
                        tags="map",
                        anchor="se"
                    )
                )
            
            self.tiles_ids.append(ids)
        
        print(self.tiles_ids, zero)