import pygame
import math
from camera import camera

EQUIP_EVENT = pygame.USEREVENT + 1
DEQUIP_EVENT = pygame.USEREVENT + 2 

class Gun():
    def __init__(self,x, y, ammo):
        self.surface = pygame.surface.Surface((30, 10), pygame.SRCALPHA)
        self.surface.fill((50, 200, 255))
        self.rect = self.surface.get_rect()
        self.rect.center = (x, y)
        self.ammo = ammo
        self.equiped = False
        self.angle = 0
        self.blts = []
        self.blt_speed = 8
        self.x = (0, 0, 0)  # Track previous mouse state

    def update(self, plr, screen):
        keys_pressed = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        if self.equiped == False:
            screen.blit(self.surface, (self.rect.x - camera.x, self.rect.y - camera.y))

            if self.rect.colliderect(plr):
                if keys_pressed[pygame.K_e] and plr.equiped == False:
                    self.equiped = True
                    pygame.event.post(pygame.event.Event(EQUIP_EVENT))

        else:
            if keys_pressed[pygame.K_q] and plr.equiped == True:
                self.equiped = False
                pygame.event.post(pygame.event.Event(DEQUIP_EVENT))

            # Detecta se o jogador está apontando para direita ou esquerda
            if self.angle > 90 or self.angle < -90:
                self.rect.centerx = plr.rect.centerx - (plr.rect.width // 2)
                self.rect.centery = plr.rect.centery
            else:
                self.rect.centerx = plr.rect.centerx + (plr.rect.width // 2)
                self.rect.centery = plr.rect.centery

            pos_x, pos_y = pygame.mouse.get_pos()

            if keys_pressed[pygame.K_t]:
                print([pos_x, pos_y, self.rect])

            # Calcular o ângulo do mouse comparado com a arma
            dx = pos_x - self.rect.centerx + camera.x
            dy = pos_y - self.rect.centery + camera.y
            self.angle = math.degrees(math.atan2(-dy, dx))

            self.rotated_surface = pygame.transform.rotate(self.surface, self.angle)
            self.rotated_rect = self.rotated_surface.get_rect(center=self.rect.center)
            screen.blit(self.rotated_surface, (self.rotated_rect.x - camera.x, self.rotated_rect.y - camera.y))

        for bullet in self.blts:
            bullet.get("rect").x += bullet.get("speed_x")
            bullet.get("rect").y += bullet.get("speed_y")

            #TODO: Criar uma cor para a balaa
            screen.blit(bullet.get("surface"), (bullet.get("rect").x - camera.x, bullet.get("rect").y - camera.y))

        if mouse_buttons[0] and self.prev_mouse_buttons[0] == 0:
            self.shoot()

        self.prev_mouse_buttons = mouse_buttons

    def shoot(self):
        if self.equiped == True:

            #criando a bala e transformando para ficar com o ângulo correto
            bullet_surface = pygame.surface.Surface((10, 4), pygame.SRCALPHA)
            bullet_surface.fill((255, 0, 0))
            bullet_surface_r = pygame.transform.rotate(bullet_surface, self.angle)
            bullet = bullet_surface_r.get_rect()
            bullet.x, bullet.y = self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2
        
            #calcula a velocidade y e x da bala 
            radians = math.radians(-self.angle)
            cos_mouse = math.cos(radians)
            sin_mouse = math.sin(radians)
            
            bullet_info = {
                "surface": bullet_surface_r,
                "rect": bullet,
                "speed_x": self.blt_speed * cos_mouse,
                "speed_y": self.blt_speed * sin_mouse
            }
            self.blts.append(bullet_info)

class Laser_gun():
    def __init__(self,x, y, ammo):
        self.surface = pygame.surface.Surface((30, 10), pygame.SRCALPHA)
        self.surface.fill((50, 100, 120))
        self.rect = self.surface.get_rect()
        self.rect.center = (x, y)
        self.ammo = ammo
        self.curr_ammo = ammo
        self.overheat_timer = 0
        self.equiped = False
        self.angle = 0
        self.laser = {}

    def update(self, plr, screen):
        keys_pressed = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        if self.equiped == False:
            screen.blit(self.surface, (self.rect.x - camera.x, self.rect.y - camera.y))

            if self.rect.colliderect(plr):
                if keys_pressed[pygame.K_e] and plr.equiped == False:
                    self.equiped = True
                    pygame.event.post(pygame.event.Event(EQUIP_EVENT))


        else:
            if keys_pressed[pygame.K_q] and plr.equiped == True:
                self.equiped = False
                pygame.event.post(pygame.event.Event(DEQUIP_EVENT))

            pos_x, pos_y = pygame.mouse.get_pos()

            if keys_pressed[pygame.K_t]:
                print([pos_x, pos_y, self.rect])

            # Calcular o ângulo do mouse comparado com a arma
            dx = pos_x - self.rect.centerx + camera.x
            dy = pos_y - self.rect.centery + camera.y
            self.angle = math.degrees(math.atan2(-dy, dx))

            # Criar a superficie e o retângulo da arma
            self.rotated_surface = pygame.transform.rotate(self.surface, self.angle)
            self.rotated_rect = self.rotated_surface.get_rect(center=self.rect.center)
            screen.blit(self.rotated_surface, (self.rotated_rect.x - camera.x, self.rotated_rect.y - camera.y))
    
            # Detecta se o jogador está apontando para direita ou esquerda
            if self.angle > 90 or self.angle < -90:
                self.rect.centerx = plr.rect.centerx - (plr.rect.width // 2)
                self.rect.centery = plr.rect.centery
            else:
                self.rect.centerx = plr.rect.centerx + (plr.rect.width // 2)
                self.rect.centery = plr.rect.centery

            # Laser pode atirar até acabar a munição e arma sobreaquece
            if self.laser:
                if self.curr_ammo > 0 and self.overheat_timer == 0:
                    screen.blit(self.laser.get('surface'), self.laser.get('rect'))
                    self.curr_ammo -= 1
                else:
                    self.overheat_timer = 60
                    
            if mouse_buttons[0]:
                self.firing()
            else:
                self.laser = {}

            # Desenha a munição da arma
            pygame.draw.rect(screen, (255, 0, 0), (50, 50, self.ammo, 20))
            pygame.draw.rect(screen, (0, 255, 0), (50, 50, self.curr_ammo, 20))
            # avisa caso esteja em overheat
            if self.overheat_timer:
                pygame.draw.rect(screen, (255, 0, 0), (60, 10, 60, 20))
                pygame.draw.rect(screen, (255, 255, 0), (60, 10, self.overheat_timer, 20))

        
        # Recarrega enquanto a munição é menor que a munição máxima e não está atirando
        if self.curr_ammo < self.ammo and not self.laser:
            self.curr_ammo += 1
            
        # Se a arma sobreaqueceu diminui o timer do sobreaquecimento
        if self.overheat_timer > 0:
            self.overheat_timer -= 1
            self.laser = {}

    def firing(self):
        if self.equiped == True:

            # definindo Tamanho do laser
            pos_x, pos_y = pygame.mouse.get_pos()
            dx = pos_x - self.rect.centerx + camera.x
            dy = pos_y - self.rect.centery + camera.y
            laser_length = (dx ** 2 + dy ** 2) ** 0.5

            #criando o laser com o ângulo
            laser_surface = pygame.surface.Surface((laser_length , 4), pygame.SRCALPHA)
            laser_surface.fill((255, 255, 0))
            laser_surface_rotated = pygame.transform.rotate(laser_surface, self.angle)
            laser = laser_surface_rotated.get_rect()
            
            # Lógica para o laser ficar na posição correta
            if self.angle < -90:
                laser.x, laser.y = self.rect.centerx - camera.x + dx, self.rect.centery - camera.y
            elif self.angle > 0 and self.angle < 90:
                laser.x, laser.y = self.rect.centerx - camera.x, self.rect.centery - camera.y + dy
            elif self.angle > 90:
                laser.x, laser.y = self.rect.centerx - camera.x + dx, self.rect.centery - camera.y + dy
            else:
                laser.x, laser.y = self.rect.centerx - camera.x, self.rect.centery - camera.y

            # laser.center = (self.rect.centerx - camera.x, self.rect.centery - camera.y)

            self.laser = {
                "surface": laser_surface_rotated,
                "rect": laser,
            }
            