import pygame
from camera import camera
import math
from guns import Gun

class Enemy():
    def __init__(self, x, y, image, life, ammo, acc):
        self.surface = pygame.surface.Surface((50, 50))
        self.surface.fill((80, 190, 255))
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
        if self.dist < 500: 
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
            print(self.dist)

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
