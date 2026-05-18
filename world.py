class WumpusWorld:
    def __init__(self):
        self.size = 6

        self.EMPTY = "empty"
        self.WALL = "wall"
        self.WUMPUS = "wumpus"
        self.PIT = "pit"
        self.GOLD = "gold"

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

        # 객체 배치
        world[1][4] = self.GOLD
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

        return percepts