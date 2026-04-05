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

AGENT_MODES = {
	pyglet.window.key._1: 'seek',
	pyglet.window.key._2: 'flee',
	pyglet.window.key._3: 'pursuit',
	pyglet.window.key._4: 'follow_path',
	pyglet.window.key._5: 'wander',
}

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
		self.vehicle_shape = [
			Point2D(-10,  6),
			Point2D( 10,  0),
			Point2D(-10, -6)
		]
		self.vehicle = pyglet.shapes.Triangle(
			self.pos.x+self.vehicle_shape[1].x, self.pos.y+self.vehicle_shape[1].y,
			self.pos.x+self.vehicle_shape[0].x, self.pos.y+self.vehicle_shape[0].y,
			self.pos.x+self.vehicle_shape[2].x, self.pos.y+self.vehicle_shape[2].y,
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
		self.orig_color = self.vehicle.color

		self.hide_marker = [
			pyglet.shapes.Star(
			self.world.cx / 2, self.world.cy / 2, 
			30, 1, 4, 
			color=COLOUR_NAMES['RED'], 
			batch=window.get_batch("main")),
			pyglet.shapes.Star(
			self.world.cx / 2, self.world.cy / 2, 
			30, 1, 4, 
			color=COLOUR_NAMES['RED'], 
			batch=window.get_batch("main")),
			pyglet.shapes.Star(
			self.world.cx / 2, self.world.cy / 2, 
			30, 1, 4, 
			color=COLOUR_NAMES['RED'], 
			batch=window.get_batch("main"))
		]
		for marker in self.hide_marker:
			marker.visible = False	

		self.b_hide_marker = pyglet.shapes.Star(
			self.world.cx / 2, self.world.cy / 2, 
			30, 1, 4, 
			color=COLOUR_NAMES['YELLOW'], 
			batch=window.get_batch("main"))
		self.b_hide_marker.visible = False

	def is_hit(self, hit_radius=30.0):
		if self==self.world.prey:
			to_hunter = self.world.hunter.pos - self.pos
			if to_hunter.length() < hit_radius:
				self.world.agents.remove(self)
				self.delete()
				return True
		return False
	
	def delete(self):
		if self.vehicle:
			self.vehicle.delete()
			self.vehicle = None
		self.info_force_vector.delete()
		self.info_vel_vector.delete()
		for line in self.info_net_vectors:
			line.delete()
		self.info_wander_circle.delete()
		self.info_wander_target.delete()

	def get_hide_spot(self):
		best_spot = None
		best_dist = float('inf')
		hunter_pos = self.world.hunter.pos
		margin = 15.0 
		hiding_spots = []

		for obj in self.world.objects:
			obj_pos = Vector2D(obj.x, obj.y)
			to_obj = (obj_pos - hunter_pos).get_normalised()
			hide_dist = obj.radius + margin
			hiding_spot = obj_pos + to_obj * hide_dist

			if (hiding_spot - obj_pos).length() < obj.radius:
				continue
			if not (0 <= hiding_spot.x <= self.world.cx and 0 <= hiding_spot.y <= self.world.cy):
				continue

			hiding_spots.append(hiding_spot)

			dist_sq = (hiding_spot - self.pos).lengthSq()
			if dist_sq < best_dist:
				best_dist = dist_sq
				best_spot = hiding_spot
		
		for i,h_spot in enumerate(hiding_spots):
			if h_spot:
				self.hide_marker[i].x = h_spot.x
				self.hide_marker[i].y = h_spot.y
				self.hide_marker[i].visible = True
			else:
				self.hide_marker[i].visible = False

		if best_spot:
			self.b_hide_marker.x = best_spot.x
			self.b_hide_marker.y = best_spot.y
			self.b_hide_marker.visible = True
		else:
			self.b_hide_marker.visible = False

		return best_spot

	def flee_to_hide_spot(self, delta):
		best_spot = self.get_hide_spot()
		self.hide_target = best_spot  

		if best_spot:
			seek_force = self.seek(best_spot)
		else:
			seek_force = self.flee(self.world.hunter.pos)

		avoid_force = Vector2D()
		for obj in self.world.objects:
			obj_pos = Vector2D(obj.x, obj.y)
			to_obj = obj_pos - self.pos
			dist = to_obj.length()
			min_dist = self.bRadius + obj.radius*2 + 10.0 

			if dist < min_dist:
				away = (self.pos - obj_pos).normalise() * self.max_force
				weight = (min_dist - dist) / min_dist
				avoid_force += away * weight

		total_force = seek_force + avoid_force
		return total_force

	def randomize_path(self):
		cx = self.world.cx # width
		cy = self.world.cy # height
		margin = min(cx, cy) * (1/6) 
		num_pts = randrange(5, 11)
		self.path.create_random_path(num_pts, margin, margin, cx-margin, cy-margin) #check 

	def calculate(self, delta):
		# calculate the current steering force
		mode = self.mode
		if mode == 'flee':
			if self.world.hunter is not None:
				target_pos = self.world.hunter.pos 
			else:
				target_pos = Vector2D()
		else:
			target_pos = Vector2D(self.world.target.x, self.world.target.y)
			
		if mode == 'seek':
			force = self.seek(target_pos)
		elif mode == 'flee':
			force = self.flee_to_hide_spot(delta)
		elif mode == 'pursuit':
			force = self.pursuit(target_pos, 'normal')
		elif mode == 'wander':
			force = self.wander(delta)
		elif mode == 'follow_path':
			force = self.follow_path()
		else:
			force = Vector2D()

		avoid_force = Vector2D()

		for obj in self.world.objects:
			obj_pos = Vector2D(obj.x, obj.y)
			to_obj = obj_pos - self.pos
			dist = to_obj.length()
			min_dist = self.bRadius + obj.radius + 20.0 

			if dist < min_dist:
				away = (self.pos - obj_pos).normalise() * self.max_force
				weight = (min_dist - dist) / min_dist
				avoid_force += away * weight
	
		self.force = force + avoid_force
		return self.force

	def update(self, delta):
		''' update vehicle position and orientation '''
		if self.is_hit():
			return 
		# calculate and set self.force to be applied
		## force = self.calculate()
		force = self.calculate(delta)  # <-- delta needed for wander
		## limit force? <-- for wander
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

	def seek(self, target_pos):
		''' move towards target position '''
		desired_vel = (target_pos - self.pos).normalise() * self.max_speed
		return (desired_vel - self.vel)

	def flee(self, hunter_pos):
		''' move away from hunter position '''
		## add panic distance (second)
		panic_distance = 500
		## add flee calculations (first)
		to_hunter = self.pos - hunter_pos
		dist = to_hunter.length()

		if panic_distance>dist:
			desired_vel = to_hunter.normalise() * self.max_speed
			return (desired_vel - self.vel)
		
		return Vector2D()

	def pursuit(self, target_pos, speed):
		if hasattr(self.world.prey, 'vel') and hasattr(self.world.prey, 'heading'):
			# Predictive pursuit for moving targets
			to_target = target_pos - self.pos
			relative_heading = self.heading.dot(self.world.prey.heading)
			
			# If target is ahead and facing towards us, just seek directly
			if (to_target.dot(self.heading) > 0) and (relative_heading < -0.95):
				return self.seek(target_pos)
			
			# Calculate interception point
			target_speed = self.world.prey.vel.length()
			time_to_intercept = to_target.length() / (self.max_speed + target_speed)
			predicted_pos = self.world.prey.pos + self.world.prey.vel * time_to_intercept
			
			return self.seek(predicted_pos)
		else:
			# Simple pursuit - just seek towards the target position
			return self.seek(target_pos)


	def follow_path(self):
		if self.path.is_finished():
			return self.arrive(self.path.current_pt(), 'slow')
		else:
			to_waypoint = self.path.current_pt() - self.pos
			dist_squared = to_waypoint.lengthSq() 

			if dist_squared < self.waypoint_threshold * self.waypoint_threshold:
				self.path.inc_current_pt()
			return self.seek(self.path.current_pt())

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
