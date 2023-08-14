import pygame
import sys
import time
import random
import math

from scripts.entities import PhysicsEntity, Player
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle

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
            'clouds': load_images('clouds'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur = 6),
            'player/run': Animation(load_images('entities/player/run'), img_dur = 4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/run')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'),img_dur=20,loop=False),
            'particle/particle': Animation(load_images('particles/particle'),img_dur=6,loop=False)
        }

        self.clouds = Clouds(self.assets['clouds'],count = 16)
        self.player = Player(self, (100,0), (8,15))
        self.tilemap = Tilemap(self)
        self.tilemap.load('map.json')

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor',2)],keep=True):
            self.leaf_spawners.append(
                pygame.Rect(4+tree['pos'][0],4+tree['pos'][1],23,13))
            


        self.particles = []
        

        self.scroll = [0,0]
    

    
    def run(self):
        while True:
            self.display.blit(self.assets['background'],(0,0))
            self.scroll[0]+=(self.player.entity_rect.centerx-self.display.get_width()/2-self.scroll[0])//30
            self.scroll[1]+=(self.player.entity_rect.centery-self.display.get_height()/2-self.scroll[1])//30

            self.clouds.update()
            self.clouds.render(self.display,offset=self.scroll)
            self.tilemap.render(self.display,offset=self.scroll)

            for rect in self.leaf_spawners:
                if random.random()*49999<rect.width*rect.height:
                    pos = (rect.x + random.random()*rect.width,rect.y + random.random()*rect.height )
                    self.particles.append(Particle(self,'leaf',pos,velocity=[-0.1,0.3],frame=random.randint(0,20)))


            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display,offset=self.scroll)
            
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=self.scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame*0.035)*0.3
                if kill:
                    self.particles.remove(particle)

          
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
                        self.player.jump()
                    if event.key == pygame.K_x:
                        self.player.dash()
                        
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()),(0,0))
            pygame.display.update()
            self.clock.tick(RUNNING_FPS)

Game().run()