import pygame
import sys
from random import randrange, randint

from player import Player, ShowKey
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
pygame.mixer.init()

#--------------Variáveis----------------
clock = pygame.time.Clock()
FPS = 60

ANIMATION_COOLDOWN = 60

# Mapa
map_boss = Map("./map/mapa-boss/mapboss.tmx")
map_1 = Map("./map/primeiro_mapa/fase_1.tmx")

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
btn_posx = camera.width//2 - game_over_btn_img.get_width()*3//2
game_over_btn = Button(btn_posx, 500, game_over_btn_img, 3)

# Jogador
PLAYER_MAX_HP = 200
PLAYER_INITIAL_X = 300
PLAYER_INITIAL_Y = 300
INITIAL_AMMO = (5, 4)

player = Player(PLAYER_INITIAL_X, PLAYER_INITIAL_Y, PLAYER_MAX_HP, 'Img/characters/protagonista.png', 2.5, ANIMATION_COOLDOWN, [1, 3], 28, 31)
e_key = ShowKey()

player.rect.clamp_ip(camera)

gun_spawn_cooldown = 0 #8000
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

def reset(player, map):
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

    # Armas
    init_pistol = Gun(PLAYER_INITIAL_X + 50, PLAYER_INITIAL_Y + 50, 20, 'Img/Armas/pistol.png', 14, 60, 10, False)
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
    loaded_enemies.clear()
    # Reseta as armas
    loaded_guns.clear()
    loaded_guns.append(init_pistol)
    #limpa os itens
    loaded_items.clear()

    # Reseta as armas
    game_guns = [gun, laser_gun, bazooka]

    # Reseta as balas
    player_blts.clear()
    enemies_blts.clear()

    # Reseta o jogador
    player.equiped = False
    player.weapon = None
    player.frame = 0
    player.direction = 'right'
    player.state = 'idle'
    player.life = PLAYER_MAX_HP
    player.rect.topleft = (PLAYER_INITIAL_X, PLAYER_INITIAL_Y)
    player.ammo_pack = INITIAL_AMMO[0]
    player.bazooka_ammo_pack = INITIAL_AMMO[1]

    # Reseta a camera
    camera.x = max(0, min(player.rect.x - SCREEN_WIDTH // 2, (map.width) - SCREEN_WIDTH))
    camera.y = max(0, min(player.rect.y - SCREEN_HEIGHT // 2, (map.height) - SCREEN_HEIGHT))

def fade_in(screen):
    fade_surface = pygame.Surface((camera.width, camera.height))
    fade_surface.fill((0, 0, 0))
    fade_alpha = 0

    fade_ativo = True

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if fade_ativo:
            fade_alpha += 5
            if fade_alpha >= 255:
                fade_alpha = 255
                fade_ativo = False
                break

        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))

        pygame.display.flip()

def fade_out(screen, map):
    fade_surface = pygame.Surface((camera.width, camera.height))
    fade_surface.fill((0, 0, 0))
    fade_alpha = 255

    fade_ativo = True

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        map.draw_map(screen)
        player.draw_player(screen)
        screen.blit(game_boss.surface, (game_boss.rect.x - camera.x, game_boss.rect.y - camera.y))

        if fade_ativo:
            fade_alpha -= 5
            if fade_alpha <= 0:
                fade_alpha = 0
                fade_ativo = False
                break

        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))

        pygame.display.flip()

