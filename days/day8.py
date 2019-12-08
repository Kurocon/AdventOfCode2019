from collections import Counter

from days import AOCDay, day


@day(8)
class Day8(AOCDay):
    test_input = """123456789012"""
    test_input2 = """0222112222120000"""
    width = 25
    height = 6

    BLACK = "0"
    WHITE = "1"
    TRANSPARENT = "2"

    image_data = []
    final_image = []

    def common(self, input_data):
        self.image_data = []
        i = 0
        layer = -1
        while i < len(input_data):
            layer += 1
            self.image_data.append([])
            for y in range(self.height):
                self.image_data[layer].append([])
                for x in range(self.width):
                    self.image_data[-1][-1].append(input_data[i])
                    i += 1

    def part1(self, input_data):
        fewest_zeroes = None
        fewest_layer = None
        for i, layer in enumerate(self.image_data):
            layer = list("".join("".join(line) for line in layer))
            c = Counter(layer)
            amount = c.get("0", 0)
            if fewest_zeroes is None or amount < fewest_zeroes:
                print("new best layer {} with {} zeroes".format(i, fewest_zeroes))
                fewest_zeroes = amount
                fewest_layer = c
        print("has {} ones and {} twos".format(fewest_layer.get("1"), fewest_layer.get("0")))
        yield fewest_layer.get("1", 0) * fewest_layer.get("2", 0)

    def part2(self, input_data):
        # Generate empty image
        for y in range(self.height):
            self.final_image.append([])
            for x in range(self.width):
                self.final_image[-1].append(self.TRANSPARENT)

        for y in range(self.height):
            for x in range(self.width):
                for layer in self.image_data:
                    if self.final_image[y][x] == self.TRANSPARENT:
                        if layer[y][x] != self.TRANSPARENT:
                            self.final_image[y][x] = layer[y][x]
                            break

        yield "\n".join("".join(x) for x in self.final_image).replace("0", " ").replace("1", "#").replace("2", " ")
