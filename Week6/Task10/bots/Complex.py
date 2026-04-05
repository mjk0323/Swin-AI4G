import random

class Complex(object):
    def update(self, gameinfo):
        if not gameinfo._my_planets() or not gameinfo._not_my_planets():
            return  # Do nothing if no planets

        src = list(gameinfo._my_planets().values())[0]
        dest = list(gameinfo._not_my_planets().values())[0]

        is_under_attack = any(
            fleet.dest.ID == dest.ID and fleet.owner == 2
            for fleet in gameinfo._enemy_fleets().values()
        )

        roll = random.random()

        if is_under_attack:
            if roll < 0.2:
                # 20% chance: persuade (enemy becomes friendly)
                src.ships += dest.ships
            elif roll < 0.5:
                # 30% chance: defense (do nothing)
                pass
            else:
                # 50% chance: attack
                gameinfo.planet_order(src, dest, src.ships)
        else:
            # Not under attack: just attack normally
            gameinfo.planet_order(src, dest, src.ships)