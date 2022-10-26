import socket
from multiprocessing import Process, Manager
from game import room
import random

idx = []


def start(id, state):
    state.append(100+id)
    room.start(id, state)


if __name__ == '__main__':
    print('Server starting....')
    print('Listening to port 5005')
    UDP_IP = '127.0.0.1'
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    manager = Manager()
    state = manager.dict()

    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode('utf-8')
        print("message %s" % message)
        if message.strip() == 'start':
            print('start recv')
            id = random.randint(1, 10)
            idx.append(id)
            state[id] = manager.list()
            state[id].append(id)
            p = Process(target=start, args=(id, state[id]))
            p.start()
        elif message.strip() == 'add':
            ran = random.randint(1, 100)
            id = idx[0]
            state[id].append(ran)
            print(state)
