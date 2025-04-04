import pygame

# classe para os botões
class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()
        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            pygame.transform.scale(self.image, (int(self.image.get_width() * 0.2), int(self.image.get_height() * 0.2)))

            if pygame.mouse.get_pressed()[0] and self.clicked == False:
                self.clicked = True
                action = True
            if not pygame.mouse.get_pressed()[0] and self.clicked == True:
                self.clicked = False
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
        # Desenha o botão na tela
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action
    