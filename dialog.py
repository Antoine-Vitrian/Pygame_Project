import pygame

class DialogBox():
    def __init__(self, image_path, color):
        self.image_path = image_path
        self.image = pygame.image.load(image_path)
        self.char_box = pygame.image.load('Img/other/char_box.png')
        self.font = pygame.font.Font('fonts/Pixel_Digivolve.otf', 18)
        self.counter = 0
        self.line_counter = 0
        self.write_cooldown = 40
        self.last_write = pygame.time.get_ticks()
        self.color = color
        self.done = False

    def draw(self, screen, pos, text, img):
        keys_pressed = pygame.key.get_pressed()

        # Ajusta o tamanho da imagem
        size = self.char_box.get_width() - 15
        resized_img = pygame.transform.scale(img, (size, size))

        char_box_pos = (20, (self.image.get_height() - self.char_box.get_height()) // 2)
        self.image.blit(self.char_box, char_box_pos)

        img_x = char_box_pos[0] + (self.char_box.get_width() // 2 - resized_img.get_width() // 2)
        img_y = char_box_pos[1] + (self.char_box.get_height() // 2 - resized_img.get_height() // 2)
        self.image.blit(resized_img, (img_x, img_y))

        screen.blit(self.image, pos)
        self.write(text)
        skip_text = self.font.render('Pressione esc para pular', True, (200, 255, 255))
        screen.blit(skip_text, (pos[0] + self.image.get_width() - skip_text.get_width(), pos[1] + self.image.get_height()))

        if keys_pressed[pygame.K_SPACE]:
            if not self.done:     
                self.write_cooldown = 1 
            else:
                return 1
        else:
            self.write_cooldown = 40

    def write(self, text):
        if not self.done:
            current_time = pygame.time.get_ticks()

            text_width = self.image.get_width() - self.char_box.get_width() - 40
            lines = self.wrap_text(text, text_width)

            # Atualiza a linha a ser exibida
            if current_time - self.last_write >= self.write_cooldown:
                self.last_write = current_time
                self.counter += 1
                line = lines[self.line_counter]
                snip = self.font.render(line[0:self.counter], True, self.color)
                self.image.blit(snip, (self.char_box.get_width() + 30, 20 + 20 * self.line_counter))
                if self.counter > len(line):
                    self.counter = 0
                    if self.line_counter < len(lines) - 1:
                        self.line_counter += 1
                    else:
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