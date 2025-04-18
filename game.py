import pygame
import sys
from random import randrange, randint

from character import Player
from guns import *
from enemies import Enemy, Boss1
from camera import camera
from game_map import *
from itens import AmmoPack
from sprites import *
from button import Button
from dialog import DialogBox
from map_tiled import *

pygame.init()

#--------------Variáveis----------------
clock = pygame.time.Clock()
FPS = 60

ANIMATION_COOLDOWN = 60

# Mapa

map = Map("./map\mapa-boss\mapboss.tmx")

# Tiled map

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

player = Player(PLAYER_INITIAL_X, PLAYER_INITIAL_Y, PLAYER_MAX_HP, 'Img/characters/protagonista.png', 2.5, ANIMATION_COOLDOWN, [1, 3], 28, 31)

player.rect.clamp_ip(camera)

# Armas
init_pistol = Gun(PLAYER_INITIAL_X + 50, PLAYER_INITIAL_Y + 50, 20, 'Img/Armas/pistol.png', 14, 60, 10, False)

gun_spawn_cooldown = 0
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
player_blts = []
enemies_blts = []

# BOSS
game_boss = Boss1('')
# Funções para o jogo

def reset(player):
    global last_spawned_enemy
    global enemy_spawn_chance
    global game_guns
    global loaded_guns
    global last_gun_spawn
    global gun_spawn_chance
    global last_item_spawn
    global item_spawn_chance

    laser_gun = Laser_gun(300, 300, 200, 'Img/Armas/laser_gun.png')
    bazooka = Bazooka(100, 100, 10, 'Img/Armas/bazuca_FW1000.png', 100, ANIMATION_COOLDOWN, 'Img/other/bazooka_spritesheet.png')
    gun = Gun(500, 450, 50, 'Img/Armas/arma_RW4.png', 18, 80, 8, True)

    # reseta os spawns
    last_gun_spawn = pygame.time.get_ticks()
    gun_spawn_chance = 0
    last_spawned_enemy = pygame.time.get_ticks()
    enemy_spawn_chance = 0
    last_item_spawn = pygame.time.get_ticks()
    item_spawn_chance = 0

    # Limpa os inimigos
    for enemy in loaded_enemies:
        loaded_enemies.remove(enemy)
    # Reseta as armas
    for gun in loaded_guns:
        loaded_guns.remove(gun)
    loaded_guns.append(init_pistol)
    #limpa os itens
    for item in loaded_items:
        loaded_items.remove(item)

    # Reseta as armas
    game_guns = [gun, laser_gun, bazooka]
    pistol = loaded_guns[0]
    pistol.rect.topleft = (PLAYER_INITIAL_X + 50, PLAYER_INITIAL_Y + 50)
    pistol.curr_ammo = pistol.ammo

    for gun in game_guns:
        gun.equiped = False

    # Reseta o jogador
    player.equiped = False
    player.life = PLAYER_MAX_HP
    player.rect.topleft = (PLAYER_INITIAL_X, PLAYER_INITIAL_Y)
    player.ammo_pack = INITIAL_AMMO[0]
    player.bazooka_ammo_pack = INITIAL_AMMO[1]

def item_handler(items, guns, plr_blts, enemy_blts, spawn_guns=True):
    current_time = pygame.time.get_ticks()
    # Items
    global last_item_spawn
    global item_spawn_chance

    item_x = randrange(75, map.width) - 50
    item_y = randrange(75, map.height) - 50

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
    if spawn_guns == True:
        global last_gun_spawn
        global gun_spawn_chance
        global game_guns

        gun_x = randrange(75, map.width) - 50
        gun_y = randrange(75, map.height) - 50

        if current_time - last_gun_spawn >= gun_spawn_cooldown and len(game_guns):
            gun_spawn_chance += randint(0, 5)
            last_gun_spawn = current_time
            if gun_spawn_chance >= 5:
                rnd_gun = randint(0, len(game_guns) - 1)
                
                loaded_guns.append(game_guns.pop(rnd_gun))
                loaded_guns[len(loaded_guns) - 1].rect.topleft = (gun_x, gun_y) 
                print('gun spawned')
    
    handle_blts(plr_blts, enemy_blts)
    for gun in guns:
        if not isinstance(gun, Laser_gun):
            gun.update(player, screen, player_blts)
        else:
            gun.update(player, screen, loaded_enemies)

        if gun.equiped:
            gun.draw_ammo(screen)
        elif not player.equiped:
            gun.check_equip(player)

