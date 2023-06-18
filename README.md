# Tic-Tac-Toe Server

This is a very simple implementation of a tic-tac-toe server and client. It allows two players to play tic-tac-toe via http requests.  

## Running the code

The project uses poetry for dependencies.  
Instructions for installing [here](https://python-poetry.org/docs/#installation).  
`poetry install` to install the required packages. 

`poetry run uvicorn server.server_main:app` to run the server.  

## Playing

The full api documentation is available at `/docs`  

There's a cli client under `t3_client/client_main.py`.  
Run `poetry run python t3_client/client_main.py --help` for instructions on how to use it.  

Start a game with  
`poetry run python ./t3_client/client_main.py start --name "player1"`

Join a game as the second player with  
`poetry run python ./t3_client/client_main.py --cache-location t4_cache join --name "player2" --game-id <GAME_ID>`

Get the game state with  
`poetry run python ./t3_client/client_main.py state`

Play a turn with  
`poetry run python ./t3_client/client_main.py turn 0 0`

Play a turn with an image with  
`poetry run python ./t3_client/client_main.py image-turn tic-tac-toe-example.png`