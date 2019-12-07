from queue import Queue
from typing import List

from days import AOCDay, day

DEBUG = False
INFO = False

def add(pc, xarg, yarg, addrarg):
    xmode, x = xarg
    ymode, y = yarg
    _, addr = addrarg
    if xmode == MODE_POS:
        x = pc.memory[x]
    if ymode == MODE_POS:
        y = pc.memory[y]

    if DEBUG:
        print("/ add {} {} ".format(x, y), end="")
    pc.memory[addr] = x + y
    if DEBUG:
        print("=> {}".format(pc.memory[addr]))

def mult(pc, xarg, yarg, addrarg):
    xmode, x = xarg
    ymode, y = yarg
    _, addr = addrarg
    if xmode == MODE_POS:
        x = pc.memory[x]
    if ymode == MODE_POS:
        y = pc.memory[y]

    if DEBUG:
        print("/ mul {} {} ".format(x, y), end="")
    pc.memory[addr] = x * y
    if DEBUG:
        print("=> {}".format(pc.memory[addr]))

def i_input(pc: 'Amplifier', addrarg):
    _, addr = addrarg
    if DEBUG:
        print("/ inp {} ".format(addr))
    if pc.input_queue.empty():
        if INFO or DEBUG:
            print("Waiting for input...")
        return True
    else:
        value = pc.input_queue.get()
        pc.memory[addr] = value
    return False

def output(pc: 'Amplifier', addrarg):
    addrmode, addr = addrarg
    if addrmode == MODE_POS:
        addr = pc.memory[addr]
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
    if addrmode == MODE_POS:
        addr = pc.memory[addr]
    if DEBUG:
        print("/ jit {} => {} ".format(x, addr))
    if x != 0:
        pc.pc = addr

def jump_if_false(pc, xarg, addrarg):
    xmode, x = xarg
    addrmode, addr = addrarg
    if xmode == MODE_POS:
        x = pc.memory[x]
    if addrmode == MODE_POS:
        addr = pc.memory[addr]
    if DEBUG:
        print("/ jif {} => {} ".format(x, addr))
    if x == 0:
        pc.pc = addr

def less_than(pc, xarg, yarg, addrarg):
    xmode, x = xarg
    ymode, y = yarg
    _, addr = addrarg
    if xmode == MODE_POS:
        x = pc.memory[x]
    if ymode == MODE_POS:
        y = pc.memory[y]
    if DEBUG:
        print("/ lt {} {} => {} ".format(x, y, addr))
    if x < y:
        pc.memory[addr] = 1
    else:
        pc.memory[addr] = 0

def equals(pc, xarg, yarg, addrarg):
    xmode, x = xarg
    ymode, y = yarg
    _, addr = addrarg
    if xmode == MODE_POS:
        x = pc.memory[x]
    if ymode == MODE_POS:
        y = pc.memory[y]
    if DEBUG:
        print("/ eq {} {} => {} ".format(x, y, addr))
    if x == y:
        pc.memory[addr] = 1
    else:
        pc.memory[addr] = 0


INSTR_ADD = 1
INSTR_MUL = 2
INSTR_INP = 3
INSTR_OUT = 4
INSTR_JIT = 5
INSTR_JIF = 6
INSTR_LT = 7
INSTR_EQ = 8
INSTR_END = 99

MODE_POS = 0
MODE_IMM = 1


