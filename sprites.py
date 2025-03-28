import pygame

class SpriteSheet():
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale):
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(self.sheet, (0, 0), ((width * frame), 0, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey((0, 0, 0))

        return image
    
    def get_animations(self, steps, width, height, scale):
        animation_list = []
        step_counter = 0
        for animation in steps:
            temp_img_list = []
            for _ in range(animation):
                temp_img_list.append(self.get_image(step_counter, width, height, scale))
                step_counter += 1
            animation_list.append(temp_img_list)

        return animation_list