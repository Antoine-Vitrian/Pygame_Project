import pygame
import pytmx
from pytmx import load_pygame
from pytmx import TiledImageLayer
import pytmx.util_pygame

# Configurações
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Inicializa Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mapa do Tiled no Pygame")
clock = pygame.time.Clock()

TILE_SCALE = 3
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
                    surface.blit(tile, (x * tmx_data.tilewidth * TILE_SCALE, y * tmx_data.tileheight * TILE_SCALE))

# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))  # Limpa a tela
    draw_map(screen)        # Desenha o mapa
    pygame.display.flip()   # Atualiza a tela
    clock.tick(60)

pygame.quit()
