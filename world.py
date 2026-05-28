class WumpusWorld:
    def __init__(self):
        self.size = 6

        self.EMPTY = "empty"
        self.WALL = "wall"
        self.WUMPUS = "wumpus"
        self.PIT = "pit"
        self.GOLD = "gold"

        self.SCREAM = False

        self.world = self.create_world()

    def create_world(self):
        world = []

        for row in range(self.size):
            line = []

            for col in range(self.size):
                if row == 0 or row == 5 or col == 0 or col == 5:
                    line.append(self.WALL)
                else:
                    line.append(self.EMPTY)

            world.append(line)

        world[4][4] = self.GOLD
        world[2][2] = self.WUMPUS
        world[3][3] = self.PIT

        return world

    def get_percepts(self, row, col):
        percepts = []

        directions = [
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1)
        ]

        for r, c in directions:
            if self.world[r][c] == self.WUMPUS:
                percepts.append("Stench")
            elif self.world[r][c] == self.PIT:
                percepts.append("Breeze")

        if self.world[row][col] == self.GOLD:
            percepts.append("Glitter")

        if self.SCREAM:
            percepts.append("Scream")
            self.SCREAM = False

        return percepts

    def shoot(self, row, col, direction):
        r, c = row, col

        while True:
            if direction == "NORTH":
                r -= 1
            elif direction == "SOUTH":
                r += 1
            elif direction == "WEST":
                c -= 1
            elif direction == "EAST":
                c += 1

            if self.world[r][c] == self.WALL:
                return False

            if self.world[r][c] == self.WUMPUS:
                self.world[r][c] = self.EMPTY
                self.SCREAM = True
                return True