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

AGENTS_STEERINGS = {
	pyglet.window.key._1: 'cohesion',
	pyglet.window.key._2: 'separation',
	pyglet.window.key._3: 'alignment',
}

class Agent(object):
	def __init__(self, world=None, scale=30.0, mass=1.0, mode='seek', steering = 'cohesion'):
		# keep a reference to the world object
		self.world = world
		self.mode = mode
		self.steering = steering
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

		self.wander_weight = 0.6
		self.separation_weight = 1.5
		self.alignment_weight = 1.0
		self.cohesion_weight = 1.0

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
		self.max_speed = 20.0 * scale
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
		force = Vector2D()

		self.TagNeighbours(self.world.agents, 100)
		force += self.wander(delta) * self.wander_weight

		force += self.Cohesion(self.world.agents) * self.cohesion_weight
		force += self.Separation(self.world.agents) * self.separation_weight
		force += self.Alignment(self.world.agents) * self.alignment_weight
		force.truncate(self.max_force)

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

	#--------------------------------------------------------------------------
	def TagNeighbours(self, agents, radius):
		for agent in agents:
			# untag all first
			agent.tagged = False
			# get the vector between us
			to = self.pos - agent.pos
			# take into account the bounding radius
			gap = radius + agent.bRadius
			if to.lengthSq() < gap**2:
				agent.tagged = True

	def Separation(self, agents):
		SteeringForce = Vector2D()
		for agent in agents:
			# don’t include self, only include neighbours (already tagged)
			if agent != self and agent.tagged:
				ToBot = self.pos - agent.pos
				# scale based on inverse distance to neighbour
				SteeringForce += Vector2D.get_normalised(ToBot) / ToBot.length()
		return SteeringForce
	
	def Alignment(self, agents):
		AvgHeading = Vector2D()
		AvgCount = 0
		for agent in agents:
			if agent != self and agent.tagged:
				AvgHeading += agent.heading
				AvgCount += 1
			if AvgCount > 0:
				AvgHeading /= float(AvgCount)
				AvgHeading -= self.heading
		return AvgHeading
	
	def Cohesion(self, agents):
		CentreMass = Vector2D()
		SteeringForce = Vector2D()
		AvgCount = 0
		for agent in agents:
			if agent != self and agent.tagged:
				CentreMass += agent.pos
				AvgCount += 1
		if AvgCount > 0:
			CentreMass /= float(AvgCount)
			SteeringForce = self.seek(CentreMass)
		return SteeringForce

	#--------------------------------------------------------------------------
	def seek(self, target_pos):
		''' move towards target position '''
		desired_vel = (target_pos - self.pos).normalise() * self.max_speed
		return (desired_vel - self.vel)

	def wander(self, delta):
		''' random wandering using a projected jitter circle '''
		wander_target = self.wander_target
		# this behaviour is dependent on the update rate, so this line must
		# be included when using time independent framerate.
		jitter = self.wander_jitter * delta # this time slice
		# first, add a small random vector to the target's position
		wander_target += Vector2D(uniform(-1,1) * jitter, uniform(-1,1) * jitter)
		# re-project this new vector back on to a unit circle
		wander_target.normalise()
		# increase the length of the vector to the same as the radius
		# of the wander circle
		wander_target *= self.wander_radius
		# move the target into a position wander_dist in front of the agent
		wander_dist_vector = Vector2D(self.wander_dist, 0) #also used for rendering
		target = wander_target + Vector2D(self.wander_dist, 0)
		# set the position of the Agent’s debug circle to match the vectors we’ve created
		circle_pos = self.world.transform_point(wander_dist_vector, self.pos, self.heading, self.side,)
		self.info_wander_circle.x = circle_pos.x
		self.info_wander_circle.y = circle_pos.y
		self.info_wander_circle.radius = self.wander_radius
		# project the target into world space
		world_target = self.world.transform_point(target, self.pos, self.heading, self.side)
		#set the target debug circle position
		self.info_wander_target.x = world_target.x
		self.info_wander_target.y = world_target.y
		# and steer towards it
		return self.seek(world_target)
