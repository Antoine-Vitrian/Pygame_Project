import pygame
from camera import create_screen, camera
import pygame
import pytmx
import pytmx.util_pygame
from camera import create_screen, camera
from enemies import Boss1


# Inicializa Pygame
pygame.init()
TILE_SCALE = 4
# Carrega o mapa .tmx

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = create_screen(SCREEN_WIDTH, SCREEN_HEIGHT, 'game')

class Map:
    def __init__(self, caminho):
        self.tmx_data = pytmx.util_pygame.load_pygame(caminho)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth * TILE_SCALE
        self.height = self.tmx_data.height * self.tmx_data.tileheight * TILE_SCALE
        self.scaled_tiles = []
        self.abvplr_scaled_tiles = []
        self.entities = []
        self.collision_tiles = []
        

    def draw_map(self, surface):

        surface.fill('black')

        if not len(self.scaled_tiles) and not len(self.collision_tiles) and not len(self.abvplr_scaled_tiles):
            for layer in self.tmx_data.layers:
                # tiles que serão desenhadas
                if isinstance(layer, pytmx.TiledTileLayer) and layer.name not in ['colisoes', 'acima_player']:
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
                if layer.name == 'acima_player':
                    for x, y, gid in layer:
                        tile = self.tmx_data.get_tile_image_by_gid(gid)
                        if tile:
                            tile = pygame.transform.scale(
                                tile,
                                (self.tmx_data.tilewidth *  TILE_SCALE, self.tmx_data.tileheight * TILE_SCALE)
                            )
                            self.abvplr_scaled_tiles.append({
                                "tile": tile,
                                "x_pos": x * self.tmx_data.tilewidth * TILE_SCALE,
                                "y_pos": y * self.tmx_data.tileheight * TILE_SCALE
                            })

                    
        for tile in self.scaled_tiles:
            surface.blit(tile["tile"], (tile["x_pos"] - camera.x,tile["y_pos"] - camera.y))    

    def draw_above_player(self, surface):
        for tile in self.abvplr_scaled_tiles:
            surface.blit(tile["tile"], (tile["x_pos"] - camera.x, tile["y_pos"] - camera.y))


    def check_block_collisions(self, player, enemies, blts):
        entities = [player] + [enemy for enemy in enemies]
        
        for entity in entities:
            entity_area = entity.rect.inflate(20, 20)  # Área 20px maior em cada direção

            for block in self.collision_tiles:
                if not entity_area.colliderect(block):
                    continue  # Pula blocos longe demais
                
                #Colisões no eixo X
                if block.colliderect(entity.rect.x + entity.speed_x, entity.rect.y, entity.rect.width, entity.rect.height):
                    if entity.speed_x > 0 and entity.rect.centerx < block.centerx:
                        entity.rect.right = block.left - 2
                        entity.speed_x = 0
                    elif entity.speed_x < 0 and entity.rect.centerx > block.centerx:
                        entity.rect.left = block.right + 2
                        entity.speed_x = 0

                    if isinstance(entity, Boss1):
                        entity.collided = True
                
                # Colisões no eixo Y
                if block.colliderect(entity.rect.x, entity.rect.y + entity.speed_y, entity.rect.width, entity.rect.height):
                    if entity.speed_y > 0 and entity.rect.centery < block.centery:
                        entity.rect.bottom = block.top - 2
                        entity.speed_y = 0
                    elif entity.speed_y < 0 and entity.rect.centery > block.centery:
                        entity.rect.top = block.bottom + 2
                        entity.speed_y = 0

                    if isinstance(entity, Boss1):
                        entity.collided = True

            # Trazer de volta ao mapa caso alguém saia do mapa
            if entity.rect.x < 0:
                entity.rect.x += 170
            elif entity.rect.x > self.width:
                entity.rect.x -= 170

            if entity.rect.y < 0:
                entity.rect.y += 170
            elif entity.rect.y > self.height:
                entity.rect.y -= 170

        for blt in blts:
            for tile in self.collision_tiles:
                if blt.rect.colliderect(tile):
                    blt.time_to_live = 0

        