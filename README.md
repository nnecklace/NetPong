# NetPong

## Client

To run the client, you need to install dependencies and create a config file for the server configuration.

### Dependencies

The client program uses the [pygame](https://www.pygame.org/news) library for the graphics interface. You can install pygame directly or by entering the `client` directory and running `pip/pip3 install -r requirements.txt`.

### Configuration

Create a file called `config.py` in the `client/src/` directory, that defines a 'config' dictionary including the keys 'SERVER_IP' and 'SERVER_PORT'. Set these values to point to the NetPong server of your choosing.

### Running the Client

To run the program on Linux or Mac, simply execute the script `run_client.sh`. If this doesn't work, try changing `python3` to just `python` in the file. On Windows, just make sure you have Python installed and you should be able to just double click the `main.py` file in `client/src/`.

## Server

To run the program on Linux or Mac, simply execute the script `run_server.sh`. If this doesn't work, try changing `python3` to just `python` in the file. On Windows, just make sure you have Python installed and you should be able to just double click the `main.py` file in `server/src/`. The server runs by default on port 5005, but this can be edited in the source code.
