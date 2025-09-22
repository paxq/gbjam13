import sys
import pygame
import asyncio
import random
import math
import glob
from settings import *
from game_objects import *
from world_keys import *

pygame.init()
pygame.display.set_caption("GBJam13 [insert name here]")
screen = pygame.display.set_mode((SCREEN_WIDTH * SCALE_MODIFIER, SCREEN_HEIGHT * SCALE_MODIFIER))
aspect_ratio = 10 / 9

clock = pygame.time.Clock()
deltaTime = 0
running = True

world_keys = load_world_keys()

# IMG & SOUND SAVED
# font = pygame.font.SysFont("Arial", 20)
# text = font.render("Hello World!", False, (255, 255, 255))

# img = pygame.image.load("img/char_idle-1.png")
# img = pygame.transform.scale(img, (64, 64))

# pygame.mixer.init()
# sfx = pygame.mixer.Sound("sfx/step.wav")


class MenuItem:
    def __init__(self, x, y, img, w=48, h=16):
        self.width = w * SCALE_MODIFIER
        self.height = h * SCALE_MODIFIER

        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.img = pygame.transform.scale(pygame.image.load(img), (self.rect.width, self.rect.height))

        self.selected = False
        self.selected_overlay = pygame.transform.scale(pygame.image.load("img/menu/overlay.png"), (self.rect.width, self.rect.height))
        self.parent = ""

    def draw(self, surface):
        if self.parent == "":
            return
        surface.blit(self.img, self.rect)
        if self.selected:
            surface.blit(self.selected_overlay, self.rect)

class Menu:
    def __init__(self, x, y, w, h, background_img, padding):
        self.x = x
        self.y = y
        self.width = w * SCALE_MODIFIER
        self.height = h * SCALE_MODIFIER

        self.active = False
        self.contents = []
        self.selected_item_index = 0
        self.input_cooldown = 0
        self.item_padding = padding * SCALE_MODIFIER

        self.rect = pygame.Rect(x, y, w, h)
        self.img = pygame.transform.scale(pygame.image.load(background_img), (self.rect.width, self.rect.height))

    def add_item(self, menu_item):
        self.contents.append(menu_item)
        menu_item.parent = self

        # Figure out padding
        menu_item.rect.left = self.x + self.item_padding
        menu_item.rect.top = self.y + self.item_padding

        for i in range(1, len(self.contents)):
            x = self.item_padding
            y = self.item_padding + self.contents[i - 1].height * i

            menu_item.rect.left = self.x + x
            menu_item.rect.top = self.y + y

    def add_items(self, items):
        for item in items:
            self.add_item(item)

    def get_input(self):
        self.input_cooldown += 1
        if self.input_cooldown > 30:
            key = pygame.key.get_pressed()
            if key[pygame.K_x]:
                self.input_cooldown = 0
                return -1
            if key[pygame.K_w] or key[pygame.K_UP] or key[pygame.K_SPACE]:
                self.input_cooldown = 0
                return 0
            if key[pygame.K_s] or key[pygame.K_DOWN]:
                self.input_cooldown = 0
                return 1

    def update(self):
        nav_dir = self.get_input()
        if nav_dir == -1:
            self.active = False
            return
        if nav_dir == 0:
            self.selected_item_index -= 1
        if nav_dir == 1:
            self.selected_item_index += 1

        if self.selected_item_index > len(self.contents) - 1:
            self.selected_item_index = 0
        elif self.selected_item_index < 0:
            self.selected_item_index = len(self.contents) - 1

        for item in self.contents:
            item.selected = False
            if self.contents[self.selected_item_index] == item:
                item.selected = True

    def draw(self, surface):
        if not self.active:
            return
        surface.blit(self.img, self.rect)
        for item in self.contents:
            item.draw(surface)