def item_handler(items, plr_blts, enemy_blts, map, spawn_guns=True):
    current_time = pygame.time.get_ticks()
    # Items
    global last_item_spawn
    global item_spawn_chance

    valid_item = False

    if current_time - last_item_spawn >= item_spawn_cooldown:
        item_spawn_chance += randint(0, 5)
        last_item_spawn = current_time
        if item_spawn_chance >= 5 and len(items) < items_limit:
            rnd_item = randint(0, 2)

            while not valid_item:
                item_x = randrange(75, map.width) - 50
                item_y = randrange(75, map.height) - 50

                if rnd_item in [0, 1]:
                    ammo_pack = AmmoPack(item_x, item_y, 'gun', 0.7)
                elif rnd_item == 2:
                    ammo_pack = AmmoPack(item_x, item_y, 'bazooka', 0.7)

                for block in map.collision_tiles:
                    if block.colliderect(ammo_pack):
                        break
                else:
                    valid_item = True

            loaded_items.append(ammo_pack)
            item_spawn_chance = 0
            print('item spawned')

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

        valid_gun = False

        if current_time - last_gun_spawn >= gun_spawn_cooldown and len(game_guns):
            gun_spawn_chance += randint(0, 5)
            last_gun_spawn = current_time
            if gun_spawn_chance >= 5:
                rnd_gun = randint(0, len(game_guns) - 1)
                
                while not valid_gun:
                    gun_x = randrange(75, map.width) - 50
                    gun_y = randrange(75, map.height) - 50
                    game_guns[rnd_gun].rect.topleft = (gun_x, gun_y)

                    # testa se a arma está em uma posição inválida
                    for block in map.collision_tiles:
                        if block.colliderect(game_guns[rnd_gun]):
                            valid_gun = False
                            break
                        else:
                            valid_gun = True

                loaded_guns.append(game_guns.pop(rnd_gun))
                print('gun spawned')
    
    handle_blts(plr_blts, enemy_blts)

def handle_blts(plr_blts, enemy_blts):
    all_blts = plr_blts + enemy_blts

    for bullet in all_blts:
        bullet.rect.x += bullet.speed_x
        bullet.rect.y += bullet.speed_y

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

def enemies_handler(enemies, map, boss_level=False):
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
                enemy.check_collisions(enemies)
            else:
                enemies.remove(enemy)
                return 1
        return 0
    else:
        for enemy in enemies:
            if not isinstance(enemy, Boss1):
                enemies.remove(enemy)

