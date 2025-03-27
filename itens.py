import pygame
from camera import camera

class AmmoPack:
    def __init__(self, x, y, ammo_type, scale):
        self.ammo_type = ammo_type
        if self.ammo_type == 'gun':
            self.image = pygame.image.load('Img/other/gun_battery.png')
        elif self.ammo_type == 'bazooka':
            self.image = pygame.image.load('Img/other/bazooka_ammo.png')
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * scale, self.image.get_height() * scale))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.droped = True


    def update(self, screen, plr):
        keys_pressed = pygame.key.get_pressed()

        if self.rect.colliderect(plr) and keys_pressed[pygame.K_f]: # aumenta a munição reserva do player
            if self.ammo_type == 'gun':
                plr.ammo_pack += 1
            elif self.ammo_type == 'bazooka':
                plr.bazooka_ammo_pack += 1
            self.droped = False
        
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

