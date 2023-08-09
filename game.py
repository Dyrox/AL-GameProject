import pygame
import sys
import time

from scripts.entities import PhysicsEntity
from scripts.utils import load_image, load_images
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds

RUNNING_FPS = 60
DISPLAYING_FPS = 120

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('My Game')

        window_size = (1280,720)
        self.screen = pygame.display.set_mode(window_size)
        self.display = pygame.Surface((640,360))
        # self.display = pygame.Surface((1280,720))
        
        self.clock = pygame.time.Clock()
        self.movement = [False,False]

        self.assets = {
            'player': load_image('entities/player.png'),
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'stone': load_images('tiles/stone'),
            'large_decor': load_images('tiles/large_decor'),
            'background': load_image('genshin-background.png'),
            'clouds': load_images('clouds')
        }

        self.clouds = Clouds(self.assets['clouds'],count = 16)
        self.player = PhysicsEntity(self, 'player', (100,0), (8,15))
        self.tilemap = Tilemap(self)

        self.scroll = [0,0]
    

    
    def run(self):
        while True:
            self.display.blit(self.assets['background'],(0,0))
            self.scroll[0]+=(self.player.entity_rect.centerx-self.display.get_width()/2-self.scroll[0])//30
            self.scroll[1]+=(self.player.entity_rect.centery-self.display.get_height()/2-self.scroll[1])//30

            self.clouds.update()
            self.clouds.render(self.display,offset=self.scroll)
            self.tilemap.render(self.display,offset=self.scroll)

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display,offset=self.scroll)
            
          
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.velocity[1] = -3
                        
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()),(0,0))
            pygame.display.update()
            self.clock.tick(RUNNING_FPS)

Game().run()