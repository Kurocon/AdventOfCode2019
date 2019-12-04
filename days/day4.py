from collections import defaultdict

from days import AOCDay, day


@day(4)
class Day4(AOCDay):
    minimum = None
    maximum = None

    def common(self, input_data):
        self.minimum, self.maximum = [int(x) for x in input_data.split("-")]

    def part1(self, input_data):
        def check(pw):
            try:
                # Has to be at least a repeat number
                assert len(set(pw)) < len(pw)
                # Only increasing numbers
                assert "".join(sorted(pw)) == pw
            except AssertionError:
                return 0
            return 1

        yield sum(check(str(pw)) for pw in range(self.minimum, self.maximum))


    def part2(self, input_data):
        def check(pw):
            try:
                # Has to be at least a repeat number
                assert len(set(pw)) < len(pw)
                # Has to have a spot with only two same digits next to each other
                counter = defaultdict(int)
                for x in pw:
                    counter[x] += 1
                assert 2 in counter.values()
                # Only increasing numbers
                assert "".join(sorted(pw)) == pw
            except AssertionError:
                return 0
            return 1

        yield sum(check(str(pw)) for pw in range(self.minimum, self.maximum))
