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
WIN_TIMEOUT = 10
TICKS_PER_SECOND = 60 # for production a value of 60 should be okay
TICK_RATE = 1/TICKS_PER_SECOND
BALL_SPEED_MULTIPLIER = 1 # 1 for production

room_state = {
    "player_1_id": random.getrandbits(32),
    "player_2_id": None,
    "ball_pos": [0.5, 0.5],
    "ball_velocity": [0, 0],
    "paddle_positions": [0.5, 0.5],
    "state": 'waiting',
    "score": [0, 0],
    "player_1_addr": None,
    "player_2_addr": None,
    "winner": 0,
    "player_1_socket": None,
    "player_2_socket": None,
    "player_1_last_update": 0,
    "player_2_last_update": 0
}


def mag(vec):
    return math.sqrt((math.pow(vec[0], 2) + math.pow(vec[1], 2)))


def normalize(vec):
    magnitude = mag(vec)
    return [vec[0]/magnitude, vec[1]/magnitude]


def start(room_id, state, socket):
    packet = state.pop()
    print(f'starting game room %s' % room_id)
    room_state["room_id"] = room_id
    room_state["player_1_addr"] = packet['addr']
    room_state["player_1_socket"] = socket
    answer(socket, packet['addr'])
    run(room_id, state, socket)


def answer(socket, addr):
    response = {k: i for k, i in room_state.items(
    ) if k != "player_1_socket" and k != "player_2_socket" and "player_1_addr" and "player_2_addr"}
    res = json.dumps(response)
    socket.sendto(str.encode(res), addr)


def connect(room_id, state, socket, addr):
    print('connecting')
    if room_state["state"] != 'running':
        room_state["player_2_pos"] = 0.5
        room_state["player_2_id"] = random.getrandbits(32)
        room_state["player_2_addr"] = addr
        room_state["player_2_socket"] = socket
        answer(socket, addr)
        init()


def update(delta_time):
    room_state['ball_pos'][0] += room_state['ball_velocity'][0] * delta_time * BALL_SPEED_MULTIPLIER
    room_state['ball_pos'][1] += room_state['ball_velocity'][1] * delta_time * BALL_SPEED_MULTIPLIER


    # ball collision check on top and bottom walls
    if room_state['ball_pos'][1] <= BALL_HEIGHT/2:
        room_state['ball_velocity'][1] = - room_state['ball_velocity'][1]
    if room_state['ball_pos'][1] >= 1 - BALL_HEIGHT/2:
        room_state['ball_velocity'][1] = - room_state['ball_velocity'][1]
    # if someone scores, do something

    # ball collison check on gutters or paddles
    if room_state['ball_pos'][0] <= BALL_WIDTH/2 + PAD_WIDTH:
        if (room_state['ball_pos'][1] <= room_state['paddle_positions'][0] + HALF_PAD_HEIGHT
                and room_state['ball_pos'][1] >= room_state['paddle_positions'][0] - HALF_PAD_HEIGHT):
            if room_state['ball_velocity'][0] < 0:
                bounce_from_paddle(0)
        elif room_state['ball_pos'][0] <= BALL_WIDTH/2:
            score(1)
    elif room_state['ball_pos'][0] >= 1 - (BALL_WIDTH/2 + PAD_WIDTH):
        if (room_state['ball_pos'][1] <= room_state['paddle_positions'][1] + HALF_PAD_HEIGHT and room_state['ball_pos'][1] >= room_state['paddle_positions'][1] - HALF_PAD_HEIGHT):
            if room_state['ball_velocity'][0] > 0:
                bounce_from_paddle(1)
        elif room_state['ball_pos'][0] >= 1 - BALL_WIDTH/2:
            score(0)


def ball_init(right):
    room_state['ball_pos'] = [0.5, 0.5]
    horz = random.uniform(BALL_HORZ_RANGE[0], BALL_HORZ_RANGE[1])
    vert = random.uniform(BALL_VERT_RANGE[0], BALL_VERT_RANGE[1])
    if random.randrange(0, 2) == 0:
        vert = -vert
    if not right:
        horz = - horz

    room_state['ball_velocity'] = [horz, -vert]


def init():
    print('Initializing game...')
    room_state['state'] = 'running'
    room_state['winner'] = 0
    if random.randrange(0, 2) == 0:
        ball_init(True)
    else:
        ball_init(False)


def score(p):
    room_state['score'][p] += 1
    if room_state['score'][p] >= WINNING_SCORE:
        room_state['state'] = 'ended'
        room_state['winner'] = p
        room_state['win_time'] = time.time()
    else:
        ball_init(p == 1)


def bounce_from_paddle(paddle):
    room_state['ball_velocity'][0] = -room_state['ball_velocity'][0]
    room_state['ball_velocity'][0] *= BOUNCE_SPEED_UP
    room_state['ball_velocity'][1] *= BOUNCE_SPEED_UP
    # get speed
    speed = mag(room_state['ball_velocity'])
    # get diff from paddle middle
    diff_frac = (room_state['ball_pos'][1] -
                 room_state['paddle_positions'][paddle]) / HALF_PAD_HEIGHT
    # calculate new direction vector
    new_dir = normalize(
        [room_state['ball_velocity'][0] / abs(room_state['ball_velocity'][0]), diff_frac])
    # multiply by speed
    room_state['ball_velocity'] = [new_dir[0] * speed, new_dir[1] * speed]

def update_paddle(player_id, paddle_pos):
    if player_id == room_state['player_1_id']:
        room_state['paddle_positions'][0] = paddle_pos
    elif player_id == room_state['player_2_id']:
        room_state['paddle_positions'][1] = paddle_pos


# Kill room if there are no connections for 10 seconds
def should_kill():
    current = time.time()
    if ((current - room_state['player_1_last_update'] > KILL_TIMEOUT and
        current - room_state['player_1_last_update'] > KILL_TIMEOUT) or
        (room_state['state'] == 'ended' and current - room_state['win_time'] > WIN_TIMEOUT)):
        return True
    else:
        return False

def run(room_id, state, socket):

    prev_tick = time.time()
    room_state['player_1_last_update'] = time.time()
    room_state['player_2_last_update'] = time.time()
    
    while not should_kill():
        current_time = time.time()
        delta_time = current_time - prev_tick
        # time.sleep(5)

        try:
            if len(state) > 0:
                next = state.pop()
                addr = next['addr']
                if next['message'] == 'connect':
                    connect(room_id, state, socket, addr)
                elif next['message'] == 'update':
                    if next['timestamp'] > room_state['player_1_last_update'] and next['data']['player_id'] == room_state['player_1_id']:
                        data = next['data']
                        room_state['player_1_last_update'] = current_time
                        update_paddle(data['player_id'], data['paddle_pos'])
                    
                    elif next['timestamp'] > room_state['player_2_last_update'] and next['data']['player_id'] == room_state['player_2_id']:
                        data = next['data']
                        room_state['player_2_last_update'] = current_time
                        update_paddle(data['player_id'], data['paddle_pos'])
        
        except Exception:
            print('Unknown exception!')
            #socket.sendto(str.encode('wat'), addr)

        # Updates game state 60 times per second
        if delta_time > TICK_RATE:
            #update
            update(delta_time)
            #send state
            if room_state['state'] == 'running' or room_state['state'] == 'ended':
                answer(room_state['player_1_socket'],
                    room_state['player_1_addr'])
                answer(room_state['player_2_socket'],
                       room_state['player_2_addr'])

            prev_tick = current_time

    print('killing room', room_state['room_id'])