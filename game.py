import pygame
import sys
import time

RUNNING_FPS = 60
DISPLAYING_FPS = 120

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('My Game')

        window_size = (1280,720)
        self.screen = pygame.display.set_mode(window_size)

        self.clock = pygame.time.Clock()

        self.img = pygame.image.load('data/images/clouds/cloud_1.png')
        self.img_pos = [300,200]
        self.img.set_colorkey((0,0,0))
        self.movement = [False,False]

        self.collision_area = pygame.Rect(300,400,300,50)
        
    def run(self):
        while True:
            self.screen.fill((0,0,0))
            self.img_pos[1] += (self.movement[1] - self.movement[0])*5
            
            img_r = pygame.Rect(self.img_pos[0],self.img_pos[1],self.img.get_width(),self.img.get_height())
            if img_r.colliderect(self.collision_area):
                pygame.draw.rect(self.screen,(50,100,255),self.collision_area)
            else:
                pygame.draw.rect(self.screen,(50,50,155 ),self.collision_area)
            self.screen.blit(self.img, self.img_pos)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.movement[0] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = True
                        
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.movement[0] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = False

        
            pygame.display.update()
            self.clock.tick(RUNNING_FPS)

Game().run()