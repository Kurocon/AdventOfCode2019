import time
from queue import Queue, PriorityQueue
from typing import List, Optional, Tuple, Dict

from days import AOCDay, day

DEBUG = False
INFO = False
VISUALIZE = False


class defaultlist(list):
    def __init__(self, fx):
        self._fx = fx
    def _fill(self, index):
        while len(self) <= index:
            self.append(self._fx())
    def __setitem__(self, index, value):
        self._fill(index)
        list.__setitem__(self, index, value)
    def __getitem__(self, index):
        self._fill(index)
        return list.__getitem__(self, index)


def add(pc, xarg, yarg, addrarg):
    xmode, x = xarg
    ymode, y = yarg
    addrmode, addr = addrarg
    if xmode == MODE_POS:
        x = pc.memory[x]
    elif xmode == MODE_REL:
        x = pc.memory[pc.relative_base + x]
    if ymode == MODE_POS:
        y = pc.memory[y]
    elif ymode == MODE_REL:
        y = pc.memory[pc.relative_base + y]
    if addrmode == MODE_REL:
        addr = pc.relative_base + addr

    if DEBUG:
        print("/ add {} {} ".format(x, y), end="")
    pc.memory[addr] = x + y
    if DEBUG:
        print("=> @{}={}".format(addr, pc.memory[addr]))

def mult(pc, xarg, yarg, addrarg):
    xmode, x = xarg
    ymode, y = yarg
    addrmode, addr = addrarg
    if xmode == MODE_POS:
        x = pc.memory[x]
    elif xmode == MODE_REL:
        x = pc.memory[pc.relative_base + x]
    if ymode == MODE_POS:
        y = pc.memory[y]
    elif ymode == MODE_REL:
        y = pc.memory[pc.relative_base + y]
    if addrmode == MODE_REL:
        addr = pc.relative_base + addr

    if DEBUG:
        print("/ mul {} {} ".format(x, y), end="")
    pc.memory[addr] = x * y
    if DEBUG:
        print("=> @{}={}".format(addr, pc.memory[addr]))

def i_input(pc: 'VirtualMachine', addrarg):
    addrmode, addr = addrarg
    if addrmode == MODE_REL:
        addr = pc.relative_base + addr
    if DEBUG:
        print("/ inp {} ".format(addr))
    if pc.input_queue.empty():
        if INFO or DEBUG:
            print("Waiting for input...")
        return True
    else:
        if INFO or DEBUG:
            print("Inputting...")
        value = pc.input_queue.get()
        pc.memory[addr] = value
    return False

def output(pc: 'VirtualMachine', addrarg):
    addrmode, addr = addrarg
    if addrmode == MODE_POS:
        addr = pc.memory[addr]
    elif addrmode == MODE_REL:
        addr = pc.memory[pc.relative_base + addr]
    if DEBUG:
        print("/ out {} ".format(addr))
    if INFO or DEBUG:
        print("Outputting...")
    pc.output_queue.put(addr)

def jump_if_true(pc, xarg, addrarg):
    xmode, x = xarg
    addrmode, addr = addrarg
    if xmode == MODE_POS:
        x = pc.memory[x]
    elif xmode == MODE_REL:
        x = pc.memory[pc.relative_base + x]
    if addrmode == MODE_POS:
        addr = pc.memory[addr]
    elif addrmode == MODE_REL:
        addr = pc.memory[pc.relative_base + addr]
    if DEBUG:
        print("/ jit {} => {} ".format(x, addr))
    if x != 0:
        pc.pc = addr

def jump_if_false(pc, xarg, addrarg):
    xmode, x = xarg
    addrmode, addr = addrarg
    if xmode == MODE_POS:
        x = pc.memory[x]
    elif xmode == MODE_REL:
        x = pc.memory[pc.relative_base + x]
    if addrmode == MODE_POS:
        addr = pc.memory[addr]
    elif addrmode == MODE_REL:
        addr = pc.memory[pc.relative_base + addr]
    if DEBUG:
        print("/ jif {} => {} ".format(x, addr))
    if x == 0:
        pc.pc = addr

