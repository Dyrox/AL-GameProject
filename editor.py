import sys
import pygame

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
        self.clock = pygame.time.Clock()
        self.speed = 1
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'spawners': load_images('tiles/spawners'),
        }

        self.movement = [False, False, False, False]

        self.tilemap = Tilemap(self, tile_size=16)

        map_name = input("Map name: ")
        self.file_path = f'data/maps/{map_name}.json'
        if self.file_path:
            try:
                self.tilemap.load(self.file_path)
            except FileNotFoundError:
                pass
        else:
            print("No file selected!")
            sys.exit()

        self.scroll = [0, 0]

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True

    
    def take_screen_shot(self):
        pygame.image.save(self.display, 'editorscreenshot.png')
        print("Screenshot saved!")

    def run(self):

        while True:
            self.display.fill((0, 0, 0))

            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, offset=render_scroll)

            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)

            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size),
                        int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))

            if self.ongrid:
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0],
                                                     tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)

            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {
                    'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1],
                                         tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            self.display.blit(current_tile_img, (5, 5))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append(
                                {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant,
                                 'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(
                                self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(
                                self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = self.speed
                    if event.key == pygame.K_d:
                        self.movement[1] = self.speed
                    if event.key == pygame.K_w:
                        self.movement[2] = self.speed
                    if event.key == pygame.K_s:
                        self.movement[3] = self.speed
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    if event.key == pygame.K_o:
                        self.tilemap.save(self.file_path)
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                    if event.key == pygame.K_j:
                        self.speed = 5
                    if event.key == pygame.K_k:
                        self.speed = 1
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

                    if event.key == pygame.K_u:
                        self.take_screen_shot()

            # write text: tile type
            font = pygame.font.Font('minecraft.otf', 10)
            text = font.render(self.tile_list[self.tile_group], True, (255, 255, 255))
            self.display.blit(text, (5, 5 + current_tile_img.get_height()))
            # write text: o to save
            text = font.render('o to save', True, (255, 255, 255))
            self.display.blit(text, (5, 5 + current_tile_img.get_height() + text.get_height()))
            # write text: g to toggle grid
            text = font.render('g to toggle grid', True, (255, 255, 255))
            self.display.blit(text, (5, 5 + current_tile_img.get_height() + text.get_height() * 2))
            # write text: t to autotile
            text = font.render('t to autotile', True, (255, 255, 255))
            self.display.blit(text, (5, 5 + current_tile_img.get_height() + text.get_height() * 3))
            # write text: j to speed up
            text = font.render('j to speed up', True, (255, 255, 255))
            self.display.blit(text, (5, 5 + current_tile_img.get_height() + text.get_height() * 4))
            # write text: k to slow down
            text = font.render('k to slow down', True, (255, 255, 255))
            self.display.blit(text, (5, 5 + current_tile_img.get_height() + text.get_height() * 5))
            # write text: shift + scroll to change variant
            text = font.render('shift + scroll to change variant', True, (255, 255, 255))
            self.display.blit(text, (5, 5 + current_tile_img.get_height() + text.get_height() * 6))
            # write text: a/d/w/s to move
            text = font.render('a/d/w/s to move', True, (255, 255, 255))
            self.display.blit(text, (5, 5 + current_tile_img.get_height() + text.get_height() * 7))
 
            #show level name on the top right
            text = font.render(self.file_path, True, (255, 255, 255))
            self.display.blit(text, (self.display.get_width() - text.get_width() - 5, 5))



            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)


Editor().run()
