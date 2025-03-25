import pygame
import math
from camera import camera

EQUIP_EVENT = pygame.USEREVENT + 1
DEQUIP_EVENT = pygame.USEREVENT + 2 

class Gun():
    def __init__(self,x, y, ammo, image, blt_speed, recharge_time):
        # surface e rectangle
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        #munições
        self.ammo = ammo
        self.curr_ammo = ammo
        self.blts = []
        self.blt_speed = blt_speed
        self.blt_time = 150
        self.recharge_time = recharge_time
        self.recharge = False

        # outros
        self.angle = 0
        self.equiped = False
        self.x = (0, 0, 0)  # Track previous mouse state
        self.hand = 'right'

    def update(self, plr, screen):
        keys_pressed = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        if self.equiped == False:
            screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y)) # desenha a arma jogada no chão

            if self.rect.colliderect(plr):
                if keys_pressed[pygame.K_e] and plr.equiped == False: # evento para equipar a arma
                    self.equiped = True
                    pygame.event.post(pygame.event.Event(EQUIP_EVENT))

        else:
            if keys_pressed[pygame.K_q] and plr.equiped == True: # evento para desequipar a arma
                self.equiped = False
                pygame.event.post(pygame.event.Event(DEQUIP_EVENT))

            # Posição do mouse    
            pos_x, pos_y = pygame.mouse.get_pos()

            # Calcular o ângulo do mouse comparado com a arma
            dist_x = pos_x - self.rect.centerx + camera.x
            dist_y = pos_y - self.rect.centery + camera.y
            self.angle = math.degrees(math.atan2(-dist_y, dist_x))

            self.draw_gun(screen, plr)

            # Lógica para atirar
            if mouse_buttons[0] and self.prev_mouse_buttons[0] == 0 and self.curr_ammo > 0 and self.recharge == False:
                self.shoot()
                self.curr_ammo -= 1

            # Recarregar arma
            if keys_pressed[pygame.K_r] and self.recharge == False and self.curr_ammo != self.ammo:
                self.recharge = True

        if self.recharge == True:
            self.recharging()

        self.handle_bullets(screen)

        self.prev_mouse_buttons = mouse_buttons

    def shoot(self):
        if self.equiped == True:

            #criando a bala e transformando para ficar com o ângulo correto
            bullet_surface = pygame.surface.Surface((10, 4), pygame.SRCALPHA)
            bullet_surface.fill((255, 0, 0))
            rotated_bullet_surface = pygame.transform.rotate(bullet_surface, self.angle)
            bullet = rotated_bullet_surface.get_rect()
            bullet.x, bullet.y = self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 4
        
            #calcula a velocidade y e x da bala 
            radians = math.radians(-self.angle)
            cos_mouse = math.cos(radians)
            sin_mouse = math.sin(radians)
            
            bullet_info = {
                "surface": rotated_bullet_surface,
                "rect": bullet,
                "speed_x": self.blt_speed * cos_mouse,
                "speed_y": self.blt_speed * sin_mouse,
                "time_to_live": self.blt_time
            }
            self.blts.append(bullet_info)

    def handle_bullets(self, screen):
        for bullet in self.blts:
            bullet.get("rect").x += bullet.get("speed_x")
            bullet.get("rect").y += bullet.get("speed_y")

            #TODO: Criar uma cor para a balaa
            screen.blit(bullet.get("surface"), (bullet.get("rect").x - camera.x, bullet.get("rect").y - camera.y))

            # Diminui tempo de vida da bala e remove se acabar
            if bullet.get("time_to_live"):
                bullet["time_to_live"] -= 1
            else:
                self.blts.remove(bullet)

    def recharging(self):
        if self.recharge_time:
            self.recharge_time -= 1
        else:
            self.curr_ammo = self.ammo
            self.recharge_time = 80
            self.recharge = False    
            

    def draw_ammo(self, screen):
        # Desenha a munição da arma
        pygame.draw.rect(screen, (255, 0, 0), (50, 50, self.ammo, 20))
        pygame.draw.rect(screen, (0, 255, 0), (50, 50, self.curr_ammo, 20))

    def draw_gun(self, screen, plr):
        pos_x, pos_y = pygame.mouse.get_pos()

        if pos_x <= plr.rect.x - camera.x:
            self.hand = 'left'
        elif pos_x >= plr.rect.x + plr.rect.width  - camera.x:
            self.hand = 'right'

        # Detecta se o jogador está apontando para direita ou esquerda
        if self.hand == 'left':
            self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
            self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)
            self.fliped_image = pygame.transform.flip(self.rotated_image, False, True)

            self.rect.centerx = plr.rect.centerx - (plr.rect.width // 2)
            self.rect.centery = plr.rect.centery

            screen.blit(self.fliped_image, (self.rotated_rect.x - camera.x, self.rotated_rect.y - camera.y))
        elif self.hand == 'right':
            self.rotated_image = pygame.transform.rotate(self.image, self.angle)
            self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)

            self.rect.centerx = plr.rect.centerx + (plr.rect.width // 2)
            self.rect.centery = plr.rect.centery

            screen.blit(self.rotated_image, (self.rotated_rect.x - camera.x, self.rotated_rect.y - camera.y))


#------------------Arma Laser------------------------------------------
class Laser_gun():
    def __init__(self,x, y, ammo, image, scale):
        # superfície e retângulo
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.gun_radius = self.rect.width

        # munição
        self.ammo = ammo
        self.curr_ammo = ammo
        self.overheat_timer = 0
        

        # outras coisas da arma
        self.equiped = False
        self.angle = 0
        self.hand = 'right'


    def update(self, plr, screen):
        keys_pressed = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        # arma não equipada
        if self.equiped == False:
            screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

            if self.rect.colliderect(plr):
                if keys_pressed[pygame.K_e] and plr.equiped == False:
                    self.equiped = True
                    pygame.event.post(pygame.event.Event(EQUIP_EVENT))

        # arma equipada
        else:
            if keys_pressed[pygame.K_q] and plr.equiped == True:
                self.equiped = False
                pygame.event.post(pygame.event.Event(DEQUIP_EVENT))
            
            # calcula o ângulo da arma (com math)
            # dist_x = pos_x - self.rect.centerx + camera.x
            # dist_y = pos_y - self.rect.centery + camera.y
            # self.angle = math.degrees(math.atan2(-dist_y, dist_x))

            self.get_angle() # usando Vector2
    
            self.draw_gun(screen, plr)
                
            # lógica para atirar
            if mouse_buttons[0] and self.overheat_timer == 0:
                if self.curr_ammo > 0:
                    pygame.draw.line(screen, (255, 255, 0), *self.get_laser_pos(), 3)
                    self.curr_ammo -= 1
                else:
                    self.overheat_timer = 60


        
        # Recarrega enquanto a munição é menor que a munição máxima e não está atirando
        if (self.curr_ammo < self.ammo and not mouse_buttons[0]) or self.overheat_timer:
            self.curr_ammo += 1
            
        # Se a arma sobreaqueceu diminui o timer do sobreaquecimento
        if self.overheat_timer > 0:
            self.overheat_timer -= 1
            self.laser = {}

    def get_angle(self):
        # calcula o ângulo da arma (com pygame.Vector2)
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())  # Get raw mouse position
        gun_pos = pygame.Vector2((self.rect.centerx - camera.x, self.rect.centery - camera.y))

        direction = mouse_pos - gun_pos  # Vector from player to mouse
        if direction.length() > 0:
            self.angle = direction.angle_to(pygame.Vector2(1, 0))

    def draw_gun(self, screen, plr):
        pos_x, pos_y = pygame.mouse.get_pos()

        if pos_x <= plr.rect.x - camera.x:
            self.hand = 'left'
        elif pos_x >= plr.rect.x + plr.rect.width  - camera.x:
            self.hand = 'right'

        # Detecta se o jogador está apontando para direita ou esquerda
        if self.hand == 'left':
            self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
            self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)
            # inverte a arma para ficar na posição certa do lado contrário
            self.fliped_image = pygame.transform.flip(self.rotated_image, False, True)

            # Define o centro da arma
            self.rect.centerx = plr.rect.x
            self.rect.centery = plr.rect.centery

            screen.blit(self.fliped_image, (self.rotated_rect.x - camera.x, self.rotated_rect.y - camera.y))
        elif self.hand == 'right':
            self.rotated_image = pygame.transform.rotate(self.image, self.angle)
            self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)

            self.rect.centerx = plr.rect.x + plr.rect.width
            self.rect.centery = plr.rect.centery

            screen.blit(self.rotated_image, (self.rotated_rect.x - camera.x, self.rotated_rect.y - camera.y))

    def draw_ammo(self, screen):
        # Desenha a munição da arma
        pygame.draw.rect(screen, (255, 0, 0), (50, 50, self.ammo, 20))
        pygame.draw.rect(screen, (0, 255, 0), (50, 50, self.curr_ammo, 20))

        # avisa caso esteja em overheat
        if self.overheat_timer:
            pygame.draw.rect(screen, (255, 0, 0), (60, 10, 60, 20))
            pygame.draw.rect(screen, (255, 255, 0), (60, 10, self.overheat_timer, 20))

    def get_laser_pos(self):
        pos_x, pos_y = pygame.mouse.get_pos()
        
        #calcula a ponta do laser
        laser_tip_x = pos_x
        laser_tip_y = pos_y

        #calcula a ponta da arma de onde deveria sair o laser usando seno e cosseno
        radians = math.radians(self.angle)
        laser_start_x = self.rect.centerx + (self.rect.width * math.cos(radians)) // 2
        laser_start_y = (self.rect.centery - (self.rect.width * math.sin(radians)) // 2) - self.rect.width // 4
        
        return (laser_start_x - camera.x, laser_start_y - camera.y), (laser_tip_x, laser_tip_y)
    

#--------------------------Basuca--------------------------------------------
class Bazooka():
    def __init__(self,x, y, ammo, image, scale):
        # surface e rectangle
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        #munições
        self.ammo = ammo
        self.curr_ammo = ammo
        self.blts = []
        self.blt_speed = 5
        self.recharge_time = 80
        self.recharge = False

        # outros
        self.angle = 0
        self.equiped = False
        self.x = (0, 0, 0)  # Track previous mouse state
        self.hand = 'right'

    def update(self, plr, screen):
        keys_pressed = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        if self.equiped == False:
            screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y)) # desenha a arma jogada no chão

            if self.rect.colliderect(plr):
                if keys_pressed[pygame.K_e] and plr.equiped == False: # evento para equipar a arma
                    self.equiped = True
                    pygame.event.post(pygame.event.Event(EQUIP_EVENT))

        else:
            if keys_pressed[pygame.K_q] and plr.equiped == True: # evento para desequipar a arma
                self.equiped = False
                pygame.event.post(pygame.event.Event(DEQUIP_EVENT))

            # Posição do mouse    
            pos_x, pos_y = pygame.mouse.get_pos()

            # Calcular o ângulo do mouse comparado com a arma
            # dist_x = pos_x - self.rect.centerx + camera.x
            # dist_y = pos_y - self.rect.centery + camera.y
            # self.angle = math.degrees(math.atan2(-dist_y, dist_x))

            self.get_angle() #calcula o ângulo com vetores

            # Lógica para atirar
            if mouse_buttons[0] and self.prev_mouse_buttons[0] == 0 and self.curr_ammo > 0 and self.recharge == False:
                self.shoot(pos_x, pos_y)
                self.curr_ammo -= 1

            # Recarregar arma
            if keys_pressed[pygame.K_r] and self.recharge == False and self.curr_ammo != self.ammo:
                self.recharge = True

            self.draw_gun(screen, plr)

        if self.recharge == True:
            self.recharging()

        self.handle_bullets(screen)

        self.prev_mouse_buttons = mouse_buttons

    #-----------------munição e balas-------------------------------
    def shoot(self, mouse_x, mouse_y):
        if self.equiped == True:

            #criando a bala e transformando para ficar com o ângulo correto
            bullet_surface = pygame.surface.Surface((19, 10), pygame.SRCALPHA)
            bullet_surface.fill((255, 0, 0))
            rotated_bullet_surface = pygame.transform.rotate(bullet_surface, self.angle)
            bullet = rotated_bullet_surface.get_rect()
            bullet.x, bullet.y = self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 4
        
            #calcula a velocidade y e x da bala 
            radians = math.radians(-self.angle)
            cos_mouse = math.cos(radians)
            sin_mouse = math.sin(radians)
            
            self.blts.append({
                "surface": rotated_bullet_surface,
                "rect": bullet,
                "speed_x": self.blt_speed * cos_mouse,
                "speed_y": self.blt_speed * sin_mouse,
                "explode_point": (mouse_x + camera.x, mouse_y + camera.y),
                "explosion_time": 60
            })

    def handle_bullets(self, screen):
        for bullet in self.blts:
            bullet.get("rect").x += bullet.get("speed_x")
            bullet.get("rect").y += bullet.get("speed_y")

            #TODO: Criar uma cor para a balaa
            screen.blit(bullet.get("surface"), (bullet.get("rect").x - camera.x, bullet.get("rect").y - camera.y))

            x, y = bullet.get("explode_point")

            if bullet["rect"].colliderect(x, y, 50, 50):
                bullet["speed_x"] = 0
                bullet["speed_y"] = 0
                self.explosion(screen, bullet)

            
    def explosion(self, screen, bullet):
        EXPLOSION_SIZE = 70

        if bullet["explosion_time"]:
            pygame.draw.rect(screen, (255, 100, 59), (bullet["rect"].x - EXPLOSION_SIZE//2 - camera.x, bullet["rect"].y - EXPLOSION_SIZE//2 - camera.y, EXPLOSION_SIZE, EXPLOSION_SIZE))
            bullet["explosion_time"] -= 1
        else:
            self.blts.remove(bullet)

    def recharging(self):
        if self.recharge_time:
            self.recharge_time -= 1
        else:
            self.curr_ammo = self.ammo
            self.recharge_time = 80
            self.recharge = False    
            
    def draw_ammo(self, screen):
        # Desenha a munição da arma
        pygame.draw.rect(screen, (255, 0, 0), (50, 50, self.ammo * 5, 20))
        pygame.draw.rect(screen, (0, 255, 0), (50, 50, self.curr_ammo * 5, 20))

    #--------------arma-----------------
    def draw_gun(self, screen, plr):
        pos_x, pos_y = pygame.mouse.get_pos()

        if pos_x <= plr.rect.x - camera.x:
            self.hand = 'left'
        elif pos_x >= plr.rect.x + plr.rect.width  - camera.x:
            self.hand = 'right'

        # Detecta se o jogador está apontando para direita ou esquerda
        if self.hand == 'left':
            self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
            self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)
            self.fliped_image = pygame.transform.flip(self.rotated_image, False, True)

            self.rect.centerx = plr.rect.centerx - (plr.rect.width // 2)
            self.rect.centery = plr.rect.centery

            screen.blit(self.fliped_image, (self.rotated_rect.x - camera.x, self.rotated_rect.y - camera.y))
        elif self.hand == 'right':
            self.rotated_image = pygame.transform.rotate(self.image, self.angle)
            self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)

            self.rect.centerx = plr.rect.centerx + (plr.rect.width // 2)
            self.rect.centery = plr.rect.centery

            screen.blit(self.rotated_image, (self.rotated_rect.x - camera.x, self.rotated_rect.y - camera.y))

    def get_angle(self):
        # calcula o ângulo da arma (com pygame.Vector2)
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())  # Get raw mouse position
        gun_pos = pygame.Vector2((self.rect.centerx - camera.x, self.rect.centery - camera.y))

        direction = mouse_pos - gun_pos  # Vector from player to mouse
        if direction.length() > 0:
            self.angle = direction.angle_to(pygame.Vector2(1, 0))
