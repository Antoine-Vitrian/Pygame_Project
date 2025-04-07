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

# Game Over
game_over_img = pygame.image.load("Img/game_over/game_over.png")
menor_game_over = pygame.transform.smoothscale(game_over_img, (400, 400))

# Botões menu
start_btn_img = pygame.image.load('Img/btns/start_btn.png')
start_btn = Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, start_btn_img, 3)
start_btn.rect.x -= start_btn.rect.width//2
start_btn.rect.y -= start_btn.rect.height//2

# Botões game over
game_over_btn_img = pygame.image.load('Img/game_over/botao12.png')
game_over_btn = Button(400, 500, game_over_btn_img, 3)

# Jogador
PLAYER_MAX_HP = 200
PLAYER_INITIAL_X = 300
PLAYER_INITIAL_Y = 300
INITIAL_AMMO = (5, 4)

player = Player(PLAYER_INITIAL_X, PLAYER_INITIAL_Y, PLAYER_MAX_HP, 'Img/characters/main_character.png', 2, animation_cooldown, [8, 4], 34, 46,)

player.rect.clamp_ip(camera)

# Armas
init_pistol = Gun(PLAYER_INITIAL_X + 50, PLAYER_INITIAL_Y + 50, 20, 'Img/Armas/pistol.png', 7, 60, 10, False)
pistol = Gun(500, 700, 20, 'Img/Armas/pistol.png', 7, 60, 10, False)

gun_spawn_cooldown = 13000
last_gun_spawn = pygame.time.get_ticks()
gun_spawn_chance = 0

game_guns = []

# inimigos
enemy_limit = 10
spawn_cooldown = 1000 # em ms
last_spawned_enemy = pygame.time.get_ticks()
enemy_spawn_chance = 0


# Munições
items_limit = 8
item_spawn_cooldown = 10000
last_item_spawn = pygame.time.get_ticks()
item_spawn_chance = 0


loaded_guns = []
loaded_items = []
loaded_enemies = []

# Telas

