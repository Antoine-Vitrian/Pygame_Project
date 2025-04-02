import pygame
import sys
import random

from character import Player_rect
from guns import *
from enemies import Enemy
from camera import camera
from game_map import *
from itens import AmmoPack
from sprites import *
from button import Button

pygame.init()

#--------------Variáveis----------------
clock = pygame.time.Clock()
FPS = 60

animation_cooldown = 60
last_update = pygame.time.get_ticks()

# Mapa
tile_kinds = [
    Tile_kind("sand", "Img/tiles/areia.png", False),
    Tile_kind("sand", "Img/tiles/areia_2.png", False),
    Tile_kind("sand", "Img/tiles/areia_3.png", False),
]
map = Map("map/mapa_1.csv", tile_kinds, TILES_SIZE)

# Botões
start_btn_img = pygame.image.load('Img/btns/start_btn.png')
start_btn = Button(SCREEN_HEIGHT//2, SCREEN_WIDTH//2, start_btn_img, 5)

# Jogador
plr_col = (255, 150, 100)
player = Player_rect(300, 200, 100, plr_col)

# Armas
gun = Gun(500, 450, 50, 'Img/Armas/arma_RW4.png', 12, 80, 8, True)
pistol = Gun(500, 700, 20, 'Img/Armas/pistol.png', 7, 60, 10, False)
laser_gun = Laser_gun(300, 300, 200, 'Img/Armas/laser_gun.png', 1)
bazooka = Bazooka(100, 100, 10, 'Img/Armas/bazuca_FW1000.png', 100, animation_cooldown, 'Img/other/bazooka_spritesheet.png', 32, 32)

# inimigos
soldier = Enemy(500, 500, '', 80, 60, 0.2)
soldier2 = Enemy(600, 800, '', 80, 60, 0.2)

enemy_limit = 10

# Munições
ammo_pack = AmmoPack(500, 200, 'gun', 0.7)
bazooka_pack = AmmoPack(500, 300, 'bazooka', 0.7)

loaded_guns = [gun, pistol, laser_gun, bazooka]
loaded_items = [ammo_pack, bazooka_pack]
loaded_enemies = [soldier]

def main_menu():
    menu = True
    while menu:
        screen.fill((80, 200, 255))

        start_btn.draw(screen)

        if start_btn.clicked:
            game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        
def game_over():
    game_over_menu = True
    while game_over_menu:

        screen.fill((255, 200, 180))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()

def item_handler(items):
    for item in items:
        if item.droped == True:
            item.update(screen, player)
        else:
            loaded_items.remove(item)

def enemies_handler(enemies, screen, player):
    for enemy in enemies:
        if enemy.life > 0:
            enemy.update(screen, player)
        else:
            enemies.remove(enemy)

def check_blt_collisions(player, enemies):
    for enemy in enemies: # checa tiros do player
        for gun in loaded_guns:
            gun.check_collision(enemy)
        
        # checa tiros dos inimigos
        enemy.gun.check_collision( player)

def update_screen(player, guns, camera, enemies):
    camera.x = max(0, min(player.rect.x - SCREEN_WIDTH // 2, (len(map.tiles[0]) * TILES_SIZE) - SCREEN_WIDTH))
    camera.y = max(0, min(player.rect.y - SCREEN_HEIGHT // 2, (len(map.tiles) * TILES_SIZE) - SCREEN_HEIGHT))

    item_handler(loaded_items)

    player.update(screen)

    enemies_handler(enemies, screen, player)

    for gun in guns:
        gun.update(player, screen)
        if gun.equiped == True:
            gun.draw_ammo(screen)

def game():

    run = True
    while run:
        clock.tick(FPS)

        map.draw(screen) # desenha o mapa (background)

        update_screen(player, loaded_guns, camera, loaded_enemies) # desenha o jogo e os objetos (precisa estar depois do mapa)

        # collisions
        check_blt_collisions(player, loaded_enemies)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    soldier.life = soldier.max_life
                    soldier2.life = soldier.max_life

            if event.type == EQUIP_EVENT:
                player.equip()
            elif event.type == DEQUIP_EVENT:   
                player.dequip()

        if not player.life:
            game_over()

        
        pygame.display.flip()

if __name__ == "__main__":
    main_menu()

pygame.quit()
sys.exit()