class Tile(GameObject):
    def __init__(self, x, y, ID, collidable=True):
        self.x = x # world units
        self.y = y # world units
        self.id = ID
        self.rect = pygame.Rect(x, y, TILE_SIZE * SCALE_MODIFIER, TILE_SIZE * SCALE_MODIFIER) # pixel units
        self.collidable = collidable

        img = ""
        for sprite in world_keys:
            if sprite['id'] == self.id:
                img = sprite['img']

        self.img = pygame.transform.scale(img, (self.rect.width, self.rect.height))

        super().__init__(self.x, self.y, self.rect)

class Interaction(GameObject):
    def __init__(self, x, y, sprite_id, display_text='- INTERACT -'):
        img = ""
        for key in world_keys:
            if key['id'] == sprite_id:
                img = key['img']
                w = key['size'][0] * SCALE_MODIFIER
                h = key['size'][1] * SCALE_MODIFIER
                func = key['function']

        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.id = sprite_id
        self.function = func
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.img = pygame.transform.scale(img, (self.rect.width, self.rect.height))
        self.text = display_text
        self.text_width = 8 * SCALE_MODIFIER
        self.text_height = 5 * SCALE_MODIFIER
        self.displayed = False

        self.interaction_cooldown = 0

        super().__init__(self.x, self.y, self.rect)

    def check_for_interaction(self, game):
        key = pygame.key.get_pressed()
        if (key[pygame.K_s] or key[pygame.K_DOWN]) and self.interaction_cooldown > 30:
            self.function(self, game)
            self.interaction_cooldown = 0

    def check_for_collision(self, game):
        test_rect = game.player.rect
        test_rect.x *= TILE_SIZE * SCALE_MODIFIER

        test_rect.y *= TILE_SIZE * SCALE_MODIFIER
        self.displayed = False
        if self.rect.colliderect(test_rect):
            self.interaction_cooldown += 1
            self.displayed = True
            self.check_for_interaction(game)


class World:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.backgrounds = []
        self.tiles = []
        self.interactions = []
        self.entities = []

        # Load world info
        with open('world.txt') as world_data:
            data = world_data.read().replace('\n', '').split('NL')

            world_size = data.pop(0)
            worldX = int(world_size.split("x")[0])
            worldY = int(world_size.split("x")[1])

            start_pos = data.pop(0)
            startX = float(start_pos.split("x")[0])
            startY = float(start_pos.split("x")[1])

            offsetX = worldX - startX
            offsetY = worldY - startY

            for column in range(0, len(data) - 1):
                row = 0
                while row < worldX * 2:
                    ID = data[column][row] + data[column][row + 1]
                    if ID == "00":
                        pass
                    elif ID[0] == 'I':
                        interaction = Interaction(row / 2 + offsetX, column + offsetY, ID)
                        self.interactions.append(interaction)
                    else:
                        collision = True
                        if ID[0] == "D":
                            collision = False
                        tile = Tile(row / 2 + offsetX, column + offsetY, ID, collidable=collision)
                        self.tiles.append(tile)

                    row += 2

    def move(self, x, y):
        # for background in self.backgrounds:
        #     background.move(x, y)
        for tile in self.tiles:
            tile.move(x, y)
        for interaction in self.interactions:
            interaction.move(x, y)
        # for entity in self.entities:
        #     entity.move(x, y)

    def draw(self, screen):
        for tile in self.tiles:
            screen.blit(tile.img, tile.rect)
        for interaction in self.interactions:
            screen.blit(interaction.img, interaction.rect)
            if interaction.displayed:
                text = game.font.render(interaction.text, False, (255, 255, 255))
                screen.blit(text, (interaction.rect.left  - interaction.text_width, interaction.rect.top - interaction.text_height))

