import pygame

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.entity_rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.collisions = {'up':False,'down':False,'right':False,'left': False}
    
    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up':False,'down':False,'right':False,'left': False}
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        
        self.pos[0] += frame_movement[0]
        self.entity_rect.x = self.pos[0]
        for rect in tilemap.physics_rects_around(self.pos):
            if self.entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    self.entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    self.entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = self.entity_rect.x
        
        self.pos[1] += frame_movement[1]
        self.entity_rect.y = self.pos[1]
        for rect in tilemap.physics_rects_around(self.pos):
            if self.entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    self.entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    self.entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = self.entity_rect.y
                
        
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        
    def render(self, surf, offset=[0,0]):
        
        adjusted_pos = (self.pos[0] - offset[0], self.pos[1] - offset[1])
        surf.blit(self.game.assets['player'], adjusted_pos)
