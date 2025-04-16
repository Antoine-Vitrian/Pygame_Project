import pygame
from camera import create_screen, camera
import pygame
import pytmx
from pytmx import load_pygame
from pytmx import TiledImageLayer
import pytmx.util_pygame
from camera import create_screen, camera
from enemies import Boss1


# Inicializa Pygame
pygame.init()
TILE_SCALE = 4
# Carrega o mapa .tmx


TILES_SIZE = 32

SCREEN_WIDTH = TILES_SIZE * 30
SCREEN_HEIGHT = TILES_SIZE * 25

screen = create_screen(SCREEN_WIDTH, SCREEN_HEIGHT, 'game')

class Map:
    def __init__(self, caminho):
        self.tmx_data = pytmx.util_pygame.load_pygame(caminho)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth * TILE_SCALE
        self.height = self.tmx_data.height * self.tmx_data.tileheight * TILE_SCALE
        self.scaled_tiles = []
        self.entities = []
        self.collision_tiles = []
        

    def draw_map(self, surface):

        surface.fill('black')

        if not len(self.scaled_tiles) and not len(self.collision_tiles):
            for layer in self.tmx_data.layers:
                # tiles que serão desenhadas
                if isinstance(layer, pytmx.TiledTileLayer) and layer.name != 'colisoes':
                    for x, y, gid in layer:
                        tile = self.tmx_data.get_tile_image_by_gid(gid)
                        if tile:
                            tile = pygame.transform.scale(
                                tile,
                                (self.tmx_data.tilewidth * TILE_SCALE, self.tmx_data.tileheight * TILE_SCALE)
                            )
                            self.scaled_tiles.append({
                                    "tile": tile,
                                    "x_pos": x * self.tmx_data.tilewidth * TILE_SCALE,
                                    "y_pos": y * self.tmx_data.tileheight * TILE_SCALE
                                })
                # Tiles de colisão
                if layer.name == 'colisoes':
                    for x, y, gid in layer:
                        if gid != 0:
                            self.collision_tiles.append(
                                pygame.Rect(
                                    x * self.tmx_data.tilewidth * TILE_SCALE,
                                    y * self.tmx_data.tileheight * TILE_SCALE,
                                    self.tmx_data.tilewidth * TILE_SCALE,
                                    self.tmx_data.tileheight * TILE_SCALE
                                )
                            )
        for tile in self.scaled_tiles:
            surface.blit(tile["tile"], (tile["x_pos"] - camera.x,tile["y_pos"] - camera.y))    
            
    def check_block_collisions(self, player, enemies, blts):
        entities = [player] + [enemy for enemy in enemies]
        
        for entity in entities:
            entity_area = entity.rect.inflate(100, 100)  # Área 100px maior em cada direção

            for block in self.collision_tiles:
                if not entity_area.colliderect(block):
                    continue  # Pula blocos longe demais

                elif block.colliderect(entity) and block:
                    if entity.speed_x > 0 and block.centerx > entity.rect.centerx:
                        entity.speed_x = 0
                        entity.rect.right = block.left
                    elif entity.speed_x < 0 and block.centerx < entity.rect.centerx:
                        entity.speed_x = 0
                        entity.rect.left = block.right      
                    elif entity.speed_y > 0 and block.centery > entity.rect.centery:
                        entity.speed_y = 0
                        entity.rect.bottom = block.top
                    elif entity.speed_y < 0 and block.centery < entity.rect.centery:
                        entity.speed_y = 0
                        entity.rect.top = block.bottom
                    if isinstance(entity, Boss1):
                        entity.collided = True

        for blt in blts:
            for tile in self.collision_tiles:
                if blt.rect.colliderect(tile):
                    blt.time_to_live = 0

        