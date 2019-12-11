from days import AOCDay, day

DEBUG = True

@day(0)
class DayTemplate(AOCDay):
    test_input = """""""".split("\n")

    def common(self, input_data):
        input_data = self.test_input

    def part1(self, input_data):
        pass

    def part2(self, input_data):
        pass