def update_screen(player, camera, map):
    camera.x = max(0, min(player.rect.x - SCREEN_WIDTH // 2, (map.width) - SCREEN_WIDTH))
    camera.y = max(0, min(player.rect.y - SCREEN_HEIGHT // 2, (map.height) - SCREEN_HEIGHT))

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

    # desenha o jogo
    # Chão
    map.draw_map(screen)

    # Jogador, inimigos e itens
    # armas

    print(loaded_guns)
    if len(loaded_guns):
        for gun in loaded_guns:
            if not isinstance(gun, Laser_gun):
                gun.update(player, screen, player_blts)
            else:
                gun.update(player, screen, loaded_enemies)

            if not player.equiped:
                gun.check_equip(player)

                if gun.rect.colliderect(player.rect):
                    e_key.show_key(screen, player)

    # player
    player.draw_player(screen)

    # inimigos
    for enemy in loaded_enemies:
        enemy.update(screen, player, enemies_blts)

    # balas
    all_blts = player_blts + enemies_blts
    curr_time = pygame.time.get_ticks()

    for bullet in all_blts:
        if bullet.type == "gun":
            screen.blit(bullet.surf, (bullet.rect.x - camera.x, bullet.rect.y - camera.y))
        elif bullet.type == "explosive": # Lógica para animar a explosão
            bullet.update(screen, curr_time, ANIMATION_COOLDOWN)

    # tiles acima do jogador
    map.draw_above_player(screen)

    player.update(screen)

    if game_boss in loaded_enemies:
        game_boss.show_life(screen)

def first_dialog():
    pygame.mixer.music.stop()
    # caixa de dialogo 
    dialog_box = DialogBox('Img/other/dialog_box.png', (255, 255, 255))

    position_x = (SCREEN_WIDTH - dialog_box.image.get_width()) // 2
    position_y = SCREEN_HEIGHT - dialog_box.image.get_height() - 20
    
    # caminho das imagens do Erik e do Viktor respectivamente
    imgs = ['Img/characters/protagonista_rosto.png', 'Img/tiles/arame_farpado.png']

    dialogo = [
        'ERIK: Eu voltei com sucesso Viktor! Estou no meio do fogo cruzado aqui! Mas, cara... é exatamente o que eu imaginava!',
        'ERIK: Só que... espera, acho que a máquina não estava 100% pronta, viu? As armas estão caindo do céu!',
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
        
        # Carregar texto e imagem de cada um dos personagens
        if 'erik:' in dialogo[text_counter].lower():
            text = dialogo[text_counter].replace('ERIK: ', '')
            img = pygame.image.load(imgs[0])
        else:
            text = dialogo[text_counter].replace('VIKTOR: ', '')
            img = pygame.image.load(imgs[1]) 
        

        if dialog_box.draw(screen, (position_x, position_y), text, img):
            if text_counter < len(dialogo) - 1 and dialog_box.done:
                text_counter += 1
                dialog_box.reset()
            else:
                dialog = False


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    dialog = False
                    
        pygame.display.flip()

def boss_dialog():
    pygame.mixer.music.stop()
    # caixa de dialogo 
    dialog_box = DialogBox('Img/other/dialog_box.png', (255, 255, 255))

    position_x = (SCREEN_WIDTH - dialog_box.image.get_width()) // 2
    position_y = SCREEN_HEIGHT - dialog_box.image.get_height() - 20

    # caminho das imagens do Erik e do Viktor respectivamente
    imgs = ['Img/characters/protagonista_rosto.png', 'Img/tiles/arame_farpado.png']

    dialogo = [
        'ERIK: Viktor...? Não pode ser... Você veio! Conseguiu fazer a viagem também?',
        'VIKTOR: Sim, Erik... Consegui. Mas não pelo mesmo motivo que você.',
        'ERIK: Do que você está falando? Eu não estou te entendendo...',
        'ERIK: Isso é sobre nosso sonho de mudar Varsênia? Não prometemos um ao outro que iríamos mudar isso',
        'VIKTOR: Eu pensei que fosse possível. Mas não é. Zypharia me fez ver... que estamos lutando uma guerra perdida. Que estamos tentando salvar algo que já morreu há muito tempo.',
        'ERIK: Eles te compraram... não foi? Eles te prometeram conforto, poder... e você aceitou?! Você traiu tudo que a gente construiu!',
        'VIKTOR: Você acha que foi fácil? Eu vi Varsênia se desfazendo diante dos meus olhos, dia após dia.', 
        'VIKTOR: Eu tentei manter a fé. Mas você... você ainda acredita em fantasias. Mudar o passado não vai apagar as cicatrizes. Vai apenas criar outras.',
        'ERIK: Isso não é sobre cicatrizes! É sobre dar ao nosso povo uma chance! Uma chance de lutar, de viver! E você... era meu irmão, Viktor!',
        'VIKTOR: Ainda é difícil, Erik. Mas... eu tomei minha decisão. Eles me prometeram paz... e depois de tudo, eu acho que é isso que eu quero. Mesmo que custe a sua vida.',
        'ERIK: Então venha. Se vai me matar, olhe nos meus olhos e veja o que ainda resta de Varsênia neles. Veja se consegue puxar o gatilho sabendo que a esperança morreu com você.',
        'VIKTOR: Adeus, Erik...'
        ]
    text_counter = 0

    dialog = True
    while dialog:
        clock.tick(FPS)
        
        # Carregar texto e imagem de cada um dos personagens
        if 'erik:' in dialogo[text_counter].lower():
            text = dialogo[text_counter].replace('ERIK: ', '')
            img = pygame.image.load(imgs[0])
        else:
            text = dialogo[text_counter].replace('VIKTOR: ', '')
            img = pygame.image.load(imgs[1]) 
        

        if dialog_box.draw(screen, (position_x, position_y), text, img):
            if text_counter < len(dialogo) - 1 and dialog_box.done:
                text_counter += 1
                dialog_box.reset()
            else:
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
    pygame.mixer.music.stop()
    menu = True
    while menu:
        screen.blit(fundo_menu,(0, 0))
        screen.blit(menu_logo, (SCREEN_WIDTH// 2 - menu_logo.get_width()//2, 100))

        if start_btn.draw(screen):
            reset(player, map_1)
            fade_in(screen)
            if level1():
                fade_in(screen)
                boss_level1()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False

        pygame.display.flip()
        
def game_over():
    pygame.mixer.music.stop()
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
    global camera

    pygame.mixer.music.stop()

    game_boss.life = game_boss.max_life
    game_boss.blts = []
    game_boss.last_circle_atk = pygame.time.get_ticks()
    game_boss.last_plr_atk = pygame.time.get_ticks()

    # Remove todos os inimigos do mapa
    loaded_enemies.clear()

    # Remove todas as armas que não estão equipadas
    loaded_guns.clear()
    loaded_guns.append(player.weapon)

    loaded_enemies.append(game_boss)

    # Define a posição do jogador e do boss
    player.rect.x, player.rect.y = 470, 700
    player.direction = 'right'
    player.state = 'idle'
    player.frame = 0

    game_boss.rect.x, game_boss.rect.y = 800, 700

    camera.centerx = (player.rect.centerx + game_boss.rect.centerx)//2
    camera.centery = player.rect.centery
    map_boss.draw_map(screen)
    player.draw_player(screen)
    for enemy in loaded_enemies:
        enemy.update(screen, player, enemies_blts)

    # voltar a tela para o mapa do boss
    fade_out(screen, map_boss)

    boss_dialog()

    # Caso o jogador não esteja segurando uma arma
    if not len(loaded_guns) and player.weapon == None:
        loaded_guns.append(
            Gun(530, 740, 20, 'Img/Armas/pistol.png', 14, 60, 10, False)
        )

    boss = True
    while boss:


        clock.tick(FPS)

        map_boss.draw_map(screen)
        map_boss.check_block_collisions(player, loaded_enemies, player_blts + enemies_blts)

        update_screen(player, camera, map_boss)
        
        item_handler(loaded_items, player_blts, enemies_blts, map_boss, spawn_guns=False)
        enemies_handler(loaded_enemies, map_boss, boss_level=True)

        if player.life <= 0:
            game_over()
            boss = False

        elif game_boss.life <= 0:
            pass #TODO Tela de vitória
            boss = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
    

def level1():
    pygame.mixer.music.stop()
    defeated_enemies = 0
    won = False

    update_screen(player, camera, map_1)
    player.update(screen)
    first_dialog()

    # música da primeira fase 
    pygame.mixer.music.load("audio/music/iron_maiden-wasted_years-fase1.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)

    run = True
    while run:
        clock.tick(FPS)
        

        map_1.draw_map(screen) # desenha o mapa (background)
        map_1.check_block_collisions(player, loaded_enemies, player_blts + enemies_blts) # checa colisões no mapa
        
        update_screen(player, camera, map_1)

        item_handler(loaded_items, player_blts, enemies_blts, map_1)

        if enemies_handler(loaded_enemies, map_1):
            defeated_enemies += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    print(player.weapon, player.equiped, loaded_guns, player_blts, enemies_blts)

            if event.type == EQUIP_EVENT:
                player.equip()
            elif event.type == DEQUIP_EVENT:   
                player.dequip()

        if player.life <= 0:
            fade_in(screen)
            game_over()
            run = False

        #Define a quantidade de inimigos que devem ser derrotados para avançar de fase
        if defeated_enemies >= 1 and not won:
            won_time = pygame.time.get_ticks()
            won = True
        if won:
            if pygame.time.get_ticks() - won_time >= 500:
                return True

        pygame.display.flip()
    

if __name__ == "__main__":
    main_menu()

pygame.quit()
sys.exit()