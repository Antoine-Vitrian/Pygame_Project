import pygame
from camera import camera
from game_map import SCREEN_HEIGHT, SCREEN_WIDTH
from sprites import SpriteSheet

class Player():
    def __init__(self, x, y, life, sprite_sheet, scale, animation_cooldown, animations_steps, sprite_width, sprite_height):
        # Animação
        self.sprite_image = pygame.image.load(sprite_sheet) 
        self.sprite_sheet = SpriteSheet(self.sprite_image)
        self.animation_list = self.sprite_sheet.get_animations(animations_steps, sprite_width, sprite_height, scale)
        self.animation_cooldown = animation_cooldown
        self.last_update = pygame.time.get_ticks() 
        self.state = 'idle'
        self.direction = 'right'
        self.idle_animation_list = self.animation_list[0]
        self.walking_animation_list = self.animation_list[1]
        self.frame = 0

        # status
        self.rect = pygame.rect.Rect(x, y, sprite_width * scale, sprite_height * scale)
        self.max_life = life
        self.last_life = life
        self.life = life
        self.equiped = False
        self.bazooka_ammo_pack = 4
        self.ammo_pack = 5
        self.weapon = None
        self.invincible = False
        self.last_invincible = pygame.time.get_ticks()
        self.invincible_cooldown = 600
        
        # Movimentação 
        self.speed_x = 0
        self.speed_y = 0
        self.acc = 2
        self.friction = 0.3


    def update(self, screen):
        current_time = pygame.time.get_ticks()
        self.draw_life(screen)

        if self.last_life > self.life:
            self.last_life = self.life
            self.invincible = True
            self.last_invincible = pygame.time.get_ticks()

        if self.invincible and current_time - self.last_invincible >= self.invincible_cooldown:
            self.invincible = False

        self.inputs(screen)

        # Checa se está andando ou não
        if abs(self.speed_x) != 0 or abs(self.speed_y) != 0:
            if self.state == 'idle':
                self.frame = 0
                self.state = 'walking'
        else:
            if self.state == 'walking':
                self.frame = 0
                self.state = 'idle'

        # Se estiver andando diminui a velocidade para cada eixo
        if abs(self.speed_x) >= 1:
            self.speed_x -= self.friction * self.speed_x
        else:
            self.speed_x = 0

        if abs(self.speed_y) >= 1:
            self.speed_y -= self.friction * self.speed_y
        else:
            self.speed_y = 0


        if not self.equiped:
            if self.speed_x > 0:
                self.direction = 'right'
            elif self.speed_x < 0: 
                self.direction = 'left' 

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        self.draw_player(screen)

    def inputs(self, screen):
        keys_pressed = pygame.key.get_pressed()

        # Movimentação
        if keys_pressed[pygame.K_a]:
            self.speed_x -= self.acc
        if keys_pressed[pygame.K_d]:
            self.speed_x += self.acc
        if keys_pressed[pygame.K_w]:
            self.speed_y -= self.acc
        if keys_pressed[pygame.K_s]:
            self.speed_y += self.acc

        if self.equiped == True or keys_pressed[pygame.K_c]:
            self.show_ammo_packs(screen)

    def draw_player(self, screen):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time

        if self.state == 'idle':
            if self.frame == len(self.idle_animation_list):
                self.frame = 0
            if self.direction == 'right':
                screen.blit(self.idle_animation_list[self.frame], (self.rect.x - camera.x, self.rect.y - camera.y))
            elif self.direction == 'left':
                fliped_image = pygame.transform.flip(self.idle_animation_list[self.frame], True, False).convert_alpha()
                screen.blit(fliped_image, (self.rect.x - camera.x, self.rect.y - camera.y))

        elif self.state == 'walking':
            if self.frame == len(self.walking_animation_list) - 1:
                self.frame = 0
            
            if self.direction == 'right':
                screen.blit(self.walking_animation_list[self.frame], (self.rect.x - camera.x, self.rect.y - camera.y))
            elif self.direction == 'left':
                fliped_image = pygame.transform.flip(self.walking_animation_list[self.frame], True, False).convert_alpha()
                screen.blit(fliped_image, (self.rect.x - camera.x, self.rect.y - camera.y))

    def equip(self):
        self.equiped = True

    def dequip(self):
        self.equiped = False

    def draw_life(self, screen):
        
        #desenha a vida do jogador na tela
        pygame.draw.rect(screen, (255, 0, 0), (50, 20, 300, 15))
        pygame.draw.rect(screen, (0, 255, 0), (50, 20, 300 * self.life / self.max_life, 15))

    def show_ammo_packs(self, screen):
        # Texto
        #fonte da munição
        font = pygame.font.Font('freesansbold.ttf', 24) 

        text = font.render('Munição:', True, (100, 180, 180))
        screen.blit(text, (20, SCREEN_HEIGHT - 100))

        # Imagens
        ammo_pack = pygame.image.load('Img/other/gun_battery.png')
        bazooka_ammo_pack = pygame.image.load('Img/other/bazooka_ammo.png')
        dist = 26


        for pack in range(self.ammo_pack):
            screen.blit(ammo_pack, (20 + dist * pack, SCREEN_HEIGHT - 60))
            
        for pack in range(self.bazooka_ammo_pack):
            screen.blit(bazooka_ammo_pack, (20 + dist * pack, SCREEN_HEIGHT - 30))

