import pygame

class DialogBox():
    def __init__(self, image_path, color):
        self.image = pygame.image.load(image_path)
        self.char_box = pygame.image.load('Img/other/char_box.png')
        self.image.blit(self.char_box, (20, (self.image.get_height() - self.char_box.get_height())//2))
        self.font = pygame.font.Font('fonts/Pixel_Digivolve.otf', 18)
        self.counter = 0
        self.line_counter = 0
        self.lines = []
        self.speed = 3
        self.color = color
        self.done = False

    def draw(self, screen, pos, text):
        screen.blit(self.image, pos)
        self.write(text)

    def write(self, text):
        text_width = self.image.get_width() - self.char_box.get_width() - 40
        self.lines = self.wrap_text(text, text_width)

        # Atualiza a linha a ser exibida
        if self.line_counter < len(self.lines):
            line = self.lines[self.line_counter]
            max_chars = self.counter // self.speed
            snip = self.font.render(line[0:max_chars], True, self.color)
            self.image.blit(snip, (200, 20 + 20 * self.line_counter))

            # Quando toda a linha for escrita, passe para a próxima linha
            if max_chars >= len(line):
                self.line_counter += 1
                self.counter = 0  # Reseta o contador de caracteres para a próxima linha

        if self.line_counter < len(self.lines):
            if self.counter < self.speed * len(self.lines[self.line_counter]):
                self.counter += 1
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
        self.image.blit(self.image, (0, 0))