def handle_blts(plr_blts, enemy_blts):
    all_blts = plr_blts + enemy_blts
    curr_time = pygame.time.get_ticks()

    for bullet in all_blts:
        bullet.rect.x += bullet.speed_x
        bullet.rect.y += bullet.speed_y

        if bullet.type == "gun":
            screen.blit(bullet.surf, (bullet.rect.x - camera.x, bullet.rect.y - camera.y))
        
        elif bullet.type == "explosive": # Lógica para animar a explosão
            bullet.update(screen, curr_time, ANIMATION_COOLDOWN)

        # Diminui tempo de vida da bala e remove se acabar
        if bullet.time_to_live:
            bullet.time_to_live -= 1
        elif bullet.enemy:
            enemy_blts.remove(bullet)
        elif isinstance(bullet, Blt):
            plr_blts.remove(bullet)
        elif bullet.get_explosion(screen, loaded_enemies):
            plr_blts.remove(bullet)

        if bullet.enemy:
            check_blt_collision(bullet, player)
        else:
            for enemy in loaded_enemies:
                check_blt_collision(bullet, enemy)

def check_blt_collision(blt, target): # checa se a bala acertou o alvo
    if blt.rect.colliderect(target) and blt.time_to_live:
        if not target.invincible:
            target.life -= blt.damage
        blt.time_to_live = 0

def enemies_handler(enemies, screen, player, boss_level=False):
    current_time = pygame.time.get_ticks()
    global last_spawned_enemy
    global enemy_spawn_chance

    if not boss_level:
        enemy_spawn_x = randrange(map.width)
        enemy_spawn_y = randrange(map.height)

        # Gerenciar spawn de inimigos
        while enemy_spawn_x >= camera.x and enemy_spawn_x <= camera.x + camera.width:
            enemy_spawn_x = randrange(map.width)
        while enemy_spawn_y >= camera.y and enemy_spawn_y <= camera.y + camera.height:
            enemy_spawn_y = randrange(map.height)

        if current_time - last_spawned_enemy >= spawn_cooldown: # aleatóriamente adiciona chance de spawnar um inimigo
            enemy_spawn_chance += randint(0, 5)
            last_spawned_enemy = current_time
            if enemy_spawn_chance >= 5 and len(enemies) < enemy_limit:
                soldier = Enemy(enemy_spawn_x, enemy_spawn_y, 'Img/characters/soldado_1.png', ANIMATION_COOLDOWN, (17, 23), 80, 60, 0.2, 3)
                soldier2 = Enemy(enemy_spawn_x, enemy_spawn_y, 'Img/characters/soldado_2.png', ANIMATION_COOLDOWN, (17, 23), 60, 60, 0.3, 3)
                if randint(0, 1):
                    enemies.append(soldier)
                else:
                    enemies.append(soldier2)
                enemy_spawn_chance = 0
                print('enemy spawned')

        # Lógica para desenhar inimigos na tela e eliminar inimigos mortos
        for enemy in enemies:
            if enemy.life > 0 and isinstance(enemy, Enemy):
                enemy.update(screen, player, enemies_blts)
                enemy.check_collisions(enemies)
            else:
                enemies.remove(enemy)
                return 1
        return 0
    else:
        for enemy in enemies:
            if not isinstance(enemy, Boss1):
                enemies.remove(enemy)
            enemy.update(screen, player, enemies_blts)

