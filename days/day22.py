from typing import List

from days import AOCDay, day

DEBUG = True

@day(22)
class Day22(AOCDay):
    test_input = """deal into new stack
cut -2
deal with increment 7
cut 8
cut -4
deal with increment 7
cut 3
deal with increment 9
deal with increment 3
cut -1""".split("\n")

    cards = list(range(10007))

    instructions = []
    instructionset = {}

    def deal_into_new_stack(self, cards: List[int], n: int):
        return list(reversed(cards))

    def cut(self, cards: List[int], n: int):
        return cards[n:] + cards[:n]

    def deal_with_increment(self, cards: List[int], n: int):
        new_cards: List[int] = [-1 for _ in range(len(cards))]
        for i in range(len(cards)):
            new_cards[(i * n) % len(cards)] = cards[i]
        return new_cards

    def common(self, input_data):
        # input_data = self.test_input
        self.cards = list(range(10007))
        # self.cards = list(range(10))
        self.instructions = []
        self.instructionset = {
            'dealnew': self.deal_into_new_stack,
            'deali': self.deal_with_increment,
            'cut': self.cut,
        }
        for line in input_data:
            line = line.split(" ")
            if line[0] == "deal":
                if line[2] == "increment":
                    n = int(line[3])
                    self.instructions.append(["deali", n])
                elif line[2] == "new":
                    self.instructions.append(["dealnew", 0])
                else:
                    raise ValueError("Unknown instruction {}".format(" ".join(line)))
            elif line[0] == "cut":
                n = int(line[1])
                self.instructions.append(["cut", n])
            else:
                raise ValueError("Unknown instruction {}".format(" ".join(line)))

    def part1(self, input_data):
        for instruction in self.instructions:
            self.cards = self.instructionset[instruction[0]](self.cards, instruction[1])
        yield self.cards.index(2019)

    def deal_into_new_stack_lcg(self, a, b, k, N):
        return -a, b - a

    def cut_lcg(self, a, b, k, N):
        return a, b + k * a

    def deal_with_increment_lcg(self, a, b, k, N):
        return a * pow(k, -1, N), b

    def card_at_pos(self, a, b, position, num_repetitions, deck_size):
        return (
            pow(a, num_repetitions, deck_size) * position +
            (1 - pow(a, num_repetitions, deck_size)) * pow(1 - a, -1, deck_size) * b
        ) % deck_size

    def part2(self, input_data):
        # https://en.wikipedia.org/wiki/Linear_congruential_generator
        # https://www.nayuki.io/page/fast-skipping-in-a-linear-congruential-generator
        self.instructionset = {
            'dealnew': self.deal_into_new_stack_lcg,
            'deali': self.deal_with_increment_lcg,
            'cut': self.cut_lcg,
        }

        deck_size = 119315717514047
        num_repetitions = 101741582076661

        a, b = 1, 0
        for instruction in self.instructions:
            a, b = self.instructionset[instruction[0]](a, b, instruction[1], deck_size)
            a, b = a % deck_size, b % deck_size

        yield self.card_at_pos(a, b, 2020, num_repetitions, deck_size)
