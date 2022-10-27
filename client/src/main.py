#PONG pygame
import math
import random
import pygame, sys
from game.gamestate import GameState
from pygame.locals import *
from helpers.convert import *


pygame.init()
clock = pygame.time.Clock()

#colors
WHITE = (255,255,255)
BLACK = (0,0,0)

#globals
game = GameState()
WIDTH = 600
HEIGHT = 400
BALL_WIDTH = .025
BALL_HEIGHT = BALL_WIDTH * 3 / 2
PAD_WIDTH = .015
PAD_HEIGHT = .2
HALF_PAD_WIDTH = PAD_WIDTH / 2
HALF_PAD_HEIGHT = PAD_HEIGHT / 2
paddle0_vel = 0
paddle1_vel = 0
paddle0_x = HALF_PAD_WIDTH
paddle1_x = 1 - HALF_PAD_WIDTH
BOUNCE_SPEED_UP = 1.1

#surface declaration
window = pygame.display.set_mode((WIDTH, HEIGHT), RESIZABLE, 32)
pygame.display.set_caption('NetPong')

# helper function that spawns a ball, returns a position vector and a velocity vector
# if right is True, spawn to the right, else spawn to the left
def ball_init(right):
    game.ball_pos = [.5, .5]
    horz = px_to_frac(random.randrange(2,4), 600)
    vert = px_to_frac(random.randrange(1,3), 400)
    
    if right == False:
        horz = - horz
        
    game.ball_vel = [horz,-vert]

# define event handlers
def init():
    global paddle0_vel, paddle1_vel  # these are floats
    global score1, score2  # these are ints
    #paddle0_pos = [HALF_PAD_WIDTH - 1,HEIGHT/2]
    #paddle1_pos = [WIDTH +1 - HALF_PAD_WIDTH,HEIGHT/2]
    game.paddle_positions = [.5,.5]
    game.score = [0,0]
    if random.randrange(0,2) == 0:
        ball_init(True)
    else:
        ball_init(False)


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

def bounce_from_paddle(paddle):
    game.ball_vel[0] = -game.ball_vel[0]
    game.ball_vel[0] *= BOUNCE_SPEED_UP
    game.ball_vel[1] *= BOUNCE_SPEED_UP
    #get speed
    speed = mag(game.ball_vel)
    #calculate new direction vector
    #get diff from paddle middle
    diff_frac = (game.ball_pos[1] - game.paddle_positions[paddle]) / HALF_PAD_HEIGHT
    new_dir = normalize([game.ball_vel[0] / abs(game.ball_vel[0]), diff_frac])
    #multiply by speed
    game.ball_vel = [new_dir[0] * speed, new_dir[1] * speed]

