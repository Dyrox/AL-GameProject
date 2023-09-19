import pygame
class ObjectAnimation:
    def __init__(self, pos, images):
        self.images = images
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(topleft=pos)
        self.animation_time = pygame.time.get_ticks()


    def animate(self, dt):
        if pygame.time.get_ticks() - self.animation_time > 100:  # change 100 to adjust speed
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]
            self.animation_time = pygame.time.get_ticks()

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)