def less_than(pc, xarg, yarg, addrarg):
    xmode, x = xarg
    ymode, y = yarg
    addrmode, addr = addrarg
    if xmode == MODE_POS:
        x = pc.memory[x]
    elif xmode == MODE_REL:
        x = pc.memory[pc.relative_base + x]
    if ymode == MODE_POS:
        y = pc.memory[y]
    elif ymode == MODE_REL:
        y = pc.memory[pc.relative_base + y]
    if addrmode == MODE_REL:
        addr = pc.relative_base + addr
    if DEBUG:
        print("/ lt {} {} => {} ".format(x, y, addr))
    if x < y:
        pc.memory[addr] = 1
    else:
        pc.memory[addr] = 0

def equals(pc, xarg, yarg, addrarg):
    xmode, x = xarg
    ymode, y = yarg
    addrmode, addr = addrarg
    if xmode == MODE_POS:
        x = pc.memory[x]
    elif xmode == MODE_REL:
        x = pc.memory[pc.relative_base + x]
    if ymode == MODE_POS:
        y = pc.memory[y]
    elif ymode == MODE_REL:
        y = pc.memory[pc.relative_base + y]
    if addrmode == MODE_REL:
        addr = pc.relative_base + addr
    if DEBUG:
        print("/ eq {} {} => {} ".format(x, y, addr))
    if x == y:
        pc.memory[addr] = 1
    else:
        pc.memory[addr] = 0

def rebase(pc, xarg):
    xmode, x = xarg
    if xmode == MODE_POS:
        x = pc.memory[x]
    elif xmode == MODE_REL:
        x = pc.memory[pc.relative_base + x]
    if DEBUG:
        print("/ reb {} => {} ".format(x, pc.relative_base + x))
    pc.relative_base += x


INSTR_ADD = 1
INSTR_MUL = 2
INSTR_INP = 3
INSTR_OUT = 4
INSTR_JIT = 5
INSTR_JIF = 6
INSTR_LT = 7
INSTR_EQ = 8
INSTR_REB = 9
INSTR_END = 99

MODE_POS = 0
MODE_IMM = 1
MODE_REL = 2


class VirtualMachine:
    pc = 0
    memory = defaultlist(lambda: 0)
    initial_memory = defaultlist(lambda: 0)
    input_queue: Queue = None
    output_queue: Queue = None
    waiting = False
    relative_base = 0
    breakpt = False
    instr_set = {
        # CONST: (func, nargs, name)
        INSTR_ADD: (add, 3, "add"),
        INSTR_MUL: (mult, 3, "mult"),
        INSTR_INP: (i_input, 1, "in"),
        INSTR_OUT: (output, 1, "out"),
        INSTR_JIT: (jump_if_true, 2, "jit"),
        INSTR_JIF: (jump_if_false, 2, "jif"),
        INSTR_LT: (less_than, 3, "lt"),
        INSTR_EQ: (equals, 3, "eq"),
        INSTR_REB: (rebase, 1, "reb"),

        INSTR_END: (lambda: None, 0, "end"),
    }

    def reset(self):
        self.memory = defaultlist(0)
        for i in self.initial_memory:
            self.memory.append(i)
        while not self.input_queue.empty():
            self.input_queue.get()
        while not self.output_queue.empty():
            self.output_queue.get()
        self.waiting = False
        self.pc = 0
        self.relative_base = 0

    def initialize(self):
        self.pc = 0
        self.relative_base = 0

    def run_instruction(self):
        instr = self.memory[self.pc]
        if self.waiting and not self.input_queue.empty():
            if INFO or DEBUG:
                print("Got input!")
            # self.breakpt = True
            self.waiting = False
        if not self.waiting and instr != INSTR_END:
            if DEBUG:
                print("{}: ".format(self.pc), end="")

            instr_opcode = int(str(instr)[-2:])
            instr_modes = [int(x) for x in reversed(str(instr)[:-2])]
            instr_func, instr_narg, instr_name = self.instr_set[instr_opcode]
            while len(instr_modes) < instr_narg:
                instr_modes.append(MODE_POS)  # Default mode

            if DEBUG:
                print("{} ".format(instr_name), end="")
                for i in range(instr_narg):
                    mode = "I" if instr_modes[i] == MODE_IMM else "@" if instr_modes[i] == MODE_POS else "#"
                    print("{}{} ".format(mode, self.memory[self.pc + 1 + i]), end="")

            instr_args = [(instr_modes[i], self.memory[self.pc + 1 + i]) for i in range(instr_narg)]

            pc_pre = self.pc
            res = instr_func(self, *instr_args)
            if res:
                self.waiting = True
            else:
                if pc_pre == self.pc:
                    self.pc += 1 + instr_narg
            if self.breakpt:
                i = input("Step?")
                if i == "n":
                    self.breakpt = False
            return False
        elif not self.waiting:
            return True
        else:
            return False

    def run_program(self):
        self.initialize()

        while not self.run_instruction():
            pass

        return self.memory[0]

