from collections import defaultdict
from queue import PriorityQueue
from typing import Dict, Tuple, List, Optional
import networkx as nx

from days import AOCDay, day

DEBUG = True

NEIGHBOURS = [(-1, 0), (0, -1), (1, 0), (0, 1)]
DIAGONALS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]


class Map:
    field = defaultdict(str)
    size = (0, 0)
    positions: List[Tuple[int, int]] = []
    doors: Dict[str, Tuple[int, int]] = {}
    keys: Dict[str, Tuple[int, int]] = {}
    part: int = 1
    graph: Optional[nx.Graph] = None

    def __init__(self, map):
        self.field = defaultdict(str)
        self.size = (len(map[0]), len(map))
        self.positions = []
        self.doors = {}
        self.keys = {}
        self.part = 1
        self.graph = None
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                self.field[(x, y)] = map[y][x]
                if self.field[(x, y)].isupper():
                    self.doors[self.field[(x, y)]] = (x, y)
                if self.field[(x, y)].islower():
                    self.keys[self.field[(x, y)]] = (x, y)
                if self.field[(x, y)] == "@":
                    self.positions.append((x, y))

    def modify_dungeon(self):
        pos = self.positions[0]
        self.positions = []
        self.field[pos] = "#"
        for neighbor in NEIGHBOURS:
            neigh_pos = (pos[0] + neighbor[0], pos[1] + neighbor[1])
            self.field[neigh_pos] = "#"
        for diagonal in DIAGONALS:
            diag_pos = (pos[0] + diagonal[0], pos[1] + diagonal[1])
            self.field[diag_pos] = "@"
            self.positions.append(diag_pos)

    def valid_char(self, char):
        return char != "#"

    def build_graph(self):
        graph = nx.Graph()
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                if not self.valid_char(self.field[(x, y)]):
                    continue
                graph.add_node((x, y))
                for neighbor in NEIGHBOURS:
                    neigh_pos = (x + neighbor[0], y + neighbor[1])
                    if self.valid_char(self.field[neigh_pos]):
                        graph.add_edge((x, y), neigh_pos)
        self.graph = graph
        return graph

    def doors_on_path(self, path):
        return set(door.lower() for door in self.doors.keys() if self.doors[door] in path)

    def build_key_paths(self):
        important_locations = list(self.keys.values()) + self.positions
        path_info = {}

        for loc1 in important_locations:
            for loc2 in important_locations:
                if loc1 == loc2 or (loc1, loc2) in path_info:
                    continue
                path = None
                try:
                    path = nx.dijkstra_path(self.graph, loc1, loc2)
                except nx.NetworkXNoPath:
                    continue
                steps_taken = len(path) - 1
                doors_on_path = self.doors_on_path(path)
                path_info[(loc1, loc2)] = (steps_taken, doors_on_path)
                path_info[(loc2, loc1)] = (steps_taken, doors_on_path)
        self.path_info = path_info

    def solve(self):
        distance_to = defaultdict(lambda: 999999)
        edge_to = {}
        pq = PriorityQueue()
        collected_keys = set()
        state = (tuple(self.positions), tuple(collected_keys))
        distance_to[state] = 0
        pq.put((0, state))

        while not pq.empty():
            length, state = pq.get()

            # Stop on solution found
            if state[0] == (-1, -1):
                break

            steps = self.possible_steps(state)
            for new_state, length in steps:
                if distance_to[new_state] > distance_to[state] + length:
                    distance_to[new_state] = distance_to[state] + length
                    edge_to[new_state] = state
                    if new_state[0] != (-1, -1):
                        pq.put((distance_to[new_state], new_state))

        for k, v in distance_to.items():
            if k[0] == (-1, -1):
                return v
        a = [print(x) for x in distance_to.items()]
        return 0

    def possible_steps(self, state):
        (locations, collected_keys) = state
        steps = []
        remaining_keys = set(self.keys.keys()) - set(collected_keys)

        # Move to -1, -1 if all keys are collected to indicate we are done
        if len(remaining_keys) == 0 and locations != (-1, -1):
            new_state = ((-1, -1), collected_keys)
            steps.append((new_state, 0))

        for key in remaining_keys:
            info = None
            location_to_update = None
            for i, cur_location in enumerate(locations):
                pair = (cur_location, self.keys[key])
                if pair in self.path_info:
                    info = self.path_info[pair]
                    location_to_update = i

            blocking_doors = info[1] - set(collected_keys)
            if len(blocking_doors) > 0:
                continue

            new_locations = list(locations)
            new_locations[location_to_update] = self.keys[key]
            new_locations = tuple(new_locations)
            new_state = new_locations, tuple(set(collected_keys) | set(key))
            steps.append((new_state, info[0]))
        return steps


@day(18)
class Day18(AOCDay):
    test_input = """#########
#b.A.@.a#
#########""".split("\n")
    test_input2 = """########################
#f.D.E.e.C.b.A.@.a.B.c.#
######################.#
#d.....................#
########################""".split("\n")
    test_input3 = """#######
#a.#Cd#
##...##
##.@.##
##...##
#cB#Ab#
#######""".split("\n")
    test_input4 = """#############
#g#f.D#..h#l#
#F###e#E###.#
#dCba...BcIJ#
#####.@.#####
#nK.L...G...#
#M###N#H###.#
#o#m..#i#jk.#
#############""".split("\n")

    def common(self, input_data):
        # input_data = self.test_input4
        self.map = Map(input_data)

    def part1(self, input_data):
        self.map.build_graph()
        self.map.build_key_paths()
        yield self.map.solve()

    def part2(self, input_data):
        self.map.part = 2
        self.map.modify_dungeon()
        self.map.build_graph()
        self.map.build_key_paths()
        yield self.map.solve()
