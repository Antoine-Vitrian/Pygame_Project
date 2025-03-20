import pygame
from pygame.locals import *
from sys import exit

# Inicia o pygame
pygame.init()

# Definindo variáveis para altura e largura da janela
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 500

# Criando a tela
tela = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Criando o player(x, y, largura, altura)
player = pygame.Rect((300, 250, 50, 50))

# Mudando o nome da janela
pygame.display.set_caption("Era das Conquistas")

# Loop principal de jogo
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

        # Desenhando personagem jogador
        # ordem dos parâmetros rect (tela, cor, (posição(x,y), largura, altura))
        pygame.draw.rect(tela, (100, 100, 250), player)
        # circle (tela, posição, raio)
        # line (tel, ponto inicial, ponto final)

        pygame.display.update()
