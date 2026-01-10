import pygame
import sys
from constants import WIDTH, HEIGHT
from game import Game

pygame.init()

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
pygame.mouse.set_pos(WIDTH // 2, HEIGHT // 2)
pygame.mouse.get_rel()



def main():
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
    sys.exit()
