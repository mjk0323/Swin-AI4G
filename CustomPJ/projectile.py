'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for COS30002 AI for Games by 
	Clinton Woodward <cwoodward@swin.edu.au>
	James Bonner <jbonner@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

'''
import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from graphics import COLOUR_NAMES, window, ArrowLine
from math import sin, cos, radians
from random import random, randrange, uniform
from path import Path
from random import uniform

class Projectile(object):

	# NOTE: Class Object (not *instance*) variables!
	DECELERATION_SPEEDS = {
        'slow': 2.0,
        'fast': 1.0,
    }

	def __init__(self, world=None, shooter=None, scale=30.0, mass=1.0, mode='rifle'):
		# keep a reference to the world object
		self.world = world
		self.mode = mode
		self.shooter = shooter
		self.pos = Vector2D(world.cx / 2, world.cy / 2) if world else Vector2D(0, 0)
		# where am i and where am i going? random start pos
		dir = radians(random()*360)
		self.vel = Vector2D()
		self.heading = Vector2D(sin(dir), cos(dir))
		self.side = self.heading.perp()
		self.scale = Vector2D(scale, scale)  # easy scaling of agent size
		self.force = Vector2D()  # current steering force
		self.accel = Vector2D() # current acceleration due to force
		self.mass = mass
		self.initialised = False 
		if shooter:
			self.pos = Vector2D(shooter.pos.x, shooter.pos.y)
			if shooter == world.hunter:
				self.initial_target_pos = Vector2D(world.player.pos.x, world.player.pos.y)
				self.initial_target_vel = Vector2D(world.player.vel.x, world.player.vel.y)
			elif shooter == world.player:
				self.initial_target_pos = Vector2D(world.hunter.pos.x, world.hunter.pos.y)
				self.initial_target_vel = Vector2D(world.hunter.vel.x, world.hunter.vel.y)
		
		# data for drawing this agent
		self.color = 'WHITE'
		self.vehicle_shape = [
			Point2D(-10,  6),
			Point2D( 10,  0),
			Point2D(-10, -6)
		]
		self.vehicle = pyglet.shapes.Circle(
				3,3,3,
				color=COLOUR_NAMES['WHITE'], 
				batch=window.get_batch("main")
			)

		# wander info render objects
		self.info_wander_circle = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['WHITE'], batch=window.get_batch("info"))
		self.info_wander_target = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['GREEN'], batch=window.get_batch("info"))
		# add some handy debug drawing info lines - force and velocity
		self.info_force_vector = ArrowLine(Vector2D(0,0), Vector2D(0,0), colour=COLOUR_NAMES['BLUE'], batch=window.get_batch("info"))
		self.info_vel_vector = ArrowLine(Vector2D(0,0), Vector2D(0,0), colour=COLOUR_NAMES['AQUA'], batch=window.get_batch("info"))
		self.info_net_vectors = [
			ArrowLine(
				Vector2D(0,0), 
				Vector2D(0,0), 
				colour=COLOUR_NAMES['GREY'], 
				batch=window.get_batch("info")
			),
			ArrowLine(
				Vector2D(0,0), 
				Vector2D(0,0), 
				colour=COLOUR_NAMES['GREY'], 
				batch=window.get_batch("info")
			),
		]

		### path to follow
		self.path = Path()
		self.randomize_path()
		self.waypoint_threshold = 10.0 

		### wander details
		self.wander_target = Vector2D(1, 0)
		self.wander_dist = 1.0 * scale
		self.wander_radius = 1.0 * scale
		self.wander_jitter = 10.0 * scale
		self.bRadius = scale

		# limits
		self.max_speed = 20.0 * scale
		self.max_force = 500.0

		# debug draw info?
		self.show_info = False

		# self.pos = Vector2D(world.hunter.pos.x, world.hunter.pos.y)
		# self.target_pos = Vector2D(world.player.pos.x, world.player.pos.y)

	def randomize_path(self):
		cx = self.world.cx # width
		cy = self.world.cy # height
		margin = min(cx, cy) * (1/6) 
		num_pts = randrange(5, 11)
		self.path.create_random_path(num_pts, margin, margin, cx-margin, cy-margin) #check 

	def calculate(self):
		
		# calculate the current steering force
		mode = self.mode
		if mode == 'rifle':
			force = self.rifle('fast')
		elif mode == 'rocket':
			force = self.rocket('slow')
		elif mode == 'hand_gun':
			force = self.hand_gun('fast')
		elif mode == 'hand_grenade':
			force = self.hand_grenade('slow')
		else:
			force = Vector2D()
		self.force = force
		self.vel += self.force 
		if self.vel.length() > self.max_speed:
			self.vel = self.vel.get_normalised() * self.max_speed
		return force

	def update(self, delta):
		if not self.initialised and self.shooter:
			if self.shooter == self.world.hunter:
				self.initial_target_pos = Vector2D(self.world.player.pos.x, self.world.player.pos.y)
				self.initial_target_vel = Vector2D(self.world.player.vel.x, self.world.player.vel.y)
			elif self.shooter == self.world.player:
				self.initial_target_pos = Vector2D(self.world.hunter.pos.x, self.world.hunter.pos.y)
				self.initial_target_vel = Vector2D(self.world.hunter.vel.x, self.world.hunter.vel.y)
		
		if not self.initialised:
			self.calculate()
			self.vel = self.force
			self.initialised = True
		self.pos += self.vel * delta
		if self.world.hunter.state == 'attack':
			# keep diraction
			if self.vel.lengthSq() > 0.00001:
				self.heading = self.vel.get_normalised()
				self.side = self.heading.perp()

		# delete projectile when it goes outside of the window
		if (self.pos.x < 0 or self.pos.x > self.world.cx or
			self.pos.y < 0 or self.pos.y > self.world.cy):
			self.world.projectiles.remove(self)  
			return

		# apply location
		self.vehicle.x = self.pos.x + self.vehicle_shape[0].x
		self.vehicle.y = self.pos.y + self.vehicle_shape[0].y
		self.vehicle.rotation = -self.heading.angle_degrees()

	def speed(self):
		return self.vel.length()
	
	#--------------------------------------------------------------------------

	def rifle(self, speed):
		if isinstance(speed, str):
			speed = self.DECELERATION_SPEEDS.get(speed, 1.0)
		
		if self.shooter == self.world.hunter:
			target_pos = self.world.player.pos
			target_vel = self.world.player.vel
		else:
			target_pos = self.world.hunter.pos
			target_vel = self.world.hunter.vel

		projectile_speed = self.max_speed / speed
		to_target = target_pos - self.pos
		distance = to_target.length()

		time_to_intercept = distance / (projectile_speed + 0.0001)
		predicted_pos = target_pos + target_vel * time_to_intercept

		desired_vel = (predicted_pos - self.pos).get_normalised() * projectile_speed
		return desired_vel - self.vel
	
	def rocket(self, speed):
		if isinstance(speed, str):
			speed = self.DECELERATION_SPEEDS.get(speed, 1.0)
		
		if self.shooter == self.world.hunter:
			target_pos = self.world.player.pos
			target_vel = self.world.player.vel
		else:
			target_pos = self.world.hunter.pos
			target_vel = self.world.hunter.vel

		projectile_speed = self.max_speed / speed
		to_target = target_pos - self.pos
		distance = to_target.length()

		max_time = 1.0
		time_to_intercept = min(distance / (projectile_speed + 0.0001), max_time)
		predicted_pos = target_pos + target_vel * time_to_intercept

		desired_vel = (predicted_pos - self.pos).get_normalised() * projectile_speed
		return desired_vel - self.vel
	
	def hand_gun(self, speed):
		if isinstance(speed, str):
			speed = self.DECELERATION_SPEEDS.get(speed, 1.0)

		if self.shooter == self.world.hunter:
			target_pos = self.world.player.pos
			target_vel = self.world.player.vel
		else:
			target_pos = self.world.hunter.pos
			target_vel = self.world.hunter.vel

		inaccuracy_range = 80.0 
		offset_x = uniform(-inaccuracy_range, inaccuracy_range)
		offset_y = uniform(-inaccuracy_range, inaccuracy_range)
		inaccurate_target_pos = Vector2D(target_pos.x + offset_x, target_pos.y + offset_y)

		to_target = inaccurate_target_pos - self.pos
		distance = to_target.length()

		projectile_speed = self.max_speed / speed

		time_to_intercept = distance / (projectile_speed + 0.0001)
		time_to_intercept *= uniform(0.5, 1.5)

		predicted_pos = inaccurate_target_pos + target_vel * time_to_intercept

		desired_direction = (predicted_pos - self.pos).get_normalised()

		desired_direction.x += uniform(-0.2, 0.2)
		desired_direction.y += uniform(-0.2, 0.2)
		desired_direction.normalise()

		desired_vel = desired_direction * projectile_speed
		return desired_vel - self.vel
	
	def hand_grenade(self, speed):
		if isinstance(speed, str):
			speed = self.DECELERATION_SPEEDS.get(speed, 1.0)

		if self.shooter == self.world.hunter:
			target_pos = self.world.player.pos
			target_vel = self.world.player.vel
		else:
			target_pos = self.world.hunter.pos
			target_vel = self.world.hunter.vel

		inaccuracy_range = 80.0 
		offset_x = uniform(-inaccuracy_range, inaccuracy_range)
		offset_y = uniform(-inaccuracy_range, inaccuracy_range)
		inaccurate_target_pos = Vector2D(target_pos.x + offset_x, target_pos.y + offset_y)

		to_target = inaccurate_target_pos - self.pos
		distance = to_target.length()

		projectile_speed = self.max_speed / speed

		time_to_intercept = distance / (projectile_speed + 0.0001)
		time_to_intercept *= uniform(0.5, 1.5)

		predicted_pos = inaccurate_target_pos + target_vel * time_to_intercept

		desired_direction = (predicted_pos - self.pos).get_normalised()

		desired_direction.x += uniform(-0.2, 0.2)
		desired_direction.y += uniform(-0.2, 0.2)
		desired_direction.normalise()

		desired_vel = desired_direction * projectile_speed
		return desired_vel - self.vel
