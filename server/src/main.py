import socket
from multiprocessing import Process
from game import room
import random


def start(id):
    room.start(id)


if __name__ == '__main__':
    print('Server starting....')
    print('Listening to port 5005')
    UDP_IP = '127.0.0.1'
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode('utf-8')
        print("message %s" % message)
        if message.strip() == 'start':
            print('start recv')
            id = random.randint(1, 10)
            p = Process(target=start, args=(id,))
            p.start()
            p.join()
