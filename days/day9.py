from queue import Queue
from typing import List
from defaultlist import defaultlist

from days import AOCDay, day

DEBUG = False
INFO = False

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


@day(9)
class Day9(AOCDay):
    virtual_machines: List[VirtualMachine] = []
    test_input = """109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99"""
    test_input2 = """1102,34915192,34915192,7,4,7,99,0"""
    test_input3 = """104,1125899906842624,99"""
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

    def part1(self, input_data):
        vm_inputs = [[1]]

        for i, vm_input in enumerate(vm_inputs):
            if INFO or DEBUG:
                print("-- Input {} --".format(vm_input))

            for j in vm_input:
                self.virtual_machines[i].input_queue.put(j)

        states = [False for _ in self.virtual_machines]
        if INFO or DEBUG:
            print("Running virtual machines...")
        while not all(states):
            for i, vm in enumerate(self.virtual_machines):
                try:
                    states[i] = vm.run_instruction()
                except Exception as e:
                    print("=== EXCEPTION ===")
                    print("PC:", vm.pc)
                    print("Memory", vm.memory)
                    raise e

        outputs = []

        for vm in self.virtual_machines:
            output = []
            while not vm.output_queue.empty():
                output.append(vm.output_queue.get())
            outputs.append(output)

        if INFO or DEBUG:
            for i, output in enumerate(outputs):
                print("Output for virtual machine {}".format(i))
                print(output)

        yield outputs[0][0]

    def part2(self, input_data):
        vm_inputs = [[2]]

        for i, vm_input in enumerate(vm_inputs):
            if INFO or DEBUG:
                print("-- Input {} --".format(vm_input))

            for j in vm_input:
                self.virtual_machines[i].input_queue.put(j)

        states = [False for _ in self.virtual_machines]
        if INFO or DEBUG:
            print("Running virtual machines...")
        while not all(states):
            for i, vm in enumerate(self.virtual_machines):
                try:
                    states[i] = vm.run_instruction()
                except Exception as e:
                    print("=== EXCEPTION ===")
                    print("PC:", vm.pc)
                    print("Memory", vm.memory)
                    raise e

        outputs = []

        for vm in self.virtual_machines:
            output = []
            while not vm.output_queue.empty():
                output.append(vm.output_queue.get())
            outputs.append(output)

        if INFO or DEBUG:
            for i, output in enumerate(outputs):
                print("Output for virtual machine {}".format(i))
                print(output)

        yield outputs[0][0]