class Animation:
    def __init__(self, animation_dir, animator, flip_frames=False):
        # load frames
        self.images = []
        self.animator = animator # Object to animate
        self.current_frame = 0
        self.tick = 0

        paths = glob.glob(f"{animation_dir}/*.png")
        for path in paths:
            img = pygame.transform.scale(pygame.image.load(path), (self.animator.width, self.animator.height))
            if flip_frames:
                self.images.append(pygame.transform.flip(img, True, False))
            else:
                self.images.append(img)

    def animate(self):
        self.tick += 1
        if self.tick % ANIMATION_COOLDOWN == 0:
            self.current_frame += 1
            self.tick = 0

        # Reset current frame
        if self.current_frame >= len(self.images):
            self.current_frame = 0
        
        # Return frame
        return self.images[self.current_frame]
        # alternatively:
        # screen.blit(self.images[self.current_frame], self.animator.x, self.animator.y)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16 * SCALE_MODIFIER
        self.height = 16 * SCALE_MODIFIER

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.center_pos = self.rect.center
        self.player_trigger = pygame.Rect(((self.center_pos[0] - self.width / 2) * self.width), ((self.center_pos[1] - self.height / 2) * self.height), self.width, self.height)

        self.speed = 0.035
        self.velocityX = 0
        self.velocityY = 0
        self.jump_strength = 0.0925 # for some reason this acts like an exponential sacle but it works
        self.better_jump_strength = self.jump_strength
        self.gravity = 0.032
        self.is_grounded = False
        self.jumping = 1

        self.held_item = ""
        self.input_delay = 0

        playerImg = pygame.image.load('Assets/Player_placeholder.png')
        self.playerImg = pygame.transform.scale(playerImg, (self.width, self.height))

        self.walk_right = Animation('img/player/walk_right', self)
        self.walk_left = Animation('img/player/walk_right', self, True)
        self.idle = Animation('img/player/idle', self)

    def move(self, world):
        self.velocityX /= 2
        self.velocityY /= 1.4
        
        if self.velocityY > 0:
            self.is_grounded = False

        # Get keypresses
        key = pygame.key.get_pressed()
        self.input_delay += 1
        # Drop Item
        if key[pygame.K_x] and self.input_delay > 30 and self.held_item != "":
            self.input_delay = 0
            # Create new tile and add it to the world
            interaction = Interaction(self.rect.left, self.rect.bottom - self.held_item.rect.height, self.held_item.id)
            game.world.interactions.append(interaction)
            # Remove Item from inventory
            self.held_item = ""
        # Jump
        if key[pygame.K_w] or key[pygame.K_SPACE] or key[pygame.K_UP]:
            if self.is_grounded:
                self.is_grounded = False
                self.jumping = 20
                self.better_jump_strength = self.jump_strength
            if self.jumping > 0:
                self.jumping += 0.4
                self.better_jump_strength += 0.0010
        # Move X-Axis
        if key[pygame.K_a] or key[pygame.K_LEFT]:
            self.velocityX -= self.speed
            self.playerImg = self.walk_left.animate()
        elif key[pygame.K_d] or key[pygame.K_RIGHT]:
            self.velocityX += self.speed
            self.playerImg = self.walk_right.animate()
        elif self.velocityY == 0:
            self.playerImg = self.idle.animate()

        if self.jumping > 0:
            self.better_jump_strength *= 0.95
            self.velocityY -= self.better_jump_strength
            self.jumping -= 1
        # Add Gravity
        self.velocityY += self.gravity

        # Check for collisions
        for tile in world.tiles:
            # Test x dir
            test_rect = pygame.Rect((self.x + self.velocityX) * self.width, self.y * self.height, self.width, self.height)
            if test_rect.colliderect(tile.rect) and tile.collidable:
                self.velocityX = 0
            # Test y dir
            test_rect = pygame.Rect(self.x * self.width, (self.y + self.velocityY) * self.height, self.width, self.height)
            if test_rect.colliderect(tile.rect) and tile.collidable:
                # Reset is_grounded
                if self.velocityY > 0:
                    self.is_grounded = True
                # Reset velocity on headbang
                if self.velocityY < 0:
                    self.jumping = 0
                self.velocityY = 0
        
        # quit game if u ded
        if self.y > 16:
            game.running = False

        self.update_vars()

        return {
                "x" : self.x,
                "y" : self.y,
                "velX" : self.velocityX,
                "velY" : self.velocityY,
                "c_pos" : self.center_pos,
                "collider" : self.player_trigger
               }

    def draw(self, surface):
        surface.blit(self.playerImg, ((self.x * self.width), (self.y * self.height), self.width, self.height))
                    

    def update_vars(self):
        self.center_pos = ((self.x + self.width / 2), (self.y + self.height / 2))
        self.rect.top = self.y
        self.rect.left = self.x
        self.player_trigger = pygame.Rect(((self.center_pos[0] - self.width / 2) * self.width), ((self.center_pos[1] - self.height / 2) * self.height), self.width, self.height)


