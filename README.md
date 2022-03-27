# Tic-Tac-Toe Server

## Running the code

The project uses pipenv for dependencies.  
`pip install pipenv` to install it.  
`pipenv sync` to install the required packages. 

`pipenv run uvicorn server.server_main:app` to run the server.  

## Playing

The full api is available at `/docs`  

starting a game: `curl -X POST http://127.0.0.1:8000/new_game -H "Content-Type: application/json" -d '{\"player_name\":\"player1\"}'`

joining as a second player: `curl -X POST http://127.0.0.1:8000/GAME_ID/join -H "Content-Type: application/json" -d '{\"player_name\":\"player2\"}'`

