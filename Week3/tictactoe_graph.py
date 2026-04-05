from random import choice
from collections import deque

WIN_SET = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
    (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)
)

board = [''] * 9
G = {
    0: [1, 3, 4], 1: [0, 2, 3, 4, 5], 2: [1, 4, 5],
    3: [0, 1, 4, 6, 7], 4: [0, 1, 2, 3, 5, 6, 7, 8],
    5: [1, 2, 4, 7, 8], 6: [3, 4, 7], 7: [3, 4, 5, 6, 8], 8: [4, 5, 7]
}

players = {'o': 'AI1', 'x': 'AI2'}
winner = None
current_player = 'o'
HR = '-' * 40

def input_move():
    global place_num
    if current_player == 'o':
        place_num = AI2_move()
    elif current_player == 'x':
        place_num = AI3_move()
    else:
        place_num = AI1_move()

def AI1_move():
    # Random search algorithm
    able_moves = [i for i in range(9) if board[i] == '']
    return choice(able_moves) if able_moves else -1

def AI2_move():  # BFS search algorithm
    able_moves = [i for i in range(9) if board[i] == '']
    if not able_moves:
        return -1
    
    queue = deque([choice(able_moves)])  # Randomly select a starting node
    visited = set()
    
    while queue:
        node = queue.popleft()
        if board[node] == '':
            return node
        visited.add(node)
        for neighbor in G[node]:
            if neighbor not in visited and board[neighbor] == '':
                queue.append(neighbor)
    return -1

def AI3_move():  # DFS search algorithm
    able_moves = [i for i in range(9) if board[i] == '']
    if not able_moves:
        return -1
    
    stack = [choice(able_moves)]  # Randomly select a starting node
    visited = set()
    
    while stack:
        node = stack.pop()
        if board[node] == '':
            return node
        visited.add(node)
        for neighbor in G[node]:
            if neighbor not in visited and board[neighbor] == '':
                stack.append(neighbor)
    return -1

def update():
    global winner, current_player, place_num
    # Check if move is valid and update the board
    if check_valid(place_num):
        board[place_num] = current_player
        winner = check_result()
        current_player = 'o' if current_player == 'x' else 'x'
    else:
        print('This place is already taken')

def check_valid(place_num):
    # Check if the chosen position is empty
    return board[place_num] == ''

def check_result():
    # Check if there is a winner
    for row in WIN_SET:
        if board[row[0]] == board[row[1]] == board[row[2]] != '':
            return board[row[0]]
    if '' not in board:
        return 'tie'
    return None

def render_board():
    # Print the current game board
    print('    %s | %s | %s' % tuple(board[:3]))
    print('   -----------')
    print('    %s | %s | %s' % tuple(board[3:6]))
    print('   -----------')
    print('    %s | %s | %s' % tuple(board[6:]))

if __name__ == '__main__':
    # render_board()
    while winner is None:
        # print(HR)
        input_move()
        update()
        # render_board()
    print('Winner is', winner)