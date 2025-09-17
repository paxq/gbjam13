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

async def main():
    global game, deltaTime, clock

    PosX = 5
    PosY = 5
    Xvelocity = 0
    Yvelocity = 0
    grounded = False
    game.draw_player(5, 5)
    while game.running:
        game.handle_pygame_events(pygame.event.get())
        screen.fill((0, 0, 0))
        game._debug_draw_grid(screen)

        # player:
        if PosY == 8:
            grounded = True
       
        Xvelocity /= 2
        Yvelocity /= 2

        key = pygame.key.get_pressed()

        if key[pygame.K_LEFT] == True or key[pygame.K_a]:
            if PosX > 0:
                Xvelocity -= 0.1
        if key[pygame.K_RIGHT] == True or key[pygame.K_d]:
            if PosX < 9:
                Xvelocity += 0.1
        if key[pygame.K_UP] == True or key[pygame.K_w]:
            if PosY > 0:
                if grounded == True:
                    Yvelocity -= 2
                    grounded = False

        PosY += 0.2
        PosX += Xvelocity
        PosY += Yvelocity
        if PosY < 0:
            PosY = 0
        if PosY > 8:
            PosY = 8  
        if PosX < 0:
            PosX = 0
        if PosX > 9:
            PosX = 9
        game.draw_player(PosX, PosY)
        pygame.display.update()

        deltaTime = clock.tick(FPS) / 1000
        await asyncio.sleep(0) # do not forget that one, it must be called on every frame
        
    # Closing the game (not strictly required)
    pygame.quit()

asyncio.run(main())