'''A 2d world that supports agents with steering behaviour

Created for COS30002 AI for Games by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

'''

from vector2d import Vector2D
from matrix33 import Matrix33
import pyglet
from graphics import COLOUR_NAMES, window
from agent import AGENTS_STEERINGS  # Agent with seek, arrive, flee and pursuit


class World(object):
	def __init__(self, cx, cy):
		self.cx = cx
		self.cy = cy
		self.target = Vector2D(cx / 2, cy / 2)
		self.hunter = None
		self.agents = []
		self.path = []
		self.paused = True
		self.show_info = True
		self.target = pyglet.shapes.Star(
			cx / 2, cy / 2, 
			30, 1, 4, 
			color=COLOUR_NAMES['RED'], 
			batch=window.get_batch("main")
		)

	def update(self, delta):
		if not self.paused:
			for agent in self.agents:
				agent.update(delta)

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

	def input_mouse(self, x, y, button, modifiers):
		if button == 1:  # left
			self.target.x = x
			self.target.y = y
	
	def input_keyboard(self, symbol, modifiers):
		if symbol == pyglet.window.key.P:
			self.paused = not self.paused
		elif symbol == pyglet.window.key.R:
			for agent in self.agents:
				agent.randomize_path()
		elif symbol == pyglet.window.key.W:
			for agent in self.agents:
				agent.wander_weight += 1.0
		elif symbol == pyglet.window.key.Q:
			for agent in self.agents:
				agent.wander_weight -= 1.0
		elif symbol == pyglet.window.key.C:
			for agent in self.agents:
				agent.cohesion_weight += 1.0
		elif symbol == pyglet.window.key.D:
			for agent in self.agents:
				agent.cohesion_weight -= 1.0
		elif symbol == pyglet.window.key.S:
			for agent in self.agents:
				agent.separation_weight += 1.0
		elif symbol == pyglet.window.key.X:
			for agent in self.agents:
				agent.separation_weight -= 1.0
		elif symbol == pyglet.window.key.A:
			for agent in self.agents:
				agent.alignment_weight += 1.0
				print(agent.alignment_weight)
		elif symbol == pyglet.window.key.Z:
			for agent in self.agents:
				agent.alignment_weight -= 1.0
				print(agent.alignment_weight)
		
		elif symbol in AGENTS_STEERINGS:
			for agent in self.agents:
				agent.steering = AGENTS_STEERINGS[symbol]