NORTH = 1
SOUTH = 2
WEST = 3
EAST = 4

STATUS_WALL = 0
STATUS_SUCCESS = 1
STATUS_OXYGEN = 2

GROUND_EMPTY = 0
GROUND_WALL = 1
GROUND_OXYGEN = 2
GROUND_UNKNOWN = None

CHARS = {
    GROUND_EMPTY: ".",
    GROUND_WALL: "#",
    GROUND_OXYGEN: "O",
    GROUND_UNKNOWN: " "
}

class Point:
    ground = GROUND_UNKNOWN
    position: Tuple[int, int] = (0, 0)
    north: Optional['Point'] = None
    south: Optional['Point'] = None
    west: Optional['Point'] = None
    east: Optional['Point'] = None

    def __init__(self):
        self.ground = GROUND_UNKNOWN
        self.position = (0, 0)
        self.north = None
        self.south = None
        self.west = None
        self.east = None

    def __str__(self):
        return "Point: type={} x={} y={}".format(self.ground, self.position[1], self.position[0])

    def __lt__(self, other):
        if isinstance(other, Point):
            return self.position < other.position
        else:
            raise TypeError('Cannot compare State with {}'.format(type(other)))

    def __gt__(self, other):
        if isinstance(other, Point):
            return self.position > other.position
        else:
            raise TypeError('Cannot compare State with {}'.format(type(other)))

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.position == other.position
        else:
            raise TypeError('Cannot compare State with {}'.format(type(other)))

    def __ne__(self, other):
        if isinstance(other, Point):
            return self.position != other.position
        else:
            raise TypeError('Cannot compare State with {}'.format(type(other)))

    def __hash__(self):
        return hash((self.ground, self.position))


