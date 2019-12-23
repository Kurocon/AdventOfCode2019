from days import AOCDay, day
import networkx as nx

DEBUG = False

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MAZE = ".#"
OUTER = 0
INNER = 1
NEIGHBOURS = [(-1, 0), (0, -1), (1, 0), (0, 1)]

@day(20)
class Day20(AOCDay):
    test_input = """         A           
         A           
  #######.#########  
  #######.........#  
  #######.#######.#  
  #######.#######.#  
  #######.#######.#  
  #####  B    ###.#  
BC...##  C    ###.#  
  ##.##       ###.#  
  ##...DE  F  ###.#  
  #####    G  ###.#  
  #########.#####.#  
DE..#######...###.#  
  #.#########.###.#  
FG..#########.....#  
  ###########.#####  
             Z       
             Z       """.split("\n")
    test_input2 = """                   A               
                   A               
  #################.#############  
  #.#...#...................#.#.#  
  #.#.#.###.###.###.#########.#.#  
  #.#.#.......#...#.....#.#.#...#  
  #.#########.###.#####.#.#.###.#  
  #.............#.#.....#.......#  
  ###.###########.###.#####.#.#.#  
  #.....#        A   C    #.#.#.#  
  #######        S   P    #####.#  
  #.#...#                 #......VT
  #.#.#.#                 #.#####  
  #...#.#               YN....#.#  
  #.###.#                 #####.#  
DI....#.#                 #.....#  
  #####.#                 #.###.#  
ZZ......#               QG....#..AS
  ###.###                 #######  
JO..#.#.#                 #.....#  
  #.#.#.#                 ###.#.#  
  #...#..DI             BU....#..LF
  #####.#                 #.#####  
YN......#               VT..#....QG
  #.###.#                 #.###.#  
  #.#...#                 #.....#  
  ###.###    J L     J    #.#.###  
  #.....#    O F     P    #.#...#  
  #.###.#####.#.#####.#####.###.#  
  #...#.#.#...#.....#.....#.#...#  
  #.#####.###.###.#.#.#########.#  
  #...#.#.....#...#.#.#.#.....#.#  
  #.###.#####.###.###.#.#.#######  
  #.#.........#...#.............#  
  #########.###.###.#############  
           B   J   C               
           U   P   P               """.split("\n")
    test_input3 = """             Z L X W       C                 
             Z P Q B       K                 
  ###########.#.#.#.#######.###############  
  #...#.......#.#.......#.#.......#.#.#...#  
  ###.#.#.#.#.#.#.#.###.#.#.#######.#.#.###  
  #.#...#.#.#...#.#.#...#...#...#.#.......#  
  #.###.#######.###.###.#.###.###.#.#######  
  #...#.......#.#...#...#.............#...#  
  #.#########.#######.#.#######.#######.###  
  #...#.#    F       R I       Z    #.#.#.#  
  #.###.#    D       E C       H    #.#.#.#  
  #.#...#                           #...#.#  
  #.###.#                           #.###.#  
  #.#....OA                       WB..#.#..ZH
  #.###.#                           #.#.#.#  
CJ......#                           #.....#  
  #######                           #######  
  #.#....CK                         #......IC
  #.###.#                           #.###.#  
  #.....#                           #...#.#  
  ###.###                           #.#.#.#  
XF....#.#                         RF..#.#.#  
  #####.#                           #######  
  #......CJ                       NM..#...#  
  ###.#.#                           #.###.#  
RE....#.#                           #......RF
  ###.###        X   X       L      #.#.#.#  
  #.....#        F   Q       P      #.#.#.#  
  ###.###########.###.#######.#########.###  
  #.....#...#.....#.......#...#.....#.#...#  
  #####.#.###.#######.#######.###.###.#.#.#  
  #.......#.......#.#.#.#.#...#...#...#.#.#  
  #####.###.#####.#.#.#.#.###.###.#.###.###  
  #.......#.....#.#...#...............#...#  
  #############.#.#.###.###################  
               A O F   N                     
               A A D   M                     """.split("\n")
    grid = {}
    gridsize = None
    outer_or_inner = {}
    graph = None

    def common(self, input_data):
        # input_data = self.test_input3
        self.grid = {}
        self.outer_or_inner = {}
        self.graph = None
        for y, line in enumerate(input_data):
            for x, char in enumerate(line):
                if char != " ":
                    self.grid[(x, y)] = char
        self.gridsize = (len(input_data[0]), len(input_data))
        if DEBUG:
            self.display()
        self.parse_portal_names()

    def display(self):
        for y in range(self.gridsize[1]):
            for x in range(self.gridsize[0]):
                print(self.grid.get((x, y), " "), end="")
            print("")

    def generate_coordinates(self):
        for y in range(self.gridsize[1]):
            for x in range(self.gridsize[0]):
                yield x, y

    def get_neighbors(self, x, y):
        return [(x + n[0], y + n[1]) for n in NEIGHBOURS]

    def parse_portal_names(self):
        midx, midy = self.gridsize[0] // 2, self.gridsize[1] // 2
        self.outer_or_inner = {}
        for x, y in self.generate_coordinates():
            val = self.grid.get((x, y), None)
            if val is None or val not in LETTERS:
                continue

            neigh_l, neigh_u, neigh_r, neigh_d = [self.grid.get(n, None) for n in self.get_neighbors(x, y)]
            # If we got the bottom letter of a vertical pair on the top edge
            if neigh_u is not None and neigh_u in LETTERS and neigh_d is not None and neigh_d in MAZE:
                name = neigh_u + val
                del self.grid[(x, y - 1)]
                self.grid[(x, y)] = name
                self.outer_or_inner[(x, y)] = OUTER if y < midy else INNER
            # If the top letter of vertical pair on the bottom edge
            if neigh_d is not None and neigh_d in LETTERS and neigh_u is not None and neigh_u in MAZE:
                name = val + neigh_d
                del self.grid[(x, y + 1)]
                self.grid[(x, y)] = name
                self.outer_or_inner[(x, y)] = INNER if y < midy else OUTER
            # If the right letter of horizontal pair on the left edge
            if neigh_l is not None and neigh_l in LETTERS and neigh_r is not None and neigh_r in MAZE:
                name = neigh_l + val
                del self.grid[(x - 1, y)]
                self.grid[(x, y)] = name
                self.outer_or_inner[(x, y)] = OUTER if x < midx else INNER
            # If the left letter of horizontal pair on the right edge
            if neigh_r is not None and neigh_r in LETTERS and neigh_l is not None and neigh_l in MAZE:
                name = val + neigh_r
                del self.grid[(x + 1, y)]
                self.grid[(x, y)] = name
                self.outer_or_inner[(x, y)] = INNER if x < midx else OUTER

    def find_all(self, needle):
        for coords, value in self.grid.items():
            if value == needle:
                yield coords

    def find_open_space(self, coord):
        for neighbor in self.get_neighbors(coord[0], coord[1]):
            if self.grid.get(neighbor, None) == ".":
                return neighbor
        return None

    def get_start(self):
        return self.find_open_space(next(self.find_all("AA")))

    def get_end(self):
        return self.find_open_space(next(self.find_all("ZZ")))

    def get_other_portal(self, location, portal_location):
        portal_name = self.grid.get(portal_location, None)
        portals = self.find_all(portal_name)
        try:
            return [self.find_open_space(portal) for portal in portals if self.find_open_space(portal) != location][0]
        except IndexError:
            return None

    def get_graph(self):
        self.graph = nx.Graph()
        for x, y in self.generate_coordinates():
            if self.grid.get((x, y), None) != ".":
                continue
            self.graph.add_node((x, y))
            for neighbor in self.get_neighbors(x, y):
                if self.grid.get(neighbor, None) == ".":
                    self.graph.add_edge((x, y), neighbor)
                elif self.grid.get(neighbor, None) is not None and len(self.grid.get(neighbor, None)) == 2:
                    connected_space = self.get_other_portal((x, y), neighbor)
                    if connected_space is not None:
                        if DEBUG:
                            print("Connected {} ({}) to {} ({})".format((x, y), self.grid[(x, y)], neighbor, self.grid[neighbor]))
                        self.graph.add_edge((x, y), connected_space)
                    else:
                        if DEBUG:
                            print("Could not find connection for {}".format(self.grid[neighbor]))

    def part1(self, input_data):
        if DEBUG:
            self.display()
        self.get_graph()
        if DEBUG:
            self.display()
        start, end = self.get_start(), self.get_end()
        path = nx.shortest_path(self.graph, start, end)
        yield len(path) - 1

    def get_recursive_graph(self):
        self.graph = nx.Graph()
        max_levels = 30
        for x, y in self.generate_coordinates():
            if self.grid.get((x, y), None) != ".":
                continue
            for z in range(max_levels):
                self.graph.add_node(((x, y), z))
            for neighbor in self.get_neighbors(x, y):
                if self.grid.get(neighbor, None) == ".":
                    for z in range(max_levels):
                        self.graph.add_edge(((x, y), z), (neighbor, z))
                elif self.grid.get(neighbor, None) is not None and len(self.grid.get(neighbor, None)) == 2:
                    inout = self.outer_or_inner[neighbor]
                    connected_space = self.get_other_portal((x, y), neighbor)
                    for z in range(max_levels):
                        # Outer portals on level 0 don't go anywhere
                        if z == 0 and inout == OUTER:
                            continue
                        # Inner portals on the maximum lavel go nowhere (to limit the search algorithm)
                        if z == (max_levels - 1) and inout == INNER:
                            continue
                        if connected_space is not None:
                            # Outer portals go one level lower
                            if inout == OUTER:
                                self.graph.add_edge(((x, y), z), (connected_space, z - 1))
                            # Inner portals go one level higher
                            elif inout == INNER:
                                self.graph.add_edge(((x, y), z), (connected_space, z + 1))
                            else:
                                if DEBUG:
                                    print("Could not find connection for {}".format(self.grid[neighbor]))

    def part2(self, input_data):
        if DEBUG:
            self.display()
        self.get_recursive_graph()
        if DEBUG:
            self.display()
        start, end = (self.get_start(), 0), (self.get_end(), 0)
        path = nx.shortest_path(self.graph, start, end)
        yield len(path) - 1
