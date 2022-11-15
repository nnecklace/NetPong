# NetPong

## Client

To run the client, you need to install dependencies and create a config file for the server configuration.

### Dependencies

The client program uses the [pygame](https://www.pygame.org/news) library for the graphics interface. You can install pygame directly or by entering the `client` directory and running `pip/pip3 install -r requirements.txt`.

### Configuration

Create a file called `config.py` in the `client/src/` directory, that defines a 'config' dictionary including the keys 'SERVER_IP', 'SERVER_PORT' and 'CLIENT_PORT'. Set the first two values to point to the NetPong server you are using. The client port is used for the client itself, so make sure that it's set to a port that is free. All of the above can also be set as environment or shell variables, which allows running several clients on one machine by overriding the client port (e.g., running one instance with simply `./run_client.sh` and another one with `CLIENT_PORT=<SOME_OTHER_PORT> ./run_client.sh`).

### Running the Client

To run the program on Linux or Mac, simply execute the script `run_client.sh`. If this doesn't work, try changing `python3` to just `python` in the file. On Windows, just make sure you have Python installed and you should be able to just double click the `main.py` file in `client/src/`.

## Server

The server has no other dependencies expect for Python 3 and should be ready to run out-of-the-box.

### Configuration

Regardless of where the server is hosted, make sure that incoming UDP messages to the port (5005 by default) are allowed to pass, and that outbound UDP transmissions are also free to go. Game settings, such as ball speed, paddle speed and score limits can be edited directly in the source code `server/src/game/room.py`.

### Running the Server

To run the program on Linux or Mac, simply execute the script `run_server.sh`. If this doesn't work, try changing `python3` to just `python` in the file. On Windows, just make sure you have Python installed and you should be able to just double click the `main.py` file in `server/src/`. The server runs by default on port 5005, but this can be edited in the source code.

## Playing the game

The user interface uses nothing but keyboard inputs for control, so menu buttons can not be pressed using mouse or touch devices. In the menu, the user can navigate through the different buttons using arrow keys and press the return or space bar keys to select any action. Inside the game, the player can move their own paddle using the up and down arrow keys. The game starts only once two players have connected.

**Note: In the current build the game crashes if a player tries to join a room that does not exist!**
