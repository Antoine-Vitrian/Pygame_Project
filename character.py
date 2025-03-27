import pygame
from camera import camera
from game_map import SCREEN_HEIGHT, SCREEN_WIDTH

class Player():
    def __init__(self, x, y, life, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.life = life
        self.equiped = False
        self.speed = 5

    def update(self, screen):
        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_a]:
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_d]:
            self.rect.x += self.speed
        if keys_pressed[pygame.K_w]:
            self.rect.y -= self.speed
        if keys_pressed[pygame.K_s]:
            self.rect.y += self.speed

        screen.blit(self.surface, (self.rect.x - camera.x, self.rect.y - camera.y))

    def equip(self):
        self.equiped = True

    def dequip(self):
        self.equiped = False

class Player_rect():
    def __init__(self, x, y, life, col):
        self.surface = pygame.surface.Surface((50, 50))
        self.surface.fill(col)
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.life = life
        self.equiped = False
        self.speed = 5
        self.bazooka_ammo_pack = 4
        self.ammo_pack = 5
    
    def update(self, screen):
        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_a]:
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_d]:
            self.rect.x += self.speed
        if keys_pressed[pygame.K_w]:
            self.rect.y -= self.speed
        if keys_pressed[pygame.K_s]:
            self.rect.y += self.speed

        screen.blit(self.surface, (self.rect.x - camera.x, self.rect.y - camera.y))

        self.draw_life(screen)
        if self.equiped == True or keys_pressed[pygame.K_c]:
            self.show_ammo_packs(screen)

    def equip(self):
        self.equiped = True

    def dequip(self):
        self.equiped = False

    def draw_life(self, screen):
        #desenha a vida do jogador na tela
        pygame.draw.rect(screen, (255, 0, 0), (50, 20, self.life * 2, 15))
        pygame.draw.rect(screen, (0, 255, 0), (50, 20, self.life * 2, 15))

    def show_ammo_packs(self, screen):
        ammo_pack = pygame.image.load('Img/other/gun_battery.png')
        bazooka_ammo_pack = pygame.image.load('Img/other/bazooka_ammo.png')
        dist = 26


        for pack in range(self.ammo_pack):
            screen.blit(ammo_pack, (20 + dist * pack, SCREEN_HEIGHT - 60))
            
        for pack in range(self.bazooka_ammo_pack):
            screen.blit(bazooka_ammo_pack, (20 + dist * pack, SCREEN_HEIGHT - 30))