def update_screen(player, camera):
    camera.x = max(0, min(player.rect.x - SCREEN_WIDTH // 2, (map.width) - SCREEN_WIDTH))
    camera.y = max(0, min(player.rect.y - SCREEN_HEIGHT // 2, (map.height) - SCREEN_HEIGHT))

    player.update(screen)

    # prende o jogador na tela
    if player.speed_x > 0 and player.rect.x + player.rect.width >= map.width:
            player.speed_x = 0
            player.rect.x = map.width - player.rect.width
    if player.speed_x < 0 and player.rect.x <= 0:
            player.speed_x = 0
            player.rect.x = 0
    if player.speed_y > 0 and player.rect.y + player.rect.height >= map.height:
            player.speed_y = 0
            player.rect.y = map.height - player.rect.height
    if player.speed_y < 0 and player.rect.y <= 0:
            player.speed_y = 0
            player.rect.y = 0

def first_dialog():
    # caixa de dialogo 
    dialog_box = DialogBox('Img/other/dialog_box.png', (255, 255, 255))

    position_x = (SCREEN_WIDTH - dialog_box.image.get_width()) // 2
    position_y = SCREEN_HEIGHT - dialog_box.image.get_height() - 20
    

    dialogo = [
        'ERIK: Eu voltei com sucesso Viktor! Estou no meio do fogo cruzado aqui! Mas, cara... é exatamente o que eu imaginava! Só que... espera, acho que a máquina não estava 100% pronta, viu? As armas estão caindo do céu!',
        'VIKTOR: Erik, isso não está certo. A instabilidade da máquina...',
        'VIKTOR: As armas não deveriam estar caindo assim. Isso pode estar afetando o tempo! Você precisa se apressar! Não podemos deixar que isso piore!',
        'ERIK: Certo, tem munição caindo para todo lado! Eu... não esperava que fosse ficar tão caótico assim. O que mais pode dar errado?',
        'VIKTOR: A distorção temporal está se espalhando. Se você não agir rápido, a linha do tempo pode ser comprometida. Se apresse, Erik!',
        'ERIK: Ok... vou me apressar. Vamos ver o que eu consigo fazer para corrigir isso.'
        ]
    text_counter = 0

    dialog = True
    while dialog:
        clock.tick(FPS)

        imgs = ['Img/Armas/laser_gun.png', 'Img/tiles/arame_farpado.png']
        if 'erik:' in dialogo[text_counter].lower():
            img = pygame.image.load(imgs[0])
        elif 'viktor:' in dialogo[text_counter].lower():
            img = pygame.image.load(imgs[1]) 
        
        if dialog_box.draw(screen, (position_x, position_y), dialogo[text_counter], img):
            if text_counter < len(dialogo) - 1 and dialog_box.done:
                text_counter += 1
                dialog_box.reset()
            elif text_counter >= len(dialogo) - 1:
                dialog = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    dialog = False
            
                    
        pygame.display.flip()

# -----------------Telas--------------------------
def main_menu():
    menu = True
    while menu:
        screen.blit(fundo_menu,(0, 0))
        screen.blit(menu_logo, (SCREEN_WIDTH// 2 - menu_logo.get_width()//2, 100))

        if start_btn.draw(screen):
            reset(player)
            if level1():
                boss_level1()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False

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

def boss_level1():
    game_boss.life = game_boss.max_life
    game_boss.blts = []
    game_boss.last_circle_atk = pygame.time.get_ticks()
    game_boss.last_plr_atk = pygame.time.get_ticks()

    for enemy in loaded_enemies:
        loaded_enemies.remove(enemy)

    loaded_enemies.append(game_boss)

    boss = True
    while boss:
        clock.tick(FPS)

        map.draw_map(screen)
        map.check_block_collisions(player, loaded_enemies, player_blts + enemies_blts)

        update_screen(player, camera)
        item_handler(loaded_items, [player.weapon], player_blts, enemies_blts)
        enemies_handler(loaded_enemies, screen, player, boss_level=True)

        if player.life <= 0:
            game_over()
            boss = False

        elif game_boss.life <= 0:
            pass # Tela de vitória
            boss = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
    

def level1():
    defeated_enemies = 0
    game_started = False

    run = True
    while run:
        clock.tick(FPS)

        map.draw_map(screen) # desenha o mapa (background)
        map.check_block_collisions(player, loaded_enemies, player_blts + enemies_blts) # checa colisões no mapa
        update_screen(player, camera) # desenha o jogo e os objetos (precisa estar depois do mapa)

        if not game_started:
            first_dialog()
            game_started = True

        item_handler(loaded_items, loaded_guns, player_blts, enemies_blts)

        if enemies_handler(loaded_enemies, screen, player):
            defeated_enemies += 1

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

        if defeated_enemies >= 1:
            return True

        pygame.display.flip()

if __name__ == "__main__":
    main_menu()

pygame.quit()
sys.exit()