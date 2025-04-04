import pygame
import sys
from random import randrange, randint

from character import Player
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

# Menu
menu_logo = pygame.image.load('Img/logo/logo_semfundo.png')
fundo_menu = pygame.image.load('Img/logo/fundo_menu.jpg')

# Botões
start_btn_img = pygame.image.load('Img/btns/start_btn.png')
start_btn = Button(SCREEN_HEIGHT//2, SCREEN_WIDTH//2, start_btn_img, 3)
start_btn.rect.x -= start_btn.rect.width//2
start_btn.rect.y -= start_btn.rect.height//2

# Jogador
player = Player(300, 300, 1, 'Img/characters/main_character.png', 2, animation_cooldown, [8, 4], 34, 46,)

# Armas
gun = Gun(500, 450, 50, 'Img/Armas/arma_RW4.png', 12, 80, 8, True)
pistol = Gun(500, 700, 20, 'Img/Armas/pistol.png', 7, 60, 10, False)
laser_gun = Laser_gun(300, 300, 200, 'Img/Armas/laser_gun.png', 1)
bazooka = Bazooka(100, 100, 10, 'Img/Armas/bazuca_FW1000.png', 100, animation_cooldown, 'Img/other/bazooka_spritesheet.png', 32, 32)

# inimigos
enemy_limit = 10
loaded_enemies = []
spawn_cooldown = 1000 # em ms
last_spawned_enemy = pygame.time.get_ticks()
spawn_chance = 0


# Munições
ammo_pack = AmmoPack(500, 200, 'gun', 0.7)
bazooka_pack = AmmoPack(500, 300, 'bazooka', 0.7)

loaded_guns = [gun, pistol, laser_gun, bazooka]
loaded_items = [ammo_pack, bazooka_pack]

# Telas

def main_menu():
    menu = True
    while menu:
        screen.blit(fundo_menu,(0, 0))
        screen.blit(menu_logo, (SCREEN_WIDTH// 2 - menu_logo.get_width()//2, 100))

        if start_btn.draw(screen):
            game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        
def game_over():
    game_over_menu = True
    while game_over_menu:

        screen.fill((0, 0, 0))

        if start_btn.draw(screen):
            game_over_menu = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()


# Funções para o jogo

def item_handler(items):
    for item in items:
        if item.droped == True:
            item.update(screen, player)
        else:
            loaded_items.remove(item)

def enemies_handler(enemies, screen, player):
    current_time = pygame.time.get_ticks()
    global last_spawned_enemy
    global spawn_chance

    enemy_spawn_x = randrange(len(map.tiles[0] * map.tile_size))
    enemy_spawn_y = randrange(len(map.tiles * map.tile_size))

    # Gerenciar spawn de inimigos
    while enemy_spawn_x >= camera.x and enemy_spawn_x <= camera.x + camera.width:
        enemy_spawn_x = randrange(len(map.tiles[0] * map.tile_size))
    while enemy_spawn_y >= camera.y and enemy_spawn_y <= camera.y + camera.height:
        enemy_spawn_y = randrange(len(map.tiles * map.tile_size))

    if current_time - last_spawned_enemy >= spawn_cooldown:
        spawn_chance += randint(0, 5)
        last_spawned_enemy = current_time
        if spawn_chance >= 5 and len(enemies) < enemy_limit:
            soldier = Enemy(enemy_spawn_x, enemy_spawn_y, '', 80, 60, 0.2)
            enemies.append(soldier)
            spawn_chance = 0
            print('enemy spawned')

    # Lógica para desenhar inimigos na tela e eliminar inimigos mortos
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

        map.draw(screen) # desenha o mapa (background)

        item_handler(loaded_items)
        enemies_handler(loaded_enemies, screen, player)
        
        update_screen(player, loaded_guns, camera) # desenha o jogo e os objetos (precisa estar depois do mapa)

        # collisions
        check_blt_collisions(player, loaded_enemies)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


            if event.type == EQUIP_EVENT:
                player.equip()
            elif event.type == DEQUIP_EVENT:   
                player.dequip()

        if player.life < 0:
            game_over()
            run = False

        
        pygame.display.flip()

if __name__ == "__main__":
    main_menu()

pygame.quit()
sys.exit()