import pygame
import sys
import time

from scripts.utils import load_images
from scripts.tilemap import Tilemap


RENDER_SCALE = 2.0

RUNNING_FPS = 60
DISPLAYING_FPS = 120

class Editor:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('editor')

        window_size = (1280,720)
        self.screen = pygame.display.set_mode(window_size)
        self.display = pygame.Surface((640,360))
        # self.display = pygame.Surface((1280,720))
        
        self.clock = pygame.time.Clock()
        self.movement = [False,False]

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'stone': load_images('tiles/stone'),
            'large_decor': load_images('tiles/large_decor'),
        }

        self.tilemap = Tilemap(self)
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            print('where the map bro')

        self.scroll = [0,0]
        self.movement = [False,False,False,False]
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True

    

    
    def run(self):
        while True:
            self.display.fill((0,0,0))
            self.scroll[0] += (self.movement[1]-self.movement[0])*2
            self.scroll[1] += (self.movement[3]-self.movement[2])*2
            render_scroll = (int(self.scroll[0]),int(self.scroll[1]))
            self.tilemap.render(self.display, offset=render_scroll)

            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)


            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0]/RENDER_SCALE, mpos[1]/RENDER_SCALE)
            tile_pos = (int((mpos[0]+self.scroll[0])//self.tilemap.tile_size), int((mpos[1]+self.scroll[1])//self.tilemap.tile_size))
            if self.ongrid:
                preview_block_loc = (tile_pos[0]*self.tilemap.tile_size-self.scroll[0],tile_pos[1]*self.tilemap.tile_size-self.scroll[1])
                self.display.blit(current_tile_img,preview_block_loc)
            else:
                self.display.blit(current_tile_img, mpos)

            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0])+';'+str(tile_pos[1])] = {'type': self.tile_list[self.tile_group],'variant': self.tile_variant, 'pos':tile_pos}


            if self.right_clicking:
                tile_loc = str(tile_pos[0])+';'+str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0]-self.scroll[0], tile['pos'][1]-self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)
                        break

            self.display.blit(current_tile_img,(5,5))
          
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group],'variant': self.tile_variant, 'pos':(mpos[0]+self.scroll[0],mpos[1]+self.scroll[1])})
                    if event.button == 3: #right mouse
                        self.right_clicking = True
                    
                    if self.shift: #change variant
                        if event.button == 4: #scroll up
                            self.tile_variant = (self.tile_variant -1)%len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5: #scroll down
                            self.tile_variant = (self.tile_variant +1)%len(self.assets[self.tile_list[self.tile_group]])
                    else: #change block type
                        if event.button == 4: #scroll up
                            self.tile_group = (self.tile_group -1)%len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5: #scroll down
                            self.tile_group = (self.tile_group +1)%len(self.tile_list)
                            self.tile_variant = 0

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3: #right mouse
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2]=True
                    if event.key == pygame.K_s:
                        self.movement[3]=True

                    if event.key == pygame.K_t:
                        self.tilemap.autotile()

                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid

                    if event.key == pygame.K_o:
                        self.tilemap.save('map.json')

                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                        
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2]=False
                    if event.key == pygame.K_s:
                        self.movement[3]=False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False
            
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()),(0,0))
            pygame.display.update()
            self.clock.tick(RUNNING_FPS)

Editor().run()