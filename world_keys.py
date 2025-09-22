import pygame
from game_objects import Item
from settings import *

class Storage:
    def __init__(self):
        pass

    def default_interaction(self, interaction, game):
        print("This code runs when you interact with an object.")
        print(f"Here is the player: {game.player.rect.center}\n")

    def menu_1_interaction(self, interaction, game):
        game.menu_1.active = True

    def pick_up_box(self, interaction, game):
        # Put box in players inventory/hands
        img_id = "I0"
        for key in load_world_keys():
            if key['id'].split()[0] == "I":
                if key['function'] == storage.pick_up_box:
                    img_id = key['id']
        item = Item(interaction.rect, interaction.img, img_id)
        game.player.held_item = item
        # Remove box from world
        index = game.world.interactions.index(interaction)
        game.world.interactions.pop(index)
        # Display buttons to drop (handled in player script)

storage = Storage()

def load_world_keys():
    return [
        {
            'id': '00',
            'img': pygame.image.load(f"{img_dir}/transparent.png")
        },
        {
            'id': 'B0',
            'img': pygame.image.load(f"{img_dir}/grass.png")
        },
        {
            'id': 'B1',
            'img': pygame.image.load(f"{img_dir}/gray_block.png")
        },
        {
            'id': 'D0',
            'img': pygame.image.load(f"{img_dir}/grass_top.png")
        },
        {
            'id': 'D1',
            'img': pygame.image.load(f'{img_dir}/rock.png')
        },
        {
            'id': 'I0',
            'img': pygame.image.load(f'{img_dir}/box.png'),
            'size': (16, 16),
            'function': storage.pick_up_box
        }
    ]