#draw function of surface
def draw_game(surface):
    surface.fill(BLACK)
    pygame.draw.line(surface, WHITE, [WIDTH / 2, 0],[WIDTH / 2, HEIGHT], 1)
    pygame.draw.line(surface, WHITE, [PAD_WIDTH, 0],[PAD_WIDTH, HEIGHT], 1)
    pygame.draw.line(surface, WHITE, [WIDTH - PAD_WIDTH, 0],[WIDTH - PAD_WIDTH, HEIGHT], 1)
    pygame.draw.circle(surface, WHITE, [WIDTH//2, HEIGHT//2], 70, 1)

    # update paddle's vertical position, keep paddle on the screen
    if game.paddle_positions[0] > HALF_PAD_HEIGHT and game.paddle_positions[0] < 1 - HALF_PAD_HEIGHT:
        game.paddle_positions[0] += paddle0_vel
    elif game.paddle_positions[0] <= HALF_PAD_HEIGHT and paddle0_vel > 0:
        game.paddle_positions[0] += paddle0_vel
    elif game.paddle_positions[0] >= 1 - HALF_PAD_HEIGHT and paddle0_vel < 0:
        game.paddle_positions[0] += paddle0_vel
    
    if game.paddle_positions[1] > HALF_PAD_HEIGHT and game.paddle_positions[1] < 1 - HALF_PAD_HEIGHT:
        game.paddle_positions[1] += paddle1_vel
    elif game.paddle_positions[1] <= HALF_PAD_HEIGHT and paddle1_vel > 0:
        game.paddle_positions[1] += paddle1_vel
    elif game.paddle_positions[1] >= 1 - HALF_PAD_HEIGHT and paddle1_vel < 0:
        game.paddle_positions[1] += paddle1_vel

    #update ball
    game.ball_pos[0] += game.ball_vel[0]
    game.ball_pos[1] += game.ball_vel[1]

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

    #ball collision check on top and bottom walls
    if game.ball_pos[1] <= BALL_HEIGHT/2:
        game.ball_vel[1] = - game.ball_vel[1]
    if game.ball_pos[1] >= 1 - BALL_HEIGHT/2:
        game.ball_vel[1] = - game.ball_vel[1]
    
    #ball collison check on gutters or paddles
    if game.ball_pos[0] <= BALL_WIDTH/2 + PAD_WIDTH:
        if (game.ball_pos[1] <= game.paddle_positions[0] + HALF_PAD_HEIGHT
            and game.ball_pos[1] >= game.paddle_positions[0] - HALF_PAD_HEIGHT):
            if game.ball_vel[0] < 0:
                bounce_from_paddle(0)
        elif game.ball_pos[0] <= BALL_WIDTH/2:
            game.score[1] += 1
            ball_init(True)
    elif game.ball_pos[0] >= 1 - (BALL_WIDTH/2 + PAD_WIDTH):
        if (game.ball_pos[1] <= game.paddle_positions[1] + HALF_PAD_HEIGHT
            and game.ball_pos[1] >= game.paddle_positions[1] - HALF_PAD_HEIGHT):
            if game.ball_vel[0] > 0:
                bounce_from_paddle(1)
        elif game.ball_pos[0] >= 1 - BALL_WIDTH/2:
            game.score[0] += 1
            ball_init(False)

    #update scores
    myfont1 = pygame.font.SysFont("agencyfb", 20)
    label1 = myfont1.render("Score "+str(game.score[0]), 1, WHITE)
    surface.blit(label1, (50,20))

    myfont2 = pygame.font.SysFont("agencyfb", 20)
    label2 = myfont2.render("Score "+str(game.score[1]), 1, WHITE)
    surface.blit(label2, (470,20))  
    
    
#keydown handler
def keydown(event):
    global paddle0_vel, paddle1_vel
    
    if event.key == K_UP:
        paddle1_vel = -.02
    elif event.key == K_DOWN:
        paddle1_vel = .02
    elif event.key == K_w:
        paddle0_vel = -.02
    elif event.key == K_s:
        paddle0_vel = .02

#keyup handler
def keyup(event):
    global paddle0_vel, paddle1_vel
    
    if event.key in (K_w, K_s):
        paddle0_vel = 0
    elif event.key in (K_UP, K_DOWN):
        paddle1_vel = 0


cont = False
while not cont:

    draw_menu(window)

    for event in pygame.event.get():
        if event.type == KEYDOWN and (event.key == K_RETURN or event.key == K_SPACE):
            cont = True
        elif event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == VIDEORESIZE:
            if (window.get_width() / window.get_height() >= 3 / 2):
                HEIGHT = window.get_height()
                WIDTH = int(window.get_height() * 3 / 2)
            else:
                WIDTH = window.get_width()
                HEIGHT = int(window.get_width() * 2 / 3)
            
    pygame.display.update()
    clock.tick(30)

init()

#game loop
while True:
    draw_game(window)

    for event in pygame.event.get():

        if event.type == KEYDOWN:
            keydown(event)
        elif event.type == KEYUP:
            keyup(event)
        elif event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == VIDEORESIZE:
            if (window.get_width() / window.get_height() >= 3 / 2):
                HEIGHT = window.get_height()
                WIDTH = int(window.get_height() * 3 / 2)
            else:
                WIDTH = window.get_width()
                HEIGHT = int(window.get_width() * 2 / 3)
        
    pygame.display.update()
    clock.tick(60)