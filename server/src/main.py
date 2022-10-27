import socket
from multiprocessing import Process, Manager
from game import room
import random
import json


def start(id, state, socket):
    room.start(id, state, socket)


if __name__ == '__main__':
    print('Server starting....')
    print('Listening to port 5005')
    UDP_IP = '127.0.0.1'
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', UDP_PORT))

    manager = Manager()
    state = manager.dict()

    while True:
        data, addr = sock.recvfrom(1024)
        packet = data.decode('utf-8')
        print("message %s" % packet)
        packet = json.loads(packet)
        message = packet['message']
        if message.strip() == 'start':
            print('start recv')
            id = random.randint(1, 10)
            state[id] = manager.list()
            state[id].append(addr)
            p = Process(target=start, args=(id, state[id], sock))
            p.start()
        elif message.strip() == 'connect':
            print('connect recv')
            id = packet['id']
            state[id].append({message: 'connect', addr: addr})