@day(15)
class Day15(AOCDay):
    virtual_machines: List[VirtualMachine] = []
    num_vms = 1

    position: Point = None
    points: Dict[Tuple[int, int], Point] = {}
    undiscovered: List[Point] = []

    prev_move = None
    next_pos: Optional[Point] = None
    oxygen: Optional[Point] = None

    def next_undiscovered(self):
        if self.undiscovered:
            sorted_undiscovereds = sorted(self.undiscovered, key=lambda x: self.manhattan_distance(self.position.position, x.position) + self.undiscovered.index(x))
            dist = self.path_towards(self.position, sorted_undiscovereds[0])
            return self.undiscovered[0], dist[0][1], dist[0][2], dist
        return None, None, None, None

    def possible_moves(self, position: Point):
        moves = []
        if position.north is not None and position.north.ground != GROUND_WALL:
            moves.append((NORTH, position.north))
        if position.south is not None and position.south.ground != GROUND_WALL:
            moves.append((SOUTH, position.south))
        if position.west is not None and position.west.ground != GROUND_WALL:
            moves.append((WEST, position.west))
        if position.east is not None and position.east.ground != GROUND_WALL:
            moves.append((EAST, position.east))
        return moves

    def manhattan_distance(self, start: Tuple[int, int], target: Tuple[int, int]):
        return sum(abs(p1 - p2) for p1, p2 in zip(start, target))

    def path_towards(self, position: Point, target: Point):
        """"A* shortest path algorithm"""
        costs = {position: 0}
        history = {position: []}
        paths_to_explore = PriorityQueue()
        paths_to_explore.put((0, position))
        finished = True

        state = None
        while not paths_to_explore.empty():
            _, state = paths_to_explore.get()
            if state == target:
                # Goal reached!
                finished = True
                break

            for move, point in self.possible_moves(state):
                new_cost = costs[state] + 1
                if point not in costs or new_cost < costs[point]:
                    costs[point] = new_cost
                    history[point] = history[state][:]
                    history[point].append([new_cost, move, point])
                    priority = self.manhattan_distance(point.position, target.position)
                    paths_to_explore.put((priority, point))
        if finished:
            return history[state]
        return None

    def fill_point(self, point: Point):
        if point.north is None:
            pos = point.position[0] - 1, point.position[1]
            if pos in self.points:
                point.north = self.points[pos]
            else:
                point.north = Point()
                point.north.position = pos
                point.north.south = point
                self.points[pos] = point.north
                self.undiscovered.append(point.north)
        if point.south is None:
            pos = point.position[0] + 1, point.position[1]
            if pos in self.points:
                point.south = self.points[pos]
            else:
                point.south = Point()
                point.south.position = pos
                point.south.north = point
                self.points[pos] = point.south
                self.undiscovered.append(point.south)
        if point.west is None:
            pos = point.position[0], point.position[1] - 1
            if pos in self.points:
                point.west = self.points[pos]
            else:
                point.west = Point()
                point.west.position = pos
                point.west.east = point
                self.points[pos] = point.west
                self.undiscovered.append(point.west)
        if point.east is None:
            pos = point.position[0], point.position[1] + 1
            if pos in self.points:
                point.east = self.points[pos]
            else:
                point.east = Point()
                point.east.position = pos
                point.east.west = point
                self.points[pos] = point.east
                self.undiscovered.append(point.east)

    def mark_position(self, output_from_program: int):
        if output_from_program == STATUS_WALL:
            # We hit a wall, mark it
            self.next_pos.ground = GROUND_WALL
            if INFO or DEBUG:
                print("Mark {} as WALL".format(self.next_pos))
        elif output_from_program == STATUS_SUCCESS:
            self.fill_point(self.next_pos)
            self.position = self.next_pos
            self.next_pos.ground = GROUND_EMPTY
            if INFO or DEBUG:
                print("Mark {} as EMPTY".format(self.next_pos))
        elif output_from_program == STATUS_OXYGEN:
            self.fill_point(self.next_pos)
            self.position = self.next_pos
            self.next_pos.ground = GROUND_OXYGEN
            self.oxygen = self.position
            if INFO or DEBUG:
                print("Mark {} as OXYGEN".format(self.next_pos))
        if self.next_pos in self.undiscovered:
            self.undiscovered.remove(self.next_pos)

    def do_step(self, output_from_program: Optional[int] = None):
        if output_from_program is not None:
            self.mark_position(output_from_program)

        # Try to move to closest undiscovered cell
        target, move, nextpoint, path = self.next_undiscovered()
        if VISUALIZE:
            self.print_screen()
            time.sleep(0.005)
        if INFO or DEBUG:
            print("{}: {} - T:{} M:{} N:{}".format(self.position, output_from_program, target, move, nextpoint))
            print("Path ", path)
        if move:
            self.next_pos = nextpoint
            return move
        else:
            return None

    def print_screen(self):
        min_y = sorted(x[0] for x in self.points.keys())[0]
        max_y = sorted(x[0] for x in self.points.keys())[-1]
        min_x = sorted(x[1] for x in self.points.keys())[0]
        max_x = sorted(x[1] for x in self.points.keys())[-1]
        print("\033c", end="")
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if (y, x) in self.points.keys():
                    if self.position == self.points[(y, x)]:
                        print("B", end="")
                    else:
                        print(CHARS[self.points[(y, x)].ground], end="")
                else:
                    print(" ", end="")
            print("")
        print("")

    def common(self, input_data):
        self.memory = list(map(int, input_data.split(',')))
        self.virtual_machines = []
        for i in range(self.num_vms):
            vm = VirtualMachine()
            vm.input_queue = Queue()
            vm.output_queue = Queue()
            for i in self.memory:
                vm.memory.append(i)
                vm.initial_memory.append(i)
            self.virtual_machines.append(vm)

        # Build map once
        if self.position is None:
            self.position = Point()
            self.position.ground = GROUND_EMPTY
            self.points = {(0, 0): self.position}
            self.position.north = Point()
            self.position.north.position = (-1, 0)
            self.points[(-1, 0)] = self.position.north
            self.position.south = Point()
            self.position.south.position = (1, 0)
            self.points[(1, 0)] = self.position.south
            self.position.east = Point()
            self.position.east.position = (0, 1)
            self.points[(0, 1)] = self.position.east
            self.position.west = Point()
            self.position.west.position = (0, -1)
            self.points[(0, -1)] = self.position.west
            self.undiscovered = [self.position.north, self.position.south, self.position.west, self.position.east]
            self.prev_move = None
            self.next_pos = None
            self.oxygen = None
            self.build_map()

    def build_map(self):
        vm_inputs = [[self.do_step()]]

        for i, vm_input in enumerate(vm_inputs):
            if INFO or DEBUG:
                print("-- Input {} --".format(vm_input))

            for j in vm_input:
                self.virtual_machines[i].input_queue.put(j)

        states = [False for _ in self.virtual_machines]
        if INFO or DEBUG:
            print("Running virtual machines...")
        screen_x, screen_y, tile_type = None, None, None
        while not all([vm.memory[vm.pc] == INSTR_END for vm in self.virtual_machines]):
            for i, vm in enumerate(self.virtual_machines):
                try:
                    states[i] = vm.run_instruction()
                except Exception as e:
                    print("=== EXCEPTION ===")
                    print("PC:", vm.pc)
                    print("Memory", vm.memory)
                    raise e

                # Provide next step if VM is waiting
                if vm.waiting:
                    # Get VM output
                    vm_output = None
                    if not vm.output_queue.empty():
                        vm_output = vm.output_queue.get()

                    move = self.do_step(vm_output)
                    if move:
                        vm.input_queue.put(move)
                    elif self.oxygen is not None:
                        # Mapping complete
                        return
                    else:
                        raise ValueError("Mapping complete but Oxygen not found!")

    def part1(self, input_data):
        # Mapping should be complete, find shortest path to oxygen
        yield len(self.path_towards(self.points[(0, 0)], self.oxygen))

    def part2(self, input_data):
        # Find the longest distance from the sensor
        paths_to_visit = PriorityQueue()
        paths_to_visit.put((0, self.oxygen))
        last_distance = 0
        while not paths_to_visit.empty():
            distance, point = paths_to_visit.get()
            if distance > last_distance:
                last_distance = distance
            point.ground = GROUND_OXYGEN
            for move, point in self.possible_moves(point):
                if point.ground == GROUND_EMPTY:
                    paths_to_visit.put((distance + 1, point))
        yield last_distance
