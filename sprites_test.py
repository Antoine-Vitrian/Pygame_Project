import pygame
from sprites import SpriteSheet

pygame.init()

BLACK = (0, 0, 0)

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Spritesheet')

sprite_sheet_image = pygame.image.load('Img//other/bazooka_bullet.png').convert_alpha()
sprite_sheet = SpriteSheet(sprite_sheet_image)

# create animation list
animation_list = []
animation_steps = [3]
action = 0 
last_update = pygame.time.get_ticks()
animation_cooldown = 50
frame = 0
step_counter = 0

for animation in animation_steps:
    temp_img_list = []
    for _ in range(animation):
        temp_img_list.append(sprite_sheet.get_image(step_counter, 17, 17, 2, BLACK))
        step_counter += 1
    animation_list.append(temp_img_list)

run = True
while run:
    screen.fill((70, 70, 70))

    #show frame image
    screen.blit(animation_list[action][frame], (0, 0))

    #update animation
    current_time = pygame.time.get_ticks()
    if current_time - last_update >= animation_cooldown:
        frame += 1
        last_update = current_time
        if frame >= len(animation_list[action]):
            frame = 0


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.flip()

pygame.quit()