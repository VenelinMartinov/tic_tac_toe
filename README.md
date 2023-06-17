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