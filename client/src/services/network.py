import time, socket, json, os, threading
from services.game.gamestate import GameState
from config import config

SERVER_IP = os.getenv('SERVER_IP')
if SERVER_IP == None:
  SERVER_IP = config['SERVER_IP']

SERVER_PORT = os.getenv('SERVER_PORT')
if SERVER_PORT == None:
  SERVER_PORT = config['SERVER_PORT']
else:
  SERVER_PORT = int(SERVER_PORT)

CLIENT_PORT = os.getenv('CLIENT_PORT')
if CLIENT_PORT == None:
  CLIENT_PORT = config['CLIENT_PORT']
else:
  CLIENT_PORT = int(CLIENT_PORT)

print('Server address set to ', SERVER_IP, 'port', SERVER_PORT, ', client using port', CLIENT_PORT)

class Session:

  #some kind of other session data idk
  def __init__(self, mock_game=None):
    self.debug = mock_game != None
    self.stop = False
    self.mock = mock_game
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.bind(('', CLIENT_PORT))
    self.state = None
    self.rec_thread = threading.Thread(target=self.rec, args=())
    self.n = 0


  # sends data to the server, includes
  # player paddle position and metadata
  def send(self, paddle_pos):
    # update game state based on received data
    if self.mock != None:
      self.mock.update_paddle_pos(paddle_pos)
    else:
      if self.sock and self.state and (self.n == 1 and 'player_1_id' in self.state and self.state['player_1_id'] != 0):
        print('sending updated player 1 pos')
        self.sock.sendto(str.encode(json.dumps({
          'message': 'update',
          'timestamp': time.time(),
          'data': {
            'room_id': self.state['room_id'],
            'player_id': self.state['player_1_id'],
            'paddle_pos': paddle_pos
            }
          },)), (SERVER_IP, SERVER_PORT))
      elif self.sock and self.state and (self.n == 2 and 'player_2_id' in self.state and self.state['player_2_id'] != 0):
        print('sending updated player 2 pos')
        self.sock.sendto(str.encode(json.dumps({
          'message': 'update',
          'timestamp': time.time(),
          'data': {
            'room_id': self.state['room_id'],
            'player_id': self.state['player_2_id'],
            'paddle_pos': paddle_pos
            }
          },)), (SERVER_IP, SERVER_PORT))
  
  def get_state(self):
    if self.mock == None:
      game = GameState()
      #print(self.state)
      if self.state != None:
        game.paddle_positions = self.state['paddle_positions']
        game.ball_pos = self.state['ball_pos']
        game.score = self.state['score']
        game.winner = self.state['winner']
        game.room_id = self.state['room_id']
        game.playernumber = self.n
      return game
    return self.mock.game

  def quit(self):
    self.stop = True
    self.sock.close()
    self.rec_thread.join()
    print('quitting you fuck')

  def init_connection(self, mode, room_id=0):
    print('initiating connection', mode, room_id)
    if mode == 'start':
      self.sock.sendto(str.encode(json.dumps({'message': 'start', 'timestamp': time.time()})), (SERVER_IP, SERVER_PORT))
      self.rec_thread.start()
      self.n = 1
    if mode == 'join':
      print('connecting...')
      self.sock.sendto(str.encode(json.dumps({'message': 'connect', 'timestamp': time.time(), 'data': {'room_id': int(room_id)}})), (SERVER_IP, SERVER_PORT))
      self.n = 2

  def rec(self):
    print('starting receive thread')
    while not self.stop:
      data, addr = self.sock.recvfrom(1024)
      packet = data.decode('utf-8')
      print('INCOMING MESSAGE', packet)
      packet = json.loads(packet)
      self.state = packet
      
    print('stopping the running')

    


      

    
    