class Camera:
    def __init__(self):
        self.padding_horizontal = 48 * SCALE_MODIFIER
        self.padding_vertical = 32 * SCALE_MODIFIER
        self.correctional_strength = 0.1

        self.correctional_timer = 0

        self.camera_collider_x = pygame.Rect((SCREEN_WIDTH * SCALE_MODIFIER) / 2 - self.padding_horizontal / 2, (SCREEN_HEIGHT * SCALE_MODIFIER) - TILE_SIZE * SCALE_MODIFIER, self.padding_horizontal, TILE_SIZE * SCALE_MODIFIER)
        self.camera_collider_y = pygame.Rect((SCREEN_WIDTH * SCALE_MODIFIER) / 2 - (TILE_SIZE * SCALE_MODIFIER) / 2, (SCREEN_HEIGHT * SCALE_MODIFIER) - self.padding_vertical, TILE_SIZE * SCALE_MODIFIER, self.padding_vertical)

    def calculate_movements(self, player_info, world_info):
        player_trigger = player_info['collider']
        playerX = player_info['x']
        playerY = player_info['y']
        velocityX = player_info['velX']
        velocityY = player_info['velY']

        worldX = world_info.x
        worldY = world_info.y

        # Reset Padding zone
        if velocityX <= 0.03 and velocityX >= -0.03:
            self.camera_collider_x.width = self.padding_horizontal
            self.camera_collider_x.left = (SCREEN_WIDTH * SCALE_MODIFIER) / 2 - self.padding_horizontal / 2
            self.correctional_timer = 0

        # Move padding zone
        self.camera_collider_x.bottom = player_trigger.bottom
        self.camera_collider_y.right = player_trigger.right

        # Shrink padding zone symmetrically
        if self.correctional_timer > 0:
            pr = -1/32 * (self.correctional_timer - 32) ** 2 + 32 # Smoothing function

            self.camera_collider_x.width -= self.correctional_strength * pr / 2 # added /2 on this one now it works like the left side idk why
            self.camera_collider_x.left += self.correctional_strength * pr / 2
        if self.correctional_timer < 64:
            self.correctional_timer += 1


        # Calculate Movement
        if self.camera_collider_x.colliderect(player_trigger):
            # Calculate Player movement
            playerX += velocityX
        else:
            # X-axis
            if player_trigger.left > SCREEN_WIDTH * SCALE_MODIFIER / 2: #EDIT: FIXED.  center pos takes the 0-9 coorinate system and adds half the pixel width  ##Upon closer inspection the previous information is false. I don't know how it works or why, but it works, soo....
                worldX -= velocityX
                if self.correctional_timer > 0 and player_trigger.left > self.camera_collider_x.right:
                    playerX = self.camera_collider_x.right / player_trigger.width
            elif player_trigger.right < SCREEN_WIDTH * SCALE_MODIFIER / 2:
                worldX -= velocityX
                if self.correctional_timer > 0 and player_trigger.right < self.camera_collider_x.left:    
                    playerX = (self.camera_collider_x.left - player_trigger.width) / player_trigger.width
                
        # Y-Axis
        worldY -= velocityY
        if player_trigger.bottom <= self.camera_collider_y.top:
            self.camera_collider_y.top = player_trigger.centery
        elif player_trigger.top >= self.camera_collider_y.bottom:
            self.camera_collider_y.bottom = player_trigger.centery
        else:
            playerY += velocityY
            worldY += velocityY # Cancel it out

        return {
            'playerX' : playerX,
            'playerY' : playerY,
            'worldX' : worldX,
            'worldY' : worldY
            }

