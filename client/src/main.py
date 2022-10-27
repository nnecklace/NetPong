#PONG pygame
import math
import pygame, sys
from services.game.gamestate import GameState
from pygame.locals import *
from helpers.convert import *
from helpers.config import *
from services.network import Session
from services.mock_service import MockGame


pygame.init()
clock = pygame.time.Clock()

mock = None
if len(sys.argv) > 1 and sys.argv[1] == '-d':
    mock = MockGame()

session = Session(mock)
#globals
WHITE = (255,255,255)
BLACK = (0,0,0)
END_SCREEN_DURATION = 3000
STATE = 'MENU'
game = GameState()
WIDTH = 600
HEIGHT = 400
paddle0_vel = 0
paddle1_vel = 0


#surface declaration
window = pygame.display.set_mode((WIDTH, HEIGHT), RESIZABLE, 32)
pygame.display.set_caption('NetPong')


def draw_menu(surface):
    surface.fill(BLACK)
    # Start button
    button_width = .4
    button_height = .15
    border_width = .008
    pygame.draw.rect(surface, WHITE, (
        frac_to_px(.5 - button_width / 2, WIDTH),
        frac_to_px(.5 - button_height / 2, HEIGHT),
        frac_to_px(button_width, WIDTH),
        frac_to_px(button_height, HEIGHT)))
    pygame.draw.rect(surface, BLACK, (
        frac_to_px((.5 - button_width / 2) + border_width, WIDTH),
        frac_to_px((.5 - button_height / 2) + border_width * 1.5, HEIGHT),
        frac_to_px(button_width - 2 * border_width, WIDTH),
        frac_to_px(button_height - 3 * border_width, HEIGHT)))

    font_height = .1
    myfont1 = pygame.font.SysFont("agencyfb", int(frac_to_px(font_height, HEIGHT)), bold=True)
    label1 = myfont1.render("START", 1, WHITE)
    surface.blit(label1, (frac_to_px(.42, WIDTH), frac_to_px(.47, HEIGHT)))

def end_game(p):
    global STATE, win_time
    print('player ' + str(p+1) + ' has won')
    STATE = 'GAME_END'
    WINNER = p+1
    win_time = pygame.time.get_ticks()

def draw_end(surface):
    global win_time, STATE
    surface.fill(BLACK)
    font_height = .1
    myfont1 = pygame.font.SysFont("agencyfb", int(frac_to_px(font_height, HEIGHT)), bold=True)
    label1 = myfont1.render("WINNER", 1, WHITE)
    surface.blit(label1, (frac_to_px(.42, WIDTH), frac_to_px(.43, HEIGHT)))
    label2 = myfont1.render("P1", 1, WHITE)
    surface.blit(label2, (frac_to_px(.49, WIDTH), frac_to_px(.5, HEIGHT)))
    if (pygame.time.get_ticks() >= win_time + END_SCREEN_DURATION):
        STATE = 'MENU'

def update_state():
    global game, session
    net_state = session.get_state()
    game.paddle_positions = net_state.paddle_positions
    game.score = net_state.score
    game.ball_pos = net_state.ball_pos
    game.status = net_state.status
    game.winner = net_state.winner
    if game.status == 'ended':
        end_game(game.winner)

