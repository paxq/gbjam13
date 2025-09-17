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

playerImg = pygame.image.load('Assets/Player_placeholder.png')
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
    def __init__(self, x, y, scaleX=(16 * SCALE_MODIFIER), scaleY=(16 * SCALE_MODIFIER)):
        self.x = x
        self.y = y
        self.width = scaleX
        self.height = scaleY

        self.speed = 7 * SCALE_MODIFIER
        self.velocityX = 1
        self.velocityY = 1
        self.jump_height = self.height * 1.5
        self.jump_multiplier = 0.99
        self.initial_height = 0

        self.gravity = 0.2
        self.is_jumping = False
        self.is_grounded = True

    def move(self):
        # dx = 0
        # dy = 0

        self.velocityX /= 2
        self.velocityY /= 2

        if self.y >= SCREEN_HEIGHT * SCALE_MODIFIER - self.height:
            self.is_grounded = True
        if self.initial_height - self.y >= self.jump_height:
            self.is_jumping = False

        # Get keypresses
        key = pygame.key.get_pressed()
        if key[pygame.K_w] or key[pygame.K_SPACE] or key[pygame.K_UP]:
            if self.is_grounded:
                self.initial_height = self.y
                self.is_grounded = False
                self.is_jumping = True
            if self.initial_height - self.y < self.jump_height and self.is_jumping:
                self.velocityY -= 0.4

        if key[pygame.K_a] or key[pygame.K_LEFT]:
            self.velocityX -= 0.1
        if key[pygame.K_d] or key[pygame.K_RIGHT]:
            self.velocityX += 0.1

        self.velocityY += self.gravity

        # Check for collisions
        # (add world first)
        if self.y - self.velocityY < 0:
            self.velocityY += 0.1
        if self.y + self.velocityY > SCREEN_HEIGHT * SCALE_MODIFIER - self.height:
            self.velocityY -= 0.2
        if self.x - self.velocityX < 0:
            self.velocityX += 0.1
        if self.x + self.velocityX > SCREEN_WIDTH * SCALE_MODIFIER - self.width:
            self.velocityX -= 0.1

        self.x += self.velocityX * self.speed
        self.y += self.velocityY * self.speed

    def draw(self, surface):
        surface.blit(playerImg, (self.x, self.y, self.width, self.height))

    def update(self, events):
        pass

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
    
    def draw_player(self, playerPosX, playerPosY):
        screen.blit(playerImg, (7 + (playerPosX * 64), (7 + (playerPosY * 64))))

        
game = Game()
player = Player(5, 5)

async def main():
    global game, deltaTime, clock

    PosX = 5
    PosY = 5
    Xvelocity = 0
    Yvelocity = 0
    grounded = False

    while game.running:
        game.handle_pygame_events(pygame.event.get())
        screen.fill((0, 0, 0))
        game._debug_draw_grid(screen)

        player.move()
        player.draw(screen)
        
        pygame.display.update()

        deltaTime = clock.tick(FPS) / 1000
        await asyncio.sleep(0) # do not forget that one, it must be called on every frame
        
    # Closing the game (not strictly required)
    pygame.quit()

asyncio.run(main())