import pygame
import os
BASE_IMG_PATH = 'data/images/'

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0,0,0))
    return img

def load_images(path):
    images = []
    image_names = os.listdir(BASE_IMG_PATH + path)
    image_names.sort()  # Sort the image names
    for img_name in image_names:
        images.append(load_image(path + '/' + img_name))
    return images
