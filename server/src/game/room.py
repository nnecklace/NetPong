import time


def start(id, state):
    print(f'starting game room %s' % id)
    print('')
    # poll queue in shared memory
    while True:
        time.sleep(5)
        print(state)
        if len(state) > 0:
            n = state.pop()
            if n:
                print(f'state is %s' % n)
                print(state)
                # break
    # do logic
    return None
