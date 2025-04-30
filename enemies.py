import pygame
import math
from random import randrange
from guns import Gun, Blt
from camera import camera
from sprites import SpriteSheet

class Enemy():
    def __init__(self, x, y, image, animation_cooldown, sprite_size, life, ammo, acc, scale):
        self.sprite_image = pygame.image.load(image)
        self.sprite_sheet = SpriteSheet(self.sprite_image)
        self.sprite_width, self.sprite_height = sprite_size
        animation_list = self.sprite_sheet.get_animations([4, 4], self.sprite_width, self.sprite_height, scale)
        self.idle_animation = animation_list[0]
        self.running_animation = animation_list[1]
        self.animation_cooldown = animation_cooldown
        self.last_update = pygame.time.get_ticks()
        self.frame = 0
        self.dist = 99999999999

        #retângulo
        self.rect = pygame.rect.Rect(x, y, self.sprite_width * scale, self.sprite_height * scale)

        # Enemy status
        self.max_life = life
        self.life = life
        self.last_life = life
        self.ammo = ammo
        self.curr_ammo = ammo
        self.acc = acc
        self.speed_x = 0
        self.speed_y = 0
        self.invincible = False

        self.action = 'idle'
        self.last_action = ''

        # arma do inimigo
        self.gun = Gun(self.rect.x, self.rect.y, 30, 'Img/Armas/Arma_Soldado_inimigo.png', 8, 80, 20, False)
        self.gun.equiped = True
        self.last_shot = pygame.time.get_ticks()
        self.shoot_cooldown = 1700 # cooldown para o inimigo atacar

        # other
        self.angle = 0
        self.hurt_sfx = pygame.mixer.Sound('audio/effects/enemy_hurt.mp3')
        self.hurt_sfx.set_volume(0)
        self.channel = None

    def update(self, screen, player, blts):
        curr_time = pygame.time.get_ticks()

        self.look_player(player)
        self.move()
        self.show_life(screen)

        if curr_time - self.last_shot > self.shoot_cooldown and self.action == 'pursuing':
            blts.append(self.gun.shoot(enemy=True))
            self.last_shot = curr_time

        self.animate(screen)

        self.gun.update_enemy(self, screen, player)

        # Detecta se leva dano
        if self.last_life != self.life:
            self.hurt_sound()
            self.last_life = self.life

    def animate(self, screen):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_update >= self.animation_cooldown:
            if self.action == 'idle':
                max_frame = len(self.idle_animation) - 1
            elif self.action == 'pursuing':
                max_frame = len(self.running_animation) - 1 

            # se mudar de estado reinicia o frame
            if self.last_action != self.action or self.frame + 1 == max_frame:
                self.frame = 0
                self.last_action = self.action
            else:
                self.frame += 1

            self.last_update = current_time

        # Muda entre animações
        if self.action == 'idle':
            if self.gun.hand == 'right':
                blit_image = self.idle_animation[self.frame]
            else:
                blit_image = pygame.transform.flip(self.idle_animation[self.frame], True, False).convert_alpha()
        elif self.action == 'pursuing':
            if self.gun.hand == 'right':
                blit_image = self.running_animation[self.frame]
            else:
                blit_image = pygame.transform.flip(self.running_animation[self.frame], True, False).convert_alpha()

        screen.blit(blit_image, (self.rect.x - camera.x, self.rect.y - camera.y))

    def hurt_sound(self):
        self.hurt_sfx.set_volume(max(0, (5 - self.dist//100)/10))
        if self.channel is None or not self.channel.get_busy():
            self.channel = self.hurt_sfx.play()

    def angle_difference(self, a, b):
        """Smallest difference between two angles (in radians)."""
        diff = (b - a + math.pi) % (2 * math.pi) - math.pi
        return diff

    def look_player(self, plr):
        # calcula a distância entre o jogador e o inimigo
        dist_x = plr.rect.centerx - self.rect.centerx
        dist_y = plr.rect.centery - self.rect.centery
        self.dist = (dist_x ** 2 + dist_y ** 2) ** 0.5

        # Área de agressão 
        if self.dist < 600: 
            self.action = 'pursuing'
        else:
            self.action = 'idle'

        if self.dist >= 200:
            # calcula o ângulo entre o inimigo e o player
            target_angle = math.atan2(dist_y, dist_x)
        elif self.dist < 200:
            target_angle = math.atan2(dist_y, dist_x)
            target_angle += math.radians(90)

        """Returns a new angle rotated toward target_angle by max_turn_speed."""
        diff = self.angle_difference(self.angle, target_angle)

        vel_rotacao = math.radians(2.5)
        
        # Clamp the angle change to max_turn_speed
        if abs(diff) < vel_rotacao:
            self.angle = target_angle
        else:
            self.angle = self.angle + vel_rotacao * math.copysign(1, diff)

    def move(self):
        cos = math.cos(self.angle)
        sin = math.sin(self.angle)


        # movimenta o inimigo se o player estiver dentro do alcance
        if self.action == 'pursuing': 
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y    
            if self.dist < 180:
                self.speed_x -= self.acc * cos
                self.speed_y -= self.acc * sin
            else:
                self.speed_x += self.acc * cos
                self.speed_y += self.acc * sin

        # desacelera o inimigo
        if self.speed_x > 0.01 or self.speed_x < -0.01:
            self.speed_x *= 0.9
        else:
            self.speed_x = 0
        if self.speed_y > 0.01 or self.speed_y < -0.01:
            self.speed_y *= 0.9
        else:
            self.speed_y = 0

    def get_hits(self, enemies):
        hits = []
        for enemy in enemies:
            if self.rect.colliderect(enemy) and enemy != self:
                hits.append(enemy)
        return hits

    def check_collisions(self, enemies):
        collisions = self.get_hits(enemies)
        for enemy in collisions:
            # horizontal
            if enemy.speed_x > 0 and self.rect.centerx > enemy.rect.centerx:
                enemy.speed_x = -3
                enemy.action = 'idle'
            elif enemy.speed_x < 0 and self.rect.centerx < enemy.rect.centerx:
                enemy.speed_x = 3
                enemy.action = 'idle'
            # Vertical
            if enemy.speed_y > 0 and self.rect.centery > enemy.rect.centery:
                enemy.speed_y = -3
                enemy.action = 'idle'
            elif enemy.speed_x < 0 and self.rect.centery < enemy.rect.centery:
                enemy.speed_y = 3
                enemy.action = 'idle'


    def show_life(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x - camera.x, self.rect.y - camera.y - 16, self.rect.width, 10))
        pygame.draw.rect(screen, (255, 255, 0), (self.rect.x - camera.x, self.rect.y - 16 - camera.y, self.rect.width * (self.life/self.max_life), 10))


class Boss1():
    def __init__(self, image, animation_steps, animation_cooldown, life, scale):
        #status
        self.max_life = life
        self.life = life
        self.acc = 0.5
        self.speed_x = 0
        self.speed_y = 0
        self.invincible = False

        # movimentação
        self.action = 'walking'
        self.direction = 0 # direção de movimento
        self.change_cooldown = 1900 # tempo máximo andando para uma direção
        self.last_change = pygame.time.get_ticks()
        self.collided = False

        # ataques (2 ataques, um mirando no player e outro em circulo)
        self.sml_blt_image = pygame.image.load('Img/other/boss_blt.png')
        self.blt_image = pygame.transform.scale(self.sml_blt_image, (25, 25))
        self.blt_speed = 5
        self.blt_time = 500
        self.damage = 20
        self.cirlce_atk_cooldown = 2500
        self.last_circle_atk = pygame.time.get_ticks()
        self.plr_atk_cooldown = 700
        self.last_plr_atk = pygame.time.get_ticks()
        self.blts = []
        self.angle = 0 # mira para o player

        # animação
        self.sprite_sheet = SpriteSheet(image)
        self.animation_list = self.sprite_sheet.get_animations(animation_steps, 30, 34, scale)
        self.animation_cooldown = animation_cooldown
        self.last_update = pygame.time.get_ticks()
        self.idle_animation_list = self.animation_list[0]
        self.walking_animation_list = self.animation_list[1]
        self.frame = 0

        self.rect = self.animation_list[0][0].get_rect()
        self.rect.x, self.rect.y = (800, 700)
        
    def update(self, screen, player, blt_list):
        current_time = pygame.time.get_ticks()

        if self.life > 0:
            if not self.action == 'idle':
                # Movimentação
                self.look_player(player)
                
                self.movement()

                # ataques
                if current_time - self.last_circle_atk >= self.cirlce_atk_cooldown:
                    self.circle_atack(blt_list)
                    self.last_circle_atk = current_time
                self.look_player(player) # conseguir o ângulo que o boss deve mirar
                if current_time - self.last_plr_atk >= self.plr_atk_cooldown:
                    self.plr_atack(blt_list)
                    self.last_plr_atk = current_time

            self.animate(screen)

    def animate(self, screen):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time

        if self.action == 'idle':
            if self.frame == len(self.idle_animation_list):
                self.frame = 0
            if self.angle >= -1.5 and self.angle < 1.5:
                screen.blit(self.idle_animation_list[self.frame], (self.rect.x - camera.x, self.rect.y - camera.y))
            else:
                fliped_image = pygame.transform.flip(self.idle_animation_list[self.frame], True, False).convert_alpha()
                screen.blit(fliped_image, (self.rect.x - camera.x, self.rect.y - camera.y))

        elif self.action == 'walking':
            if self.frame == len(self.walking_animation_list) - 1:
                self.frame = 0
            
            if self.angle >= -1.5 and self.angle < 1.5:
                screen.blit(self.walking_animation_list[self.frame], (self.rect.x - camera.x, self.rect.y - camera.y))
            else:
                fliped_image = pygame.transform.flip(self.walking_animation_list[self.frame], True, False).convert_alpha()
                screen.blit(fliped_image, (self.rect.x - camera.x, self.rect.y - camera.y))


    def look_player(self, plr):
        dist_x = self.rect.centerx - plr.rect.centerx
        dist_y = self.rect.centery - plr.rect.centery
        self.angle = math.atan2(-dist_y, -dist_x) # em radianos

    def change_direction(self, curr_time):
        if curr_time - self.last_change >= self.change_cooldown or self.collided:
            if int(self.direction) in range(int(math.radians(-135)), int(math.radians(45))):
                self.direction = math.radians(randrange(46, 180))

            else:
                self.direction = math.radians(randrange(-135, 45))

            self.last_change = curr_time
            self.collided = False

        return math.cos(self.direction), math.sin(self.direction)
        
    def movement(self):
        current_time = pygame.time.get_ticks()
        cos, sin = self.change_direction(current_time)

        # Atualiza a velocidade do boss
        self.speed_x += self.acc * cos
        self.speed_y += self.acc * sin 

        # Movimenta o boss
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # desacelera o boss
        if self.speed_x > 0.01 or self.speed_x < -0.01:
            self.speed_x *= 0.9
        else:
            self.speed_x = 0
        if self.speed_y > 0.01 or self.speed_y < -0.01:
            self.speed_y *= 0.9
        else:
            self.speed_y = 0

    def circle_atack(self, blt_list):
        for i in range(16):
            # calcula o ângulo da bala junto do seno e cosseno
            angle = 22.5 * i
            radians = math.radians(angle)
            cos = math.cos(radians)
            sin = math.sin(radians)

            # retângulo da bala
            blt_rect = self.blt_image.get_rect()
            blt_rect.centery = self.rect.bottom - self.rect.height//3
            if self.angle >= -1.5 and self.angle < 1.5:
                blt_rect.centerx = self.rect.right
            else:
                blt_rect.centerx = self.rect.left

            blt_list.append(Blt( # adiciona a bala na lista de balas
                self.blt_image,
                blt_rect,
                self.blt_speed * cos,
                self.blt_speed * sin,
                self.blt_time,
                self.damage,  
                True  
            )) 

    def plr_atack(self, blt_list):
        # cosseno e seno do ângulo atual
        cos = math.cos(self.angle)
        sin = math.sin(self.angle)

        blt_rect = self.blt_image.get_rect()
        blt_rect.centery = self.rect.bottom - self.rect.height//3
        if self.angle >= -1.5 and self.angle < 1.5:
            blt_rect.centerx = self.rect.right
        else:
            blt_rect.centerx = self.rect.left

        blt_list.append(Blt( # adiciona a bala na lista de balas
                self.blt_image,
                blt_rect,
                self.blt_speed * cos,
                self.blt_speed * sin,
                self.blt_time,
                self.damage,  
                True  
            ))

    def show_life(self, screen):
        pygame.draw.rect(screen, (70, 70, 70), (camera.width/8, camera.height*7/8, camera.width*6/8, 40))
        pygame.draw.rect(screen, (255, 50, 30), (camera.width/8, camera.height*7/8, (camera.width*6/8) * self.life/self.max_life, 40))
