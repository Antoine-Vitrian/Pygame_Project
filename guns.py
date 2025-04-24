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
        # jogador
        self.audio1 = pygame.mixer.Sound('audio/effects/manual.mp3')
        self.audio1.set_volume(0.04)
        #inimigos
        self.audio2 = pygame.mixer.Sound('audio/effects/gun_shot.mp3')
        self.audio2.set_volume(0.01)
        self.enemy = False
        
        # balas
        self.damage = 20
        self.shoot_cooldown = shoot_cooldown
        self.curr_shoot_cooldown = 0
        self.auto_shoot = auto_shoot

    def update(self, plr, screen, blts):
        keys_pressed = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        if self.equiped == False:
            screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y)) # desenha a arma jogada no chão

        else:
            if keys_pressed[pygame.K_q] and plr.equiped == True: # evento para desequipar a arma
                self.equiped = False
                plr.equiped = False
                plr.weapon = None
                pygame.event.post(pygame.event.Event(DEQUIP_EVENT))

            # Posição do mouse    
            pos_x, pos_y = pygame.mouse.get_pos()
            self.get_angle((pos_x, pos_y))

            self.draw_gun(screen, plr, (pos_x, pos_y))

            # Lógica para atirar
            if mouse_buttons[0] and (self.prev_mouse_buttons[0] == 0 or self.auto_shoot) and self.curr_ammo > 0 and not self.recharge and not self.curr_shoot_cooldown:
                blts.append(self.shoot())
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

        self.prev_mouse_buttons = mouse_buttons

    def check_equip(self, plr):
        keys_pressed = pygame.key.get_pressed()
        if self.equiped == False:
        
            if self.rect.colliderect(plr):
                if keys_pressed[pygame.K_e] and plr.equiped == False:
                    self.equiped = True
                    plr.equiped = True
                    plr.weapon = self  # define essa arma como equipada pelo jogador
                    pygame.event.post(pygame.event.Event(EQUIP_EVENT))

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
            holder.direction = 'left'
        elif pos_x >= holder.rect.x + holder.rect.width  - camera.x:
            self.hand = 'right'
            holder.direction = 'right'

        # Detecta se o jogador está apontando para direita ou esquerda
        if self.hand == 'left':
            self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
            self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)
            self.fliped_image = pygame.transform.flip(self.rotated_image, False, True)

            self.rect.centerx = holder.rect.centerx - (holder.rect.width // 2)
            self.rect.centery = holder.rect.centery + holder.rect.height // 5

            screen.blit(self.fliped_image, (self.rotated_rect.x - camera.x, self.rotated_rect.y - camera.y))
        elif self.hand == 'right':
            self.rotated_image = pygame.transform.rotate(self.image, self.angle)
            self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)

            self.rect.centerx = holder.rect.centerx + (holder.rect.width // 2)
            self.rect.centery = holder.rect.centery + holder.rect.height // 5

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

            if not self.enemy:
                self.audio1.play()
            else:
                self.audio2.play()

            return Blt(
                rotated_bullet_surface,
                bullet,
                self.blt_speed * cos,
                self.blt_speed * sin,
                self.blt_time,
                self.damage,
                enemy
                )

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
        if not self.enemy:
            self.enemy = True
        self.draw_gun(screen, enemy, (plr.rect.centerx - camera.x, plr.rect.centery - camera.y))
        self.get_angle((plr.rect.centerx, plr.rect.centery), enemy=True)

#------------------Arma Laser------------------------------------------
class Laser_gun():
    def __init__(self,x, y, ammo, image):
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
        self.damage = 5
        self.damage_cooldown = 50
        self.last_hit = pygame.time.get_ticks()
        self.shooting = False

        # outras coisas da arma
        self.equiped = False
        self.angle = 0
        self.hand = 'right'
        self.tiro_sfx = pygame.mixer.Sound('audio/effects/laser.mp3')
        self.tiro_sfx.set_volume(0.1)
        self.channel = None

    def update(self, plr, screen, enemies):
        keys_pressed = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        # arma não equipada
        if self.equiped == False:
            screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

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

                    # Toca o som só se ainda não estiver tocando
                    if self.channel is None or not self.channel.get_busy():
                        self.channel = self.tiro_sfx.play(-1)  # -1 = loop
                else:
                    self.overheat_timer = 120
            else:
                self.shooting = False
                if self.channel is not None:
                    self.channel.stop()

            # checa colisão
            for enemy in enemies:
                self.check_collision(enemy)
        
        # Recarrega enquanto a munição é menor que a munição máxima e não está atirando
        if (self.curr_ammo < self.ammo and not mouse_buttons[0]) or self.overheat_timer and self.curr_ammo <= self.ammo:
            self.curr_ammo += 1.3
            
        # Se a arma sobreaqueceu diminui o timer do sobreaquecimento
        if self.overheat_timer > 0:
            self.overheat_timer -= 1
            self.laser = {}

    def check_equip(self, plr):
        keys_pressed = pygame.key.get_pressed()
        if not self.equiped and self.rect.colliderect(plr) and keys_pressed[pygame.K_e] and plr.equiped == False:
            self.equiped = True
            plr.equiped = True
            plr.weapon = self  # define essa arma como equipada pelo jogador
            pygame.event.post(pygame.event.Event(EQUIP_EVENT))

    def get_angle(self):
        # calcula o ângulo da arma (com pygame.Vector2)
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())  # Get raw mouse position
        gun_pos = pygame.Vector2((self.rect.centerx - camera.x, self.rect.centery - camera.y))

        direction = mouse_pos - gun_pos  # Vector from player to mouse
        if direction.length() > 0:
            self.angle = direction.angle_to(pygame.Vector2(1, 0))

    def draw_gun(self, screen, holder):
        pos_x, pos_y = pygame.mouse.get_pos()

        if pos_x <= holder.rect.x - camera.x:
            self.hand = 'left'
            holder.direction = 'left'
        elif pos_x >= holder.rect.x + holder.rect.width  - camera.x:
            self.hand = 'right'
            holder.direction = 'right'

        # Detecta se o jogador está apontando para direita ou esquerda
        if self.hand == 'left':
            self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
            self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)
            # inverte a arma para ficar na posição certa do lado contrário
            self.fliped_image = pygame.transform.flip(self.rotated_image, False, True)

            # Define o centro da arma
            self.rect.centerx = holder.rect.x
            self.rect.centery = holder.rect.centery + holder.rect.height//5

            screen.blit(self.fliped_image, (self.rotated_rect.x - camera.x, self.rotated_rect.y - camera.y))
        elif self.hand == 'right':
            self.rotated_image = pygame.transform.rotate(self.image, self.angle)
            self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)

            self.rect.centerx = holder.rect.x + holder.rect.width
            self.rect.centery = holder.rect.centery + holder.rect.height//5

            screen.blit(self.rotated_image, (self.rotated_rect.x - camera.x, self.rotated_rect.y - camera.y))

    def check_collision(self, target):
        if self.shooting == True:
            (laser_ix, laser_iy), (laser_fx, laser_fy) = self.get_laser_pos()

            current_time = pygame.time.get_ticks()

            target_position = pygame.rect.Rect(target.rect.x - camera.x, target.rect.y - camera.y, target.rect.width, target.rect.height)

            hit = False

            for i in range(0, 201):
                px = laser_ix + (laser_fx - laser_ix) * i / 200
                py = laser_iy + (laser_fy - laser_iy) * i / 200
                if target_position.collidepoint(px, py):
                    hit = True
                    break

            if hit and current_time - self.last_hit >= self.damage_cooldown:
                target.life -= self.damage
                self.last_hit = current_time

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
    def __init__(self,x, y, ammo, image, recharge_time, animation_cooldown, sprite_sheet):
        # surface e rectangle
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        #munições
        self.ammo = ammo
        self.curr_ammo = ammo
        self.blt_speed = 10
        self.recharge_time = recharge_time
        self.curr_recharge_time = recharge_time
        self.recharge = False

        # Projetil
        self.damage = 30
        self.shoot_cooldown = 30
        self.curr_shoot_cooldown = 0

        # Explosão
        self.explosion_damage = 3
        self.explosion_cooldown = 150

        # Animação
        self.sprite_image = pygame.image.load(sprite_sheet)
        self.sprite_sheet = SpriteSheet(self.sprite_image)
        self.sprite_width = self.sprite_image.get_width() / 10
        self.sprite_height = self.sprite_image.get_height()
        self.animation_list = self.sprite_sheet.get_animations([3, 7], self.sprite_width, self.sprite_height, 2)
        self.animation_cooldown = animation_cooldown
        self.last_update = pygame.time.get_ticks()

        # outros
        self.angle = 0
        self.equiped = False
        self.x = (0, 0, 0)  # Track previous mouse state
        self.hand = 'right'
        self.tiro_sfx = pygame.mixer.Sound('audio/effects/bazuca2.mp3')
        self.tiro_sfx.set_volume(0.1)


    def update(self, plr, screen, blts):
        keys_pressed = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        if self.equiped == False:
            screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y)) # desenha a arma jogada no chão

        else:
            if keys_pressed[pygame.K_q] and plr.equiped == True: # evento para desequipar a arma
                self.equiped = False
                pygame.event.post(pygame.event.Event(DEQUIP_EVENT))

            # Posição do mouse    
            pos_x, pos_y = pygame.mouse.get_pos()

            self.get_angle() #calcula o ângulo com vetores

            # Lógica para atirar
            if mouse_buttons[0] and self.prev_mouse_buttons[0] == 0 and self.curr_ammo > 0 and not self.recharge and not self.curr_shoot_cooldown:
                blts.append(self.shoot(pos_x, pos_y))
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

        # self.handle_bullets(screen, current_time)

        self.prev_mouse_buttons = mouse_buttons

    def check_equip(self, plr):
        keys_pressed = pygame.key.get_pressed()
        if self.equiped == False:
        
            if self.rect.colliderect(plr):
                if keys_pressed[pygame.K_e] and plr.equiped == False:
                    self.equiped = True
                    plr.equiped = True
                    plr.weapon = self  # define essa arma como equipada pelo jogador
                    pygame.event.post(pygame.event.Event(EQUIP_EVENT))

    #-----------------munição e balas-------------------------------
    def shoot(self, mouse_x, mouse_y):
        if self.equiped == True:

            #criando a bala e transformando para ficar com o ângulo correto
            bullet = pygame.rect.Rect(
                self.rect.x - self.rect.width // 2, # posição x
                self.rect.y - self.rect.height // 2, # posição y
                self.sprite_width, # largura
                self.sprite_height # altura
            )
        
            #calcula a velocidade y e x da bala 
            radians = math.radians(-self.angle)
            cos_mouse = math.cos(radians)
            sin_mouse = math.sin(radians)

            # Distância do mouse para a arma
            dx = self.rect.centerx - camera.x - mouse_x
            dy = self.rect.centery - camera.y - mouse_y
            dist = (dx**2 + dy**2) ** 0.5

            # Calcula o tempo de vida da bala
            time = dist // self.blt_speed

            self.tiro_sfx.play()
            
            return Exp_Blt(
                self.animation_list[0],
                self.animation_list[1],
                bullet,
                self.blt_speed * cos_mouse,
                self.blt_speed * sin_mouse,
                time,
                self.damage
            )

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
    def draw_gun(self, screen, holder):
        pos_x, pos_y = pygame.mouse.get_pos()

        if pos_x <= holder.rect.x - camera.x:
            self.hand = 'left'
            holder.direction = 'left'
        elif pos_x >= holder.rect.x + holder.rect.width  - camera.x:
            self.hand = 'right'
            holder.direction = 'right'

        # Detecta se o jogador está apontando para direita ou esquerda
        if self.hand == 'left':
            self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
            self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)
            self.fliped_image = pygame.transform.flip(self.rotated_image, False, True)

            self.rect.centerx = holder.rect.x
            self.rect.centery = holder.rect.centery + holder.rect.height//5

            screen.blit(self.fliped_image, (self.rotated_rect.x - camera.x, self.rotated_rect.y - camera.y))
        elif self.hand == 'right':
            self.rotated_image = pygame.transform.rotate(self.image, self.angle)
            self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)

            self.rect.centerx = holder.rect.centerx + (holder.rect.width // 2)
            self.rect.centery = holder.rect.centery + holder.rect.height//5

            screen.blit(self.rotated_image, (self.rotated_rect.x - camera.x, self.rotated_rect.y - camera.y))

    def get_angle(self):
        # calcula o ângulo da arma (com pygame.Vector2)
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())  # Get raw mouse position
        gun_pos = pygame.Vector2((self.rect.centerx - camera.x, self.rect.centery - camera.y))

        direction = mouse_pos - gun_pos  # Vector from player to mouse
        if direction.length() > 0:
            self.angle = direction.angle_to(pygame.Vector2(1, 0))

