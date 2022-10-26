#PONG pygame

import random
import pygame, sys
from game.gamestate import GameState
from pygame.locals import *
from helpers.convert import *


pygame.init()
fps = pygame.time.Clock()

#colors
WHITE = (255,255,255)
BLACK = (0,0,0)

#globals
game = GameState()
WIDTH = 600
HEIGHT = 400
BALL_EDGE = .035
BALL_HEIGHT = (3*BALL_EDGE/2)
PAD_WIDTH = .015
PAD_HEIGHT = .2
HALF_PAD_WIDTH = PAD_WIDTH / 2
HALF_PAD_HEIGHT = PAD_HEIGHT / 2
paddle1_vel = 0
paddle2_vel = 0
paddle1_x = HALF_PAD_WIDTH
paddle2_x = 1 - HALF_PAD_WIDTH

#canvas declaration
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
    global paddle1_vel, paddle2_vel  # these are floats
    global score1, score2  # these are ints
    #paddle1_pos = [HALF_PAD_WIDTH - 1,HEIGHT/2]
    #paddle2_pos = [WIDTH +1 - HALF_PAD_WIDTH,HEIGHT/2]
    game.paddle_positions = [.5,.5]
    game.score = [0,0]
    if random.randrange(0,2) == 0:
        ball_init(True)
    else:
        ball_init(False)


#draw function of canvas
def draw(canvas):
    canvas.fill(BLACK)
    pygame.draw.line(canvas, WHITE, [WIDTH / 2, 0],[WIDTH / 2, HEIGHT], 1)
    pygame.draw.line(canvas, WHITE, [PAD_WIDTH, 0],[PAD_WIDTH, HEIGHT], 1)
    pygame.draw.line(canvas, WHITE, [WIDTH - PAD_WIDTH, 0],[WIDTH - PAD_WIDTH, HEIGHT], 1)
    pygame.draw.circle(canvas, WHITE, [WIDTH//2, HEIGHT//2], 70, 1)

    # update paddle's vertical position, keep paddle on the screen
    if game.paddle_positions[0] > HALF_PAD_HEIGHT and game.paddle_positions[0] < 1 - HALF_PAD_HEIGHT:
        game.paddle_positions[0] += paddle1_vel
    elif game.paddle_positions[0] <= HALF_PAD_HEIGHT and paddle1_vel > 0:
        game.paddle_positions[0] += paddle1_vel
    elif game.paddle_positions[0] >= 1 - HALF_PAD_HEIGHT and paddle1_vel < 0:
        game.paddle_positions[0] += paddle1_vel
    
    if game.paddle_positions[1] > HALF_PAD_HEIGHT and game.paddle_positions[1] < 1 - HALF_PAD_HEIGHT:
        game.paddle_positions[1] += paddle2_vel
    elif game.paddle_positions[1] <= HALF_PAD_HEIGHT and paddle2_vel > 0:
        game.paddle_positions[1] += paddle2_vel
    elif game.paddle_positions[1] >= 1 - HALF_PAD_HEIGHT and paddle2_vel < 0:
        game.paddle_positions[1] += paddle2_vel

    #update ball
    game.ball_pos[0] += game.ball_vel[0]
    game.ball_pos[1] += game.ball_vel[1]

    #draw paddles and ball
    #pygame.draw.circle(canvas, WHITE, [frac_to_px(game.ball_pos[0], WIDTH), frac_to_px(game.ball_pos[1], HEIGHT)], 20, 0)
    pygame.draw.rect(canvas, WHITE, (
        frac_to_px(game.ball_pos[0] - BALL_EDGE / 2, WIDTH), #left
        frac_to_px(game.ball_pos[1] - BALL_EDGE / 2, HEIGHT), #top
        frac_to_px(BALL_EDGE, WIDTH),#width
        frac_to_px(BALL_EDGE, HEIGHT)#height
    ))
    pygame.draw.polygon(canvas, WHITE,[[0, frac_to_px(game.paddle_positions[0] - HALF_PAD_HEIGHT, HEIGHT)], [0, frac_to_px(game.paddle_positions[0] + HALF_PAD_HEIGHT, HEIGHT)], [frac_to_px(PAD_WIDTH, WIDTH), frac_to_px(game.paddle_positions[0] + HALF_PAD_HEIGHT, HEIGHT)], [frac_to_px(PAD_WIDTH, WIDTH), frac_to_px(game.paddle_positions[0] - HALF_PAD_HEIGHT, HEIGHT)]], 0)
    pygame.draw.polygon(canvas, WHITE, [[frac_to_px(1-PAD_WIDTH, WIDTH), frac_to_px(game.paddle_positions[1] - HALF_PAD_HEIGHT, HEIGHT)], [frac_to_px(1-PAD_WIDTH, WIDTH), frac_to_px(game.paddle_positions[1] + HALF_PAD_HEIGHT, HEIGHT)], [frac_to_px(1, WIDTH), frac_to_px(game.paddle_positions[1] + HALF_PAD_HEIGHT, HEIGHT)], [frac_to_px(1, WIDTH), frac_to_px(game.paddle_positions[1] - HALF_PAD_HEIGHT, HEIGHT)]], 0)

    #ball collision check on top and bottom walls
    if game.ball_pos[1] <= BALL_EDGE/2:
        game.ball_vel[1] = - game.ball_vel[1]
    if game.ball_pos[1] >= 1 - BALL_EDGE/2:
        game.ball_vel[1] = - game.ball_vel[1]
    
    #ball collison check on gutters or paddles
    if game.ball_pos[0] <= BALL_EDGE/2 + PAD_WIDTH:
        if (game.ball_pos[1] <= game.paddle_positions[0] + HALF_PAD_HEIGHT
            and game.ball_pos[1] >= game.paddle_positions[0] - HALF_PAD_HEIGHT):
            game.ball_vel[0] = -game.ball_vel[0]
            game.ball_vel[0] *= 1.1
            game.ball_vel[1] *= 1.1
        else:
            game.score[1] += 1
            ball_init(True)
    elif game.ball_pos[0] >= 1 - (BALL_EDGE/2 + PAD_WIDTH):
        if (game.ball_pos[1] <= game.paddle_positions[1] + HALF_PAD_HEIGHT
            and game.ball_pos[1] >= game.paddle_positions[1] - HALF_PAD_HEIGHT):
            game.ball_vel[0] = -game.ball_vel[0]
            game.ball_vel[0] *= 1.1
            game.ball_vel[1] *= 1.1
        else:
            game.score[0] += 1
            ball_init(False)

    #update scores
    myfont1 = pygame.font.SysFont("agencyfb", 20)
    label1 = myfont1.render("Score "+str(game.score[0]), 1, WHITE)
    canvas.blit(label1, (50,20))

    myfont2 = pygame.font.SysFont("agencyfb", 20)
    label2 = myfont2.render("Score "+str(game.score[1]), 1, WHITE)
    canvas.blit(label2, (470,20))  
    
    
#keydown handler
def keydown(event):
    global paddle1_vel, paddle2_vel
    
    if event.key == K_UP:
        paddle2_vel = -.02
    elif event.key == K_DOWN:
        paddle2_vel = .02
    elif event.key == K_w:
        paddle1_vel = -.02
    elif event.key == K_s:
        paddle1_vel = .02

#keyup handler
def keyup(event):
    global paddle1_vel, paddle2_vel
    
    if event.key in (K_w, K_s):
        paddle1_vel = 0
    elif event.key in (K_UP, K_DOWN):
        paddle2_vel = 0

init()


#game loop
while True:

    draw(window)

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
    fps.tick(60)