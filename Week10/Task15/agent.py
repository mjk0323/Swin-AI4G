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

class Agent(object):
	# NOTE: Class Object (not *instance*) variables!
	DECELERATION_SPEEDS = {
        'slow': 9,
        'normal': 5.0,
        'fast': 0.2,
    }

	def __init__(self, world=None, scale=30.0, mass=1.0, mode='seek'):
		# keep a reference to the world object
		self.world = world
		self.mode = mode
		# where am i and where am i going? random start pos
		dir = radians(random()*360)
		self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
		self.vel = Vector2D()
		self.heading = Vector2D(sin(dir), cos(dir))
		self.side = self.heading.perp()
		self.scale = Vector2D(scale, scale)  # easy scaling of agent size
		self.force = Vector2D()  # current steering force
		self.accel = Vector2D() # current acceleration due to force
		self.mass = mass

		# data for drawing this agent
		self.color = 'ORANGE'
		self.vehicle_shape = [
			Point2D(-10,  6),
			Point2D( 10,  0),
			Point2D(-10, -6)
		]
		self.vehicle = pyglet.shapes.Triangle(
			self.pos.x+self.vehicle_shape[1].x, self.pos.y+self.vehicle_shape[1].y,
			self.pos.x+self.vehicle_shape[0].x, self.pos.y+self.vehicle_shape[0].y,
			self.pos.x+self.vehicle_shape[2].x, self.pos.y+self.vehicle_shape[2].y,
			color= COLOUR_NAMES[self.color],
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
		self.max_speed = 10.0 * scale
		self.max_force = 500.0

		# debug draw info?
		self.show_info = False

	def randomize_path(self):
		cx = self.world.cx # width
		cy = self.world.cy # height
		margin = min(cx, cy) * (1/6) 
		num_pts = randrange(5, 11)
		self.path.create_random_path(num_pts, margin, margin, cx-margin, cy-margin) #check 

	def calculate(self, delta):
		# calculate the current steering force
		mode = self.mode
		target_pos = self.world.target.pos
		if mode == 'seek':
			force = self.seek(target_pos)
		elif mode == 'follow_path':
			force = self.follow_path()
		else:
			force = Vector2D()
		self.force = force
		return force

	def update(self, delta):
		''' update vehicle position and orientation '''
		# calculate and set self.force to be applied
		## force = self.calculate()
		force = self.calculate(delta)  # <-- delta needed for wander
		## limit force? <-- for wander
		force = self.calculate(delta)
		force.truncate(self.max_force)
		# determin the new acceleration
		self.accel = force / self.mass  # not needed if mass = 1.0
		# new velocity
		self.vel += self.accel * delta
		# check for limits of new velocity
		self.vel.truncate(self.max_speed)
		# update position
		self.pos += self.vel * delta
		# update heading is non-zero velocity (moving)
		if self.vel.lengthSq() > 0.00000001:
			self.heading = self.vel.get_normalised()
			self.side = self.heading.perp()
		# treat world as continuous space - wrap new position if needed
		self.world.wrap_around(self.pos)
		# update the vehicle render position
		self.vehicle.x = self.pos.x+self.vehicle_shape[0].x
		self.vehicle.y = self.pos.y+self.vehicle_shape[0].y
		self.vehicle.rotation = -self.heading.angle_degrees()

		s = 0.5 # <-- scaling factor
		# force
		self.info_force_vector.position = self.pos
		self.info_force_vector.end_pos = self.pos + self.force * s
		# velocity
		self.info_vel_vector.position = self.pos
		self.info_vel_vector.end_pos = self.pos + self.vel * s
		# net (desired) change
		self.info_net_vectors[0].position = self.pos+self.vel * s
		self.info_net_vectors[0].end_pos = self.pos + (self.force+self.vel) * s
		self.info_net_vectors[1].position = self.pos
		self.info_net_vectors[1].end_pos = self.pos + (self.force+self.vel) * s

	def speed(self):
		return self.vel.length()
	
	def is_hit(self, hit_radius=10.0):
		for projectile in list(self.world.projectiles):
			to_proj = projectile.pos - self.pos
			if to_proj.length() < hit_radius:
				self.world.projectiles.remove(projectile)
				return True
		return False
	#--------------------------------------------------------------------------

	def seek(self, target_pos):
		''' move towards target position '''
		desired_vel = (target_pos - self.pos).normalise() * self.max_speed
		return (desired_vel - self.vel)
	
	def arrive(self, target_pos, speed):
		''' this behaviour is similar to seek() but it attempts to arrive at
			the target position with a zero velocity'''
		decel_rate = self.DECELERATION_SPEEDS[speed]
		to_target = target_pos - self.pos
		dist = to_target.length()
		if dist > 0:
			# calculate the speed required to reach the target given the
			# desired deceleration rate
			speed = dist / decel_rate
			# make sure the velocity does not exceed the max
			speed = min(speed, self.max_speed)
			# from here proceed just like Seek except we don't need to
			# normalize the to_target vector because we have already gone to the
			# trouble of calculating its length for dist.
			desired_vel = to_target * (speed / dist)
			return (desired_vel - self.vel)
		return Vector2D(0, 0)

	def follow_path(self):
		if self.path.is_finished():
			return self.arrive(self.path.current_pt(), 'slow')
		else:
			to_waypoint = self.path.current_pt() - self.pos
			dist_squared = to_waypoint.lengthSq() 

			if dist_squared < self.waypoint_threshold * self.waypoint_threshold:
				self.path.inc_current_pt()
			return self.seek(self.path.current_pt())
