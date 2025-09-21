import pygame

class Storage:
    def __init__(self):
        pass

    def default_interaction(self, game):
        print("This code runs when you interact with an object.")
        print(f"Here is the player: {game.player.rect.center}\n")
storage = Storage()

def load_world_keys():
    return [
        {
            'id': '00',
            'img': pygame.image.load("img/transparent.png")
        },
        {
            'id': 'B0',
            'img': pygame.image.load("img/grass.png")
        },
        {
            'id': 'D0',
            'img': pygame.image.load('img/grass_top.png')
        },
        {
            'id': 'I0',
            'img': pygame.image.load('img/grass_top.png'),
            'size': (16, 16),
            'function': storage.default_interaction
        }
    ]