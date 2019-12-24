from copy import deepcopy
from typing import List

from days import AOCDay, day

DEBUG = False

BUG = "#"
NO_BUG = "."
NEIGHBOURS = [(-1, 0), (0, -1), (1, 0), (0, 1)]

@day(24)
class Day24(AOCDay):
    test_input = """""""".split("\n")
    grid: List[List[str]] = []
    old_grid: List[List[str]] = []
    known_biodiversities = set()

    def get_neighbours(self, x, y):
        return [self.old_grid[y + n[1]][x + n[0]] for n in NEIGHBOURS if 0 <= x + n[0] < len(self.old_grid[0]) and 0 <= y + n[1] < len(self.old_grid)]

    def copygrid(self):
        self.old_grid = deepcopy(self.grid)

    def step(self, x, y):
        current = self.old_grid[y][x]
        neighbours = self.get_neighbours(x, y)
        if current == BUG:
            if len([x for x in neighbours if x == BUG]) != 1:
                # Dies
                self.grid[y][x] = NO_BUG
        else:
            if len([x for x in neighbours if x == BUG]) in [1, 2]:
                # Spawns
                self.grid[y][x] = BUG

    def biodiversity(self):
        result = 0
        power = 1
        for y in range(len(self.grid)):
            for x in range(len(self.grid[0])):
                if self.grid[y][x] == BUG:
                    result += power
                power *= 2
        return result

    def common(self, input_data):
        # input_data = self.test_input
        self.grid = []
        self.known_biodiversities = set()
        for line in input_data:
            self.grid.append([])
            for char in line:
                self.grid[-1].append(char)

    def part1(self, input_data):
        biodiversity = self.biodiversity()
        while biodiversity not in self.known_biodiversities:
            self.known_biodiversities.add(biodiversity)
            self.copygrid()
            for y in range(len(self.grid)):
                for x in range(len(self.grid[0])):
                    self.step(x, y)
            biodiversity = self.biodiversity()
        yield biodiversity

    grid_rec: List[List[List[str]]] = []
    old_grid_rec: List[List[List[str]]] = []
    iterations: int = 200

    def count_neighbours_below(self, level, x, y):
        if x == 1:  # Left row
            return sum(self.old_grid_rec[level - 1][i][0] == BUG for i in range(5))
        if x == 3:  # Right row
            return sum(self.old_grid_rec[level - 1][i][4] == BUG for i in range(5))
        if y == 1:  # Top row
            return sum(self.old_grid_rec[level - 1][0][j] == BUG for j in range(5))
        if y == 3:  # Bottom row
            return sum(self.old_grid_rec[level - 1][4][j] == BUG for j in range(5))
        return 0

    def count_neighbours_rec(self, level, x, y):
        count = 0
        for neighbor in NEIGHBOURS:
            neigh_pos = (x + neighbor[0], y + neighbor[1])
            # Neighbours on lower level
            if neigh_pos[0] == 2 and neigh_pos[1] == 2:
                count += self.count_neighbours_below(level, x, y)
            # Left neighbour on upper level
            elif neigh_pos[0] == -1:
                if self.old_grid_rec[level + 1][2][1] == BUG:
                    count += 1
            # Right neighbour on upper level
            elif neigh_pos[0] == 5:
                if self.old_grid_rec[level + 1][2][3] == BUG:
                    count += 1
            # Top neighbour on upper level
            elif neigh_pos[1] == -1:
                if self.old_grid_rec[level + 1][1][2] == BUG:
                    count += 1
            # Bottom neighbour on upper level
            elif neigh_pos[1] == 5:
                if self.old_grid_rec[level + 1][3][2] == BUG:
                    count += 1
            # Normal field
            elif self.old_grid_rec[level][neigh_pos[1]][neigh_pos[0]] == BUG:
                count += 1
        return count

    def copygrid_rec(self):
        self.old_grid_rec = deepcopy(self.grid_rec)

    def step_rec(self, x, y, z):
        if x == 2 and y == 2:  # Skip middle field
            return

        if self.old_grid_rec[z][y][x] == BUG:
            if self.count_neighbours_rec(z, x, y) != 1:
                # Dies
                self.grid_rec[z][y][x] = NO_BUG
        else:
            if self.count_neighbours_rec(z, x, y) in [1, 2]:
                # Spawns
                self.grid_rec[z][y][x] = BUG

    def count_bugs_rec(self):
        return sum(self.grid_rec[level][y][x] == BUG for level in range(self.iterations * 2 + 3) for y in range(5) for x in range(5))

    def part2(self, input_data):
        self.iterations = 200
        self.grid_rec = [[["." for x in range(5)] for y in range(5)] for z in range(self.iterations * 2 + 3)]
        self.old_grid_rec = []

        # Fill initial grid
        for y in range(5):
            for x in range(5):
                self.grid_rec[self.iterations + 1][y][x] = self.grid[y][x]

        for step in range(self.iterations):
            if DEBUG:
                print("Step", step)
            self.copygrid_rec()
            for z in range(self.iterations * 2 + 1):
                for y in range(5):
                    for x in range(5):
                        self.step_rec(x, y, z)

        yield self.count_bugs_rec()

