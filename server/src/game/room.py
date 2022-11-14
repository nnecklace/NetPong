import time
import random
import json
import math

BALL_WIDTH = .025
BALL_HEIGHT = BALL_WIDTH * 3 / 2
PAD_WIDTH = .015
PAD_HEIGHT = .2
HALF_PAD_WIDTH = PAD_WIDTH / 2
HALF_PAD_HEIGHT = PAD_HEIGHT / 2
WINNING_SCORE = 3
BOUNCE_SPEED_UP = 1.1
PADDLE_VEL = 1.2
BALL_HORZ_RANGE = (0.2, 0.4)
BALL_VERT_RANGE = (0, 0.3)
KILL_TIMEOUT = 10 # in seconds
TICKS_PER_SECOND = 1 # for production a value of 60 should be okay
TICK_RATE = 1/TICKS_PER_SECOND

room_state = {
    "player_1_id": random.getrandbits(32),
    "player_1_pos": 0.5,
    "ball_pos": [0.5, 0.5],
    "ball_velocity": [0, 0],
    "paddle_positions": [0.5, 0.5],
    "state": 'waiting',
    "score": [0, 0],
    "last_updated": 0,
    "player_1_addr": None,
    "player_2_addr": None,
    "winner": 0,
    "player_1_socket": None,
    "player_2_socket": None
}


def mag(vec):
    return math.sqrt((math.pow(vec[0], 2) + math.pow(vec[1], 2)))


def normalize(vec):
    magnitude = mag(vec)
    return [vec[0]/magnitude, vec[1]/magnitude]


def start(id, state, socket):
    packet = state.pop()
    print(f'starting game room %s' % id)
    room_state["room_id"] = id
    room_state["player_1_addr"] = packet['addr']
    room_state["player_1_socket"] = socket
    answer(socket, packet['addr'])
    run(id, state, socket)


def answer(socket, addr):
    response = {k: i for k, i in room_state.items(
    ) if k != "player_1_socket" and k != "player_2_socket"}
    res = json.dumps(response)
    socket.sendto(str.encode(res), addr)


def connect(id, state, socket, addr):
    if room_state["state"] != 'running':
        room_state["player_2_pos"] = 0.5
        room_state["player_2_id"] = random.getrandbits(32)
        room_state["player_2_addr"] = addr
        room_state["player_2_socket"] = socket
        init()
        answer(socket, addr)


def update(state, delta_time):
    game = room_state
    game['ball_pos'][0] += game['ball_velocity'][0] * delta_time
    game['ball_pos'][1] += game['ball_velocity'][1] * delta_time

    # ball collision check on top and bottom walls
    if game['ball_pos'][1] <= BALL_HEIGHT/2:
        game['ball_velocity'][1] = - game['ball_velocity'][1]
    if game['ball_pos'][1] >= 1 - BALL_HEIGHT/2:
        game['ball_velocity'][1] = - game['ball_velocity'][1]
    # if someone scores, do something

    # ball collison check on gutters or paddles
    if game['ball_pos'][0] <= BALL_WIDTH/2 + PAD_WIDTH:
        if (game['ball_pos'][1] <= game['paddle_positions'][0] + HALF_PAD_HEIGHT
                and game['ball_pos'][1] >= game['paddle_positions'][0] - HALF_PAD_HEIGHT):
            if game['ball_velocity'][0] < 0:
                bounce_from_paddle(0)
        elif game['ball_pos'][0] <= BALL_WIDTH/2:
            score(1)
    elif game['ball_pos'][0] >= 1 - (BALL_WIDTH/2 + PAD_WIDTH):
        if (game['ball_pos'][1] <= game['paddle_positions'][1] + HALF_PAD_HEIGHT and game['ball_pos'][1] >= game['paddle_positions'][1] - HALF_PAD_HEIGHT):
            if game['ball_velocity'][0] > 0:
                bounce_from_paddle(1)
            elif game['ball_pos'][0] >= 1 - BALL_WIDTH/2:
                score(0)


def ball_init(right):
    game = room_state
    game['ball_pos'] = [0.5, 0.5]
    #horz = px_to_frac(random.randrange(2,4), 600)
    horz = random.uniform(BALL_HORZ_RANGE[0], BALL_HORZ_RANGE[1])
    #vert = px_to_frac(random.randrange(0,3), 400)
    vert = random.uniform(BALL_VERT_RANGE[0], BALL_VERT_RANGE[1])
    if random.randrange(0, 2) == 0:
        vert = -vert
    if not right:
        horz = - horz

    game['ball_vel'] = [horz, -vert]


def init():
    game = room_state
    game['state'] = 'running'
    game['winner'] = 0
    if random.randrange(0, 2) == 0:
        ball_init(True)
    else:
        ball_init(False)


def score(p):
    game = room_state
    game['score'][p] += 1
    if game['score'][p] >= WINNING_SCORE:
        game['state'] = 'ended'
        game['winner'] = p
    else:
        ball_init(p == 1)


def bounce_from_paddle(paddle):
    game = room_state
    game['ball_velocity'][0] = -game['ball_velocity'][0]
    game['ball_velocity'][0] *= BOUNCE_SPEED_UP
    game['ball_velocity'][1] *= BOUNCE_SPEED_UP
    # get speed
    speed = mag(game['ball_velocity'])
    # get diff from paddle middle
    diff_frac = (game['ball_pos'][1] -
                 game['paddle_positions'][paddle]) / HALF_PAD_HEIGHT
    # calculate new direction vector
    new_dir = normalize(
        [game['ball_velocity'][0] / abs(game['ball_velocity'][0]), diff_frac])
    # multiply by speed
    game['ball_velocity'] = [new_dir[0] * speed, new_dir[1] * speed]

def update_paddle(player_id, paddle_pos):
    pass


# Kill room if there are no connections for 10 seconds
def should_kill():
    if time.time() - room_state['last_updated'] > KILL_TIMEOUT:
        return True
    else return False

def run(id, state, socket):

    prev_tick = time.time()
    
    while not should_kill():
        delta_time = time.time() - prev_tick
        # time.sleep(5)
        

        try:
            if len(state) > 0:
                next = state.pop()
                addr = next['addr']
                if next['timestamp'] > room_state['last_updated']:
                    room_state['last_updated'] = time.time()
                    if next['message'] == 'connect':
                        connect(id, state, socket, addr)
                    elif next['message'] == 'update':
                        print('updating')
                        update_paddle(0,0)

        # Updates game state 60 times per second
        if (delta_time > TICK_RATE)
            #update
            print(f'Updating game room {id} with state {room_state}...')
            update(state, delta_time)
            #send state
            if room_state['state'] == 'running':
                answer(room_state['player_1_socket'],
                       room_state['player_1_addr'])
                #answer(room_state['player_2_socket'],
                #       room_state['player_2_addr'])
        
        except Exception:
            print('fuck')
            #socket.sendto(str.encode('wat'), addr)
