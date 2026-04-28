# 2025 AI for Games

### Main Game System: 
The shooting game I created is a game where a player-controlled character battles against AI enemies. Players can move using arrow keys and select various weapons using the keyboard. AI enemies track players location and select tactical strategies.
(Red : player, Purple : hunter AI agent)

### Player System: 
- Weapon Selection: Players can select one of rifle, hand gun, rocket, or hand grenade through keyboard input.
- Movement: Players can move the player character using arrow keys. 

### AI Enemy System: 
AI moves toward the player character while using weapons and employs various strategies such as hiding and recharge, shot, move

### Weapons: 
- Rifle: Fast and accurate projectiles fired in a straight line 
- Hand gun: Fast and inaccurate projectiles that fire multiple projectiles at once 
- Rocket: Slow and accurate projectiles fired in a straight line 
- Hand_grenade: Slow and inaccurate projectiles fired in a straight line

### AI Techniques to Use: 
- Tactical Analysis: Used to enable AI enemies to determine strategic tactics using the player's position, projectile position, speed, and direction 
- Tactical Steering: Used to enable AI enemies to flee or evade from players 
- Emergent Group Behaviour: Used to enable projectiles to move in groups 
- Predictive Targeting: Used to enable all weapons to predict opponent positions based on speed, position, and direction to improve accuracy

### Development Difficulty
When making the player agent move with keyboard arrow keys, I experienced difficulty in adjusting the coordinate values in the agent's control function when a key is pressed, rather than directly adjusting the position values upon key press. Therefore, I implemented it so that when a key press occurs in the world, a true value is assigned when pressed and a false value when released to self.left_pressed, self.right_pressed, self.up_pressed, self.down_pressed, and when these values are true, the agent's control function makes changes to the coordinate values.

### Need to Fixed
The issue that projectile is actually being fired according to the log but is not visible on the screen.
The integrated functionality for each stage of the hunter agent has been almost implemented, but the problem is that they are not separated. It needs to be implemented to allow selection of a total of 3 stages by dividing them step by step.
When running the program, when the distance of each agent comes within the attack range of the hunter agent, the projectile is not actually visible but both hunter and player agents get hit detection and their colors change - this phenomenon needs to be fixed.

### Coverage of the Intended Learning Outcomes
#### ILO 1: Software Development for Game AI
- Through this project, high-level behavior modes (patrol/attack) and low-level execution states (move/hide, shoot/recharge) were separated to manage AI agents' behaviors hierarchically. The initial high-level behavior of the hunter agent is patrol. While patrolling the world, if the hunter agent gets close enough to the target agent, the high-level behavior of the hunter agent switches to attack. If the target agent is detected and the projectile count is not zero, the mode switches to shot. If the hunter agent’s projectile count is zero, it performs a recharge behavior through the recharge mode. In patrol mode, if the projectile count is zero, it switches to hide mode to regroup, and if not, it patrols in move mode.
#### ILO 2: Graphs and Path Planning
- A patrol waypoint system was developed for the hunter agent to follow a predesignated patrol route. It was not just moving to positions, but patrolling along a specified path.
#### ILO 4: Goals and Planning Actions
- The hunter agent has high-level behaviors (patrol/attack) to eliminate the player agent. The hunter agent patrols the world and switches its behavior depending on whether the player agent is detected or not. If the projectile count is set to 0, it shows a behavior of recharging projectiles in order to perform the shot action of attack mode. Therefore, I was able to implement a program in which the hunter agent dynamically changes its behavior depending on the player agent and aims to eliminate the player agent.
#### ILO 5: Combine AI Techniques
- A program was composed by combining the firing of projectiles from the hunter agent’s position to the target agent’s position and the target agent position prediction algorithm, so that the projectile could move toward the expected position of the target agent. Through this, the accuracy of the projectile could be improved, and an algorithm was also created to intentionally calculate inaccurate positions by adding an offset value.

### Result Video
https://drive.google.com/file/d/1vFox8A9Tl9nJekEnNkS79SsUmF7GaytN/view?usp=drive_link

