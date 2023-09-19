import sys
import math
import random
import os
import datetime

import pygame

from PIL import Image, ImageFilter, ImageEnhance


from scripts.utils import load_image, load_images, Animation, APPLE_FILE_CLEAR, ease_out_quad
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.object import ObjectAnimation

RUNNING_FPS = 60
DISPLAYING_FPS = 120

import os


class Game:
    def __init__(self):
        pygame.init()

        APPLE_FILE_CLEAR()
        self.x = 0

        pygame.display.set_caption('My game')
        self.window_size = (1280,720)
        self.screen = pygame.display.set_mode(self.window_size)
        self.display = pygame.Surface((640,360), pygame.SRCALPHA)
        self.display_WIDTH = self.display.get_width()
        self.display_HEIGHT = self.display.get_height()
        self.display_2 = pygame.Surface((640,360))

        self.heart_animations = []
        self.total_time = 0
        self.current_level_time = 0
        self.show_status_menu = False
        self.debug_menu_position = -100  # Start off-screen (assuming it slides in from the left)
        self.debug_menu_target_position = 0



        self.clock = pygame.time.Clock()
        
        self.movement = [False, False]

        self.font = pygame.font.Font('minecraft.otf', 20)
        
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background2.png'),
            'clouds': load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
            'arrow_keys_diagram': load_image('上下左右.png'),
            'x_key_diagram': load_image('objects/keyboard_X.png'),
            'enemy_head': load_image('objects/enemy_head.png'),
            'e_key_diagram': load_image('objects/keyboard_E.png'),
            
        }

        self.raw_assets = {
            'hearts': load_images('objects/hearts'),
            'dash_UI_icon': pygame.image.load('data/images/objects/dash_UI_icon.png').convert_alpha(),
            'jump_UI_icon': pygame.image.load('data/images/objects/jump_UI_icon.png').convert_alpha(),
            'stopwatch': pygame.image.load('data/images/objects/stopwatch.png').convert_alpha(),
            'status_menu': pygame.image.load('data/images/objects/status_menu.png').convert_alpha(),

            }
            



        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'), 
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }

        self.HP = 3
        self.sfx['jump'].set_volume(0.7)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['ambience'].set_volume(0.2)
        
        self.take_screenshot = False


        self.player = Player(self, (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self, tile_size=16)
        self.level = 0
        self.load_level(self.level)
        
        self.screenshake = 0

        self.paused = False

        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    
        self.keyboard_x = self.assets['x_key_diagram']

        for i in range(self.HP):
            pos = (i * (self.raw_assets['hearts'][0].get_width()*1.5) + 20, self.display_HEIGHT//15)  # Change 32 and 10 accordingly
            self.heart_animations.append(ObjectAnimation(pos, self.raw_assets['hearts']))


    def draw_text(self, text, font, color, surface, pos):
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.topleft = pos
        surface.blit(textobj, textrect)


        
    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
            
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
            
        self.projectiles = []
        self.particles = []
        self.sparks = []
        
        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30
    

    def projectile_render_update(self):
        for projectile in self.projectiles.copy():
            projectile[0][0] += projectile[1]
            projectile[2] += 1
            img = self.assets['projectile']
            self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - self.render_scroll[0], projectile[0][1] - img.get_height() / 2 - self.render_scroll[1]))
            if self.tilemap.solid_check(projectile[0]):
                self.projectiles.remove(projectile)
                for i in range(4):
                    self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
            elif projectile[2] > 360:
                self.projectiles.remove(projectile)
            elif abs(self.player.dashing) < 50:
                if self.player.rect().collidepoint(projectile[0]):
                    self.projectiles.remove(projectile)
                    self.HP -= 1
                    self.sfx['hit'].play()
                    self.screenshake = max(16, self.screenshake)
                    for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                        self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
    


    def spark_particle_render_update(self):
        for spark in self.sparks.copy():
            kill = spark.update()
            spark.render(self.display, offset=self.render_scroll)
            if kill:
                self.sparks.remove(spark)
        
        for particle in self.particles.copy():
            kill = particle.update()
            particle.render(self.display, offset=self.render_scroll)
            if particle.type == 'leaf':
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
            if kill:
                self.particles.remove(particle)

    def cloud_leaf_render_update(self):
        for rect in self.leaf_spawners:
            if random.random() * 49999 < rect.width * rect.height:
                pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
        
        self.clouds.update()
        self.clouds.render(self.display, offset=self.render_scroll)

    def scroll_update(self):
        self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) // 30
        self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) // 30
        self.render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

    def entity_render_update(self):
        if not self.dead:
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=self.render_scroll)
            
        for enemy in self.enemies.copy():
            kill = enemy.update(self.tilemap, (0, 0))
            enemy.render(self.display, offset=self.render_scroll)
            if kill:
                self.enemies.remove(enemy)

    def reset_current_level_timer(self):
        self.current_level_time = 0

    def restart_level(self):
        self.load_level(self.level)
        self.reset_movement()
        self.reset_player_status()
        self.reset_current_level_timer()
        self.main_game()


    def draw_hearts(self):
        for heart in self.heart_animations[:self.HP]:
            heart.draw(self.display)


    def save_global_time(self):
        self.total_time += self.current_level_time
        self.current_level_time = 0

    def check_level_loading(self):
        if not len(self.enemies):
            

            self.transition +=1
            if self.transition >30:
                self.level +=1
                self.save_global_time()
                if self.level == len(os.listdir('data/maps')):
                    self.game_end()
                else:
                    self.load_level(self.level)
                    
                
                
                
        if self.transition <0:
            self.transition +=1        

        for heart in self.heart_animations[:self.HP]:
            heart.animate(pygame.time.get_ticks())
            self.draw_hearts()

        if self.HP <= 0:
            self.dead += 1
        if self.dead:
            self.dead += 1
            if self.dead >= 10:
                self.transition = min(30, self.transition)
            if self.dead > 40:

                self.restart_level()

        if self.transition:
            transition_surf = pygame.Surface(self.display.get_size())
            pygame.draw.circle(transition_surf, (255,255,255), (self.display.get_width() // 2, self.display.get_height() // 2), (30-abs(self.transition))*8)
            transition_surf.set_colorkey((255,255,255))
            self.display.blit(transition_surf, (0,0))


    def game_end(self):
        print(self.total_time)

        
    def running_timer(self):
        self.current_level_time += 1/RUNNING_FPS

        time_text = str(datetime.timedelta(seconds=round(self.current_level_time, 0)))
        self.draw_text(time_text, pygame.font.Font('minecraft.otf', 20), 'black', self.display, (self.display_WIDTH//20*16.5-self.raw_assets['stopwatch'].get_width()//2+4, 34+self.menu_float))
        self.draw_text(time_text, pygame.font.Font('minecraft.otf', 20), 'white', self.display, (self.display_WIDTH//20*16.5-self.raw_assets['stopwatch'].get_width()//2+2, 32+self.menu_float))

        #also display the total time+current level time, in a smaller font, at the top right corner, below the current_level_time timer
        total_time_text = str(datetime.timedelta(seconds=round(self.total_time+self.current_level_time, 0)))
        self.draw_text(total_time_text, pygame.font.Font('minecraft.otf', 10), 'black', self.display, (self.display_WIDTH//20*16.5-self.raw_assets['stopwatch'].get_width()//2+3, 53+self.menu_float))

        self.draw_text(total_time_text, pygame.font.Font('minecraft.otf', 10), 'white', self.display, (self.display_WIDTH//20*16.5-self.raw_assets['stopwatch'].get_width()//2+2, 52+self.menu_float))

        
        self.display.blit(self.raw_assets['stopwatch'], (self.display_WIDTH//20*19-self.raw_assets['stopwatch'].get_width()//2, 20+self.menu_float))

    def show_enemy_count(self):
        self.display.blit(self.assets['enemy_head'], (self.display_WIDTH//20*1,self.display_HEIGHT//20*4+self.menu_float))
        self.draw_text(f'x {len(self.enemies)}', pygame.font.Font('minecraft.otf', 20), 'black', self.display, (self.display_WIDTH//20*2.3+2,self.display_HEIGHT//20*4.5+self.menu_float+2))
        self.draw_text(f'x {len(self.enemies)}', pygame.font.Font('minecraft.otf', 20), 'white', self.display, (self.display_WIDTH//20*2.3,self.display_HEIGHT//20*4.5+self.menu_float))

    def render_status_menu(self):
        speed = 10
        if self.show_status_menu:
            progress = ease_out_quad((self.debug_menu_target_position - self.debug_menu_position) / 100)
            self.debug_menu_position += speed * progress
            # Cap the position to the target if it overshoots due to the easing function
            if self.debug_menu_position > self.debug_menu_target_position:
                self.debug_menu_position = self.debug_menu_target_position
        else:
            progress = ease_out_quad((self.debug_menu_position + 100) / 100)
            self.debug_menu_position -= speed * progress
            # Cap the position to -100 if it overshoots due to the easing function
            if self.debug_menu_position < -100:
                self.debug_menu_position = -100

        pygame.draw.rect(self.display, (255, 0, 0), (self.debug_menu_position, self.display_HEIGHT/2, 100, 200))

    def EVERYTHING_render_update(self):
        self.scroll_update()
        self.projectile_render_update()
        self.spark_particle_render_update()
        self.cloud_leaf_render_update()
        self.entity_render_update()
        self.tilemap.render(self.display, offset=self.render_scroll)
        self.refresh_menu_float()
        
        self.render_status_menu()
        if self.level == 0:
            self.display_welcome()


        if self.level:
            self.running_timer()
            self.show_enemy_count()
        self.display_CD_block()





        self.check_level_loading()
        
        # print(self.total_time)

    

    def display_CD_block(self):
        dash_CD = self.player.get_dash_CD()
        CD_fraction = dash_CD / 60

        big_jump_CD = self.player.get_big_jump_CD()
        big_jump_CD_fraction = big_jump_CD / 300
        # print(CD_fraction)
        # print(big_jump_CD)


        BLOCK_SIZE = 32  # For example, adjust this value as needed.

        JUMP_CD_BLOCK = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE * big_jump_CD_fraction))
        pygame.draw.rect(JUMP_CD_BLOCK, (0, 0, 0), pygame.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE), )

        DASH_CD_block = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE * CD_fraction))
        pygame.draw.rect(DASH_CD_block, (0, 0, 0), pygame.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE), )
        

        DASH_CD_block.fill((255, 255, 255))  
        JUMP_CD_BLOCK.fill((255, 255, 255))
        
        DASH_CD_block.set_alpha(255)
        JUMP_CD_BLOCK.set_alpha(255)
        self.display.blit(self.keyboard_x, (40, self.display_HEIGHT - 40))

        self.display.blit(self.assets['e_key_diagram'], (80+self.assets['e_key_diagram'].get_width(), self.display_HEIGHT - 40))



        dash_UI_icon = self.raw_assets['dash_UI_icon']
        jump_UI_icon = self.raw_assets['jump_UI_icon']

        JUMP_CD_BLOCK.blit(jump_UI_icon, (0,0), special_flags=pygame.BLEND_RGBA_MULT)

        DASH_CD_block.blit(dash_UI_icon, (0,0), special_flags=pygame.BLEND_RGBA_MULT)

        self.display.blit(DASH_CD_block, (35, self.display_HEIGHT - 80))
        self.display.blit(JUMP_CD_BLOCK, (75+self.assets['e_key_diagram'].get_width(), self.display_HEIGHT - 80))


    def reset_movement(self):
        self.movement[0] = False
               
        self.movement[1] = False
    def display_welcome(self):
        arrow_keys = self.assets['arrow_keys_diagram']
        arrow_keys = pygame.transform.scale(arrow_keys,(arrow_keys.get_width()*2,arrow_keys.get_height()*2))
        
        self.display.blit(arrow_keys,(self.display.get_width()//2-arrow_keys.get_width()//2,60+self.menu_float))
        
        self.draw_text('USE ARROW KEYS TO MOVE', pygame.font.Font('minecraft.otf', 20), 'black', self.display, (52, 62+self.menu_float))
        self.draw_text('USE ARROW KEYS TO MOVE', pygame.font.Font('minecraft.otf', 20), 'white', self.display, (50, 60+self.menu_float))
        
        self.display.blit(self.keyboard_x,(self.display.get_width()/4*3-arrow_keys.get_width()//2,60+self.menu_float))
        self.draw_text('[X] TO DASH', pygame.font.Font('minecraft.otf', 20), 'black', self.display, (self.display.get_width()/4*3+2, 62+self.menu_float))
        self.draw_text('[X] TO DASH', pygame.font.Font('minecraft.otf', 20), 'white', self.display, (self.display.get_width()/4*3, 60+self.menu_float))

        
    def main_game(self):
        
        while True:
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
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_x:
                        self.player.dash()
                    if event.key == pygame.K_ESCAPE:
                        # print('menu triggered')
                        self.blurred = False
                        self.ingame_menu()
                    if event.key == pygame.K_e:
                        if self.player.big_jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_TAB:
                        self.show_status_menu = not self.show_status_menu
                        

                        
                    
                    if event.key == pygame.K_5:
                        self.level = 5
                        self.load_level(self.level)
                        self.reset_movement()
                        self.reset_player_status()
                        self.reset_current_level_timer()
                        self.main_game()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

                
                
            

            self.display.blit(self.assets['background'], (0, 0))
            self.EVERYTHING_render_update()
            



            
            
            self.screenshake = max(0, self.screenshake - 1)
            self.screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), self.screenshake_offset)
            pygame.display.update()

                        
            
            self.clock.tick(RUNNING_FPS)

    def draw_buttons(self):
        button_width = 150
        button_height = 50
        button_gap = 10
        start_y = 100

        for index, button_text in enumerate(self.menu_buttons):
            button_rect = pygame.Rect((self.display.get_width() - button_width) // 2, start_y + index * (button_height + button_gap) + self.menu_float, button_width, button_height)
            
            # Highlight the button if it's selected
            if index == self.button_selector:
                pygame.draw.rect(self.display, (255, 255, 0), button_rect)
            else:
                pygame.draw.rect(self.display, (255, 255, 255), button_rect)

            # Draw button text
            text_surf = pygame.font.Font('minecraft.otf', 20).render(button_text, True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=button_rect.center)
            self.display.blit(text_surf, text_rect)

    def help_page(self):
        pass
    def refresh_menu_float(self):
        self.x += 0.05
        self.x %= math.pi * 2
        self.menu_float = 5*math.sin(self.x)

    def reset_player_status(self):
        self.HP = 3

    def ingame_menu(self):


        self.button_selector = 0
        self.menu_buttons = ['Resume', 'Restart', 'Options', 'Main Menu']
  
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
               
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # print('game resumed')
                        self.reset_movement()
                        self.main_game()
                    if event.key == pygame.K_DOWN:
                        self.sfx['jump'].play()
                        self.button_selector += 1
                        self.button_selector %= len(self.menu_buttons)
                    if event.key == pygame.K_UP:
                        self.sfx['jump'].play()
                        self.button_selector -= 1
                        if self.button_selector < 0:
                            self.button_selector = len(self.menu_buttons)-1
                        self.button_selector %= len(self.menu_buttons)


                    if event.key == pygame.K_RETURN:
                        if self.menu_buttons[self.button_selector] == "Resume":
                            self.reset_movement()
                            self.main_game()
                        elif self.menu_buttons[self.button_selector] == "Restart":
                            self.restart_level()
                            

                        elif self.menu_buttons[self.button_selector] == "Options":
                            # Implement the Options functionality here
                            pass
                        elif self.menu_buttons[self.button_selector] == "Main Menu":
                            # Implement the Main Menu functionality here
                            pass

            



            if not self.blurred:
                pygame.image.save(self.display, 'screenshot.png')
                OriImage = Image.open('screenshot.png')
                blurImage = OriImage.filter(ImageFilter.GaussianBlur(2.5))
                #make blurimage darker
                enhancer = ImageEnhance.Brightness(blurImage)
                blurImage = enhancer.enhance(0.7)
                blurImage.save('simBlurImage.png')

                blurImageBG = pygame.image.load('simBlurImage.png')
                self.blurred = True
            
            self.display.blit(blurImageBG, [0, 0])

            # print(f'{self.button_selector} is selected')

            self.mouse_pos = pygame.mouse.get_pos()
            self.mouse_x = self.mouse_pos[0]//2
            self.mouse_y = self.mouse_pos[1]//2

            
            self.refresh_menu_float()

            
            self.draw_buttons()
            self.draw_text('Paused', pygame.font.Font('minecraft.otf', 20), 'white', self.display, (50, 50+self.menu_float))
            #display this image onto display, assets/keyboard_ESC.png, also 2x bigger
            self.display.blit(pygame.transform.scale(pygame.image.load('assets/keyboard_ESC.png'), (int(2*pygame.image.load('assets/keyboard_ESC.png').get_width()), int(2*pygame.image.load('assets/keyboard_ESC.png').get_height()))), (365, 50+self.menu_float))
            
            self.draw_text('Press      to go back to game', pygame.font.Font('minecraft.otf', 20), 'white', self.display, (300, 50+self.menu_float))
            pygame.draw.circle(self.display, (255, 0, 0), (self.mouse_x, self.mouse_y), 5)
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), self.screenshake_offset)
            pygame.display.update()
            self.clock.tick(RUNNING_FPS)

    
Game().main_game()