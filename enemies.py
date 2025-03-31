import pygame
from camera import camera
import math
from guns import Gun

class Enemy():
    def __init__(self, x, y, image, life, ammo, acc):
        self.surface = pygame.surface.Surface((50, 50))
        self.surface.fill((80, 190, 255))
        self.rect = self.surface.get_rect()
        self.rect.x, self.rect.y = x - camera.x, y - camera.y

        # Enemy status
        self.life = life
        self.ammo = ammo
        self.curr_ammo = ammo
        self.acc = acc
        self.speed_x = 0
        self.speed_y = 0

        self.action = 'idle'

        # arma do inimigo
        self.gun = Gun(self.rect.x, self.rect.y, 30, 'Img/Armas/Arma_Soldado_inimigo.png', 12, 80, 20, False)
        self.gun.equiped = True
        self.last_shot = pygame.time.get_ticks()
        self.shoot_cooldown = 1700 # cooldown para o inimigo atacar

        # other
        self.angle = 0

    def update(self, screen, player):
        curr_time = pygame.time.get_ticks()

        self.look_player(player)
        self.move()

        if curr_time - self.last_shot > self.shoot_cooldown:
            self.gun.shoot()
            self.last_shot = curr_time

        screen.blit(self.surface, (self.rect.x - camera.x, self.rect.y- camera.y))

        self.gun.update_enemy(self, screen, player)

    def look_player(self, plr):
        # calcula a distância entre o jogador e o inimigo
        dist_x = plr.rect.centerx - self.rect.centerx
        dist_y = plr.rect.centery - self.rect.centery
        self.dist = (dist_x ** 2 + dist_y ** 2) ** 0.5

        # calcula o ângulo entre o inimigo e o player
        radians = math.atan2(dist_y, dist_x)
        self.angle = math.degrees(radians)

    def move(self):
        radians = math.radians(self.angle)
        cos = math.cos(radians)
        sin = math.sin(radians)
        
        if self.dist < 350: 
            self.action = 'persuing'
        else:
            self.action = 'idle'

        # movimenta o inimigo se o player estiver dentro do alcance
        if self.action == 'persuing': 
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            if self.dist > 200:
                self.speed_x += self.acc * cos
                self.speed_y += self.acc * sin
            elif self.dist >= 195 and self.dist <= 200:
                self.speed_x *= 0.6
                self.speed_y *= 0.6
            else:
                self.speed_x -= self.acc * cos
                self.speed_y -= self.acc * sin

        # desacelera o inimigo
        if self.speed_x > 0.01 or self.speed_x < -0.01:
            self.speed_x *= 0.9
        else:
            self.speed_x = 0
        if self.speed_y > 0.01 or self.speed_y < -0.01:
            self.speed_y *= 0.9
        else:
            self.speed_y = 0