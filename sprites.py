import pygame

def load_sprites():
    return [
        {
            'id': 0,
            'img': pygame.image.load("img/grass.png")
        },
        {
            'id': 1,
            'img': pygame.image.load('img/grass_top.png')
        }
    ]