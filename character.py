import pygame
from camera import camera

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