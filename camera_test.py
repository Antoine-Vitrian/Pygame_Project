import pygame
import sys

from character import Player_rect
from guns import *
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

gun = Gun(500, 450, 50, 'Img/Armas/arma_RW4.png', 12, 80, 8, True)
pistol = Gun(500, 700, 20, 'Img/Armas/pistol.png', 7, 60, 10, False)

laser_gun = Laser_gun(300, 300, 200, 'Img/Armas/laser_gun.png', 1)

bazooka = Bazooka(100, 100, 10, 'Img/Armas/bazuca_FW1000.png', 100)

loaded_guns = [gun, pistol, laser_gun, bazooka]


def update_screen(player, guns, camera):
    camera.x = max(0, min(player.rect.x - SCREEN_WIDTH // 2, (len(map.tiles[0]) * TILES_SIZE) - SCREEN_WIDTH))
    camera.y = max(0, min(player.rect.y - SCREEN_HEIGHT // 2, (len(map.tiles) * TILES_SIZE) - SCREEN_HEIGHT))

    player.update(screen)

    for gun in guns:
        gun.update(player, screen)
        if gun.equiped == True:
            gun.draw_ammo(screen)

def game():

    run = True
    while run:
        clock.tick(FPS)

        map.draw(screen)

        update_screen(player, loaded_guns, camera)

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
                player.dequip()

        # if laser_gun.laser.get('rect') and laser_gun.laser.get('rect').colliderect(gun.rect):
        #     print('teste')

        # if laser_gun.laser.get('rect') and laser_gun.laser.get('rect').colliderect(obj):
        #     print('foi\n', obj)
        
        pygame.display.flip()

if __name__ == "__main__":
    game()

pygame.quit()
sys.exit()