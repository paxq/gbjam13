import sys
import pygame
import asyncio
import random
from settings import *

pygame.init()
pygame.display.set_caption("GBJam13 [insert name here]")
screen = pygame.display.set_mode((SCREEN_WIDTH * SCALE_MODIFIER, SCREEN_HEIGHT * SCALE_MODIFIER))
aspect_ratio = 10 / 9

clock = pygame.time.Clock()
deltaTime = 0
running = True


# IMG & SOUND SAVED
# font = pygame.font.SysFont("Arial", 20)
# text = font.render("Hello World!", False, (255, 255, 255))

# img = pygame.image.load("img/char_idle-1.png")
# img = pygame.transform.scale(img, (64, 64))

# pygame.mixer.init()
# sfx = pygame.mixer.Sound("sfx/step.wav")


class WorldEvent:
    def __init__(self, event_type, location, function):
        self.type = event_type
        self.pos = location
        self.event = function

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.width = 16 * SCALE_MODIFIER
        self.height = 16 * SCALE_MODIFIER

        self.speed = 0.035
        self.velocityX = 0
        self.velocityY = 0
        self.jump_strength = 0.0925 # for some reason this acts like an exponential sacle but it works
        self.gravity = 0.032
        self.is_grounded = False
        self.jumping = 1
        self.better_jump_strength = self.jump_strength

        self.playerImg = pygame.image.load('Assets/Player_placeholder.png')
        self.playerImg = pygame.transform.scale(self.playerImg, (self.width, self.height))

    def move(self):
        # dx = 0
        # dy = 0

        self.velocityX /= 2
        self.velocityY /= 1.4

        if self.y == 8: # will need to chage this to accept colidble blocks as valid is_grouded spaces
            self.is_grounded = True


        # Get keypresses
        key = pygame.key.get_pressed()
        if key[pygame.K_w] or key[pygame.K_SPACE] or key[pygame.K_UP]:
            if self.is_grounded:
                self.is_grounded = False
                self.jumping = 20
                self.better_jump_strength = self.jump_strength
            if self.jumping > 0:
                self.jumping += 0.4
                self.better_jump_strength += 0.0010
            
        if key[pygame.K_a] or key[pygame.K_LEFT]:
            self.velocityX -= self.speed
        if key[pygame.K_d] or key[pygame.K_RIGHT]:
            self.velocityX += self.speed

        if self.jumping > 0:
            self.better_jump_strength *= 0.95
            self.velocityY -= self.better_jump_strength
            self.jumping -= 1


        self.velocityY += self.gravity

        self.x += self.velocityX

        self.y += self.velocityY

        # Check for collisions
        # (add world first)
        if self.y < 0:
            self.y = 0
        if self.y > 8:
            self.y = 8
        if self.x < 0:
            self.x = 0
        if self.x > 9:
            self.x = 9


    def draw(self):
        screen.blit(self.playerImg, ((self.x * 16 * SCALE_MODIFIER), ((self.y * 16 * SCALE_MODIFIER)), self.width, self.height))
    #def update(self, events):
    #    pass

class Game:
    def __init__(self):
        self.running = True
    
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

    def _debug_draw_grid(self, screen, block_per_width=10, block_per_height=9):
        # draw x lines
        for x in range(0, block_per_height):
            pygame.draw.line(screen, (255, 255, 255), (0, ((SCREEN_HEIGHT * SCALE_MODIFIER) / block_per_height) * x), (SCREEN_WIDTH * SCALE_MODIFIER, ((SCREEN_HEIGHT * SCALE_MODIFIER) / block_per_height) * x))
        # draw y lines
        for y in range(0, block_per_width):
            pygame.draw.line(screen, (255, 255, 255), (((SCREEN_WIDTH * SCALE_MODIFIER) / block_per_width) * y, 0), (((SCREEN_WIDTH * SCALE_MODIFIER) / block_per_width) * y, SCREEN_HEIGHT * SCALE_MODIFIER))

        
game = Game()
player = Player(0, 8)

async def main():
    global game, deltaTime, clock

    #PosX = 5
    #PosY = 5
    #Xvelocity = 0
    #Yvelocity = 0
    #grounded = False

    while game.running:
        game.handle_pygame_events(pygame.event.get())
        screen.fill((0, 0, 0))
        game._debug_draw_grid(screen)

        player.move()
        player.draw()
        
        pygame.display.update()

        deltaTime = clock.tick(FPS) / 1000
        await asyncio.sleep(0) # do not forget that one, it must be called on every frame
        
    # Closing the game (not strictly required)
    pygame.quit()

asyncio.run(main())