class Simple(object):
    def update(self, gameinfo):
        # check if we should attack 
        if gameinfo._my_planets() and gameinfo._not_my_planets():
            # select strongest friendly planet
            src = max(gameinfo._my_planets().values(), key=lambda p: p.ships)
            # select strongest enemy planet 
            dest = max(gameinfo._not_my_planets().values(), key=lambda p: p.ships)
            gameinfo.planet_order(src, dest, src.ships)
