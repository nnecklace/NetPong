import time
import random
import json

room_state = {
    "player_1_id": random.getrandbits(32),
    "player_1_pos": 0.5,
    "ball_pos": (0.5, 0.5),
    "state": 'waiting',
    "score": (0, 0)
}


def start(id, state, socket):
    print(f'starting game room %s' % id)
    room_state["room_id"] = id
    res = json.dumps(room_state)
    socket.sendto(str.encode(res), state['addr'])
    run(id, state, socket)


def connect(id, state, socket, addr):
    if room_state["state"] != 'playing':
        room_state["player_2_pos"] = 0.5
        room_state["player_2_id"] = random.getrandbits(32)
        room_state['state'] = 'playing'
        res = json.dumps(room_state)
        socket.sendto(str.encode(res), addr)


def run(id, state, socket):
    while True:
        time.sleep(5)
        print(room_state)
        if len(state) > 0:
            next = state.pop()
            print(next)
            if next['message'] == 'connect':
                connect(id, state, socket, next['addr'])
