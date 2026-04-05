from random import randrange
import random

WIN_SET = (
	(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
	(1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)
)

board=['']*9

players = {
    'o' : 'AI1',
    'x' : 'AI2'
}

winner = None
current_player = None

HR = '-' * 40

def input_move():
    global place_num
    
    if current_player == 'o':
        place_num = AI1_move()
        if place_num>8:
            place_num-=8
    else: place_num = AI2_move()

def AI1_move():
    # find a winning move for AI1
    for row in WIN_SET:
        line = [board[row[0]], board[row[1]], board[row[2]]]
        if line.count('o') == 2 and line.count('') == 1:  
            return row[line.index('')]  

    # block AI2's winning move
    for row in WIN_SET:
        line = [board[row[0]], board[row[1]], board[row[2]]]
        if line.count('x') == 2 and line.count('') == 1:  
            return row[line.index('')]  

    # select the first available empty space
    for i in range(9):
        if board[i] == '':
            return i 

    # else
    return randrange(9)  
        

def AI2_move():
    # select center first
    if board[4]=='':
        return 4
    # select corner second
    elif board[0]==board[2]==board[6]==board[8]:
        return random.choice([0,2,6,8])
    # else
    else:
        return random.choice([1,3,5,7])
        

def update():
    global winner, current_player, place_num

    # check if it's valid and winner
    if check_valid(place_num):
        board[place_num] = current_player

        winner = check_result()

        # change current player
        if current_player == 'x':
            current_player = 'o'
        else:
            current_player = 'x'

    else: print('this place is already taken')

def check_valid(place_num):
    if board[place_num]:
        return False
    return True

def check_result():
    for row in WIN_SET:
        if board[row[0]]==board[row[1]]==board[row[2]]!='':
            return board[row[0]]
    if '' not in board:
            return 'tie'
    return None


def render_board():
    print('    %s | %s | %s' % tuple(board[:3]))
    print('   -----------')
    print('    %s | %s | %s' % tuple(board[3:6]))
    print('   -----------')
    print('    %s | %s | %s' % tuple(board[6:]))


if __name__ == '__main__':
    current_player = 'o'
    render_board()

    while winner is None:
        print(HR)
        input_move()
        update()
        render_board()
    
    print('winner is '+ winner)