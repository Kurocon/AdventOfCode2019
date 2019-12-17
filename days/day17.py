from queue import Queue
from typing import List

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
        self.memory = defaultlist(lambda: 0)
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

@day(17)
class Day17(AOCDay):
    virtual_machines: List[VirtualMachine] = []
    num_vms = 1

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

    maze_data: List[List[str]] = [[]]

    DIRECTIONS = [(0, -1, "N"), (0, 1, "S"), (1, 0, "E"), (-1, 0, "W")]
    SCAFFOLDS = "#O^<>v"

    def alignment_parameters(self):
        sum = 0
        for y, line in enumerate(self.maze_data):
            for x, char in enumerate(line):
                # If character north, south, west and east are also scaffolds, this is an intersection
                try:
                    if all(self.maze_data[y][x] in self.SCAFFOLDS and self.maze_data[y+diry][x+dirx] in self.SCAFFOLDS for dirx, diry, _ in self.DIRECTIONS):
                        sum += x * y
                except IndexError:
                    pass
        return sum

    def part1(self, input_data):
        vm_inputs = [[]]
        self.maze_data = [[]]

        for i, vm_input in enumerate(vm_inputs):
            if INFO or DEBUG:
                print("-- Input {} --".format(vm_input))

            for j in vm_input:
                self.virtual_machines[i].input_queue.put(j)

        states = [False for _ in self.virtual_machines]
        if INFO or DEBUG:
            print("Running virtual machines...")
        while not all([vm.memory[vm.pc] == INSTR_END for vm in self.virtual_machines]):
            for i, vm in enumerate(self.virtual_machines):
                try:
                    states[i] = vm.run_instruction()
                except Exception as e:
                    print("=== EXCEPTION ===")
                    print("PC:", vm.pc)
                    print("Memory", vm.memory)
                    raise e

                # Get VM output
                if not vm.output_queue.empty():
                    vm_output = vm.output_queue.get()
                    char = chr(vm_output)
                    if VISUALIZE:
                        print(char, end="")
                    if char != "\n":
                        self.maze_data[-1].append(char)
                    else:
                        self.maze_data.append([])

        self.maze_data = self.maze_data[:-2]
        yield self.alignment_parameters()

    BOTS = "^><>V"
    INVERSE = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
    ROTATE = {
        ('N', 'E'): 'R',
        ('N', 'W'): 'L',
        ('E', 'S'): 'R',
        ('E', 'N'): 'L',
        ('S', 'W'): 'R',
        ('S', 'E'): 'L',
        ('W', 'N'): 'R',
        ('W', 'S'): 'L',
    }

    def neighbors(self, x, y):
        return [(x+dirx, y+diry, dir) for dirx, diry, dir in self.DIRECTIONS if 0 <= x+dirx < len(self.maze_data[y]) and 0 <= y+diry < len(self.maze_data)]

    def filter_old_direction(self, direction, fields):
        return [field for field in fields if field[2] != self.INVERSE[direction]]

    def move(self, pos, direction):
        res = None
        if direction == "N":
            res = pos[0], pos[1] - 1
        elif direction == "S":
            res = pos[0], pos[1] + 1
        elif direction == "E":
            res = pos[0] + 1, pos[1]
        elif direction == "W":
            res = pos[0] - 1, pos[1]
        if 0 <= res[0] < len(self.maze_data[0]) and 0 <= res[1] < len(self.maze_data):
            try:
                _ = self.maze_data[res[1]][res[0]]
                return res
            except IndexError:
                return None
        return None

    def calculate_path(self):
        own_pos = next((x, y) for y in range(len(self.maze_data)) for x in range(len(self.maze_data[y])) if self.maze_data[y][x] in self.BOTS)
        scaffold_neighbors = list(filter(lambda x: self.maze_data[x[1]][x[0]] in self.SCAFFOLDS, self.neighbors(own_pos[0], own_pos[1])))
        direction = scaffold_neighbors[0][2]
        rotation = self.ROTATE[('N', direction)]

        path = []

        while True:
            amount = 0
            while True:
                new_pos = self.move(own_pos, direction)
                if new_pos is not None and self.maze_data[new_pos[1]][new_pos[0]] in self.SCAFFOLDS:
                    own_pos = new_pos
                    amount += 1
                else:
                    break
            path.append(rotation)
            path.append(amount)

            scaffold_neighbors = list(filter(lambda x: self.maze_data[x[1]][x[0]] in self.SCAFFOLDS, self.neighbors(own_pos[0], own_pos[1])))
            try:
                new_direction = self.filter_old_direction(direction, scaffold_neighbors)[0][2]
                rotation = self.ROTATE[(direction, new_direction)]
                direction = new_direction
            except IndexError:
                break
        return path

    def part2(self, input_data):
        path = self.calculate_path()

        if VISUALIZE:
            print(",".join(map(str, path)))

        # L,10,L,8,R,8,L,8,R,6,L,10,L,8,R,8,L,8,R,6,R,6,R,8,R,8,R,6,R,6,L,8,L,10,R,6,R,8,R,8,R,6,R,6,L,8,L,10,R,6,R,8,R,8,R,6,R,6,L,8,L,10,R,6,R,8,R,8,L,10,L,8,R,8,L,8,R,6

        # L,10,L,8,R,8,L,8,R,6
        # L,10,L,8,R,8,L,8,R,6
        # R,6,R,8,R,8
        # R,6,R,6,L,8,L,10
        # R,6,R,8,R,8
        # R,6,R,6,L,8,L,10
        # R,6,R,8,R,8
        # R,6,R,6,L,8,L,10
        # R,6,R,8,R,8
        # L,10,L,8,R,8,L,8,R,6

        MAIN = "A,A,C,B,C,B,C,B,C,A"
        A = "L,10,L,8,R,8,L,8,R,6"
        B = "R,6,R,6,L,8,L,10"
        C = "R,6,R,8,R,8"

        vm_in = list(ord(x) for x in MAIN + "\n" + A + "\n" + B + "\n" + C + "\n" + "n\n")

        for vm in self.virtual_machines:
            vm.reset()
            vm.memory[0] = 2
            vm.initial_memory[0] = 2
            self.memory[0] = 2

        vm_inputs = [vm_in]

        for i, vm_input in enumerate(vm_inputs):
            if INFO or DEBUG:
                print("-- Input {} --".format(vm_input))

            for j in vm_input:
                self.virtual_machines[i].input_queue.put(j)

        states = [False for _ in self.virtual_machines]
        if INFO or DEBUG:
            print("Running virtual machines...")
        while not all([vm.memory[vm.pc] == INSTR_END for vm in self.virtual_machines]):
            for i, vm in enumerate(self.virtual_machines):
                try:
                    states[i] = vm.run_instruction()
                except Exception as e:
                    print("=== EXCEPTION ===")
                    print("PC:", vm.pc)
                    print("Memory", vm.memory)
                    raise e

                # Get VM output
                if not vm.output_queue.empty():
                    vm_output = vm.output_queue.get()
                    try:
                        char = chr(vm_output)
                        if VISUALIZE:
                            print(char, end="")
                    except ValueError:
                        yield vm_output
