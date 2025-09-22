import pygame
from settings import *

class Item:
    def __init__(self, rect, img, img_id):
        self.rect = rect
        self.img = img
        self.id = img_id
    
    def draw(self, surface):
        surface.blit(self.img, self.rect)

class GameObject:
    def __init__(self, x, y, rect):
        self.x = x
        self.y = y
        self.rect = rect
    
    def move(self, x, y):
        self.x += x
        self.y += y

    def update(self):
        self.rect.left = self.x * self.rect.width
        self.rect.top = self.y * self.rect.height

class WorldEvent:
    def __init__(self, event_type, location, function):
        self.type = event_type
        self.pos = location
        self.event = function