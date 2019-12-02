from days import AOCDay, day

DEBUG = False

def add(x, y):
    if DEBUG:
        print("add {} {} ".format(x, y), end="")
    return x + y

def mult(x, y):
    if DEBUG:
        print("mul {} {} ".format(x, y), end="")
    return x * y

INSTR_ADD = 1
INSTR_MUL = 2
INSTR_END = 99

@day(2)
class Day2(AOCDay):
    pc = 0
    memory = []
    initial_memory = []
    instr_set = {
        INSTR_ADD: add,
        INSTR_MUL: mult,
    }
    instr_set_debug = {
        INSTR_ADD: "add",
        INSTR_MUL: "mul",
        INSTR_END: "end",
    }

    def reset(self):
        self.memory = self.initial_memory.copy()

    def run_program(self):
        self.pc = 0
        instr = self.memory[self.pc]
        while instr != INSTR_END:
            if DEBUG:
                print("{}: {} @{} @{} => @{} / ".format(
                    self.pc, self.instr_set_debug[self.memory[self.pc]],
                    self.memory[self.pc+1], self.memory[self.pc+2], self.memory[self.pc+3]
                ), end="")
            result = self.instr_set[instr](self.memory[self.memory[self.pc + 1]], self.memory[self.memory[self.pc + 2]])
            self.memory[self.memory[self.pc + 3]] = result
            if DEBUG:
                print("=> {}".format(result))
            self.pc += 4
            instr = self.memory[self.pc]
        return self.memory[0]

    def common(self, input_data):
        self.memory = list(map(int, input_data.split(',')))
        self.initial_memory = self.memory.copy()

    def part1(self, input_data):
        self.memory[1] = 12
        self.memory[2] = 2
        yield self.run_program()


    def part2(self, input_data):
        for i in range(100):
            for j in range(100):
                self.memory[1] = i
                self.memory[2] = j

                if DEBUG:
                    print("noun: {}, verb {}".format(i, j))
                result = self.run_program()

                if result == 19690720:
                    yield (100 * i) + j
                    return
                else:
                    self.reset()
