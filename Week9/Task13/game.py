game = None

from enum import Enum
import pyglet
from world import World
from graphics import window
from agent import Agent  # Agent with seek, arrive, flee and pursuit
from graphics import COLOUR_NAMES

class Game():
	def __init__(self):
		self.world = World(window.size[0], window.size[1])
		# add two agent
		self.world.hunter = Agent(self.world, mode='pursuit')
		self.world.hunter.color = 'LIGHT_BLUE'
		self.world.hunter.orig_color = 'LIGHT_BLUE'
		self.world.hunter.vehicle.color = COLOUR_NAMES['LIGHT_BLUE']
		self.world.hunter.mode = 'pursuit'
		self.world.agents.append(self.world.hunter)
		
		self.world.prey = Agent(self.world, mode='flee')
		self.world.prey.color = 'PINK'
		self.world.prey.orig_color = 'PINK'
		self.world.prey.vehicle.color = COLOUR_NAMES['PINK']
		self.world.prey.mode = 'flee'
		self.world.agents.append(self.world.prey)

		# unpause the world ready for movement
		self.world.paused = False

	def input_mouse(self, x, y, button, modifiers):
		self.world.input_mouse(x, y, button, modifiers)

	def input_keyboard(self, symbol, modifiers):
		self.world.input_keyboard(symbol, modifiers)

	def update(self, delta):
		self.world.update(delta)