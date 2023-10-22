import sys
import math
import random
import os
import datetime
import json
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


# DISPLAYING_FPS = 120

class Game:
    def __init__(self):
        self.player_name = input('enter your name:')
        pygame.init()

        APPLE_FILE_CLEAR()
        self.x = 0

        pygame.display.set_caption('My game')
        self.window_size = (1280, 720)
        # self.window_size = (1920, 1080)
        self.screen = pygame.display.set_mode(self.window_size)
        self.display = pygame.Surface((640, 360), pygame.SRCALPHA)
        self.show_debug_menu = False
        self.textflash = 0

        self.display_WIDTH = self.display.get_width()
        self.display_HEIGHT = self.display.get_height()
        self.display_2 = pygame.Surface((640, 360))

        self.heart_animations = []
        self.total_time = 0
        self.current_level_time = 0
        self.restart_count = 0
        self.player_got_hit_count = 0
        self.in_main_menu = True
        self.render_scroll = [0, 0]

        self.level_keys = {
                    pygame.K_0: 0,
                    pygame.K_1: 1,
                    pygame.K_2: 2,
                    pygame.K_3: 3,
                    pygame.K_4: 4,
                    pygame.K_5: 5,
                    pygame.K_6: 6,
                    pygame.K_7: 7,
                }

        # Debug variables
        self.debug_timer = 0
        self.debug_font = pygame.font.Font(None, 30)
        self.debug_info_updated = False
        self.GRANDTOTAL_COUNTER = 0

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
            'player/run': Animation(load_images('entities/player/run'), img_dur=7),
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
            'e_key_diagram': load_image('objects/keyboard_Z.png'),
            'blurred_background': load_image('blurred_background.png'),
            'game_logo': load_image('objects/game_logo.png'),
            'in_game_pause_menu_status': pygame.image.load(
                'data/images/objects/in_game_pause_menu_status.png').convert_alpha(),
            'button_selector': load_image('objects/button_selector.png'),
            'leaderboard': load_image('objects/leaderboard.png'),
            'main_menu_buttons': pygame.image.load('data/images/objects/main_menu_buttons.png').convert_alpha(),
            'main_menu_button_selector': load_image('objects/main_menu_button_selector.png').convert_alpha(),
            'game_end_panel': pygame.image.load('data/images/objects/game_end_panel.png').convert_alpha(),

        }

        self.raw_assets = {
            'hearts': load_images('objects/hearts'),
            'dash_UI_icon': pygame.image.load('data/images/objects/dash_UI_icon.png').convert_alpha(),
            'jump_UI_icon': pygame.image.load('data/images/objects/jump_UI_icon.png').convert_alpha(),
            'stopwatch': pygame.image.load('data/images/objects/stopwatch.png').convert_alpha(),
            'status_menu': pygame.image.load('data/images/objects/status_menu.png').convert_alpha(),
            'menuidleplayer': load_images('entities/player/idle2x'),
            'skeleton': pygame.image.load('data/images/objects/skeleton.png').convert_alpha(),
            'arrows': pygame.image.load('data/images/objects/arrows.png').convert_alpha(),

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

        self.load_level('main_menu_map')
        self.level = 0

        self.screenshake = 0

        self.paused = False

        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.keyboard_x = self.assets['x_key_diagram']
        player_box_pos = (100, 140)  # Center of the player box
        self.playermodel = ObjectAnimation(player_box_pos, self.raw_assets['menuidleplayer'])

        self.button_selector_position = 69
        self.button_selector_target_position = 69
        self.button_selector_speed = 7

        self.end_panel_pos = -self.assets['game_end_panel'].get_height()
        self.end_panel_target_pos = (self.display_HEIGHT - self.assets['game_end_panel'].get_height()) // 2

        # if data/player_records.json doesnt exist, create a blank json file
        if not os.path.exists('data/player_records.json'):
            with open('data/player_records.json', 'w') as f:
                f.write('[]')

        for i in range(self.HP):
            pos = (i * (self.raw_assets['hearts'][0].get_width() * 1.5) + 20,
                   self.display_HEIGHT // 15)  # Change 32 and 10 accordingly
            self.heart_animations.append(ObjectAnimation(pos, self.raw_assets['hearts']))

        self.show_pause_menu = False
        self.pause_menu_position = -self.assets['in_game_pause_menu_status'].get_width()  # Start off-screen to the left
        self.pause_menu_target_position = (self.display_WIDTH - self.assets[
            'in_game_pause_menu_status'].get_width()) // 2  # Middle of the screen minus half the width of the status menu

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
        self.transition = -50

    def projectile_render_update(self):
        for projectile in self.projectiles.copy():
            projectile[0][0] += projectile[1]
            projectile[2] += 1
            img = self.assets['projectile']
            self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - self.render_scroll[0],
                                    projectile[0][1] - img.get_height() / 2 - self.render_scroll[1]))
            if self.tilemap.solid_check(projectile[0]):
                self.projectiles.remove(projectile)
                for i in range(4):
                    self.sparks.append(
                        Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0),
                              2 + random.random()))
            elif projectile[2] > 360:
                self.projectiles.remove(projectile)
            elif abs(self.player.dashing) < 50:
                if self.player.rect().collidepoint(projectile[0]):
                    self.projectiles.remove(projectile)
                    self.HP -= 1
                    self.player_got_hit_count += 1
                    self.sfx['hit'].play()
                    self.screenshake = max(16, self.screenshake)
                    for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                        self.particles.append(Particle(self, 'particle', self.player.rect().center,
                                                       velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                 math.sin(angle + math.pi) * speed * 0.5],
                                                       frame=random.randint(0, 7)))

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

        # if in_main_menu: the camera should be higher
        if self.in_main_menu:
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) // 30 - 4
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) // 30 - 3
        else:
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) // 30
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) // 30

        self.render_scroll = [int(self.scroll[0]), int(self.scroll[1])]

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

        self.restart_count += 1
        self.load_level(self.level)
        self.reset_movement()
        self.reset_player_status()
        self.reset_current_level_timer()
        self.main_game()

    def draw_hearts(self):
        for heart in self.heart_animations[:self.HP]:
            heart.animate(pygame.time.get_ticks())
            heart.draw(self.display)

    def save_global_time(self):
        self.total_time += self.current_level_time
        self.current_level_time = 0

    def check_level_loading(self):

        if self.level == len(os.listdir('data/maps')) - 2 and not len(self.enemies):
            self.save_global_time()
            # wait 2 seconds, then go to game_end

            self.game_finished = True
            self.game_end()

        if not len(self.enemies):

            self.transition += 1
            if self.transition > 40:
                self.level += 1

                self.save_global_time()

                if self.level == len(os.listdir('data/maps')) - 1:
                    print('GAME FINISHED')
                else:

                    self.load_level(self.level)

        if self.transition < 0:
            self.transition += 1

        if self.HP <= 0:
            self.dead += 1
        if self.dead:
            self.dead += 1
            if self.dead >= 10:
                self.transition = min(40, self.transition)
            if self.dead > 40:
                self.restart_level()

        if self.transition:
            transition_surf = pygame.Surface(self.display.get_size())
            pygame.draw.circle(transition_surf, (255, 255, 255),
                               (self.display.get_width() // 2, self.display.get_height() // 2),
                               (45 - abs(self.transition)) * 8)
            transition_surf.set_colorkey((255, 255, 255))
            self.display.blit(transition_surf, (0, 0))

    def render_end_game_panel(self):

        game_end_panel = self.assets['game_end_panel'].copy()
        print('rendering end game panel')

        target = self.end_panel_target_pos

        difference = target - self.end_panel_pos
        normalized_difference = abs(difference) / game_end_panel.get_width()

        if normalized_difference > 1:
            normalized_difference = 1
        elif normalized_difference < 0:
            normalized_difference = 0

        # Calculate progress using the easing function
        progress = ease_out_quad(normalized_difference)

        if difference > 0:
            self.end_panel_pos += 13 * progress
            if self.end_panel_pos > target:
                self.leaderboard_position = target
        else:
            self.end_panel_pos -= 13 * progress
            if self.end_panel_pos < target:
                self.end_panel_pos = target

        render_pos = (self.display_WIDTH // 2 - game_end_panel.get_width() // 2, self.end_panel_pos + self.menu_float)

        # draw text that says extra timef
        self.draw_text('EXTRA TIME:', pygame.font.Font('minecraft.otf', 20), 'black', game_end_panel, (27, 89))
        self.draw_text('EXTRA TIME:', pygame.font.Font('minecraft.otf', 20), 'white', game_end_panel, (26, 88))
        # self.draw_text(f'Player got hit: {self.player_got_hit_count} -> {self.player_got_hit_count*1}s', pygame.font.Font('minecraft.otf', 10), 'black', game_end_panel, ( 201,  166))
        self.draw_text(f'Player got hit: {self.player_got_hit_count} -> ', pygame.font.Font('minecraft.otf', 10),
                       'white', game_end_panel, (200, 165))
        self.draw_text(f'{self.player_got_hit_count * 1}s', pygame.font.Font('minecraft.otf', 10), 'red',
                       game_end_panel, (200 + pygame.font.Font('minecraft.otf', 10).size(
                f'Player got hit: {self.player_got_hit_count} -> ')[0], 165))

        # Draw arrow image a bit below the text
        game_end_panel.blit(self.raw_assets['arrows'], (200, + 125))

        # Draw the text "Restart count:" and the associated count, below the arrow image
        # self.draw_text(f'Restart count: {self.restart_count} -> {self.restart_count*5}s', pygame.font.Font('minecraft.otf', 10), 'black', game_end_panel, (31,  + 166))
        self.draw_text(f'Restart count: {self.restart_count} -> ', pygame.font.Font('minecraft.otf', 10), 'white',
                       game_end_panel, (30, + 165))
        # {self.restart_count*5}s is red
        self.draw_text(f'{self.restart_count * 5}s', pygame.font.Font('minecraft.otf', 10), 'red', game_end_panel, (
            30 + pygame.font.Font('minecraft.otf', 10).size(f'Restart count: {self.restart_count} -> ')[0], 165))

        game_end_panel.blit(self.raw_assets['skeleton'], (50, 125))

        # total total time
        self.draw_text(f'TOTAL TIME:', self.font, 'black', game_end_panel, (27, 196))
        self.draw_text(f'TOTAL TIME:', self.font, 'white', game_end_panel, (26, 195))

        self.textflash += 1

        if self.textflash > 60:
            basetime = round(self.total_time, 1)
            # draw a black
            self.draw_text(f'{basetime}', self.font, 'black', game_end_panel, (27, 227))
            self.draw_text(f'{basetime}', self.font, 'white', game_end_panel, (26, 226))

        if self.textflash > 120:
            # draw a black

            self.draw_text(f'+ {self.restart_count * 5}', self.font, 'black', game_end_panel,
                           (26 + self.font.size(f'{round(self.total_time, 1)} ')[0] + 1, 227))
            self.draw_text(f'+ {self.restart_count * 5}', self.font, 'red', game_end_panel,
                           (26 + self.font.size(f'{round(self.total_time, 1)} ')[0], 226))

        if self.textflash > 180:
            # draw a black
            self.draw_text(f'+ {self.player_got_hit_count}', self.font, 'black', game_end_panel, (
                26 + self.font.size(f'{round(self.total_time, 1)} + {self.restart_count * 5} ')[0] + 1, 227))
            self.draw_text(f'+ {self.player_got_hit_count}', self.font, 'red', game_end_panel,
                           (26 + self.font.size(f'{round(self.total_time, 1)} + {self.restart_count * 5} ')[0], 226))

        if self.textflash > 240:
            # add a = sign
            self.draw_text(f'=', self.font, 'black', game_end_panel, (26 + self.font.size(
                f'{round(self.total_time, 1)} + {self.restart_count * 5} + {self.player_got_hit_count} ')[0] + 1, 227))

            self.draw_text(f'=', self.font, 'white', game_end_panel, (26 + self.font.size(
                f'{round(self.total_time, 1)} + {self.restart_count * 5} + {self.player_got_hit_count} ')[0], 226))

        GRANDTOTAL = round(self.total_time + 5 * self.restart_count + self.player_got_hit_count, 1)
        if self.textflash > 300:
            if GRANDTOTAL - self.GRANDTOTAL_COUNTER > 1:

                self.GRANDTOTAL_COUNTER += 1
            elif GRANDTOTAL - self.GRANDTOTAL_COUNTER <= 1:
                self.GRANDTOTAL_COUNTER += 0.1

            if self.GRANDTOTAL_COUNTER > GRANDTOTAL:
                self.GRANDTOTAL_COUNTER = GRANDTOTAL

            td = datetime.timedelta(seconds=int(self.GRANDTOTAL_COUNTER))
            fractional_seconds = round(self.GRANDTOTAL_COUNTER % 1, 1)
            time_formatted = f"{(td.seconds // 60) % 60:02}:{td.seconds % 60:02}.{int(10 * fractional_seconds)}"

            # increment to the grandtotal
            self.draw_text(f'{time_formatted}', self.font, 'black', game_end_panel, (26 + self.font.size(
                f'{round(self.total_time, 1)} + {self.restart_count * 5} + {self.player_got_hit_count} = ')[0] + 1,
                                                                                     227))
            self.draw_text(f'{time_formatted}', self.font, 'white', game_end_panel, (26 + self.font.size(
                f'{round(self.total_time, 1)} + {self.restart_count * 5} + {self.player_got_hit_count} = ')[0], 226))

        # put a flashing text at the buttom of the panel, say PRESS ENTER FOR MAIN MENU

        # print(self.textflash)
        if self.textflash % 60 < 30:
            # but the text middled at the buttom of the panel
            self.draw_text('PRESS ENTER FOR MAIN MENU', self.font, 'black', game_end_panel, (
                game_end_panel.get_width() // 2 - self.font.size('PRESS ENTER FOR MAIN MENU')[0] // 2 + 1,
                game_end_panel.get_height() - 49))
            self.draw_text('PRESS ENTER FOR MAIN MENU', self.font, 'white', game_end_panel, (
                game_end_panel.get_width() // 2 - self.font.size('PRESS ENTER FOR MAIN MENU')[0] // 2,
                game_end_panel.get_height() - 50))

        self.display.blit(game_end_panel, render_pos)

    def game_end(self):
        self.screenshot_taken = False
        today = datetime.date.today()
        current_time = datetime.datetime.now().strftime('%H:%M')

        player_record_entry = {
            'player name': self.player_name,
            'total time': round(self.total_time + 5 * self.restart_count + self.player_got_hit_count, 1),
            'raw time': round(self.total_time, 5),
            'got hit count': self.player_got_hit_count,
            'restart count': self.player_got_hit_count,
            'completed datetime': f'{today} @ {current_time}'
        }

        # Proper way to update the JSON file
        with open('data/player_records.json', 'r') as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:  # In case the file is empty or has invalid JSON format
                data = []

        data.append(player_record_entry)

        with open('data/player_records.json', 'w') as f:
            json.dump(data, f, indent=4)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.entire_game_reset()
                        self.main_menu()

            if not self.screenshot_taken:
                if self.pause_menu_position < -490:
                    pygame.image.save(self.display, 'screenshot.png')
                OriImage = Image.open('screenshot.png')
                screenshot_no_blur = pygame.image.load('screenshot.png')
                blurImage = OriImage.filter(ImageFilter.GaussianBlur(2.5))
                # make blurimage darker
                enhancer = ImageEnhance.Brightness(blurImage)
                blurImage = enhancer.enhance(0.7)
                blurImage.save('simBlurImage.png')
                print('screenshot taken')

                blurImageBG = pygame.image.load('simBlurImage.png')
                self.screenshot_taken = True

            self.display.blit(screenshot_no_blur, (0, 0))
            self.refresh_menu_float()
            self.update_debug_stuff()

            self.render_end_game_panel()

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), self.screenshake_offset)
            if self.show_debug_menu:
                self.screen.blit(self.debug_surface, (0, 0))
            pygame.display.update()
            self.clock.tick(RUNNING_FPS)

    def running_timer(self):
        #use
        self.current_level_time += 1 / RUNNING_FPS
        
        

        time_text = str(datetime.timedelta(seconds=round(self.current_level_time, 0)))
        self.draw_text(time_text, pygame.font.Font('minecraft.otf', 20), 'black', self.display, (
            self.display_WIDTH // 20 * 16.5 - self.raw_assets['stopwatch'].get_width() // 2 + 4, 34 + self.menu_float))
        self.draw_text(time_text, pygame.font.Font('minecraft.otf', 20), 'white', self.display, (
            self.display_WIDTH // 20 * 16.5 - self.raw_assets['stopwatch'].get_width() // 2 + 2, 32 + self.menu_float))

        # also display the total time+current level time, in a smaller font, at the top right corner, below the current_level_time timer
        total_time_text = str(datetime.timedelta(seconds=round(self.total_time + self.current_level_time, 0)))
        self.draw_text(total_time_text, pygame.font.Font('minecraft.otf', 10), 'black', self.display, (
            self.display_WIDTH // 20 * 16.5 - self.raw_assets['stopwatch'].get_width() // 2 + 3, 53 + self.menu_float))

        self.draw_text(total_time_text, pygame.font.Font('minecraft.otf', 10), 'white', self.display, (
            self.display_WIDTH // 20 * 16.5 - self.raw_assets['stopwatch'].get_width() // 2 + 2, 52 + self.menu_float))

        self.display.blit(self.raw_assets['stopwatch'], (
            self.display_WIDTH // 20 * 19 - self.raw_assets['stopwatch'].get_width() // 2, 20 + self.menu_float))

    def show_enemy_count(self):
        self.display.blit(self.assets['enemy_head'],
                          (self.display_WIDTH // 20 * 1, self.display_HEIGHT // 20 * 4 + self.menu_float))
        self.draw_text(f'x {len(self.enemies)}', pygame.font.Font('minecraft.otf', 20), 'black', self.display,
                       (self.display_WIDTH // 20 * 2.3 + 2, self.display_HEIGHT // 20 * 4.5 + self.menu_float + 2))
        self.draw_text(f'x {len(self.enemies)}', pygame.font.Font('minecraft.otf', 20), 'white', self.display,
                       (self.display_WIDTH // 20 * 2.3, self.display_HEIGHT // 20 * 4.5 + self.menu_float))

    def show_level_number(self):
        # show level number at the buttom right corner of the screen
        if self.level == 0:
            level_name = 'Tutorial'
        else:
            level_name = f'Level {self.level}'

        self.draw_text(level_name, pygame.font.Font('minecraft.otf', 20), 'black', self.display, (
            self.display_WIDTH // 20 * 18.5 - self.font.size(level_name)[0] // 2 + 2,
            self.display_HEIGHT // 20 * 18.5 - self.font.size(level_name)[1] // 2 + 2 + self.menu_float))

        self.draw_text(level_name, pygame.font.Font('minecraft.otf', 20), 'white', self.display, (
            self.display_WIDTH // 20 * 18.5 - self.font.size(level_name)[0] // 2,
            self.display_HEIGHT // 20 * 18.5 - self.font.size(level_name)[1] // 2 + self.menu_float))

    def displayUI_EVERYTHING(self):
        self.refresh_menu_float()
        self.render_pause_menu()
        self.draw_hearts()
        if self.level == 0:
            self.display_welcome()
        if self.level:
            self.running_timer()
            self.show_enemy_count()
        self.display_CD_block()
    
        self.show_level_number()

    def update_debug_stuff(self):

        self.debug_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)

        currentFPS = f'FPS: {self.clock.get_fps():.0f}'

        if self.show_debug_menu:
            # display different variables

            self.draw_text(currentFPS, self.debug_font, 'white', self.debug_surface,
                           (self.debug_surface.get_width() - 100, 0))

            self.draw_text(f'self.level: {self.level}', self.debug_font, 'white', self.debug_surface, (0, 0))
            self.draw_text(f'self.pause_menu_position: {self.pause_menu_position}', self.debug_font, 'white',
                           self.debug_surface, (0, 25))
            self.draw_text(f'self.transition: {self.transition}', self.debug_font, 'white', self.debug_surface, (0, 50))
            self.draw_text(f'self.dead: {self.dead}', self.debug_font, 'white', self.debug_surface, (0, 75))
            self.draw_text(f'self.restart_count: {self.restart_count}', self.debug_font, 'white', self.debug_surface,
                           (0, 100))
            self.draw_text(f'self.player_got_hit_count: {self.player_got_hit_count}', self.debug_font, 'white',
                           self.debug_surface, (0, 125))
            self.draw_text(f'self.total_time: {self.total_time}', self.debug_font, 'white', self.debug_surface,
                           (0, 150))
            self.draw_text(f'self.current_level_time: {self.current_level_time}', self.debug_font, 'white',
                           self.debug_surface, (0, 175))
            self.draw_text(f'self.player_name: {self.player_name}', self.debug_font, 'white', self.debug_surface,
                           (0, 200))
            self.draw_text(f'self.menu_float: {self.menu_float}', self.debug_font, 'white', self.debug_surface,
                           (0, 225))
            self.draw_text(f'self.player.pos: {self.player.pos}', self.debug_font, 'white', self.debug_surface,
                           (0, 250))
            self.draw_text(f'self.player.rect(): {self.player.rect()}', self.debug_font, 'white', self.debug_surface,
                           (0, 275))
            self.draw_text(f'self.player.air_time: {self.player.air_time}', self.debug_font, 'white',
                           self.debug_surface, (0, 300))
            self.draw_text(f'self.player.dashing: {self.player.dashing}', self.debug_font, 'white', self.debug_surface,
                           (0, 325))
            self.draw_text(f'self.player.big_jump_cd: {self.player.big_jump_cd}', self.debug_font, 'white',
                           self.debug_surface, (0, 350))
            self.draw_text(f'self.player.velocity: {self.player.velocity}', self.debug_font, 'white',
                           self.debug_surface, (0, 375))

            self.draw_text(f'self.player: {self.player}', self.debug_font, 'white', self.debug_surface, (0, 400))
            self.draw_text(f'self.show_pause_menu: {self.show_pause_menu}', self.debug_font, 'white',
                           self.debug_surface, (0, 425))
            self.draw_text(f'self.button_selector_position: {self.button_selector_position}', self.debug_font, 'white',
                           self.debug_surface, (0, 450))
            self.draw_text(f'self.end_panel_pos: {self.end_panel_pos}', self.debug_font, 'white', self.debug_surface,
                           (0, 475))
            self.draw_text(f'len(self.enemies): {len(self.enemies)}', self.debug_font, 'white', self.debug_surface,
                           (0, 500))
            self.draw_text(f'self.screenshake: {self.screenshake}', self.debug_font, 'white', self.debug_surface,
                           (0, 525))
            self.draw_text(f'self.scroll: {self.scroll}', self.debug_font, 'white', self.debug_surface, (0, 550))
            self.draw_text(f'self.render_scroll: {self.render_scroll}', self.debug_font, 'white', self.debug_surface,
                           (0, 575))
            self.draw_text(f'self.movement: {self.movement}', self.debug_font, 'white', self.debug_surface, (0, 600))
            self.draw_text(f'self.end_panel_pos: {self.end_panel_pos}', self.debug_font, 'white', self.debug_surface,
                           (0, 625))

            # self.display.blit(pygame.transform.scale(self.debug_surface, self.display.get_size()), (0,0))
            self.debug_info_updated = True

    def EVERYTHING_render_update(self):

        self.scroll_update()
        self.projectile_render_update()
        self.spark_particle_render_update()
        self.cloud_leaf_render_update()
        self.entity_render_update()

        self.tilemap.render(self.display, offset=self.render_scroll)

        if self.in_main_menu:
            self.render_main_menu_panel()
            self.render_leaderboard()

        if not self.in_main_menu:
            self.displayUI_EVERYTHING()

        self.check_level_loading()

        # Assuming you're measuring delta time each frame with dt
        if self.show_debug_menu:
            self.update_debug_stuff()

    def display_CD_block(self):
        dash_CD = self.player.get_dash_CD()
        CD_fraction = dash_CD / 60

        big_jump_CD = self.player.get_big_jump_CD()
        big_jump_CD_fraction = big_jump_CD / self.player.big_jump_max_cd
        # print(CD_fraction)
        # print(big_jump_CD)

        BLOCK_SIZE = 32

        JUMP_CD_BLOCK = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE * big_jump_CD_fraction))
        pygame.draw.rect(JUMP_CD_BLOCK, (0, 0, 0), pygame.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE), )

        DASH_CD_block = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE * CD_fraction))
        pygame.draw.rect(DASH_CD_block, (0, 0, 0), pygame.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE), )

        DASH_CD_block.fill((255, 255, 255))
        JUMP_CD_BLOCK.fill((255, 255, 255))

        DASH_CD_block.set_alpha(255)
        JUMP_CD_BLOCK.set_alpha(255)
        self.display.blit(self.keyboard_x, (40, self.display_HEIGHT - 40))

        self.display.blit(self.assets['e_key_diagram'],
                          (80 + self.assets['e_key_diagram'].get_width(), self.display_HEIGHT - 40))

        dash_UI_icon = self.raw_assets['dash_UI_icon']
        jump_UI_icon = self.raw_assets['jump_UI_icon']

        JUMP_CD_BLOCK.blit(jump_UI_icon, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        DASH_CD_block.blit(dash_UI_icon, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        self.display.blit(DASH_CD_block, (35, self.display_HEIGHT - 80))
        self.display.blit(JUMP_CD_BLOCK, (75 + self.assets['e_key_diagram'].get_width(), self.display_HEIGHT - 80))

    def reset_movement(self):
        self.movement[0] = False

        self.movement[1] = False

    def display_welcome(self):
        arrow_keys = self.assets['arrow_keys_diagram']
        arrow_keys = pygame.transform.scale(arrow_keys, (arrow_keys.get_width() * 2, arrow_keys.get_height() * 2))

        self.display.blit(arrow_keys,
                          (self.display.get_width() // 2 - arrow_keys.get_width() // 2, 60 + self.menu_float))

        self.draw_text('USE ARROW KEYS TO MOVE', pygame.font.Font('minecraft.otf', 20), 'black', self.display,
                       (52, 62 + self.menu_float))
        self.draw_text('USE ARROW KEYS TO MOVE', pygame.font.Font('minecraft.otf', 20), 'white', self.display,
                       (50, 60 + self.menu_float))

        self.display.blit(self.keyboard_x,
                          (self.display.get_width() / 4 * 3 - arrow_keys.get_width() // 2, 60 + self.menu_float))
        self.draw_text('TO DASH', pygame.font.Font('minecraft.otf', 20), 'black', self.display,
                       (self.display.get_width() / 4 * 3 + 2, 62 + self.menu_float))
        self.draw_text('TO DASH', pygame.font.Font('minecraft.otf', 20), 'white', self.display,
                       (self.display.get_width() / 4 * 3, 60 + self.menu_float))

        # e to super dash

        self.display.blit(self.assets['e_key_diagram'],
                          (self.display.get_width() / 4 * 3 - arrow_keys.get_width() // 2, 100 + self.menu_float))
        self.draw_text('TO SUPER JUMP', pygame.font.Font('minecraft.otf', 20), 'black', self.display,
                       (self.display.get_width() / 4 * 3 + 2, 102 + self.menu_float))
        self.draw_text('TO SUPER JUMP', pygame.font.Font('minecraft.otf', 20), 'white', self.display,
                       (self.display.get_width() / 4 * 3, 100 + self.menu_float))

    def main_game(self):
        self.GRANDTOTAL_COUNTER = 0
        self.end_panel_pos = -self.assets['game_end_panel'].get_height()

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

                        self.show_pause_menu = not self.show_pause_menu
                        self.ingame_menu()
                    if event.key == pygame.K_z:
                        if self.player.big_jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_TAB:
                        print('bruh')
                    if event.key == pygame.K_RETURN:
                        if self.game_end:
                            self.entire_game_reset()
                            self.main_menu()

                

                    if event.key in self.level_keys:
                        self.level = self.level_keys[event.key]
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
            self.screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2,
                                       random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), self.screenshake_offset)
            if self.show_debug_menu:
                self.screen.blit(self.debug_surface, (0, 0))
            pygame.display.update()

            self.clock.tick(RUNNING_FPS)


    def refresh_menu_float(self):
        self.x += 0.05
        self.x %= math.pi * 2
        self.menu_float = 5 * math.sin(self.x)

    def reset_player_status(self):
        self.show_pause_menu = False
        # reset CD
        self.player.big_jump_cd = 0
        self.HP = 3

    def global_stats_reset(self):
        self.player_got_hit_count = 0
        self.restart_count = 0
        self.total_time = 0

    def entire_game_reset(self):
        self.reset_player_status()
        self.global_stats_reset()

        self.current_level_time = 0
        self.level = 1
        # print(self.level)
        self.reset_movement()

    def render_pause_menu(self):
        speed = 30
        if self.show_pause_menu:
            progress = ease_out_quad((self.pause_menu_target_position - self.pause_menu_position) / self.assets[
                'in_game_pause_menu_status'].get_width())
            self.pause_menu_position += speed * progress
            # Cap the position to the target if it overshoots due to the easing function
            if self.pause_menu_position > self.pause_menu_target_position:
                self.pause_menu_position = self.pause_menu_target_position
        else:
            progress = ease_out_quad(
                (self.pause_menu_position + self.assets['in_game_pause_menu_status'].get_width()) / self.assets[
                    'in_game_pause_menu_status'].get_width())
            self.pause_menu_position -= speed * progress
            # Cap the position to negative width of the menu if it overshoots due to the easing function
            if self.pause_menu_position < -self.assets['in_game_pause_menu_status'].get_width():
                self.pause_menu_position = -self.assets['in_game_pause_menu_status'].get_width()
        # print(self.pause_menu_position)
        status_menu = self.assets['in_game_pause_menu_status'].copy()
        # also add a render of player sprite, on the player box, the player box is a 82x94 box within the status_menu, with its left top corner at (61,81), onto the status_menu surface

        self.playermodel.animate(pygame.time.get_ticks())
        self.playermodel.draw(status_menu)

        self.draw_text(self.player_name, (font := pygame.font.Font('minecraft.otf', 20)), 'black', status_menu,
                       (108 - font.size(self.player_name)[0] // 2 + 1, 20 - font.size(self.player_name)[1] // 2 + 1))
        self.draw_text(self.player_name, (font := pygame.font.Font('minecraft.otf', 20)), 'white', status_menu,
                       (108 - font.size(self.player_name)[0] // 2, 20 - font.size(self.player_name)[1] // 2))
        # Define the top-left coordinates of the stats panel
        stats_panel_x, stats_panel_y = 383, 88

        # Draw the text "Player got hit:" and the associated count
        self.draw_text(f'Player got hit: {self.player_got_hit_count}', pygame.font.Font('minecraft.otf', 10), '#6b5153',
                       status_menu, (stats_panel_x + 6, stats_panel_y + 12))

        # Draw arrow image a bit below the text
        status_menu.blit(self.raw_assets['arrows'], (stats_panel_x + 6, stats_panel_y + 32))

        # Draw the text "Restart count:" and the associated count, below the arrow image
        self.draw_text(f'Restart count: {self.restart_count}', pygame.font.Font('minecraft.otf', 10), '#6b5153',
                       status_menu, (stats_panel_x + 6, stats_panel_y + 72))

        status_menu.blit(self.raw_assets['skeleton'], (stats_panel_x + 6, stats_panel_y + 92))

        # draw the button_selector onto the buttons according the variable self.button_selector

        self.button_selector_target_position = 69 + self.button_selector * 51

        difference = self.button_selector_target_position - self.button_selector_position

        # Normalize the difference for the easing function
        normalized_difference = abs(difference) / 51.0
        if normalized_difference > 2:
            self.button_selector_speed = 20
        else:
            self.button_selector_speed = 7

        # If the normalized difference is out of bounds, correct it
        if normalized_difference > 1:
            normalized_difference = 1
        elif normalized_difference < 0:
            normalized_difference = 0

        # Calculate progress using the easing function
        progress = ease_out_quad(normalized_difference)

        if difference > 0:
            self.button_selector_position += self.button_selector_speed * progress
            if self.button_selector_position > self.button_selector_target_position:
                self.button_selector_position = self.button_selector_target_position
        else:
            self.button_selector_position -= self.button_selector_speed * progress
            if self.button_selector_position < self.button_selector_target_position:
                self.button_selector_position = self.button_selector_target_position

        # print(f'self.button_selector_position{self.button_selector_position}')

        button_selector_loc = (173, self.button_selector_position)
        status_menu.blit(self.assets['button_selector'], button_selector_loc)

        # Draw skeleton image a bit below the second text

        # self.draw_text(self.player_name, pygame.font.Font('minecraft.otf', 20), 'black', status_menu, (68+102//2-self.font.size(self.player_name)[0]//2, 47+10-self.font.size(self.player_name)[1]//2))
        # self.draw_text(self.player_name, pygame.font.Font('minecraft.otf', 20), 'white', status_menu, (67+102//2-self.font.size(self.player_name)[0]//2, 46+10-self.font.size(self.player_name)[1]//2))

        self.display.blit(status_menu, (
            self.pause_menu_position,
            self.display_HEIGHT / 2 - self.assets['in_game_pause_menu_status'].get_height() / 2))

    def ingame_menu(self):

        self.screenshot_taken = False
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
                        self.show_pause_menu = not self.show_pause_menu
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
                            self.button_selector = len(self.menu_buttons) - 1
                        self.button_selector %= len(self.menu_buttons)

                    if event.key == pygame.K_RETURN:
                        if self.menu_buttons[self.button_selector] == "Resume":
                            self.show_pause_menu = False
                            self.reset_movement()
                            self.main_game()
                        elif self.menu_buttons[self.button_selector] == "Restart":

                            self.restart_level()


                        elif self.menu_buttons[self.button_selector] == "Options":
                            self.show_debug_menu = not self.show_debug_menu
                            print('debug menu show has been set to', self.show_debug_menu)
                            pass
                        elif self.menu_buttons[self.button_selector] == "Main Menu":
                            self.entire_game_reset()

                            self.main_menu()

            if not self.screenshot_taken:
                if self.pause_menu_position < -490:
                    pygame.image.save(self.display, 'screenshot.png')
                OriImage = Image.open('screenshot.png')
                screenshot_no_blur = pygame.image.load('screenshot.png')
                blurImage = OriImage.filter(ImageFilter.GaussianBlur(2.5))
                # make blurimage darker
                enhancer = ImageEnhance.Brightness(blurImage)
                blurImage = enhancer.enhance(0.7)
                blurImage.save('simBlurImage.png')

                blurImageBG = pygame.image.load('simBlurImage.png')
                self.screenshot_taken = True

            # self.display.blit(blurImageBG, [0, 0])
            
            self.display.blit(screenshot_no_blur, (0, 0))

            self.render_pause_menu()

            self.update_debug_stuff()
            # print(f'{self.button_selector} is selected')

            # self.mouse_pos = pygame.mouse.get_pos()
            # self.mouse_x = self.mouse_pos[0]//2
            # self.mouse_y = self.mouse_pos[1]//2

            self.refresh_menu_float()


            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), self.screenshake_offset)
            if self.show_debug_menu:
                self.screen.blit(self.debug_surface, (0, 0))
            pygame.display.update()
            self.clock.tick(RUNNING_FPS)

    def render_leaderboard(self):

        leaderboard = self.assets['leaderboard'].copy()
        if self.menu_buttons[self.button_selector] == "Leaderboard":
            target = self.leaderboard_target_position
        else:
            target = self.display_WIDTH - 20

        difference = target - self.leaderboard_position
        normalized_difference = abs(difference) / leaderboard.get_width()

        # If the normalized difference is out of bounds, correct it
        if normalized_difference > 1:
            normalized_difference = 1
        elif normalized_difference < 0:
            normalized_difference = 0

        # Calculate progress using the easing function
        progress = ease_out_quad(normalized_difference)

        if difference > 0:
            self.leaderboard_position += 13 * progress
            if self.leaderboard_position > target:
                self.leaderboard_position = target
        else:
            self.leaderboard_position -= 13 * progress
            if self.leaderboard_position < target:
                self.leaderboard_position = target

        with open("data/player_records.json", "r") as f:
            data = json.load(f)

        # 2. Select the Best 9 Entries
        sorted_data = sorted(data, key=lambda x: x["total time"])[:9]

        # Define a starting position for the entries
        start_x = 35  # Adjust as needed
        start_y = 80  # Adjust as needed

        # Define a gap between entries for spacing
        gap = 16  # Adjust as needed

        # Use a font to render the entries
        font = pygame.font.Font('minecraft.otf', 10)

        # 3. Display the Entries on the Leaderboard
        for index, entry in enumerate(sorted_data, 1):  # Start index from 1
            total_time_seconds = entry['total time']
            # format the time into minutes and seconds
            if total_time_seconds >= 60:
                if total_time_seconds % 60 < 10:
                    total_time_formatted_seconds = f'0{int(total_time_seconds % 60)}'
                else:
                    total_time_formatted_seconds = int(total_time_seconds % 60)
                fraction_part = round(total_time_seconds - int(total_time_seconds),1)
                fraction_part = str(fraction_part)[2:]
                total_time_formatted = f'{int(total_time_seconds // 60)}:{total_time_formatted_seconds}.{fraction_part}'
            else:
                total_time_formatted = total_time_seconds

            text = f"{index}. {entry['player name']} {total_time_formatted}"
            text_surface = font.render(text, True, (255, 255, 255))  # Render in white color, adjust as needed
            text_rect = text_surface.get_rect(topleft=(start_x, start_y + index * gap))
            # add another black shadow layer underneath the text
            text_surface_shadow = font.render(text, True, (0, 0, 0))
            text_rect_shadow = text_surface_shadow.get_rect(topleft=(start_x + 1, start_y + index * gap + 1))
            leaderboard.blit(text_surface_shadow, text_rect_shadow)

            leaderboard.blit(text_surface, text_rect)


        # BLIT IMAGE of LEADERBOARD , on the right-hand side with updated position
        self.display.blit(leaderboard, (self.leaderboard_position, self.display_HEIGHT // 20 * 1 + self.menu_float))

    def render_main_menu_panel(self):

        self.main_menu_panel = self.assets['main_menu_buttons'].copy()
        self.main_menu_button_selector_target_position = 16 + self.button_selector * 45


        difference = self.main_menu_button_selector_target_position - self.main_menu_button_selector_position
        normalized_difference = abs(difference) / 45

        if normalized_difference > 2:
            self.button_selector_speed = 20
        else:
            self.button_selector_speed = 7

        # If the normalized difference is out of bounds, correct it
        if normalized_difference > 1:
            normalized_difference = 1
        elif normalized_difference < 0:
            normalized_difference = 0

        # Calculate progress using the easing function
        progress = ease_out_quad(normalized_difference)

        if difference > 0:
            self.main_menu_button_selector_position += self.button_selector_speed * progress
            if self.main_menu_button_selector_position > self.main_menu_button_selector_target_position:
                self.main_menu_button_selector_position = self.main_menu_button_selector_target_position
        else:
            self.main_menu_button_selector_position -= self.button_selector_speed * progress
            if self.main_menu_button_selector_position < self.main_menu_button_selector_target_position:
                self.main_menu_button_selector_position = self.main_menu_button_selector_target_position

        self.main_menu_panel.blit(self.assets['main_menu_button_selector'],
                                  (74, self.main_menu_button_selector_position))
        self.display.blit(self.main_menu_panel,
                          (self.display_WIDTH // 20 * 1, self.display_HEIGHT // 20 * 7 + self.menu_float))

    def main_menu(self):

        self.game_finished = False
        self.in_main_menu = True
        self.textflash = 0

        self.leaderboard_position = self.assets['leaderboard'].get_width() + self.display_WIDTH
        self.leaderboard_target_position = self.display_WIDTH // 20 * 15 - self.assets['leaderboard'].get_width() // 2

        self.load_level('main_menu_map')
        # Load background image (Make sure you have a `background.jpg` in your assets)
        background = pygame.image.load('data/images/background.png').convert()
        background = pygame.transform.scale(background, (self.display_WIDTH, self.display_HEIGHT))

        # Define the buttons
        self.menu_buttons = ["Start", "Options", "Leaderboard", "Quit"]
        self.button_selector = 0

        self.main_menu_button_selector_position = 16
        self.main_menu_button_selector_target_position = 16

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.sfx['jump'].play()
                        self.button_selector += 1
                        self.button_selector %= len(self.menu_buttons)
                    if event.key == pygame.K_UP:
                        self.sfx['jump'].play()
                        self.button_selector -= 1
                        if self.button_selector < 0:
                            self.button_selector = len(self.menu_buttons) - 1
                        self.button_selector %= len(self.menu_buttons)

                    if event.key == pygame.K_RETURN:
                        if self.menu_buttons[self.button_selector] == "Start":
                            self.load_level(self.level)
                            self.in_main_menu = False
                            self.reset_movement()
                            self.reset_player_status()
                            self.show_status_menu = False
                            self.main_game()

                            # print(self.level)

                        elif self.menu_buttons[self.button_selector] == "Options":
                            self.show_debug_menu = not self.show_debug_menu
                            print('debug menu show has been set to', self.show_debug_menu)
                        elif self.menu_buttons[self.button_selector] == "Leaderboard":
                            # Implement the Leaderboard functionality here
                            pass
                        elif self.menu_buttons[self.button_selector] == "Quit":

                            pygame.quit()
                            sys.exit()

            # Rendering
            self.display.blit(self.assets['background'], (0, 0))

            self.refresh_menu_float()
            self.display.blit(self.assets['game_logo'],
                              (self.display_WIDTH // 20 * 1, self.display_HEIGHT // 20 * 1 + self.menu_float))

            self.EVERYTHING_render_update()


            self.movement[1] = 0.8

            self.draw_text('Made By Dyrox2333', pygame.font.Font('minecraft.otf', 10), 'black', self.display, (
                self.display_WIDTH // 20 * 19.5 - self.font.size('Made By Dyrox2333')[0] // 2 + 1,
                self.display_HEIGHT // 20 * 19.5 - self.font.size('Made By Dyrox2333')[1] // 2 + 1))
            self.draw_text('Made By Dyrox2333', pygame.font.Font('minecraft.otf', 10), 'white', self.display, (
                self.display_WIDTH // 20 * 19.5 - self.font.size('Made By Dyrox2333')[0] // 2,
                self.display_HEIGHT // 20 * 19.5 - self.font.size('Made By Dyrox2333')[1] // 2))

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))

            if self.show_debug_menu:
                self.screen.blit(self.debug_surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(RUNNING_FPS)


Game().main_menu()