#draw function of surface
def draw_game(surface):
    # playing field, static
    surface.fill(BLACK)
    pygame.draw.line(surface, WHITE, [WIDTH / 2, 0],[WIDTH / 2, HEIGHT], 1)
    pygame.draw.line(surface, WHITE, [PAD_WIDTH, 0],[PAD_WIDTH, HEIGHT], 1)
    pygame.draw.line(surface, WHITE, [WIDTH - PAD_WIDTH, 0],[WIDTH - PAD_WIDTH, HEIGHT], 1)
    pygame.draw.line(surface, WHITE, [0, 1], [WIDTH, 1], 1)
    pygame.draw.line(surface, WHITE, [0, HEIGHT-1], [WIDTH, HEIGHT-1], 1)
    pygame.draw.circle(surface, WHITE, [WIDTH//2, HEIGHT//2], 70, 1)

    # update paddle's vertical position, keep paddle on the screen
    if game.paddle_positions[0] > HALF_PAD_HEIGHT and game.paddle_positions[0] < 1 - HALF_PAD_HEIGHT:
        game.paddle_positions[0] += paddle0_vel * deltatime / 1000
    elif game.paddle_positions[0] <= HALF_PAD_HEIGHT and paddle0_vel > 0:
        game.paddle_positions[0] += paddle0_vel * deltatime / 1000
    elif game.paddle_positions[0] >= 1 - HALF_PAD_HEIGHT and paddle0_vel < 0:
        game.paddle_positions[0] += paddle0_vel * deltatime / 1000
    
    #network functions
    session.send(game.paddle_positions[0])
    update_state()
    #Opponent's paddle, should be updated on the server
    """
    if game.paddle_positions[1] > HALF_PAD_HEIGHT and game.paddle_positions[1] < 1 - HALF_PAD_HEIGHT:
        game.paddle_positions[1] += paddle1_vel
    elif game.paddle_positions[1] <= HALF_PAD_HEIGHT and paddle1_vel > 0:
        game.paddle_positions[1] += paddle1_vel
    elif game.paddle_positions[1] >= 1 - HALF_PAD_HEIGHT and paddle1_vel < 0:
        game.paddle_positions[1] += paddle1_vel
    """

    #draw paddles and ball
    pygame.draw.rect(surface, WHITE, (
        frac_to_px(game.ball_pos[0] - BALL_WIDTH / 2, WIDTH), #left
        frac_to_px(game.ball_pos[1] - BALL_HEIGHT / 2, HEIGHT), #top
        frac_to_px(BALL_WIDTH, WIDTH),#width
        frac_to_px(BALL_HEIGHT, HEIGHT)#height
    ))
    pygame.draw.polygon(surface, WHITE,[
            [0, frac_to_px(game.paddle_positions[0] - HALF_PAD_HEIGHT, HEIGHT)],
            [0, frac_to_px(game.paddle_positions[0] + HALF_PAD_HEIGHT, HEIGHT)],
            [frac_to_px(PAD_WIDTH, WIDTH), frac_to_px(game.paddle_positions[0] + HALF_PAD_HEIGHT, HEIGHT)],
            [frac_to_px(PAD_WIDTH, WIDTH), frac_to_px(game.paddle_positions[0] - HALF_PAD_HEIGHT, HEIGHT)]
        ], 0)
    pygame.draw.polygon(surface, WHITE, [
            [frac_to_px(1-PAD_WIDTH, WIDTH), frac_to_px(game.paddle_positions[1] - HALF_PAD_HEIGHT, HEIGHT)],
            [frac_to_px(1-PAD_WIDTH, WIDTH), frac_to_px(game.paddle_positions[1] + HALF_PAD_HEIGHT, HEIGHT)],
            [frac_to_px(1, WIDTH), frac_to_px(game.paddle_positions[1] + HALF_PAD_HEIGHT, HEIGHT)],
            [frac_to_px(1, WIDTH), frac_to_px(game.paddle_positions[1] - HALF_PAD_HEIGHT, HEIGHT)]
        ],0)
    
    #update scores
    myfont1 = pygame.font.SysFont("agencyfb", 20)
    label1 = myfont1.render("Score "+str(game.score[0]), 1, WHITE)
    surface.blit(label1, (50,20))

    myfont2 = pygame.font.SysFont("agencyfb", 20)
    label2 = myfont2.render("Score "+str(game.score[1]), 1, WHITE)
    surface.blit(label2, (470,20))  
    
    
#keydown handler
def keydown(event):
    global STATE
    global paddle0_vel, paddle1_vel
    if (STATE == 'MENU'):
        if event.key == K_RETURN or event.key == K_SPACE:
            STATE = 'PLAYING'
            if mock:
                mock.init()
    elif (STATE == 'PLAYING'):
        if event.key == K_w:
            paddle0_vel = -PADDLE_VEL
        elif event.key == K_s:
            paddle0_vel = PADDLE_VEL
    

#keyup handler
def keyup(event):
    global paddle0_vel, paddle1_vel
    if (STATE == 'MENU'):
        pass
    elif (STATE == 'PLAYING'):
        if event.key in (K_w, K_s):
            paddle0_vel = 0
        elif event.key in (K_UP, K_DOWN):
            paddle1_vel = 0


while True:
    if (STATE == 'MENU'):
        draw_menu(window)
    elif (STATE == 'PLAYING'):
        draw_game(window)
    elif (STATE == 'GAME_END'):
        draw_end(window)

    for event in pygame.event.get():
        if event.type == KEYDOWN:
            keydown(event)
        elif event.type == KEYUP:
            keyup(event)
        elif event.type == QUIT:
            pygame.quit()
            session.quit()
            sys.exit()
        elif event.type == VIDEORESIZE:
            if (window.get_width() / window.get_height() >= 3 / 2):
                HEIGHT = window.get_height()
                WIDTH = int(window.get_height() * 3 / 2)
            else:
                WIDTH = window.get_width()
                HEIGHT = int(window.get_width() * 2 / 3)
            
    pygame.display.update()
    deltatime = clock.tick(60)
    mock.update(deltatime)

