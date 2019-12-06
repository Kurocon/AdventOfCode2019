from days import AOCDay, day


class TreeNode:
    parent = None
    parent_str = ""
    name = ""
    children = []

    def __init__(self, name, parent_str):
        self.name = name
        self.parent_str = parent_str

@day(6)
class Day6(AOCDay):
    test_input = """COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L"""
    test_input2 = """

COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L
K)YOU
I)SAN"""

    com = None
    nodes = {}

    def common(self, input_data):
        # input_data = self.test_input.split("\n")
        self.com = TreeNode("COM", None)
        self.nodes["COM"] = self.com
        for line in input_data:
            parent, child = line.split(")")
            self.nodes[child] = TreeNode(child, parent)
        for node in self.nodes.values():
            if node.parent_str:
                node.parent = self.nodes[node.parent_str]
            node.children = list(filter(lambda x: x.parent == node, self.nodes.values()))

    def part1(self, input_data):
        direct_orbits = 0
        indirect_orbits = 0
        for node in self.nodes.values():
            if node.parent:
                direct_orbits += 1
                parent = node.parent.parent
                while parent:
                    indirect_orbits += 1
                    parent = parent.parent
        yield direct_orbits + indirect_orbits


    def part2(self, input_data):
        you = self.nodes["YOU"]
        santa = self.nodes["SAN"]

        you_parents = []
        parent = you.parent
        while parent:
            you_parents.append(parent)
            parent = parent.parent

        santa_parents = []
        parent = santa.parent
        while parent:
            santa_parents.append(parent)
            parent = parent.parent

        common_parent = None
        for p in you_parents:
            if p in santa_parents:
                common_parent = p
                break

        yield you_parents.index(common_parent) + santa_parents.index(common_parent)