def main_menu():
    menu = True
    while menu:
        screen.blit(fundo_menu,(0, 0))
        screen.blit(menu_logo, (SCREEN_WIDTH// 2 - menu_logo.get_width()//2, 100))

        if start_btn.draw(screen):
            reset(player)
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
        screen.blit(menor_game_over, (SCREEN_WIDTH// 2 - menor_game_over.get_width()//2, 50))

        if game_over_btn.draw(screen):
            game_over_menu = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()


# Funções para o jogo

def reset(player):
    global loaded_enemies
    global last_spawned_enemy
    global enemy_spawn_chance
    global game_guns
    global loaded_guns
    global last_gun_spawn
    global gun_spawn_chance
    global loaded_items
    global last_item_spawn
    global item_spawn_chance

    laser_gun = Laser_gun(300, 300, 200, 'Img/Armas/laser_gun.png', 1)
    bazooka = Bazooka(100, 100, 10, 'Img/Armas/bazuca_FW1000.png', 100, animation_cooldown, 'Img/other/bazooka_spritesheet.png', 32, 32)
    gun = Gun(500, 450, 50, 'Img/Armas/arma_RW4.png', 12, 80, 8, True)
    
    game_guns = [gun, laser_gun, bazooka]

    # reseta os spawns
    last_gun_spawn = pygame.time.get_ticks()
    gun_spawn_chance = 0
    last_spawned_enemy = pygame.time.get_ticks()
    enemy_spawn_chance = 0
    last_item_spawn = pygame.time.get_ticks()
    item_spawn_chance = 0

    loaded_enemies = []
    loaded_guns = [init_pistol]
    loaded_items = []

    # Reseta as armas
    game_guns = [gun, laser_gun, bazooka]
    pistol = loaded_guns[0]
    pistol.rect.topleft = (PLAYER_INITIAL_X + 50, PLAYER_INITIAL_Y + 50)
    pistol.equiped = False
    pistol.curr_ammo = pistol.ammo 
    pistol.blts = []

    for gun in game_guns:
        gun.equiped = False

    # Reseta o jogador
    player.equiped = False
    player.life = PLAYER_MAX_HP
    player.rect.topleft = (PLAYER_INITIAL_X, PLAYER_INITIAL_Y)
    player.ammo_pack = INITIAL_AMMO[0]
    player.bazooka_ammo_pack = INITIAL_AMMO[1]

def item_handler(items, guns):
    current_time = pygame.time.get_ticks()
    # Items
    global last_item_spawn
    global item_spawn_chance

    item_x = randrange(75, len(map.tiles[0]) * map.tile_size) - 50
    item_y = randrange(75, len(map.tiles) * map.tile_size) - 50

    if current_time - last_item_spawn >= item_spawn_cooldown:
        item_spawn_chance += randint(0, 5)
        last_item_spawn = current_time
        if item_spawn_chance >= 5 and len(items) < items_limit:
            rnd_item = randint(0, 2)
            if rnd_item in [0, 1]:
                ammo_pack = AmmoPack(item_x, item_y, 'gun', 0.7)
                items.append(ammo_pack)
            elif rnd_item == 2:
                bazooka_pack = AmmoPack(item_x, item_y, 'bazooka', 0.7)
                items.append(bazooka_pack)
            item_spawn_chance = 0
            print('item spawned', len(items))

    for item in items:
        if item.droped == True:
            item.update(screen, player)
        else:
            loaded_items.remove(item)

    # Armas
    global last_gun_spawn
    global gun_spawn_chance
    global game_guns

    gun_x = randrange(75, len(map.tiles[0]) * map.tile_size) - 50
    gun_y = randrange(75, len(map.tiles) * map.tile_size) - 50

    if current_time - last_gun_spawn >= gun_spawn_cooldown and len(game_guns):
        gun_spawn_chance += randint(0, 5)
        last_gun_spawn = current_time
        if gun_spawn_chance >= 5:
            rnd_gun = randint(0, len(game_guns) - 1)
            
            loaded_guns.append(game_guns.pop(rnd_gun))
            loaded_guns[len(loaded_guns) - 1].rect.topleft = (gun_x, gun_y) 
            print(loaded_guns)

            print('gun spawned')

    for gun in guns:
        gun.update(player, screen)
        if gun.equiped:
            gun.draw_ammo(screen)
        elif not player.equiped:
            gun.check_equip(player)

def enemies_handler(enemies, screen, player):
    current_time = pygame.time.get_ticks()
    global last_spawned_enemy
    global enemy_spawn_chance

    enemy_spawn_x = randrange(len(map.tiles[0] * map.tile_size))
    enemy_spawn_y = randrange(len(map.tiles * map.tile_size))

    # Gerenciar spawn de inimigos
    while enemy_spawn_x >= camera.x and enemy_spawn_x <= camera.x + camera.width:
        enemy_spawn_x = randrange(len(map.tiles[0] * map.tile_size))
    while enemy_spawn_y >= camera.y and enemy_spawn_y <= camera.y + camera.height:
        enemy_spawn_y = randrange(len(map.tiles * map.tile_size))

    if current_time - last_spawned_enemy >= spawn_cooldown: # aleatóriamente adiciona chance de spawnar um inimigo
        enemy_spawn_chance += randint(0, 5)
        last_spawned_enemy = current_time
        if enemy_spawn_chance >= 5 and len(enemies) < enemy_limit:
            soldier = Enemy(enemy_spawn_x, enemy_spawn_y, '', 60, 60, 0.2)
            enemies.append(soldier)
            enemy_spawn_chance = 0
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

def update_screen(player, camera):
    camera.x = max(0, min(player.rect.x - SCREEN_WIDTH // 2, (len(map.tiles[0]) * TILES_SIZE) - SCREEN_WIDTH))
    camera.y = max(0, min(player.rect.y - SCREEN_HEIGHT // 2, (len(map.tiles) * TILES_SIZE) - SCREEN_HEIGHT))

    player.update(screen)

    if player.speed_x > 0 and player.rect.x + player.rect.width >= len(map.tiles[0]) * map.tile_size:
            player.speed_x = 0
            player.rect.x = len(map.tiles[0]) * map.tile_size - player.rect.width
    if player.speed_x < 0 and player.rect.x <= 0:
            player.speed_x = 0
            player.rect.x = 0
    if player.speed_y > 0 and player.rect.y + player.rect.height >= len(map.tiles) * map.tile_size:
            player.speed_y = 0
            player.rect.y = len(map.tiles) * map.tile_size - player.rect.height
    if player.speed_y < 0 and player.rect.y <= 0:
            player.speed_y = 0
            player.rect.y = 0

def game():

    run = True
    while run:
        clock.tick(FPS)

        map.draw(screen) # desenha o mapa (background)

        item_handler(loaded_items, loaded_guns)
        enemies_handler(loaded_enemies, screen, player)
        
        update_screen(player, camera) # desenha o jogo e os objetos (precisa estar depois do mapa)

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

        if player.life <= 0:
            game_over()
            run = False

        
        pygame.display.flip()

if __name__ == "__main__":
    main_menu()

pygame.quit()
sys.exit()