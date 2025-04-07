import pygame
import math

from guns import Gun
from camera import camera

class Enemy():
    def __init__(self, x, y, image, life, ammo, acc):
        self.surface = pygame.surface.Surface((50, 50)) # temporário até ter um sprite 
        self.surface.fill((80, 190, 255))
        # self.image = pygame.image.load(image)
        self.rect = self.surface.get_rect()
        self.rect.x, self.rect.y = x, y

        # Enemy status
        self.max_life = life
        self.life = life
        self.ammo = ammo
        self.curr_ammo = ammo
        self.acc = acc
        self.speed_x = 0
        self.speed_y = 0

        # movement
        self.anchor1 = ()
        self.anchor2 = ()
        self.anchor3 = ()
        self.anchor4 = ()

        self.action = 'idle'

        # arma do inimigo
        self.gun = Gun(self.rect.x, self.rect.y, 30, 'Img/Armas/Arma_Soldado_inimigo.png', 8, 80, 20, False)
        self.gun.equiped = True
        self.last_shot = pygame.time.get_ticks()
        self.shoot_cooldown = 1700 # cooldown para o inimigo atacar

        # other
        self.angle = 0

    def update(self, screen, player):
        curr_time = pygame.time.get_ticks()

        self.look_player(player)
        self.move()
        self.show_life(screen)

        if curr_time - self.last_shot > self.shoot_cooldown and self.action == 'pursuing':
            self.gun.shoot(enemy=True)
            self.last_shot = curr_time

        screen.blit(self.surface, (self.rect.x - camera.x, self.rect.y- camera.y))

        self.gun.update_enemy(self, screen, player)

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

    def show_life(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x - camera.x, self.rect.y - camera.y - 16, self.rect.width, 10))
        pygame.draw.rect(screen, (255, 255, 0), (self.rect.x - camera.x, self.rect.y - 16 - camera.y, self.rect.width * (self.life/self.max_life), 10))


class Boss1():
    def __init__(self, image):
        self.surface = pygame.surface.Surface((80, 80)) # temporário até ter um sprite 
        self.surface.fill((255, 50, 50))
        # self.image = pygame.image.load(image) 
        self.rect = self.surface.get_rect()
        self.rect.x, self.rect.y = (900, 400)

        #status
        self.max_life = 600
        self.life = 600
        self.acc = 1.5
        self.speed_x = 0
        self.speed_y = 0

        # movimentação
        self.anchors = []
        self.action = 'anything'

        # ataques (2 ataques, um mirando no player e outro em circulo)
        self.sml_blt_image = pygame.image.load('Img/other/boss_blt.png')
        self.blt_image = pygame.transform.scale(self.sml_blt_image, (25, 25))
        self.blt_speed = 5
        self.blt_time = 300
        self.cirlce_atk_cooldown = 2000
        self.last_circle_atk = pygame.time.get_ticks()
        self.plr_atk_cooldown = 500
        self.last_plr_atk = pygame.time.get_ticks()
        self.blts = []

        self.angle = 0 # mira para o player
        self.direction = 0 # direção de movimento

    def update(self, screen, player):
        current_time = pygame.time.get_ticks()

        if self.life > 0:
            if not self.action == 'idle':
                # ataques
                if current_time - self.last_circle_atk >= self.cirlce_atk_cooldown:
                    self.circle_atack()
                    self.last_circle_atk = current_time
                self.look_player(player) # conseguir o ângulo que o boss deve mirar
                if current_time - self.last_plr_atk >= self.plr_atk_cooldown:
                    self.plr_atack()
                    self.last_plr_atk = current_time
                self.handle_blts(screen)
                self.check_collision(player)

            screen.blit(self.surface, (self.rect.x - camera.x, self.rect.y- camera.y))
            self.show_life(screen)
        

    def look_player(self, plr):
        dist_x = self.rect.centerx - plr.rect.centerx
        dist_y = self.rect.centery - plr.rect.centery
        self.angle = math.atan2(-dist_y, -dist_x) # em radianos

    def handle_blts(self, screen):
        for blt in self.blts:
            blt.get('rect').x += blt.get('speed_x')
            blt.get('rect').y += blt.get('speed_y')

            screen.blit(blt.get('image'), (blt.get('rect').x - camera.x, blt.get('rect').y - camera.y))

            if blt.get('time_to_live'):
                blt['time_to_live'] -= 1
            else:
                self.blts.remove(blt)

    def circle_atack(self):
        for i in range(16):
            # calcula o ângulo da bala junto do seno e cosseno
            angle = 22.5 * i
            radians = math.radians(angle)
            cos = math.cos(radians)
            sin = math.sin(radians)

            # retângulo da bala
            blt_rect = self.blt_image.get_rect()
            blt_rect.centerx, blt_rect.centery = self.rect.centerx, self.rect.centery

            # informações da bala
            blt_temp = {
                'image': self.blt_image,
                'rect': blt_rect,
                'speed_x': self.blt_speed * cos,
                'speed_y': self.blt_speed * sin,
                'time_to_live': self.blt_time,
            }
            self.blts.append(blt_temp) # adiciona a bala na lista do boss

    def plr_atack(self):
        # cosseno e seno do ângulo atual
        cos = math.cos(self.angle)
        sin = math.sin(self.angle)

        blt_rect = self.blt_image.get_rect()
        blt_rect.centerx, blt_rect.centery = self.rect.centerx, self.rect.centery

        blt = {
            'image': self.blt_image,
            'rect': blt_rect,
            'speed_x': self.blt_speed * cos,
            'speed_y': self.blt_speed * sin,
            'time_to_live': self.blt_time,
        }
        print(blt)
        self.blts.append(blt)

    def check_collision(self, plr):
        for blt in self.blts:
            if blt.get('rect').colliderect(plr.rect):
                self.blts.remove(blt)
                plr.life -= 30

        if plr.weapon:
            plr.weapon.check_collision(self)

    def show_life(self, screen):
        pygame.draw.rect(screen, (70, 70, 70), (camera.width/8, camera.height*7/8, camera.width*6/8, 40))
        pygame.draw.rect(screen, (255, 50, 30), (camera.width/8, camera.height*7/8, (camera.width*6/8) * self.life/self.max_life, 40))
