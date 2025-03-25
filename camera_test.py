import pygame
import sys
import random

from character import Player_rect
from guns import Gun, Laser_gun, EQUIP_EVENT, DEQUIP_EVENT
from camera import camera
from game_map import *

pygame.init()

#--------------Variáveis----------------
clock = pygame.time.Clock()
FPS = 60

plr_col = (255, 0, 0)

tile_kinds = [
    Tile_kind("sand", "Img/tiles/areia.png", False),
    Tile_kind("sand", "Img/tiles/areia_2.png", False),
    Tile_kind("sand", "Img/tiles/areia_3.png", False),
]

map = Map("map/mapa_1.csv", tile_kinds, TILES_SIZE)

player = Player_rect(300, 200, 20, plr_col)

gun = Gun(500, 450, 50, 'Img/Armas/arma_RW4.png', 1)

laser_gun = Laser_gun(300, 300, 200, 'Img/Armas/laser_gun.png', 1)

# Objeto criado para teste
obj_surface = pygame.surface.Surface((70, 70))
obj = pygame.rect.Rect(600 - camera.x, 600 - camera.y, obj_surface.get_width(), obj_surface.get_height())

def update_screen(player, gun, camera):
    camera.x = max(0, min(player.rect.x - SCREEN_WIDTH // 2, (len(map.tiles[0]) * TILES_SIZE) - SCREEN_WIDTH))
    camera.y = max(0, min(player.rect.y - SCREEN_HEIGHT // 2, (len(map.tiles) * TILES_SIZE) - SCREEN_HEIGHT))

    player.update(screen)

    gun.update(player, screen)
    laser_gun.update(player, screen)

    screen.blit(obj_surface, (obj.x - camera.x, obj.y -camera.y))
        

def game():

    run = True
    while run:
        clock.tick(FPS)

        map.draw(screen)

        update_screen(player, gun, camera)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_t:
            #         print(player.surface, player.rect)

            if event.type == EQUIP_EVENT:
                player.equip()
            elif event.type == DEQUIP_EVENT:   
                player.equip()

        # if laser_gun.laser.get('rect') and laser_gun.laser.get('rect').colliderect(gun.rect):
        #     print('teste')

        # if laser_gun.laser.get('rect') and laser_gun.laser.get('rect').colliderect(obj):
        #     print('foi\n', obj)
        
        pygame.display.flip()

if __name__ == "__main__":
    game()

pygame.quit()
sys.exit()