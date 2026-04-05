'''A 2d world that supports agents with steering behaviour

Created for COS30002 AI for Games by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

'''

import random
from vector2d import Vector2D
from matrix33 import Matrix33
import pyglet
from graphics import COLOUR_NAMES, window
from agent import Agent
from projectile import Projectile  # Agent with seek, arrive, flee and pursuit


class World(object):
	def __init__(self, cx, cy):
		self.cx = cx
		self.cy = cy
		self.player = None
		self.hunter = None
		self.agents = []
		self.projectiles = []
		self.path = []
		self.objects = []
		self.paused = True
		self.show_info = True
		self.agent_fire_timers = {}
		self.weapon_cooldowns = {
			'rifle': 0.2,
			'rocket': 1.0,
			'hand_gun': 0.2,
			'hand_grenade': 1.0,
		}
		self.is_hit_flag = False
		self.hit_timer = 0.0
		self.hit_duration = 0.5
		self.max_projectile = 10
		self.projectile_count = self.max_projectile
		self.left_pressed = False
		self.right_pressed = False  
		self.up_pressed = False
		self.down_pressed = False

	def update(self, delta):
		if not self.paused:
			for agent in list(self.agents):
				if agent not in self.agent_fire_timers:
					self.agent_fire_timers[agent] = 0.0
				agent.update(delta)
				if agent.is_dead():
					agent.delete()
					self.agents.remove(agent)
			if self.player and self.max_projectile>0:
				self.agent_fire_timers[self.player] += delta
				mode = 'rifle'
				if(self.agent_fire_timers[self.player]>=self.weapon_cooldowns[mode]):
					self.projectiles.append(Projectile(world=self, shooter=self.player, mode=mode))
					self.agent_fire_timers[self.player] = 0.0
			if self.hunter and self.max_projectile>0:
				self.agent_fire_timers[self.hunter] += delta
				mode = 'rifle'
				if (self.hunter.state == 'attack' and 
					self.agent_fire_timers[self.hunter] >= self.weapon_cooldowns[mode]):
					self.projectiles.append(Projectile(world=self, shooter=self.hunter, mode=mode))
					self.agent_fire_timers[self.hunter] = 0.0
			# Check for projectile hit and trigger color change
			if self.player.is_hit():
				self.is_hit_flag = True
				self.hit_timer = self.hit_duration
			if self.hunter.is_hit():
				self.is_hit_flag = True
				self.hit_timer = self.hit_duration

			# Handle.player hit effect duration and color
			if self.player and self.player.vehicle:
				if self.is_hit_flag:
					self.hit_timer -= delta
					if self.hit_timer <= 0:
						self.is_hit_flag = False
					self.player.vehicle.color = COLOUR_NAMES['RED']
				else:
					self.player.vehicle.color = COLOUR_NAMES['LIGHT_PINK']
			if self.hunter and self.hunter.vehicle:
				if self.is_hit_flag:
					self.hit_timer -= delta
					if self.hit_timer <= 0:
						self.is_hit_flag = False
					self.hunter.vehicle.color = COLOUR_NAMES['PURPLE']
				else:
					self.hunter.vehicle.color = COLOUR_NAMES['LIGHT_BLUE']

			# Update all projectiles and remove if dead
			for projectile in list(self.projectiles):  # Copy for safe removal
				projectile.update(delta)
				if hasattr(projectile, 'is_dead') and projectile.is_dead:
					self.projectiles.remove(projectile)

	def wrap_around(self, pos):
		''' Treat world as a toroidal space. Updates parameter object pos '''
		max_x, max_y = self.cx, self.cy
		if pos.x > max_x:
			pos.x = pos.x - max_x
		elif pos.x < 0:
			pos.x = max_x - pos.x
		if pos.y > max_y:
			pos.y = pos.y - max_y
		elif pos.y < 0:
			pos.y = max_y - pos.y

	def transform_point(self, point, pos, forward, side):
		''' Transform the given single point, using the provided position,
		and direction (forward and side unit vectors), to object world space. '''
		# make a copy of the original point (so we don't trash it)
		world_pt = point.copy()
		# create a transformation matrix to perform the operations
		mat = Matrix33()
		# rotate
		mat.rotate_by_vectors_update(forward, side)
		# and translate
		mat.translate_update(pos.x, pos.y)
		# now transform the point (in place)
		mat.transform_vector2d(world_pt)
		# done
		return world_pt

	def set_key_handler(self, key_handler):
		self.keys = key_handler

	def input_mouse(self, x, y, button, modifiers):
		if button == 1:  # left
			self.player.x = x
			self.player.y = y
	
	def input_keyboard(self, symbol, modifiers):
		if symbol == pyglet.window.key.P:
			self.paused = not self.paused
		elif symbol == pyglet.window.key.R:
			for agent in self.agents:
				agent.randomize_path()
		elif symbol == pyglet.window.key.SPACE:
			if self.player and not self.player.is_dead() and self.agent_fire_timers[self.player]<=0:
				if not hasattr(self.player, 'weapon_mode'):
					self.player.weapon_mode = 'rifle'
				self.projectiles.append(Projectile(world=self, shooter=self.player,mode=self.player.mode))
				self.agent_fire_timers[self.player] = self.weapon_cooldowns[self.player.weapon_mode]
		elif symbol == pyglet.window.key.A:
			if self.hunter.is_dead():
				self.hunter == None
				self.hunter = Agent(self, mode='rifle')
				self.hunter.color = 'LIGHT_BLUE'
				self.hunter.vehicle.color = COLOUR_NAMES['LIGHT_BLUE']
				self.agents.append(self.hunter)
		elif symbol == pyglet.window.key.LEFT:
			self.left_pressed = True
		elif symbol == pyglet.window.key.RIGHT:
			self.right_pressed = True
		elif symbol == pyglet.window.key.UP:
			self.up_pressed = True
		elif symbol == pyglet.window.key.DOWN:
			self.down_pressed = True
		if self.player:
			if symbol == pyglet.window.key._1:
				self.player.weapon_mode = 'rifle'
			elif symbol == pyglet.window.key._2:
				self.player.weapon_mode = 'rocket'
			elif symbol == pyglet.window.key._3:
				self.player.weapon_mode = 'hand_gun'
			elif symbol == pyglet.window.key._4:
				self.player.weapon_mode = 'hand_grenade'

	def input_keyboard_release(self, symbol, modifiers):
		if symbol == pyglet.window.key.LEFT:
			self.left_pressed = False
		elif symbol == pyglet.window.key.RIGHT:
			self.right_pressed = False
		elif symbol == pyglet.window.key.UP:
			self.up_pressed = False
		elif symbol == pyglet.window.key.DOWN:
			self.down_pressed = False
