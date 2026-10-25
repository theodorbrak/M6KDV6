# -*- coding: utf-8 -*-
import math, pygame, sys


pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((1200, 650)) #built for 1280 x 720 i have to do this

font = pygame.font.SysFont(None, 32)
input_rect = pygame.Rect(100, 100, 300, 40)
text = ""
active = False

# dans la boucle d'événements :
while True:
    dt = clock.tick(60)/1000
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            active = input_rect.collidepoint(event.pos)   # clic dans la boîte = actif

        if event.type == pygame.KEYDOWN and active:
            if event.key == pygame.K_RETURN:
                print(text)          # valider
                text = ""
            elif event.key == pygame.K_BACKSPACE:
                text = text[:-1]
            else:
                text += event.unicode

    # dans le dessin :
    pygame.draw.rect(screen, (255, 255, 255), input_rect)
    pygame.draw.rect(screen, (0, 0, 0) if not active else (80, 80, 240), input_rect, 2)
    screen.blit(font.render(text, True, (0, 0, 0)), (input_rect.x + 8, input_rect.y + 10))