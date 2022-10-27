import time

class Session:
  #some kind of other session data idk
  def __init__(self, mock_game=None):
    self.debug = mock_game != None
    self.stop = False
    self.mock = mock_game


  # sends data to the server, includes
  # player paddle position and metadata
  def send(self, paddle_pos):
    # update game state based on received data
    self.mock.update_paddle_pos(paddle_pos)
  
  def get_state(self):
    return self.mock.game

  def quit(self):
    self.stop = True
    print('quitting you fuck')

    
    