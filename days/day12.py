import math
import re
from typing import List, Dict, Optional

from days import AOCDay, day
from itertools import combinations

DEBUG = True


class Moon:
    x = 0
    y = 0
    z = 0

    x_velocity, y_velocity, z_velocity = 0, 0, 0

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
        self.x_velocity, self.y_velocity, self.z_velocity = 0, 0, 0

    def __str__(self):
        return "pos=<x={}, y={}, z={}> vel=<x={}, y={}, z={}>".format(
            self.x, self.y, self.z, self.x_velocity, self.y_velocity, self.z_velocity
        )

    def hash_x(self):
        return "{},{}".format(self.x, self.x_velocity)

    def hash_y(self):
        return "{},{}".format(self.y, self.y_velocity)

    def hash_z(self):
        return "{},{}".format(self.z, self.z_velocity)

    def apply_gravity(self, other: 'Moon'):
        if self.x > other.x:
            self.x_velocity -= 1
        if self.x < other.x:
            self.x_velocity += 1
        if self.y > other.y:
            self.y_velocity -= 1
        if self.y < other.y:
            self.y_velocity += 1
        if self.z > other.z:
            self.z_velocity -= 1
        if self.z < other.z:
            self.z_velocity += 1

    def apply_velocity(self):
        self.x += self.x_velocity
        self.y += self.y_velocity
        self.z += self.z_velocity

    def pot_energy(self):
        return sum([abs(self.x), abs(self.y), abs(self.z)])

    def kin_energy(self):
        return sum([abs(self.x_velocity), abs(self.y_velocity), abs(self.z_velocity)])

    def tot_energy(self):
        return self.pot_energy() * self.kin_energy()

@day(12)
class Day12(AOCDay):
    test_input = """<x=-1, y=0, z=2>
<x=2, y=-10, z=-7>
<x=4, y=-8, z=8>
<x=3, y=5, z=-1>""".split("\n")
    test_input2 = """<x=-8, y=-10, z=0>
<x=5, y=5, z=10>
<x=2, y=-7, z=3>
<x=9, y=-8, z=-3>""".split("\n")

    moons: List[Moon] = []

    IN_RE = re.compile('<x=(?:\s+)?(?P<pos_x>-?[0-9]+), y=(?:\s+)?(?P<pos_y>-?[0-9]+), z=(?:\s+)?(?P<pos_z>-?[0-9]+)>')

    def common(self, input_data):
        # input_data = self.test_input
        self.moons = []
        self.history = {'x': set(), 'y': set(), 'z': set()}
        self.repetitions = {'x': None, 'y': None, 'z': None}
        for line in input_data:
            match = self.IN_RE.match(line)
            if match:
                x, y, z = int(match.group("pos_x")), int(match.group("pos_y")), int(match.group("pos_z"))
                self.moons.append(Moon(x, y, z))
            else:
                raise ValueError("No match: {}".format(line))

    def part1(self, input_data):
        for i in range(1000):
            for moon, other in combinations(self.moons, 2):
                moon.apply_gravity(other)
                other.apply_gravity(moon)
            for moon in self.moons:
                moon.apply_velocity()
        total_energy = sum(moon.tot_energy() for moon in self.moons)
        yield total_energy

    history = {'x': set(), 'y': set(), 'z': set()}
    repetitions: Dict[str, Optional[int]] = {'x': None, 'y': None, 'z': None}

    def least_common_multiple(self, x, y, z):
        lcm_xy = (x // math.gcd(x, y) * y)
        return (lcm_xy // math.gcd(lcm_xy, z) * z)

    def part2(self, input_data):
        loop = 0
        while True:
            if all(x is not None for x in self.repetitions.values()):
                break
            for moon, other in combinations(self.moons, 2):
                moon.apply_gravity(other)
                other.apply_gravity(moon)
            for moon in self.moons:
                moon.apply_velocity()
            if self.repetitions['x'] is None:
                xkey = ";".join(x.hash_x() for x in self.moons)
                if xkey in self.history['x']:
                    self.repetitions['x'] = loop
                    print("x loops after {} iterations".format(loop))
                self.history['x'].add(xkey)
            if self.repetitions['y'] is None:
                ykey = ";".join(x.hash_y() for x in self.moons)
                if ykey in self.history['y']:
                    self.repetitions['y'] = loop
                    print("y loops after {} iterations".format(loop))
                self.history['y'].add(ykey)
            if self.repetitions['z'] is None:
                zkey = ";".join(x.hash_z() for x in self.moons)
                if zkey in self.history['z']:
                    self.repetitions['z'] = loop
                    print("z loops after {} iterations".format(loop))
                self.history['z'].add(zkey)
            loop += 1
        rx, ry, rz = self.repetitions['x'], self.repetitions['y'], self.repetitions['z']
        yield self.least_common_multiple(rx, ry, rz)
