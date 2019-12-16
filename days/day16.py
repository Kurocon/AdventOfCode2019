from days import AOCDay, day

DEBUG = False

@day(16)
class Day16(AOCDay):
    test_input = """12345678"""
    test_input2 = "80871224585914546619083218645595"
    test_input3 = "19617804207202209144916044189917"
    test_input4 = "69317163492948606335995924319873"
    test_input5 = "03036732577212944063491565474664"
    input_data = []

    def common(self, input_data):
        # input_data = self.test_input4
        self.input_data = list(map(int, list(input_data)))

    def phase(self, data):
        old_data = data[:]
        for i in range(len(old_data) // 2 + 1):
            j = i
            k = i + 1
            sum_data = 0
            while j < len(old_data):
                sum_data += sum(old_data[j:j + k])
                j += 2 * k
                sum_data -= sum(old_data[j:j + k])
                j += 2 * k
            data[i] = abs(sum_data) % 10
        for i in range(len(old_data) - 2, len(old_data) // 2, -1):
            data[i] = (data[i] + data[i + 1]) % 10
        return data

    def part1(self, input_data):
        data = self.input_data
        for i in range(100):
            data = self.phase(data)
            if DEBUG:
                print(data)
        yield "".join(list(map(str, data)))[:8]

    def part2(self, input_data):
        skip = int("".join(map(str, self.input_data[:7])))
        new_input = (self.input_data * 10000)[skip:]
        length = len(new_input)
        for i in range(100):
            for i in range(length - 2, -1, -1):
                new_input[i] = (new_input[i] + new_input[i + 1]) % 10
        yield "".join(map(str, new_input))[:8]
