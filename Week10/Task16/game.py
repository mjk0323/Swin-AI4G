game = None

from enum import Enum
import pyglet
from world import World
from graphics import window, COLOUR_NAMES
from agent import Agent  # Agent with seek, arrive, flee and pursuit
from projectile import Projectile

class Game():
	def __init__(self):
		self.world = World(window.size[0], window.size[1])
		# hunter (attacking) agent
		self.world.hunter = Agent(self.world, mode='rifle')
		self.world.hunter.color = 'LIGHT_BLUE'
		self.world.hunter.vehicle.color = COLOUR_NAMES['LIGHT_BLUE']
		self.world.agents.append(self.world.hunter)
		self.world.agent_fire_timers[self.world.hunter] = 0.0
		# moving target agent
		self.world.target = Agent(self.world, mode='follow_path')
		self.world.target.color = 'LIGHT_PINK'
		self.world.target.vehicle.color = COLOUR_NAMES['LIGHT_PINK']
		self.world.agents.append(self.world.target)
		
		# projectiles
		self.world.projectiles.append(Projectile(self.world, mode=self.world.hunter.mode))
		# unpause the world ready for movement
		self.world.paused = False

	def input_mouse(self, x, y, button, modifiers):
		self.world.input_mouse(x, y, button, modifiers)

	def input_keyboard(self, symbol, modifiers):
		self.world.input_keyboard(symbol, modifiers)

	def update(self, delta):
		self.world.update(delta)