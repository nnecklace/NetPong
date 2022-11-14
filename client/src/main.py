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
CHOSEN_BUTTON = 0
WHITE = (255,255,255)
BLACK = (0,0,0)
END_SCREEN_DURATION = 3000
STATE = 'MENU'
game = GameState()
WIDTH = 600
HEIGHT = 400
paddle0_vel = 0
paddle1_vel = 0
ROOM_ID_MAX_CHARACTERS = 5
room_id_text = ''


#surface declaration
window = pygame.display.set_mode((WIDTH, HEIGHT), RESIZABLE, 32)
pygame.display.set_caption('NetPong')

def press_button():
  global CHOSEN_BUTTON, STATE, session
  if CHOSEN_BUTTON == 0:
    STATE = "PLAYING"
    if mock != None:
      mock.init()
    else:
      session.init_connection('start')
  elif CHOSEN_BUTTON == 1:
    STATE = 'ENTER_ROOM_ID'
    if mock != None:
      mock.init()
      
  elif CHOSEN_BUTTON == 2:
    pygame.quit()
    session.quit()
    sys.exit()


def draw_button(surface, placement, text, selected):
  button_width = .4
  button_height = .15
  border_width = .008
  # Start button
  
  pygame.draw.rect(surface, WHITE, (
    frac_to_px(.5 - button_width / 2, WIDTH),
    frac_to_px(.5 - button_height / 2 + (placement * .2), HEIGHT),
    frac_to_px(button_width, WIDTH),
    frac_to_px(button_height, HEIGHT)))
  pygame.draw.rect(surface, BLACK, (
    frac_to_px((.5 - button_width / 2) + border_width, WIDTH),
    frac_to_px((.5 - button_height / 2) + border_width * 1.5 + (placement * .2), HEIGHT),
    frac_to_px(button_width - 2 * border_width, WIDTH),
    frac_to_px(button_height - 3 * border_width, HEIGHT)))
  
  # selection highlight
  if selected:
    pygame.draw.line(surface, WHITE, 
      [frac_to_px(.5 - button_width / 2 + 3 * border_width, WIDTH), frac_to_px(.5 - button_height / 2 + 3 * border_width + (placement * .2), HEIGHT)],
      [frac_to_px(.5 - button_width / 2 + 3 * border_width, WIDTH), frac_to_px(.5 + button_height / 2 - 3 * border_width + (placement * .2), HEIGHT)], 4)
    pygame.draw.line(surface, WHITE, 
      [frac_to_px(.5 + button_width / 2 - 3 * border_width, WIDTH), frac_to_px(.5 - button_height / 2 + 3 * border_width + (placement * .2), HEIGHT)],
      [frac_to_px(.5 + button_width / 2 - 3 * border_width, WIDTH), frac_to_px(.5 + button_height / 2 - 3 * border_width + (placement * .2), HEIGHT)], 4)

  # button label
  font_height = .1
  myfont1 = pygame.font.SysFont("agencyfb", int(frac_to_px(font_height, HEIGHT)), bold=True)
  label1 = myfont1.render(text, 1, WHITE)
  surface.blit(label1, (frac_to_px(.42, WIDTH), frac_to_px(.47 + (placement * .2), HEIGHT)))

def draw_menu(surface):
  surface.fill(BLACK)
  draw_button(surface, -1, 'HOST', CHOSEN_BUTTON == 0)
  draw_button(surface, 0, 'JOIN', CHOSEN_BUTTON == 1)
  draw_button(surface, 1, 'EXIT', CHOSEN_BUTTON == 2)
  # TITLE
  myfont1 = pygame.font.SysFont("agencyfb", int(frac_to_px(.2, HEIGHT)), bold=True)
  label1 = myfont1.render('NETPONG', 1, WHITE)
  surface.blit(label1, (frac_to_px(.24, WIDTH), frac_to_px(.05, HEIGHT)))

def draw_room_id(surface):
  global room_id_text
  surface.fill(BLACK)
  draw_button(surface, 0, (room_id_text + '_'), False)

  myfont1 = pygame.font.SysFont("agencyfb", int(frac_to_px(.1, HEIGHT)), bold=True)
  label1 = myfont1.render('ENTER ROOM ID', 1, WHITE)
  surface.blit(label1, (frac_to_px(.29, WIDTH), frac_to_px(.35, HEIGHT)))

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
  game = session.get_state()
  if game.state == 'ended':
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

  #draw room id in top left corner
  myfont0 = pygame.font.SysFont("agencyfb", 20)
  label0 = myfont0.render("ROOM ID:  "+str(game.room_id), 1, WHITE)
  surface.blit(label0, (2,2))

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
  global STATE, CHOSEN_BUTTON, room_id_text
  global paddle0_vel, paddle1_vel
  if (STATE == 'MENU'):
    if event.key == K_RETURN or event.key == K_SPACE:
      press_button()
    if event.key == K_UP:
      CHOSEN_BUTTON = (CHOSEN_BUTTON - 1) % 3
    if event.key == K_DOWN:
      CHOSEN_BUTTON = (CHOSEN_BUTTON + 1) % 3
  elif (STATE == 'PLAYING'):
    if event.key == K_w:
      paddle0_vel = -PADDLE_VEL
    elif event.key == K_s:
      paddle0_vel = PADDLE_VEL
  elif (STATE == 'ENTER_ROOM_ID'):
    if event.key == K_RETURN:
      session.init_connection('join', room_id_text)
      STATE = 'PLAYING'
    elif event.key == K_BACKSPACE:
      room_id_text = room_id_text[:-1]
    elif event.key == K_ESCAPE:
      STATE = 'MENU'
      room_id_text = ''
    elif len(room_id_text) < ROOM_ID_MAX_CHARACTERS:
      room_id_text += event.unicode
    

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
    elif (STATE == 'ENTER_ROOM_ID'):
        draw_room_id(window)
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
    if (mock):
      mock.update(deltatime)

