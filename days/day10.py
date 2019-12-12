import math
import time
from functools import lru_cache

from days import AOCDay, day

DEBUG = False
VISUALIZE = False

ASTEROID = 1
EMPTY = 0

cached_functions = []

def clearable_lru_cache(*args, **kwargs):
    def decorator(func):
        func = lru_cache(*args, **kwargs)(func)
        cached_functions.append(func)
        return func

    return decorator

def clear_all_cached_functions():
    for func in cached_functions:
        func.cache_clear()

@day(10)
class Day10(AOCDay):
    test_input = """.#..#
.....
#####
....#
...##""".split("\n")
    test_input2 = """......#.#.
#..#.#....
..#######.
.#.#.###..
.#..#.....
..#....#.#
#..#....#.
.##.#..###
##...#..#.
.#....####""".split("\n")
    test_input3 = """#.#...#.#.
.###....#.
.#....#...
##.#.#.#.#
....#.#.#.
.##..###.#
..#...##..
..##....##
......#...
.####.###.""".split("\n")
    test_input4 = """.#..#..###
####.###.#
....###.#.
..###.##.#
##.##.#.#.
....###..#
..#.#..#.#
#..#.#.###
.##...##.#
.....#.#..""".split("\n")
    test_input5 = """.#..##.###...#######
##.############..##.
.#.######.########.#
.###.#######.####.#.
#####.##.#.##.###.##
..#####..#.#########
####################
#.####....###.#.#.##
##.#################
#####.##.###..####..
..######..##.#######
####.##.####...##..#
.#####..#.######.###
##...#.##########...
#.##########.#######
.####.#.###.###.#.##
....##.##.###..#####
.#.#.###########.###
#.#.#.#####.####.###
###.##.####.##.#..##""".split("\n")
    test_input6 = """.#....#####...#..
##...##.#####..##
##...#...#.#####.
..#.....#...###..
..#.#.....#....##""".split("\n")

    field = []
    field_width = 0
    field_height = 0

    def common(self, input_data):
        # input_data = self.test_input5
        self.field = []
        for line in input_data:
            self.field.append([])
            for point in line:
                self.field[-1].append(ASTEROID if point == "#" else EMPTY)
        self.field_width = len(self.field[0])
        self.field_height = len(self.field)

    @clearable_lru_cache
    def asteroids(self):
        return [(x, y) for x in range(self.field_width) for y in range(self.field_height) if self.field[y][x] == ASTEROID]

    def is_blocked(self, starting_point, asteroid_pos):
        start_x, start_y = starting_point
        target_x, target_y = asteroid_pos
        delta_x, delta_y = target_x - start_x, target_y - start_y
        if (delta_x, delta_y) == (0, 0):
            return False
        gcd = math.gcd(delta_x, delta_y)
        if gcd != 0:
            gcd_x, gcd_y = delta_x // gcd, delta_y // gcd
        else:
            gcd_x, gcd_y = delta_x, delta_y
        blocks = []
        x, y = starting_point
        x += gcd_x
        y += gcd_y
        while 0 <= x < self.field_width and 0 <= y < self.field_height:
            if x > target_x > start_x or y > target_y > start_y:
                break
            if x < target_x < start_x or y < target_y < start_y:
                break
            if (x, y) != asteroid_pos:
                blocks.append((x, y))
            x += gcd_x
            y += gcd_y
        return any(self.field[y][x] == ASTEROID for (x, y) in blocks if (x, y) != asteroid_pos)

    def asteroids_visible(self, starting_point):
        return filter(lambda x: not self.is_blocked(starting_point, x) and x != starting_point, self.asteroids())

    def num_asteroids_visible(self, starting_point):
        return len(list(self.asteroids_visible(starting_point)))

    def print_field(self, asteroids=None, base=None, target=None):
        for y in range(self.field_height):
            for x in range(self.field_width):
                if asteroids:
                    if base or target:
                        if (x, y) == base:
                            print("@", end="")
                        elif (x, y) == target:
                            print("X", end="")
                        else:
                            print("#" if (x, y) in asteroids else ".", end="")
                    else:
                        print("#" if (x, y) in asteroids else ".", end="")
                else:
                    if base or target:
                        if (x, y) == base:
                            print("@", end="")
                        elif (x, y) == target:
                            print("X", end="")
                        else:
                            print("#" if self.field[y][x] == ASTEROID else ".", end="")
                    else:
                        print("#" if self.field[y][x] == ASTEROID else ".", end="")
            print("")

    def part1(self, input_data):
        max = None
        max_num = 0
        for asteroid in self.asteroids():
            asteroid_num = self.num_asteroids_visible(asteroid)
            if asteroid_num > max_num:
                max_num = asteroid_num
                max = asteroid

        if DEBUG:
            print(max)
        yield max_num

    def part2(self, input_data):
        # Find best asteroid
        max = None
        max_num = 0
        for asteroid in self.asteroids():
            asteroid_num = self.num_asteroids_visible(asteroid)
            if asteroid_num > max_num:
                max_num = asteroid_num
                max = asteroid

        prev_asteroid_destroyed = None
        i = 1

        if VISUALIZE:
            self.print_field()
            input("Please resize to fit and press enter to continue")

        if DEBUG:
            print("Listening post on {}".format(max))
        while len(self.asteroids()) > 1:
            # Find smallest angle from current laser angle
            smallest = None
            smallest_angle = None
            if prev_asteroid_destroyed is not None:
                prev_angle = math.atan2(prev_asteroid_destroyed[1] - max[1], prev_asteroid_destroyed[0] - max[0])
                prev_angle = prev_angle + 0.0001  # Don't allow the exact same angle
            else:
                prev_angle = -0.5 * math.pi  # Straight up
            for asteroid in self.asteroids_visible(max):
                new_angle = math.atan2(asteroid[1] - max[1], asteroid[0] - max[0])
                new_smallest_angle = new_angle - prev_angle
                if (smallest_angle is None and new_smallest_angle >= 0) or 0 <= new_smallest_angle < smallest_angle:
                    smallest_angle = new_smallest_angle
                    smallest = asteroid
            if smallest is None:
                # Nothing found because we wrapped around the unit circle.
                # Search again but add 2 * pi to the new smallest angle
                for asteroid in self.asteroids_visible(max):
                    new_angle = math.atan2(asteroid[1] - max[1], asteroid[0] - max[0])
                    new_smallest_angle = (new_angle - prev_angle) + (2 * math.pi)
                    if (smallest_angle is None and new_smallest_angle >= 0) or 0 <= new_smallest_angle < smallest_angle:
                        smallest_angle = new_smallest_angle
                        smallest = asteroid
            if not smallest:
                self.print_field()
            if DEBUG:
                print("Asteroid {} to destroy: {}, angle {}".format(i, smallest, smallest_angle))
            if VISUALIZE:
                self.print_field(base=max, target=smallest)
                print("")
                time.sleep(0.1)
            if i == 200 and not VISUALIZE:
                yield (smallest[0] * 100) + smallest[1]
                return
            self.field[smallest[1]][smallest[0]] = EMPTY
            i += 1
            prev_asteroid_destroyed = smallest