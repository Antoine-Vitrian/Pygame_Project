import pygame
import sys

from character import Player_rect
from guns import Gun, Laser_gun, EQUIP_EVENT, DEQUIP_EVENT
from camera import create_screen, camera

pygame.init()

#--------------Variáveis----------------
clock = pygame.time.Clock()
FPS = 60

TILES_SIZE = 50

SCREEN_WIDTH = TILES_SIZE * 20
SCREEN_HEIGHT = TILES_SIZE * 16

plr_col = (255, 0, 0)



tile_map = [
    [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2],
    [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2],
    [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [0, 0, 0, 3, 3, 0, 0, 0, 0, 1, 1, 1, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [1, 1, 1, 3, 3, 1, 1, 1, 0, 1, 1, 1, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [1, 1, 1, 3, 3, 1, 1, 1, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 2, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2],
    [1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [0, 0, 0, 3, 3, 1, 1, 1, 1, 0, 0, 0, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [1, 1, 1, 3, 3, 1, 1, 1, 0, 0, 0, 0, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [0, 0, 0, 3, 3, 0, 0, 0, 1, 1, 1, 0, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [1, 1, 1, 3, 3, 0, 0, 0, 1, 0, 0, 0, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 2, 2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 1]
]

#---------------------instances--------------------------------------
screen = create_screen(SCREEN_WIDTH, SCREEN_HEIGHT, 'Scrolling test')

player = Player_rect(300, 200, 20, plr_col)

gun = Gun(500, 450, 50, 'Img/Armas/arma_RW4.png', 1)

laser_gun = Laser_gun(300, 300, 200, 'Img/Armas/laser_gun.png', 1)

# Objeto criado para teste
obj_surface = pygame.surface.Surface((70, 70))
obj = pygame.rect.Rect(600 - camera.x, 600 - camera.y, obj_surface.get_width(), obj_surface.get_height())

def update_screen(player, gun, camera):
    camera.x = max(0, min(player.rect.x - SCREEN_WIDTH // 2, (len(tile_map[0]) * TILES_SIZE) - SCREEN_WIDTH))
    camera.y = max(0, min(player.rect.y - SCREEN_HEIGHT // 2, (len(tile_map) * TILES_SIZE) - SCREEN_HEIGHT))

    for row in range(len(tile_map)):
        for col, tile in enumerate(tile_map[row]):
            x = col * TILES_SIZE - camera.x
            y = row * TILES_SIZE - camera.y

            if -TILES_SIZE <= x < SCREEN_WIDTH and -TILES_SIZE <= y < SCREEN_HEIGHT:
                if tile == 1: 
                    pygame.draw.rect(screen, (139, 180, 59), (x, y, TILES_SIZE, TILES_SIZE))  # Cor marrom
                elif tile == 2: 
                    pygame.draw.rect(screen, (0, 0, 255), (x, y, TILES_SIZE, TILES_SIZE))  # Cor azul
                else:  
                    pygame.draw.rect(screen, (50, 120, 80), (x, y, TILES_SIZE, TILES_SIZE))

    player.update(screen)

    gun.update(player, screen)
    laser_gun.update(player, screen)

    screen.blit(obj_surface, (obj.x - camera.x, obj.y -camera.y))
        

def game():

    run = True
    while run:
        clock.tick(FPS)

        screen.fill((0, 0, 0))

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