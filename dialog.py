import pygame

class DialogBox():
    def __init__(self, image_path, color):
        self.image_path = image_path
        self.image = pygame.image.load(image_path)
        self.char_box = pygame.image.load('Img/other/char_box.png')
        self.image.blit(self.char_box, (20, (self.image.get_height() - self.char_box.get_height())//2))
        self.font = pygame.font.Font('fonts/Pixel_Digivolve.otf', 18)
        self.counter = 0
        self.line_counter = 0
        self.write_cooldown = 40
        self.last_write = pygame.time.get_ticks()
        self.color = color
        self.done = False

    def draw(self, screen, pos, text, img):
        screen.blit(self.image, pos)
        self.write(text)
        self.char_box.blit(img, ((self.char_box.get_width() - img.get_width())//2, self.char_box.get_height() - img.get_height()))

    def write(self, text):
        if not self.done:
            current_time = pygame.time.get_ticks()

            text_width = self.image.get_width() - self.char_box.get_width() - 40
            lines = self.wrap_text(text, text_width)

            # Atualiza a linha a ser exibida
            if current_time - self.last_write >= self.write_cooldown:
                self.last_write = current_time
                
                line = lines[self.line_counter]
                snip = self.font.render(line[0:self.counter], True, self.color)
                self.image.blit(snip, (self.char_box.get_width() + 30, 20 + 20 * self.line_counter))
                self.counter += 1
                if self.counter > len(line):
                    self.counter = 0
                    if self.line_counter < len(lines) - 1:
                        self.line_counter += 1
                    else:
                        print('true')
                        self.done = True

    def wrap_text(self, text, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''

        for word in words:
            if self.font.render(current_line + ' ' + word, True, self.color).get_width() <= max_width:
                if current_line == '':
                    current_line = word
                else:
                    current_line += ' ' + word
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines
    
    def reset(self):
        self.image = pygame.image.load(self.image_path)  # Recarrega a imagem original
        self.char_box = pygame.image.load('Img/other/char_box.png')
        self.image.blit(self.char_box, (20, (self.image.get_height() - self.char_box.get_height()) // 2))
        self.counter = 0
        self.line_counter = 0
        self.last_write = pygame.time.get_ticks()
        self.done = False