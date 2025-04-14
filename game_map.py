import pygame
from camera import create_screen, camera
import csv
import pygame
import pytmx
from pytmx import load_pygame
from pytmx import TiledImageLayer
import pytmx.util_pygame
from camera import create_screen, camera


# Inicializa Pygame
pygame.init()
TILE_SCALE = 4
# Carrega o mapa .tmx


TILES_SIZE = 32
0
SCREEN_WIDTH = TILES_SIZE * 30
SCREEN_HEIGHT = TILES_SIZE * 25

screen = create_screen(SCREEN_WIDTH, SCREEN_HEIGHT, 'game')

class Map:
    def __init__(self, caminho):
        self.tmx_data = pytmx.util_pygame.load_pygame(caminho)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth * TILE_SCALE
        self.height = self.tmx_data.height * self.tmx_data.tileheight * TILE_SCALE



    def draw_map(self, surface):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        tile = pygame.transform.scale(
                            tile,
                            (self.tmx_data.tilewidth * TILE_SCALE, self.tmx_data.tileheight * TILE_SCALE)
                        )
                        surface.blit(tile, (x * self.tmx_data.tilewidth * TILE_SCALE - camera.x, y * self.tmx_data.tileheight * TILE_SCALE - camera.y))
            
        