class Blt():
    def __init__(self, surf, rect, speed_x, speed_y, time_to_live, damage, enemy):
        self.type = "gun"
        self.surf = surf
        self.rect = rect
        self.damage = damage
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.time_to_live = time_to_live
        self.enemy = enemy

class Exp_Blt():
    def __init__(self, proj_anim_list, exp_anim_list, rect, speed_x, speed_y, time_to_live, damage):
        self.type = "explosive"
        self.projectile_animation = proj_anim_list
        self.exp_animation = exp_anim_list
        self.rect = rect
        self.damage = damage
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.time_to_live = time_to_live
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.explosion = {}
        self.exploded = False
        self.enemy = False
        
    def update(self, screen, curr_time, animation_cooldown):
        if curr_time - self.last_update >= animation_cooldown:
            self.frame += 1
            self.last_update = curr_time
            if self.frame >= len(self.projectile_animation) and not self.exploded:
                self.frame = 0

        if self.time_to_live:
            screen.blit(self.projectile_animation[self.frame], (self.rect.x - camera.x, self.rect.y - camera.y))

    def get_explosion(self, screen, enemies):
        if not self.exploded: # caso seja a primeira vez que a função for chamada
            self.frame = 0
            self.exploded = True
            self.speed_x, self.speed_y = 0, 0

        new_frames = []

        for ind, frame in enumerate(self.exp_animation): # Aumenta o tamanho da explosão
            new_frame = pygame.transform.scale(frame, (10 * (ind + 4), 10 * (ind + 4)))
            new_frame.set_colorkey((0, 0, 0))
            new_frames.append(new_frame)

        if self.frame < len(self.exp_animation):
            exp_surf = new_frames[self.frame]
            exp_rect = exp_surf.get_rect()
            exp_rect.centerx = self.rect.centerx
            exp_rect.centery = self.rect.centery

            self.check_collision(exp_rect, enemies)
            screen.blit(exp_surf, (exp_rect.x - camera.x, exp_rect.y - camera.y))

        else:
            return True
        
    def check_collision(self, blt_rect, enemies):
        for enemy in enemies:
            if blt_rect.colliderect(enemy):
                enemy.life -= 2.5
