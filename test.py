import pygame
from math import sin, cos, pi

pygame.init()

win = pygame.display.set_mode((800, 600))

def draw_ngon(Surface, color, n, radius, position):
    pi2 = 2 * pi

    for i in range(0, n):
        pygame.draw.line(Surface, color, position, (cos(i / n * pi2) * radius + position[0], sin(i / n * pi2) * radius + position[1]))

    return pygame.draw.lines(Surface,
          color,
          True,
          [(cos(i / n * pi2) * radius + position[0], sin(i / n * pi2) * radius + position[1]) for i in range(0, n)])

run = True
clock = pygame.time.Clock()
n = 3

while run:
    pygame.display.set_caption(str(round(1 / (clock.tick(1000) / 1000))))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                n += 1
            if event.button == 5:
                n = max(2, n - 1)

    win.fill((0, 0, 0))

    draw_ngon(win, (255, 0, 0), n, 300, (400, 300))

    pygame.display.update()

pygame.quit()