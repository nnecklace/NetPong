import socket
from multiprocessing import Process, Manager
from game import room
import random
import json


def start(room_id, state, socket):
    room.start(room_id, state, socket)


def create_message(msg, addr, timestamp, data=None):
    return {'message': msg, 'addr': addr, 'timestamp': timestamp, 'data': data}


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
        packet = json.loads(packet)
        message = packet['message']
        timestamp = packet['timestamp']
        if message.strip() == 'start':
            print("start recv, message %s" % packet)
            room_id = random.randint(1, 10)
            state[room_id] = manager.list()
            state[room_id].append(create_message('start', addr, timestamp))
            p = Process(target=start, args=(room_id, state[room_id], sock))
            p.start()
        elif message.strip() == 'connect':
            print("connect recv, message %s" % packet)
            room_id = packet['data']['room_id']
            state[room_id].append(create_message('connect', addr, timestamp, packet['data']))
        elif message.strip() == 'update':
            #print('update recv')
            room_id = packet['data']['room_id']
            state[room_id].append(create_message('update', addr, timestamp, packet['data']))
