import random

states = ['wait','attack','depend','heal']
current_state = 'wait'

HP = 100
MP = 100

enemy_alive = True
enemy_HP = 100
enemy_damage = 0

winner = ''

def npc_action(current_state):
    global HP, MP, enemy_HP, enemy_alive, enemy_damage
    
    match current_state:
        case 'wait':
            print('wait')
        case 'attack':
            enemy_HP -= random.randint(0,30)
            print(enemy_HP)
        case 'depend':
            HP += 5
            MP += 5
            if(enemy_damage>10):
                enemy_damage -= 10
            else:
                enemy_damage = 0
        case 'heal':
            HP += random.randint(10,15)
            MP += random.randint(10,15)

def npc_state():
    global current_state
    while HP>0 and enemy_alive:
        enemy_damage = random.randint(0,30)

        if HP>90:
            current_state = states[0]
        elif HP<90 and MP>30:
            current_state = states[1]
        elif enemy_damage>20:
            current_state = states[2]
        elif HP<30 and MP>=15:
            current_state = states[3]

def update():
    global enemy_alive, winner
    if enemy_HP <= 0:
        enemy_alive = False
        winner = 'npc'
        
    HP -= enemy_damage

    if HP <= 0:
        winner = 'enemy'

    print(current_state)

if __name__ == '__main__':
    while winner == '':
        npc_state()
        npc_action(current_state)
        update()
    print(winner+'is the winner!')