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
tmx_data = pytmx.util_pygame.load_pygame('./map\mapa-boss\mapboss.tmx')

def draw_map(surface):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    tile = pygame.transform.scale(
                        tile,
                        (tmx_data.tilewidth * TILE_SCALE, tmx_data.tileheight * TILE_SCALE)
                    )
                    surface.blit(tile, (x * tmx_data.tilewidth * TILE_SCALE - camera.x, y * tmx_data.tileheight * TILE_SCALE - camera.y))


