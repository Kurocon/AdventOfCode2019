from days import AOCDay, day

DEBUG = False

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

def i_input(pc, addrarg):
    _, addr = addrarg
    if DEBUG:
        print("/ inp {} ".format(addr))
    value = pc.inputs[0]
    pc.inputs = pc.inputs[1:]
    pc.memory[addr] = value

def output(pc, addrarg):
    addrmode, addr = addrarg
    if addrmode == MODE_POS:
        addr = pc.memory[addr]
    if DEBUG:
        print("/ out {} ".format(addr))
    pc.outputs.append(addr)

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

@day(5)
class Day5(AOCDay):
    pc = 0
    memory = []
    initial_memory = []
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

    def run_program(self):
        self.pc = 0
        instr = self.memory[self.pc]
        while instr != INSTR_END:
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
            instr_func(self, *instr_args)
            if pc_pre == self.pc:
                self.pc += 1 + instr_narg
            instr = self.memory[self.pc]
        return self.memory[0]

    def common(self, input_data):
        self.memory = list(map(int, input_data.split(',')))
        self.initial_memory = self.memory.copy()
        self.inputs = []
        self.outputs = []

    def part1(self, input_data):
        self.inputs = [1]
        self.run_program()
        yield self.outputs


    def part2(self, input_data):
        self.inputs = [5]
        self.run_program()
        yield self.outputs