class Game:
    def __init__(self):
        self.running = True

        self.player = Player(4.5, 7)
        self.camera = Camera()
        self.world = World()

        test_button = MenuItem(16, 16, "img/menu/text/text_placeholder.png")
        test_button_2 = MenuItem(16, 16, "img/menu/button/button_placeholder.png")
        self.menu_1 = Menu((SCREEN_WIDTH / 2) * SCALE_MODIFIER - 48 * SCALE_MODIFIER, (SCREEN_HEIGHT / 2) * SCALE_MODIFIER - 48 * SCALE_MODIFIER, 96 * SCALE_MODIFIER, 96 * SCALE_MODIFIER, 'img/menu/task_menu.png', 4)
        self.menu_1.add_items([test_button, test_button_2])

        pygame.font.init()
        font = pygame.font.match_font('font/Grand9K Pixel.ttf', 0, 0)
        self.font = pygame.font.Font(font, 8 * SCALE_MODIFIER)
    
    def handle_pygame_events(self, events):
        # Handle game quit, gui interaction, and keyboard input
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

    def update_world(self, world_events):
        # Handle all world-based interactions
        # Custom event order?
        # for event in world_events:
        #     if event.type == "placeholder-1":
        #         event.function()
        # for event in world_events:
        #     if event.type == "placeholder-2":
        #         event.function()
        pass

    def update(self):
        # Update Order:
        # • Block events
        for tile in self.world.tiles:
            tile.update()
        # • Entities
        #   – Player
        player_info = self.player.move(self.world)
        #   – Passive Entities
        #   – Enemies
        # • Interactions
        for interaction in self.world.interactions:
            interaction.update()
            interaction.check_for_collision(self)
        # • GUI
        self.menu_1.update()

        # • Camera
        movement = self.camera.calculate_movements(player_info, self.world)
        self.player.x = movement['playerX']
        self.player.y = movement['playerY']

        self.world.move(movement['worldX'], movement['worldY'])
        # print(movement['worldX'], movement['worldY'])

        # print(self.player.x, self.player.y, self.player.velocityX, self.player.velocityY)


    def draw(self, screen):
        # Draw Order:
        # • Background_1
        # • Background_2
        # • World Tiles
        # • Debug Objects
        self.world.draw(screen)
        # • Interaction Tiles
        # • Entities
        # • Player
        self.player.draw(screen)
        # • Foreground_1
        # • GUI
        self.menu_1.draw(screen)

    def _debug_draw_grid(self, screen, block_per_width=10, block_per_height=9):
        # draw x lines
        for x in range(0, block_per_height):
            pygame.draw.line(screen, (255, 255, 255), (0, ((SCREEN_HEIGHT * SCALE_MODIFIER) / block_per_height) * x), (SCREEN_WIDTH * SCALE_MODIFIER, ((SCREEN_HEIGHT * SCALE_MODIFIER) / block_per_height) * x))
        # draw y lines
        for y in range(0, block_per_width):
            pygame.draw.line(screen, (255, 255, 255), (((SCREEN_WIDTH * SCALE_MODIFIER) / block_per_width) * y, 0), (((SCREEN_WIDTH * SCALE_MODIFIER) / block_per_width) * y, SCREEN_HEIGHT * SCALE_MODIFIER))

        
game = Game()
# player = Player(0, 8)

async def main():
    global game, deltaTime, clock

    while game.running:
        # Update things
        game.handle_pygame_events(pygame.event.get())
        game.update()

        # Draw things
        screen.fill((117, 251, 253))

        # pygame.draw.rect(screen, (0, 255, 0), game.camera.camera_collider_x) # Debug
        # pygame.draw.rect(screen, (0, 200, 100), game.camera.camera_collider_y) # Debug
        # pygame.draw.rect(screen, (255, 0, 255), game.player.player_trigger) # Debug

        # game._debug_draw_grid(screen)
        game.draw(screen)
        
        pygame.display.update()

        deltaTime = clock.tick(FPS) / 1000
        await asyncio.sleep(0) # do not forget that one, it must be called on every frame
        
    # Closing the game (not strictly required)
    pygame.quit()

asyncio.run(main())