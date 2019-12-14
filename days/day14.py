import math
import re
from collections import defaultdict
from typing import List, Tuple

from days import AOCDay, day

DEBUG = False

FUEL = "FUEL"
ORE = "ORE"

class Reaction:
    inputs: List[Tuple[int, 'Element']] = []
    outputs: Tuple[int, 'Element'] = None

class Element:
    name: str = None
    reaction_to_produce: Reaction = None

@day(14)
class Day14(AOCDay):
    test_input = """10 ORE => 10 A
1 ORE => 1 B
7 A, 1 B => 1 C
7 A, 1 C => 1 D
7 A, 1 D => 1 E
7 A, 1 E => 1 FUEL""".split("\n")
    test_input2 = """9 ORE => 2 A
8 ORE => 3 B
7 ORE => 5 C
3 A, 4 B => 1 AB
5 B, 7 C => 1 BC
4 C, 1 A => 1 CA
2 AB, 3 BC, 4 CA => 1 FUEL""".split("\n")
    test_input3 = """157 ORE => 5 NZVS
165 ORE => 6 DCFZ
44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL
12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ
179 ORE => 7 PSHF
177 ORE => 5 HKGWZ
7 DCFZ, 7 PSHF => 2 XJWVT
165 ORE => 2 GPVTF
3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT""".split("\n")
    test_input4 = """2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG
17 NVRVD, 3 JNWZP => 8 VPVL
53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL
22 VJHF, 37 MNCFX => 5 FWMGM
139 ORE => 4 NVRVD
144 ORE => 7 JNWZP
5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC
5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV
145 ORE => 6 MNCFX
1 NVRVD => 8 CXFTF
1 VJHF, 6 MNCFX => 4 RFSQX
176 ORE => 6 VJHF""".split("\n")
    test_input5 = """171 ORE => 8 CNZTR
7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL
114 ORE => 4 BHXH
14 VRPVC => 6 BMBT
6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL
6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT
15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW
13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW
5 BMBT => 4 WPTQ
189 ORE => 9 KTJDG
1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP
12 VRPVC, 27 CNZTR => 2 XDBXC
15 KTJDG, 12 BHXH => 5 XCVML
3 BHXH, 2 VRPVC => 7 MZWV
121 ORE => 7 VRPVC
7 XCVML => 6 RJRHP
5 BHXH, 4 VRPVC => 5 LTCX""".split("\n")

    LINE_RE = re.compile("(?P<inputs>(?:[0-9]+ [A-Z]+(?:, )?)+) => (?P<out_num>[0-9]+) (?P<out_elem>[A-Z]+)")
    INPUT_RE = re.compile("(?P<num>[0-9]+) (?P<elem>[A-Z]+)(?:, )?")

    elements = {}
    element_counts = defaultdict(int)
    element_stock = defaultdict(int)

    def common(self, input_data):
        # input_data = self.test_input5
        self.elements = {}
        self.element_counts = defaultdict(int)
        self.element_stock = defaultdict(int)

        # Add other reactions
        for line in input_data:
            line_match = self.LINE_RE.match(line)
            inputs = []
            out_num, out_elem = int(line_match.group("out_num")), line_match.group("out_elem")
            for in_match in self.INPUT_RE.finditer(line_match.group("inputs")):
                inputs.append((int(in_match.group("num")), in_match.group("elem")))
            reaction = Reaction()
            reaction.inputs = inputs
            reaction.outputs = (out_num, out_elem)
            elem = Element()
            elem.name = out_elem
            elem.reaction_to_produce = reaction
            self.elements[out_elem] = elem

    def get_requirements_to_make(self, target, amount):
        elem = self.elements[target]
        # Re-use elements that we already have
        reusable = min(amount, self.element_stock[target])
        if DEBUG and reusable:
            print("Used {} {} from storage".format(reusable, target))
        amount -= reusable
        self.element_stock[target] -= reusable
        amount_produced = math.ceil(amount / elem.reaction_to_produce.outputs[0]) * elem.reaction_to_produce.outputs[0]
        # Store amount needed for fuel
        self.element_counts[target] += amount
        # Store waste elements for re-use
        self.element_stock[target] += amount_produced - amount
        if DEBUG:
            print("Produced {} {} ({} for reaction, {} for storage)".format(amount_produced, target, amount, amount_produced - amount))
        if amount_produced > 0:
            for requirement in elem.reaction_to_produce.inputs:
                if requirement[1] != ORE:
                    self.get_requirements_to_make(requirement[1], requirement[0] * (amount_produced // elem.reaction_to_produce.outputs[0]))
                else:
                    self.element_counts[ORE] += requirement[0] * (amount_produced // elem.reaction_to_produce.outputs[0])
                    if DEBUG:
                        print("Mined {} ORE".format(requirement[0] * (amount_produced // elem.reaction_to_produce.outputs[0])))

    def minimum_ore_required(self, amount):
        self.element_counts = defaultdict(int)
        self.element_stock = defaultdict(int)
        self.get_requirements_to_make(FUEL, amount)
        return self.element_counts[ORE]

    def part1(self, input_data):
        yield self.minimum_ore_required(1)

    def part2(self, input_data):
        # Find ballpark bounds
        target = 1000000000000
        lower_bound = 0
        upper_bound = 1

        while self.minimum_ore_required(upper_bound) < target:
            lower_bound = upper_bound
            upper_bound = upper_bound * 2

        # Narrow the bounds until we found how much
        while lower_bound + 1 < upper_bound:
            mid = (lower_bound + upper_bound) // 2
            ore = self.minimum_ore_required(mid)
            if ore > target:
                upper_bound = mid
            elif ore < target:
                lower_bound = mid

        yield lower_bound