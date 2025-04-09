import pygame

pygame.init()

screen = pygame.display.set_mode((800, 500))

font = pygame.font.Font('freesansbold.ttf', 24)
timer = pygame.time.Clock()
message = 'this is a test message'
snip = font.render('', True, (255, 255, 255))
counter = 0
speed = 3
done = False

run = True
while run:

    screen.fill((100, 100, 100))
    timer.tick(60)

    pygame.draw.rect(screen, (180, 170, 150), (0, 300, 800, 200))
    if counter < speed * len(message):
        counter += 1
    elif counter >= speed*len(message):
        done = True

    snip = font.render(message[0:counter//speed], True, (255, 255, 255))
    screen.blit(snip, (10, 310))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.flip()

pygame.quit()