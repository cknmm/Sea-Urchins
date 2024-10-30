
import asyncio, random, time
import threading as t
import pygame
pygame.init()
from game_client import GameClient
from game_objects import PlayerCharacter, PawnCharacter

#inputs
uri = input("Enter the server uri: ")
pid = ""
while len(pid) < 4 or " " in pid:
    pid = input("Enter your name (make sure that it's unique \
while containing no spaces and atleast 5 characters long): ")

#pygame variables
main = pygame.display.set_mode((1000, 650)) #pygame main window
font = pygame.font.Font(None, 36)

#in-game log variables
message_queue = [] #TODO: Use later for implementing logs

GameClient(uri, pid) #initialize the network client
#connect to the server in the background and initiate ping
t.Thread(target=asyncio.run, args=(GameClient.connect(),)).start()

#list of the all the players in the game except us
players: dict[str, PlayerCharacter] = dict()
pawn = PawnCharacter(
    random.randint(100, 900), random.randint(100, 550),
    20, pid
) #current (movable) client character

#start exchanging data indefinitely
t.Thread(target=asyncio.run, args=(
    GameClient.retry_exchange(None),)).start()

def update_player_data():
    #forward check
    for player_name in GameClient.game_state:
        if player_name != pid and player_name not in players:
            #TODO: Report joined game
            try:
                players[player_name] = PlayerCharacter(
                    GameClient.game_state[player_name]['x'],
                    GameClient.game_state[player_name]['y'],
                    20, player_name
                )
            except KeyError:
                pass
    #backward check
    for player_name in players.keys():
        if player_name not in GameClient.game_state:
            #TODO: Report left game
            del players[player_name]


ie = False #initiate exit
fps = 0 #frames per second
while not(ie): #game loop

    s = time.time()

    pass_events = [] #events to pass to characters
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #quit when window closed
            ie = True
        elif event.type == pygame.KEYDOWN:
            pass_events.append(event)
        elif event.type == pygame.KEYUP:
            pass_events.append(event)

    #update characters
    update_player_data()
    pawn.update(pass_events)
    for player_name in players:
        players[player_name].update(pass_events)
    #reset sync flag
    GameClient.sync_flag = False

    #rendering

    main.fill((0, 0, 0)) #clear display
    #TODO: Add a background (possible ocean)

    #render characters
    pawn.draw(main)
    for player_name in players:
        players[player_name].draw(main)

    pygame.display.flip()

    #lock at 60 fps
    dt = time.time() - s
    fps = int(1/dt) if dt != 0 else 60
    if dt < 0.0167:
        time.sleep(0.0167 - dt)

GameClient.stop_flag = True
pygame.quit()