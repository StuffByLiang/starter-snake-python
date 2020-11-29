import os
import random
import collections

from pprint import pprint

import cherrypy

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""

wall, clear = 1, 0

width, height = 0, 0
board = [[0 for i in range(width)] for j in range(height)]

def get_neighbours(start):
    return [(start[0] - 1, start[1]), (start[0] + 1, start[1]), (start[0], start[1] - 1), (start[0], start[1] + 1)]

def get_tail(snake):
    return (snake['body'][len(snake['body']) - 1]['x'], snake['body'][len(snake['body']) - 1]['y'])

def detect_direction(start, end):
    if end[0] < start[0]:
        return "left"
    elif end[0] > start[0]:
        return "right"
    
    if end[1] < start[1]:
        return "down"
    elif end[1] > start[1]:
        return "up"
    
    return "WTF"

def update_board(snakes, width, height):
    reset_board(width, height)
    for snake in snakes:
        for piece in snake['body']:
            board[piece['y']][piece['x']] = 1

def reset_board(width, height):
    global width, height, board
    width = width
    height = height
    board = [[0 for i in range(width)] for j in range(height)]

def bfs(grid, start, end):
    print(start)
    print(end)
    queue = collections.deque([[start]])
    seen = set([start])
    while queue:
        path = queue.popleft()
        x, y = path[-1]
        if x == end[0] and y == end[1]:
            return path
        for x2, y2 in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
            if 0 <= x2 < width and 0 <= y2 < height and grid[y2][x2] != wall and (x2, y2) not in seen:
                queue.append(path + [(x2, y2)])
                seen.add((x2, y2))
    return None

def find_move_to(start, end):
    bfs_result = bfs(board, start, end)
    if bfs_result is not None and len(bfs_result) > 1:
        return detect_direction(start, bfs_result[1])
    return None
    

class Battlesnake(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "stuffbyliang",  # TODO: Your Battlesnake Username
            "color": "#FFFF00",  # TODO: Personalize
            "head": "beluga",  # TODO: Personalize
            "tail": "curled",  # TODO: Personalize
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json

        print("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = cherrypy.request.json

        # Choose a random direction to move in
        possible_moves = ["up", "down", "left", "right"]
        move = random.choice(possible_moves)

        update_board(data['board']['snakes'], data['board']['width'], data['board']['height'])

        head = (data['you']['head']['x'], data['you']['head']['y'])

        for food in data['board']['food']:
            food = (food['x'], food['y'])
            move = find_move_to(head, food)
            if move is not None:
                print(f"FOOD MOVE: {move}")
                return {"move": move}

        # chase other snake's tail
        for snake in data['board']['snakes']:
            if (snake['name'] == data['you']['name']):
                continue
            move = find_move_to(head, get_tail(snake))
            if move is not None:
                print(f"OTHER TAIL MOVE: {move}")
                return {"move": move}

        # chase own tail
        move = find_move_to(head, get_tail(data['you']))
        if move is not None:
            print(f"SELF TAIL MOVE: {move}")
            return {"move": move}

        # no good places to go, go to a random place
        for neighbour in get_neighbours(head):
            bfs_result = bfs(board, head, neighbour)
            print(bfs_result)
            move = detect_direction(head, bfs_result[1])
            print(f"DANGER MOVE: {move}")
            return {"move": move}

        print(f"MOVE: {move}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        print("END")
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
