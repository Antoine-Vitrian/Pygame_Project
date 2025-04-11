import pygame
from camera import create_screen, camera
import csv

TILES_SIZE = 32
0
SCREEN_WIDTH = TILES_SIZE * 30
SCREEN_HEIGHT = TILES_SIZE * 25

screen = create_screen(SCREEN_WIDTH, SCREEN_HEIGHT, 'game')

class Tile_kind:
    def __init__(self, name, image, is_solid):
        self.name = name
        self.image = pygame.image.load(image)
        self.is_solid = is_solid

class Map:
    def __init__(self, map_file, tile_kinds, tile_size):
        self.tile_kinds = tile_kinds
        self.tiles = []
        self.tile_size = tile_size

        # usa o arquivo csv para pegar o mapa
        with open(map_file, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                new_row = []    
                for item in row:
                    int_item = int(item)
                    new_row.append(int_item)
                self.tiles.append(new_row)


    def draw(self, screen):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                location = (x * self.tile_size - camera.x, y * self.tile_size - camera.y)
                image = self.tile_kinds[tile].image
                screen.blit(image, location)

        
        