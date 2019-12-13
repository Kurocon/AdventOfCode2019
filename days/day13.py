from collections import defaultdict
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

EMPTY = 0
WALL = 1
BLOCK = 2
PADDLE = 3
BALL = 4

NO_MOVE = 0
LEFT = -1
RIGHT = 1

CHARS = {
    EMPTY: " ",
    WALL: "#",
    BLOCK: "@",
    PADDLE: "_",
    BALL: "O",
}

@day(13)
class Day13(AOCDay):
    virtual_machines: List[VirtualMachine] = []
    num_vms = 1

    screen = defaultdict(lambda: EMPTY)

    def common(self, input_data):
        self.memory = list(map(int, input_data.split(',')))
        self.virtual_machines = []
        self.screen = defaultdict(lambda: EMPTY)
        for i in range(self.num_vms):
            vm = VirtualMachine()
            vm.input_queue = Queue()
            vm.output_queue = Queue()
            for i in self.memory:
                vm.memory.append(i)
                vm.initial_memory.append(i)
            self.virtual_machines.append(vm)

    def print_screen(self):
        prev_y = 0
        print("\033c", end="")
        for y, x in sorted(self.screen.keys()):
            if prev_y != y:
                print("")
            print(CHARS[self.screen[(y, x)]], end="")
            prev_y = y
        print("")

    @property
    def paddle_x(self):
        p = [x for y, x in self.screen.keys() if self.screen[(y, x)] == PADDLE]
        if p:
            return p[0]
        else:
            return None

    @property
    def ball_x(self):
        p = [x for y, x in self.screen.keys() if self.screen[(y, x)] == BALL]
        if p:
            return p[0]
        else:
            return None

    def part1(self, input_data):
        vm_inputs = [[]]

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

                # On 3x output, draw on screen
                if not vm.output_queue.empty() and screen_x is None:
                    screen_x = vm.output_queue.get()
                elif not vm.output_queue.empty() and screen_y is None:
                    screen_y = vm.output_queue.get()
                elif not vm.output_queue.empty() and tile_type is None:
                    tile_type = vm.output_queue.get()
                if screen_x is not None and screen_y is not None and tile_type is not None:
                    if INFO or DEBUG:
                        print("Output = {}".format((screen_x, screen_y, tile_type)))
                    self.screen[(screen_y, screen_x)] = tile_type
                    screen_x, screen_y, tile_type = None, None, None

        yield sum([1 for x in self.screen.values() if x == BLOCK])

    def part2(self, input_data):
        vm_inputs = [[]]
        self.virtual_machines[0].memory[0] = 2
        self.score = 0

        for i, vm_input in enumerate(vm_inputs):
            if INFO or DEBUG:
                print("-- Input {} --".format(vm_input))

            for j in vm_input:
                self.virtual_machines[i].input_queue.put(j)

        states = [False for _ in self.virtual_machines]
        if INFO or DEBUG:
            print("Running virtual machines...")
        screen_x, screen_y, tile_type = None, None, None
        while not all(states):
            for i, vm in enumerate(self.virtual_machines):
                try:
                    states[i] = vm.run_instruction()
                    if vm.waiting:
                        # Provide input
                        if self.paddle_x is not None and self.ball_x is not None:
                            # If the paddle is in the same x-position as the ball, provide NO_MOVE
                            if self.paddle_x == self.ball_x:
                                vm.input_queue.put(NO_MOVE)
                            # If the paddle is in a higher x-position as the ball, provide LEFT (-1)
                            elif self.paddle_x > self.ball_x:
                                vm.input_queue.put(LEFT)
                            # Else, the paddle is in a lower x-position as the ball, provide RIGHT (1)
                            else:
                                vm.input_queue.put(RIGHT)
                        else:
                            vm.input_queue.put(NO_MOVE)
                        if VISUALIZE:
                            self.print_screen()
                except Exception as e:
                    print("=== EXCEPTION ===")
                    print("PC:", vm.pc)
                    print("Memory", vm.memory)
                    raise e

                # On 3x output, draw on screen
                if not vm.output_queue.empty() and screen_x is None:
                    screen_x = vm.output_queue.get()
                elif not vm.output_queue.empty() and screen_y is None:
                    screen_y = vm.output_queue.get()
                elif not vm.output_queue.empty() and tile_type is None:
                    tile_type = vm.output_queue.get()
                if screen_x is not None and screen_y is not None and tile_type is not None:
                    if INFO or DEBUG:
                        print("Output = {}".format((screen_x, screen_y, tile_type)))
                    if screen_x == -1 and screen_y == 0:
                        if VISUALIZE:
                            print("New score: {}".format(tile_type))
                        self.score = tile_type
                    else:
                        self.screen[(screen_y, screen_x)] = tile_type
                    screen_x, screen_y, tile_type = None, None, None

        yield self.score
