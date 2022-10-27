import random
from services.game.gamestate import GameState
from helpers.config import *
from helpers.convert import mag, normalize


class MockGame:
  def __init__(self):
    print('Mock Game initiated')
    self.game = GameState()

  def init(self):
    self.game.status = 'running'
    self.game.winner = 0
    self.game.paddle_positions = [.5,.5]
    self.game.score = [0,0]
    if random.randrange(0,2) == 0:
        self.ball_init(True)
    else:
        self.ball_init(False)

  # helper function that spawns a ball, returns a position vector and a velocity vector
  # if right is True, spawn to the right, else spawn to the left
  def ball_init(self,right):
    self.game.ball_pos = [.5, .5]
    #horz = px_to_frac(random.randrange(2,4), 600)
    horz = random.uniform(BALL_HORZ_RANGE[0], BALL_HORZ_RANGE[1])
    #vert = px_to_frac(random.randrange(0,3), 400)
    vert = random.uniform(BALL_VERT_RANGE[0], BALL_VERT_RANGE[1])
    if random.randrange(0,2) == 0:
        vert = -vert
    if not right:
        horz = - horz
        
    self.game.ball_vel = [horz,-vert]

  def update(self, deltatime):
    #update ball
    game = self.game
    game.ball_pos[0] += game.ball_vel[0] * deltatime / 1000
    game.ball_pos[1] += game.ball_vel[1] * deltatime / 1000

    #ball collision check on top and bottom walls
    if game.ball_pos[1] <= BALL_HEIGHT/2:
        game.ball_vel[1] = - game.ball_vel[1]
    if game.ball_pos[1] >= 1 - BALL_HEIGHT/2:
        game.ball_vel[1] = - game.ball_vel[1]
    #if someone scores, do something

    #ball collison check on gutters or paddles
    if game.ball_pos[0] <= BALL_WIDTH/2 + PAD_WIDTH:
      if (game.ball_pos[1] <= game.paddle_positions[0] + HALF_PAD_HEIGHT
        and game.ball_pos[1] >= game.paddle_positions[0] - HALF_PAD_HEIGHT):
        if game.ball_vel[0] < 0:
          self.bounce_from_paddle(0)
      elif game.ball_pos[0] <= BALL_WIDTH/2:
        self.score(1)
    elif game.ball_pos[0] >= 1 - (BALL_WIDTH/2 + PAD_WIDTH):
      if (game.ball_pos[1] <= game.paddle_positions[1] + HALF_PAD_HEIGHT
        and game.ball_pos[1] >= game.paddle_positions[1] - HALF_PAD_HEIGHT):
        if game.ball_vel[0] > 0:
          self.bounce_from_paddle(1)
      elif game.ball_pos[0] >= 1 - BALL_WIDTH/2:
        self.score(0)

  def bounce_from_paddle(self, paddle):
    game = self.game
    game.ball_vel[0] = -game.ball_vel[0]
    game.ball_vel[0] *= BOUNCE_SPEED_UP
    game.ball_vel[1] *= BOUNCE_SPEED_UP
    #get speed
    speed = mag(game.ball_vel)
    #get diff from paddle middle
    diff_frac = (game.ball_pos[1] - game.paddle_positions[paddle]) / HALF_PAD_HEIGHT
    #calculate new direction vector
    new_dir = normalize([game.ball_vel[0] / abs(game.ball_vel[0]), diff_frac])
    #multiply by speed
    game.ball_vel = [new_dir[0] * speed, new_dir[1] * speed]

  def score(self,p):
    game = self.game
    game.score[p] += 1
    if game.score[p] >= WINNING_SCORE:
        game.status = 'ended'
        game.winner = p
    else:
        self.ball_init(p==1)
      
  
  def update_paddle_pos(self, p):
    self.game.paddle_positions[0] = p
  
