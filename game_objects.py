

import pygame
from game_client import GameClient


class DataItems:

    colors = {
        "red": (255, 0, 0),
        "blue": (0, 0, 255),
        "green": (0, 255, 0),
        "white": (255, 255, 255),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "orange": (255, 215, 0)
    }


class RenderItems:

    font = pygame.font.Font(pygame.font.SysFont, 36)


class PlayerCharacter:

    """A (replicable) player character with boundary checks.
    Rendered as a circle with a name floating on top"""

    def __init__(self, x, y, radius, pid, color):
        self.x, self.y = x, y
        self.radius = radius
        self.pid = pid
        self.color = color

        self.name = RenderItems.font.render(
            self.pid, True, self.color
        )

        #set initial local client data
        GameClient.local_client_state['x'] = self.x
        GameClient.local_client_state['y'] = self.y
        GameClient.local_client_state["color"] = self.color

    def boundary_check(self):

        """Checks for boundary penetrations and resets"""
        if self.x < self.radius:
            self.x = self.radius
        elif self.x > 1000 - self.radius:
            self.x = 1000 - self.radius
        
        if self.y < self.radius:
            self.y = self.radius
        elif self.y > 650 - self.radius:
            self.y = 650 - self.radius

    def update(self, events: list[pygame.event.Event]):

        """Called every frame"""

        #boundary check
        self.boundary_check()

        #update from global state
        #for the current client it can be used for syncing
        #for other client replicas it is their state
        try:
            self.x = GameClient.game_state[self.pid]['x']
            self.y = GameClient.game_state[self.pid]['y']
        except KeyError:
            pass

    def draw(self, surf):

        pygame.draw.circle(surf, self.color, (self.x, self.y),
                           self.radius) #body
        pygame.draw.circle(surf, (0, 0, 0), (self.x, self.y),
                           2) #center dot
        surf.blit(self.name,
                  (self.x - self.name.get_width()//2,
                   self.y + self.radius + \
                    self.name.get_height() + 5)) #name
        

class PawnCharacter(PlayerCharacter):

    """A single character than can respond to inputs
    (Only one possible instance for each client)"""

    #keys held
    key_w = False
    key_s = False
    key_a = False
    key_d = False

    speed = 15 #movement speed

    def update(self, events: list[pygame.event.Event]):

        super().update(events)

        #respond to input
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    PawnCharacter.key_w = True
                elif event.key == pygame.K_s:
                    PawnCharacter.key_s = True
                if event.key == pygame.K_a:
                    PawnCharacter.key_a = True
                elif event.key == pygame.K_d:
                    PawnCharacter.key_d = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    PawnCharacter.key_w = False
                elif event.key == pygame.K_s:
                    PawnCharacter.key_s = False
                if event.key == pygame.K_a:
                    PawnCharacter.key_a = False
                elif event.key == pygame.K_d:
                    PawnCharacter.key_d = False
        
        if PawnCharacter.key_w:
            self.y += PawnCharacter.speed
        elif PawnCharacter.key_s:
            self.y -= PawnCharacter.speed
        if PawnCharacter.key_a:
            self.x -= PawnCharacter.speed
        elif PawnCharacter.key_d:
            self.x += PawnCharacter.speed
        
        #update local client data for sending to server
        GameClient.local_client_state['x'] = self.x
        GameClient.local_client_state['y'] = self.y