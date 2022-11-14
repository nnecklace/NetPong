import time, socket, json, os, threading
from services.game.gamestate import GameState
from config import config

SERVER_IP = config["SERVER_IP"]
SERVER_PORT = config["SERVER_PORT"]
print('Client connecting to', SERVER_IP, 'port', SERVER_PORT)

class Session:

  #some kind of other session data idk
  def __init__(self, mock_game=None):
    self.debug = mock_game != None
    self.stop = False
    self.mock = mock_game
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.bind(('', 5005))
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
        #print('state:',self.state)
        self.sock.sendto(str.encode(json.dumps({
          'message': 'update',
          'timestamp': time.time(),
          'data': {
            'room_id': self.state['room_id'],
            'player_id': self.state['player_1_id'],
            'paddle_pos': paddle_pos
            }
          },)), (SERVER_IP, SERVER_PORT))
  
  def get_state(self):
    if self.mock == None:
      game = GameState()
      print(self.state)
      if self.state != None:
        game.paddle_positions = self.state['paddle_positions']
        game.ball_pos = self.state['ball_pos']
        game.score = self.state['score']
        game.winner = self.state['winner']
      return game
    return self.mock.game

  def quit(self):
    self.stop = True
    self.sock.close()
    self.rec_thread.join()
    print('quitting you fuck')

  def init_connection(self, mode, id=0):
    print('initiating connection', mode, id)
    if mode == 'start':
      self.sock.sendto(str.encode(json.dumps({'message': 'start', 'timestamp': time.time()})), (SERVER_IP, SERVER_PORT))
      self.rec_thread.start()
      self.n = 1
    if mode == 'join':
      print("i ain't connecting to no shit ho :D")
    #  sock.sendto('connect', (SERVER_IP, SERVER_PORT))

  def rec(self):
    print('starting receive thread')
    while not self.stop:
      data, addr = self.sock.recvfrom(1024)
      packet = data.decode('utf-8')
      print('INCOMING MESSAGE', packet)
      packet = json.loads(packet)
      self.state = packet
      
    print('stopping the running')

    


      

    
    