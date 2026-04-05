game = None

from enum import Enum
import pyglet
from world import World
from graphics import window, COLOUR_NAMES
from agent import Agent  # Agent with seek, arrive, flee and pursuit
from projectile import Projectile
from vector2d import Vector2D

class Game():
	def __init__(self):
		self.world = World(window.size[0], window.size[1])
		# hunter (attacking) agent
		self.world.hunter = Agent(self.world, mode='rifle')
		self.world.hunter.color = 'LIGHT_BLUE'
		self.world.hunter.vehicle.color = COLOUR_NAMES['LIGHT_BLUE']
		self.world.agents.append(self.world.hunter)
		self.world.agent_fire_timers[self.world.hunter] = 0.0
		# moving player agent
		self.world.player = Agent(self.world, mode='control')
		self.world.player.color = 'LIGHT_PINK'
		self.world.player.vehicle.color = COLOUR_NAMES['LIGHT_PINK']
		self.world.agents.append(self.world.player)
		
		# projectiles
		self.world.projectiles.append(Projectile(self.world, mode=self.world.hunter.mode))
		self.world.projectiles.append(Projectile(self.world, mode=self.world.player.mode))
		# unpause the world ready for movement
		self.world.paused = False

	def input_mouse(self, x, y, button, modifiers):
		self.world.input_mouse(x, y, button, modifiers)

	def input_keyboard(self, symbol, modifiers):
		self.world.input_keyboard(symbol, modifiers)

	def input_keyboard_release(self, symbol, modifiers):
		self.world.input_keyboard_release(symbol, modifiers)

	def update(self, delta):
		self.world.update(delta)