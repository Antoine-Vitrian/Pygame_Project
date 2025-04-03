import pygame
import math
from camera import camera
from sprites import *

EQUIP_EVENT = pygame.USEREVENT + 1
DEQUIP_EVENT = pygame.USEREVENT + 2 

class Gun():
    def __init__(self, x, y, ammo, image, blt_speed, recharge_time, shoot_cooldown, auto_shoot):
        # surface e rectangle
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

        #munições
        self.ammo = ammo # munição total
        self.curr_ammo = ammo # munição atual
        self.blts = [] # lista para as balas carregadas
        self.blt_speed = blt_speed # velocidade da bala
        self.blt_time = 150 # tempo de vida da bala
        self.recharge_time = recharge_time #tempo de recarga
        self.curr_recharge_time = recharge_time
        self.recharge = False

        # outros
        self.angle = 0 
        self.equiped = False
        self.x = (0, 0, 0) 
        self.hand = 'right'
        
        # balas
        self.damage = 20
        self.shoot_cooldown = shoot_cooldown
        self.curr_shoot_cooldown = 0
        self.auto_shoot = auto_shoot

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

            self.get_angle((pos_x, pos_y))

            self.draw_gun(screen, plr, (pos_x, pos_y))

            # Lógica para atirar
            if mouse_buttons[0] and (self.prev_mouse_buttons[0] == 0 or self.auto_shoot) and self.curr_ammo > 0 and not self.recharge and not self.curr_shoot_cooldown:
                self.shoot()
                self.curr_ammo -= 1
                self.curr_shoot_cooldown = self.shoot_cooldown

            # Permite o jogador atirar depois de um cooldown
            if self.curr_shoot_cooldown:
                self.curr_shoot_cooldown -= 1

            # Recarregar arma
            if keys_pressed[pygame.K_r] and self.recharge == False and self.curr_ammo != self.ammo and plr.ammo_pack:
                self.recharge = True
                plr.ammo_pack -= 1

        if self.recharge:
            self.recharging(screen)

        self.handle_bullets(screen)

        self.prev_mouse_buttons = mouse_buttons

    def get_angle(self, target, enemy=False):
        pos_x, pos_y = target
        
        if not enemy:
            # Calcular o ângulo do mouse comparado com a arma
            dist_x = pos_x - self.rect.centerx + camera.x
            dist_y = pos_y - self.rect.centery + camera.y
            self.angle = math.degrees(math.atan2(-dist_y, dist_x))
        else:
            # Calcula o ângulo entre a arma e o jogador
            dist_x = pos_x - self.rect.centerx 
            dist_y = pos_y - self.rect.centery 
            self.angle = math.degrees(math.atan2(-dist_y, dist_x))

    def draw_gun(self, screen, holder, target):
        pos_x, pos_y = target

        if pos_x <= holder.rect.x - camera.x:
            self.hand = 'left'
        elif pos_x >= holder.rect.x + holder.rect.width  - camera.x:
            self.hand = 'right'

        # Detecta se o jogador está apontando para direita ou esquerda
        if self.hand == 'left':
            self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
            self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)
            self.fliped_image = pygame.transform.flip(self.rotated_image, False, True)

            self.rect.centerx = holder.rect.centerx - (holder.rect.width // 2)
            self.rect.centery = holder.rect.centery

            screen.blit(self.fliped_image, (self.rotated_rect.x - camera.x, self.rotated_rect.y - camera.y))
        elif self.hand == 'right':
            self.rotated_image = pygame.transform.rotate(self.image, self.angle)
            self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)

            self.rect.centerx = holder.rect.centerx + (holder.rect.width // 2)
            self.rect.centery = holder.rect.centery

            screen.blit(self.rotated_image, (self.rotated_rect.x - camera.x, self.rotated_rect.y - camera.y))


    def shoot(self, enemy=False):
        if self.equiped == True:

            #criando a bala e transformando para ficar com o ângulo correto
            if not enemy:
                bullet_surface = pygame.image.load('Img/other/laser_blt.png')
            else:
                bullet_surface = pygame.image.load('Img/other/enemy_blt.png')
            rotated_bullet_surface = pygame.transform.rotate(bullet_surface, self.angle)
            bullet = rotated_bullet_surface.get_rect()
            bullet.x, bullet.y = self.rect.x + self.rect.width // 2, self.rect.y
        
            #calcula a velocidade y e x da bala 
            radians = math.radians(-self.angle)
            cos = math.cos(radians)
            sin = math.sin(radians)
            
            bullet_info = {
                "surface": rotated_bullet_surface,
                "rect": bullet,
                "speed_x": self.blt_speed * cos,
                "speed_y": self.blt_speed * sin,
                "time_to_live": self.blt_time
            }
            self.blts.append(bullet_info)

    def handle_bullets(self, screen):
        for bullet in self.blts:
            bullet.get("rect").x += bullet.get("speed_x")
            bullet.get("rect").y += bullet.get("speed_y")

            screen.blit(bullet.get("surface"), (bullet.get("rect").x - camera.x, bullet.get("rect").y - camera.y))

            # Diminui tempo de vida da bala e remove se acabar
            if bullet.get("time_to_live"):
                bullet["time_to_live"] -= 1
            else:
                self.blts.remove(bullet)

    def check_collision(self, target):
        for bullet in self.blts:
            if bullet["rect"].colliderect(target):
                target.life -= self.damage
                
                self.blts.remove(bullet)

    def recharging(self, screen):
        if self.curr_recharge_time:
            self.curr_recharge_time -= 1

            # Desenha o cooldown de recarga
            pygame.draw.rect(screen, (80, 80, 80), (50, 80, self.recharge_time, 10))
            pygame.draw.rect(screen, (255, 255, 0), (50, 80, self.curr_recharge_time, 10))
        else:
            self.curr_ammo = self.ammo
            self.curr_recharge_time = self.recharge_time
            self.recharge = False    
            

    def draw_ammo(self, screen):
        # Desenha a munição da arma
        pygame.draw.rect(screen, (80, 80, 80), (50, 50, self.ammo * 3, 20))
        pygame.draw.rect(screen, (0, 200, 255), (50, 50, self.curr_ammo * 3, 20))

    # arma para o inimigo
    def update_enemy(self, enemy, screen, plr):
        self.draw_gun(screen, enemy, (plr.rect.centerx - camera.x, plr.rect.centery - camera.y))
        self.get_angle((plr.rect.centerx, plr.rect.centery), enemy=True)

        self.handle_bullets(screen)

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

        # laser
        self.damage = 0.1
        self.damage_cooldown = 100
        self.last_hit = pygame.time.get_ticks()
        self.shooting = False

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
                    self.shooting = True
                    pygame.draw.line(screen, (255, 255, 0), *self.get_laser_pos(), 3)
                    self.curr_ammo -= 1
                else:
                    self.overheat_timer = 120
            else:
                self.shooting = False
        
        # Recarrega enquanto a munição é menor que a munição máxima e não está atirando
        if (self.curr_ammo < self.ammo and not mouse_buttons[0]) or self.overheat_timer and self.curr_ammo <= self.ammo:
            self.curr_ammo += 1.3
            
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

    def check_collision(self, target):
        if self.shooting == True:
            (laser_ix, laser_iy), (laser_fx, laser_fy) = self.get_laser_pos()

            current_time = pygame.time.get_ticks()

            target_position = pygame.rect.Rect(target.rect.x - camera.x, target.rect.y - camera.y, target.rect.width, target.rect.height)

            for i in range(0, 201):
                px = laser_ix + (laser_fx - laser_ix) * i / 200
                py = laser_iy + (laser_fy - laser_iy) * i / 200
                if target_position.collidepoint(px, py) and current_time - self.last_hit >= self.damage_cooldown:
                    target.life -= self.damage

    def draw_ammo(self, screen):
        # Desenha a munição da arma
        pygame.draw.rect(screen, (80, 80, 80), (50, 50, self.ammo, 20))
        pygame.draw.rect(screen, (0, 200, 255), (50, 50, self.curr_ammo, 20))

        # avisa caso esteja em overheat
        if self.overheat_timer:
            pygame.draw.rect(screen, (80, 80, 80), (50, 90, 120, 10))
            pygame.draw.rect(screen, (255, 255, 0), (50, 90, self.overheat_timer, 10))

    def get_laser_pos(self):
        pos_x, pos_y = pygame.mouse.get_pos()

        #calcula a ponta da arma de onde deveria sair o laser usando seno e cosseno
        radians = math.radians(self.angle)
        laser_start_x = self.rect.centerx + (self.rect.width * math.cos(radians)) // 2
        laser_start_y = (self.rect.centery - (self.rect.width * math.sin(radians)) // 2) - self.rect.width // 4
        
        return (laser_start_x - camera.x, laser_start_y - camera.y), (pos_x, pos_y)
    

#--------------------------Basuca--------------------------------------------
class Bazooka():
    def __init__(self,x, y, ammo, image, recharge_time, animation_cooldown, sprite_sheet, sprite_width, sprite_height):
        # surface e rectangle
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        #munições
        self.ammo = ammo
        self.curr_ammo = ammo
        self.blts = []
        self.blt_speed = 5
        self.recharge_time = recharge_time
        self.curr_recharge_time = recharge_time
        self.recharge = False

        # Projetil
        self.projectile_damage = 30
        self.shoot_cooldown = 30
        self.curr_shoot_cooldown = 0

        # Explosão
        self.explosions = []
        self.explosion_damage = 3
        self.explosion_cooldown = 150

        # Animação
        self.sprite_image = pygame.image.load(sprite_sheet)
        self.sprite_sheet = SpriteSheet(self.sprite_image)
        self.animation_list = self.sprite_sheet.get_animations([3, 7], sprite_width, sprite_height, 2)
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.animation_cooldown = animation_cooldown
        self.last_update = pygame.time.get_ticks()
        self.projectile_action = 0
        self.explosion_action = 1

        # outros
        self.angle = 0
        self.equiped = False
        self.x = (0, 0, 0)  # Track previous mouse state
        self.hand = 'right'


    def update(self, plr, screen):
        keys_pressed = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        current_time = pygame.time.get_ticks()

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

            self.get_angle() #calcula o ângulo com vetores

            # Lógica para atirar
            if mouse_buttons[0] and self.prev_mouse_buttons[0] == 0 and self.curr_ammo > 0 and not self.recharge and not self.curr_shoot_cooldown:
                self.shoot(pos_x, pos_y)
                self.curr_ammo -= 1
                self.curr_shoot_cooldown = self.shoot_cooldown

            # Permite o jogador atirar depois de um cooldown
            if self.curr_shoot_cooldown:
                self.curr_shoot_cooldown -= 1


            # Recarregar arma
            if keys_pressed[pygame.K_r] and self.recharge == False and self.curr_ammo != self.ammo and plr.bazooka_ammo_pack:
                self.recharge = True
                plr.bazooka_ammo_pack -= 1

            self.draw_gun(screen, plr)

        if self.recharge:
            self.recharging(screen)

        self.handle_bullets(screen, current_time)

        self.prev_mouse_buttons = mouse_buttons

    #-----------------munição e balas-------------------------------
    def shoot(self, mouse_x, mouse_y):
        if self.equiped == True:

            #criando a bala e transformando para ficar com o ângulo correto
            frames = self.animation_list[self.projectile_action]
            bullet = pygame.rect.Rect(
                self.rect.x - self.rect.width // 2, # posição x
                self.rect.y - self.sprite_height, # posição y
                self.sprite_width, # largura
                self.sprite_height # altura
            )
        
            #calcula a velocidade y e x da bala 
            radians = math.radians(-self.angle)
            cos_mouse = math.cos(radians)
            sin_mouse = math.sin(radians)

            # Distância do mouse para a arma
            dx = self.rect.x - camera.x - mouse_x
            dy = self.rect.y - camera.y - mouse_y
            dist = (dx**2 + dy**2) ** 0.5

            # Calcula o tempo de vida da bala
            time = dist // self.blt_speed
            
            self.blts.append({
                "frames_img": frames,
                "frame": 0,
                "last_update": pygame.time.get_ticks(),
                "rect": bullet,
                "speed_x": self.blt_speed * cos_mouse,
                "speed_y": self.blt_speed * sin_mouse,
                "time_to_live": time,
                "explosion": 0,
                "exploded": False
            })

    def handle_bullets(self, screen, curr_time):
        for bullet in self.blts:
            bullet.get("rect").x += bullet.get("speed_x")
            bullet.get("rect").y += bullet.get("speed_y")

            # Animação do projétil
            if curr_time - bullet.get("last_update") >= self.animation_cooldown:
                bullet["frame"] += 1
                bullet["last_update"] = curr_time
                if bullet.get("time_to_live") and bullet.get("frame") >= len(self.animation_list[self.projectile_action]):
                        bullet["frame"] = 0

            # Desenha o projétil e diminui o tempo de vida
            if bullet.get("time_to_live"):
                bullet["time_to_live"] -= 1
                screen.blit(bullet["frames_img"][bullet["frame"]], (bullet.get("rect").x - camera.x, bullet.get("rect").y - camera.y))
            
            else:
                self.explosion(screen, bullet)

    def check_collision(self, target):
        curr_tick = pygame.time.get_ticks()

        for bullet in self.blts:
            if bullet["rect"].colliderect(target) and bullet["time_to_live"]:
                target.life -= self.projectile_damage
                bullet["time_to_live"] = 0

            if bullet["explosion"] and curr_tick - bullet["explosion"]["last_tick"] >= bullet["explosion"]["explosion_cooldown"]:
                if bullet["explosion"]["rect"].colliderect(target):
                    target.life -= self.explosion_damage

    def explosion(self, screen, bullet):
        explosion_frames = self.animation_list[self.explosion_action]
        
        if not bullet.get("exploded"): # caso seja a primeira vez que a função for chamada
            bullet["frame"] = 0
            bullet["exploded"] = True
            bullet["speed_x"], bullet["speed_y"] = 0, 0

        elif bullet["frame"] <= len(self.animation_list[self.explosion_action]) - 1: # lógica durante a explosão do projétil (termina quando os frames acabam)
            for i in range(len(explosion_frames)): # muda o tamanho da explosão
                explosion_frames[i] = pygame.transform.scale(explosion_frames[i], (self.sprite_width * 3, self.sprite_height * 3))
                explosion_frames[i].set_colorkey((0, 0, 0))
            exp_surf = explosion_frames[bullet["frame"]]
            exp_width, exp_height = exp_surf.get_width(), exp_surf.get_height()
            exp_rect = exp_surf.get_rect()
            exp_rect.x = bullet.get("rect").centerx - exp_width//2 
            exp_rect.y = bullet.get("rect").centery - exp_height//2

            explosion = {
                "rect": exp_rect,
                "last_tick": pygame.time.get_ticks(),
                "explosion_cooldown": 80
            }

            if not bullet["explosion"]:
                bullet["explosion"] = explosion

            # lida com a animação da explosão
            screen.blit(exp_surf, (exp_rect.x - camera.x, exp_rect.y - camera.y))

        else:
            self.blts.remove(bullet)


    def recharging(self, screen):
        if self.curr_recharge_time:
            self.curr_recharge_time -= 1

            # Desenha o cooldown de recarga
            pygame.draw.rect(screen, (80, 80, 80), (50, 80, self.recharge_time, 10))
            pygame.draw.rect(screen, (255, 255, 0), (50, 80, self.curr_recharge_time, 10))
        else:
            self.curr_ammo = self.ammo
            self.curr_recharge_time = self.recharge_time
            self.recharge = False    
            
    def draw_ammo(self, screen):
        # Desenha a munição da arma
        pygame.draw.rect(screen, (80, 80, 80), (50, 50, self.ammo * 5, 20))
        pygame.draw.rect(screen, (0, 200, 255), (50, 50, self.curr_ammo * 5, 20))

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

