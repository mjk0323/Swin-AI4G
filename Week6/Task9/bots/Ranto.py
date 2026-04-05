from random import choice

class Ranto(object):
	def update(self, gameinfo):
		# check if we should attack 
		if gameinfo._my_planets() and gameinfo._not_my_planets(): 
			# Find a target planet with the minimum number of ships. 
			dest = min(gameinfo._not_my_planets().values(), key=lambda p: p.ships)
			src = max(gameinfo._my_planets().values(), key=lambda p: p.ships) 
			gameinfo.planet_order(src, dest, src.ships) 
		