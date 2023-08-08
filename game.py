import pygame
import sys
import time

from scripts.entities import PhysicsEntity
from scripts.utils import load_image

RUNNING_FPS = 60
DISPLAYING_FPS = 120

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('My Game')

        window_size = (1280,720)
        self.screen = pygame.display.set_mode(window_size)

        self.clock = pygame.time.Clock()
        self.movement = [False,False]

        self.assets = {
            'player': load_image('entities/player.png')
        }

        self.player = PhysicsEntity(self, 'player', (300,200), (8,15))
        
    def run(self):
        while True:
            self.screen.fill((0,0,0))
            self.player.update((self.movement[1]-self.movement[0],0))
            self.player.render(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                        
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

        
            pygame.display.update()
            self.clock.tick(RUNNING_FPS)

Game().run()