class Amplifier:
    pc = 0
    memory = []
    initial_memory = []
    input_queue: Queue = None
    output_queue: Queue = None
    waiting = False
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

        INSTR_END: (lambda: None, 0, "end"),
    }

    def reset(self):
        self.memory = self.initial_memory.copy()
        while not self.input_queue.empty():
            self.input_queue.get()
        while not self.output_queue.empty():
            self.output_queue.get()
        self.waiting = False
        self.pc = 0

    def initialize(self):
        self.pc = 0

    def run_instruction(self):
        instr = self.memory[self.pc]
        if self.waiting and not self.input_queue.empty():
            if INFO or DEBUG:
                print("Got input!")
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
                    mode = "I" if instr_modes[i] == MODE_IMM else "@"
                    print("{}{} ".format(mode, self.memory[self.pc + 1 + i]), end="")

            instr_args = [(instr_modes[i], self.memory[self.pc + 1 + i]) for i in range(instr_narg)]

            pc_pre = self.pc
            res = instr_func(self, *instr_args)
            if res:
                self.waiting = True
            else:
                if pc_pre == self.pc:
                    self.pc += 1 + instr_narg
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


@day(7)
class Day7(AOCDay):
    amplifiers: List[Amplifier] = []

    def common(self, input_data):
        self.memory = list(map(int, input_data.split(',')))
        first_input = None
        prev_out = None
        self.amplifiers = []
        for i in range(5):
            amp = Amplifier()
            amp.input_queue = prev_out if prev_out is not None else Queue()
            if first_input is None:
                first_input = amp.input_queue
            amp.output_queue = Queue()
            prev_out = amp.output_queue
            amp.memory = self.memory.copy()
            amp.initial_memory = self.memory.copy()
            self.amplifiers.append(amp)

    def part1(self, input_data):
        max_inputs = None
        max_result = None
        for a in range(5):
            for b in filter(lambda x: x not in [a], range(5)):
                for c in filter(lambda x: x not in [a, b], range(5)):
                    for d in filter(lambda x: x not in [a, b, c], range(5)):
                        for e in filter(lambda x: x not in [a, b, c, d], range(5)):
                            phases = [a, b, c, d, e]
                            if INFO or DEBUG:
                                print("-- Phases {} --".format(phases))
                            for i in range(5):
                                self.amplifiers[i].input_queue.put(phases[i])
                            self.amplifiers[0].input_queue.put(0)
                            for i in range(5):
                                if INFO or DEBUG:
                                    print("Running amplifier {}".format(i))
                                self.amplifiers[i].run_program()
                            output = []
                            while not self.amplifiers[-1].output_queue.empty():
                                output.append(self.amplifiers[-1].output_queue.get())
                            if max_result is None or output[0] > max_result:
                                max_result = output[0]
                                max_inputs = [a,b,c,d,e]
        if INFO or DEBUG:
            print("Max output is for phases {}".format(max_inputs))
        yield max_result

    def part2(self, input_data):
        max_inputs = None
        max_result = None

        self.amplifiers[0].input_queue = self.amplifiers[-1].output_queue

        for a in range(5, 10):
            for b in filter(lambda x: x not in [a], range(5, 10)):
                for c in filter(lambda x: x not in [a, b], range(5, 10)):
                    for d in filter(lambda x: x not in [a, b, c], range(5, 10)):
                        for e in filter(lambda x: x not in [a, b, c, d], range(5, 10)):
                            phases = [a, b, c, d, e]
                            if INFO or DEBUG:
                                print("-- Phases {} --".format(phases))
                            for i in range(5):
                                self.amplifiers[i].reset()
                            for i in range(5):
                                self.amplifiers[i].input_queue.put(phases[i])
                            self.amplifiers[0].input_queue.put(0)
                            states = [False, False, False, False, False]
                            if INFO or DEBUG:
                                print("Running amplifiers...")
                            while not all(states):
                                for i in range(5):
                                    states[i] = self.amplifiers[i].run_instruction()
                            output = []
                            while not self.amplifiers[-1].output_queue.empty():
                                output.append(self.amplifiers[-1].output_queue.get())
                            if INFO or DEBUG:
                                print("Output = {}".format(output))
                            if max_result is None or output[0] > max_result:
                                max_result = output[0]
                                max_inputs = [a,b,c,d,e]
        if INFO or DEBUG:
            print("Max output is for phases {}".format(max_inputs))
        yield max_result
