import pygame

def load_sprites():
    return [
        {
            'id': 'A0',
            'img': pygame.image.load("img/grass.png")
        },
        {
            'id': 'A1',
            'img': pygame.image.load('img/grass_top.png')
        }
    ]