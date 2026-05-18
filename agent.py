class Agent:
    def __init__(self):
        # 시작 위치: 6x6 기준에서 실제 (1,1)은 row=4, col=1
        self.row = 4
        self.col = 1

        # 죽어도 유지되는 기억
        self.visited = set()
        self.safe_cells = {(4, 1)}
        self.danger_cells = set()

    def get_position(self):
        return self.row, self.col

    def reset_position(self):
        # 죽으면 위치만 초기화, 기억은 유지
        self.row = 4
        self.col = 1

    def remember_current_position(self):
        self.visited.add((self.row, self.col))
        self.safe_cells.add((self.row, self.col))

    def get_neighbors(self):
        # 상, 하, 좌, 우
        return [
            (self.row - 1, self.col),
            (self.row + 1, self.col),
            (self.row, self.col - 1),
            (self.row, self.col + 1)
        ]

    def reasoning(self, percepts, world):
        self.remember_current_position()

        neighbors = self.get_neighbors()

        # 현재 위치에서 Breeze나 Stench가 없으면 주변은 안전하다고 판단
        if "Breeze" not in percepts and "Stench" not in percepts:
            for cell in neighbors:
                r, c = cell
                if world[r][c] != "wall":
                    self.safe_cells.add(cell)

        # Breeze 또는 Stench가 있으면 주변 칸을 위험 후보로 저장
        else:
            for cell in neighbors:
                r, c = cell
                if world[r][c] != "wall" and cell not in self.safe_cells:
                    self.danger_cells.add(cell)

    def choose_next_move(self, world):
        neighbors = self.get_neighbors()

        # 1순위: 방문하지 않은 안전한 칸
        for cell in neighbors:
            r, c = cell
            if (
                world[r][c] != "wall"
                and cell in self.safe_cells
                and cell not in self.visited
            ):
                return cell

        # 2순위: 이미 방문했지만 안전한 칸
        for cell in neighbors:
            r, c = cell
            if world[r][c] != "wall" and cell in self.safe_cells:
                return cell

        # 3순위: 어쩔 수 없으면 위험 후보가 아닌 칸
        for cell in neighbors:
            r, c = cell
            if (
                world[r][c] != "wall"
                and cell not in self.danger_cells
            ):
                return cell

        # 이동할 곳이 없으면 현재 위치 유지
        return self.row, self.col

    def move_to(self, row, col):
        self.row = row
        self.col = col