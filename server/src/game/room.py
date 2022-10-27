import time
import random
import socket
import json

room_state = {
    "player_1_id": random.getrandbits(32),
    "player_1_pos": 0.5,
    "ball_pos": (0.5, 0.5),
    "state": 'waiting',
    "score": (0, 0)
}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def start(id, state):
    print(f'starting game room %s' % id)
    room_state["room_id"] = id
    addr = state[0]
    res = json.dumps(room_state)
    sock.sendto(str.encode(res), addr)
    run(state)


def connect():
    if room_state["state"] != 'playing':
        room_state["player_2_pos"]: 0.5
        room_state["player_2_id"]: random.getrandbits(32)
        room_state['playing']


def run(state):
    while True:
        time.sleep(5)
        print(state)
        if len(state) > 0:
            n = state.pop()
            if n:
                print(f'state is %s' % n)
                print(state)
                # break
