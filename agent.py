class Agent:
    def __init__(self):
        self.row = 4
        self.col = 1
        self.direction = "EAST"

        # 기억 정보
        self.visited = set()
        self.safe_cells = {(4, 1)}

        self.no_pit_cells = {(4, 1)}
        self.no_wumpus_cells = {(4, 1)}

        self.possible_pit = set()
        self.possible_wumpus = set()
        self.confirmed_pit = set()
        self.confirmed_wumpus = set()
        self.danger_cells = set()

        self.breeze_cells = set()
        self.stench_cells = set()

        # 화살 수 및 Wumpus 처치 여부
        self.arrows = 3
        self.wumpus_destroyed = False

        # Glitter 감지 여부
        self.has_glitter = False
        self.grab = False

        # DFS용 stack
        self.path_stack = []

        # 현재 이동 목표 칸
        self.current_target = None

    def get_position(self):
        return self.row, self.col

    def get_direction(self):
        return self.direction

    def reset_position(self):
        # 죽어도 기억은 유지, 위치와 방향만 초기화
        self.row = 4
        self.col = 1
        self.direction = "EAST"
        self.path_stack = []
        self.current_target = None

    def turn_left(self):
        directions = ["NORTH", "WEST", "SOUTH", "EAST"]
        index = directions.index(self.direction)
        self.direction = directions[(index + 1) % 4]

    def turn_right(self):
        directions = ["NORTH", "EAST", "SOUTH", "WEST"]
        index = directions.index(self.direction)
        self.direction = directions[(index + 1) % 4]

    def get_forward_position(self):
        if self.direction == "NORTH":
            return self.row - 1, self.col
        if self.direction == "SOUTH":
            return self.row + 1, self.col
        if self.direction == "WEST":
            return self.row, self.col - 1
        if self.direction == "EAST":
            return self.row, self.col + 1

    def go_forward(self):
        self.row, self.col = self.get_forward_position()
        self.current_target = None

    def get_neighbors(self, row=None, col=None):
        if row is None:
            row = self.row
        if col is None:
            col = self.col

        return [
            (row - 1, col),  # NORTH
            (row, col + 1),  # EAST
            (row + 1, col),  # SOUTH
            (row, col - 1)   # WEST
        ]

    def get_valid_neighbors(self, row, col, world):
        neighbors = []

        for r, c in self.get_neighbors(row, col):
            if world[r][c] != "wall":
                neighbors.append((r, c))

        return neighbors

    def is_adjacent(self, cell):
        return cell in self.get_neighbors(self.row, self.col)

    def remember_current_position(self):
        current = (self.row, self.col)

        self.visited.add(current)
        self.safe_cells.add(current)
        self.no_pit_cells.add(current)
        self.no_wumpus_cells.add(current)

        self.possible_pit.discard(current)
        self.possible_wumpus.discard(current)
        self.danger_cells.discard(current)

    def reasoning(self, percepts, world):
        current = (self.row, self.col)
        self.remember_current_position()

        self.has_glitter = "Glitter" in percepts
        if "Scream" in percepts:
            self.on_scream()

        neighbors = self.get_valid_neighbors(self.row, self.col, world)

        # Breeze가 없으면 주변에는 Pit이 없음
        if "Breeze" not in percepts:
            for cell in neighbors:
                self.no_pit_cells.add(cell)
        else:
            self.breeze_cells.add(current)

        # Stench가 없으면 주변에는 Wumpus가 없음
        if "Stench" not in percepts:
            for cell in neighbors:
                self.no_wumpus_cells.add(cell)
        else:
            self.stench_cells.add(current)

        self.update_candidates(world)
        self.update_safe_cells(world)

    def update_candidates(self, world):
        self.possible_pit.clear()
        self.possible_wumpus.clear()

        # Breeze를 느낀 칸들의 주변을 Pit 후보로 판단
        for breeze_cell in self.breeze_cells:
            for cell in self.get_valid_neighbors(breeze_cell[0], breeze_cell[1], world):
                if (
                    cell not in self.safe_cells
                    and cell not in self.no_pit_cells
                    and cell not in self.confirmed_pit
                ):
                    self.possible_pit.add(cell)

        # Stench를 느낀 칸들의 주변을 Wumpus 후보로 판단
        for stench_cell in self.stench_cells:
            for cell in self.get_valid_neighbors(stench_cell[0], stench_cell[1], world):
                if (
                    cell not in self.safe_cells
                    and cell not in self.no_wumpus_cells
                    and cell not in self.confirmed_wumpus
                ):
                    self.possible_wumpus.add(cell)

        # Stench 주변 후보가 하나뿐이면 Wumpus 위치 확정
        for stench_cell in self.stench_cells:
            candidates = [
                cell for cell in self.get_valid_neighbors(stench_cell[0], stench_cell[1], world)
                if cell not in self.no_wumpus_cells and cell not in self.confirmed_wumpus
            ]
            if len(candidates) == 1:
                self.confirmed_wumpus.add(candidates[0])
                self.safe_cells.discard(candidates[0])

        # Breeze 주변 후보가 하나뿐이면 Pit 위치 확정
        for breeze_cell in self.breeze_cells:
            candidates = [
                cell for cell in self.get_valid_neighbors(breeze_cell[0], breeze_cell[1], world)
                if cell not in self.no_pit_cells and cell not in self.confirmed_pit
            ]
            if len(candidates) == 1:
                self.confirmed_pit.add(candidates[0])
                self.safe_cells.discard(candidates[0])

        self.danger_cells = (
            self.confirmed_pit
            | self.confirmed_wumpus
            | self.possible_pit
            | self.possible_wumpus
        )

    def update_safe_cells(self, world):
        for row in range(1, 5):
            for col in range(1, 5):
                cell = (row, col)

                if (
                    cell in self.no_pit_cells
                    and cell in self.no_wumpus_cells
                    and cell not in self.confirmed_pit
                    and cell not in self.confirmed_wumpus
                ):
                    self.safe_cells.add(cell)
                    self.danger_cells.discard(cell)
                    self.possible_pit.discard(cell)
                    self.possible_wumpus.discard(cell)

    def on_scream(self):
        """Scream 퍼셉트 수신 시 Wumpus 관련 지식을 초기화한다."""
        self.wumpus_destroyed = True
        self.confirmed_wumpus.clear()
        self.possible_wumpus.clear()
        self.stench_cells.clear()
        self.danger_cells = self.confirmed_pit | self.possible_pit

    def is_wumpus_in_front(self):
        """현재 방향 직선 상에 confirmed_wumpus 위치가 있으면 True."""
        if not self.confirmed_wumpus or self.wumpus_destroyed or self.arrows == 0:
            return False
        r, c = self.row, self.col
        while True:
            if self.direction == "NORTH":
                r -= 1
            elif self.direction == "SOUTH":
                r += 1
            elif self.direction == "WEST":
                c -= 1
            elif self.direction == "EAST":
                c += 1
            if r < 0 or r > 4 or c < 0 or c > 4:
                return False
            if (r, c) in self.confirmed_wumpus:
                return True

    def get_direction_to_wumpus(self):
        """Wumpus와 같은 행 또는 열일 때 그 방향을 반환. 정렬 안 됐으면 None."""
        if not self.confirmed_wumpus or self.wumpus_destroyed:
            return None
        wr, wc = next(iter(self.confirmed_wumpus))
        if self.row == wr:
            return "WEST" if wc < self.col else "EAST"
        if self.col == wc:
            return "NORTH" if wr < self.row else "SOUTH"
        return None

    def mark_death_cell(self, row, col, reason):
        cell = (row, col)

        self.safe_cells.discard(cell)
        self.no_pit_cells.discard(cell)
        self.no_wumpus_cells.discard(cell)

        if reason == "pit":
            self.confirmed_pit.add(cell)
        elif reason == "wumpus":
            self.confirmed_wumpus.add(cell)

        self.danger_cells.add(cell)
        self.current_target = None
        self.path_stack = []

    def choose_target_cell(self, world):
        current = (self.row, self.col)

        # 금을 주웠다면 1, 4로
        if self.grab:
            self.current_target = [1, 4]
            return self.current_target

        # 이미 목표가 있고, 아직 인접한 안전 칸이면 유지
        if (
            self.current_target is not None
            and self.is_adjacent(self.current_target)
            and self.current_target in self.safe_cells
            and self.current_target not in self.danger_cells
        ):
            return self.current_target

        # DFS: 방문하지 않은 안전한 인접 칸 우선 선택
        for cell in self.get_neighbors():
            r, c = cell

            if (
                world[r][c] != "wall"
                and cell in self.safe_cells
                and cell not in self.visited
                and cell not in self.danger_cells
            ):
                self.path_stack.append(current)
                self.current_target = cell
                return cell

        # 갈 곳이 없으면 DFS stack을 이용해 이전 위치로 되돌아감
        while self.path_stack:
            back_cell = self.path_stack.pop()

            if (
                back_cell in self.safe_cells
                and back_cell not in self.danger_cells
                and self.is_adjacent(back_cell)
            ):
                self.current_target = back_cell
                return back_cell

        self.current_target = None
        return None

    def get_direction_to_target(self, target):
        target_row, target_col = target

        if target_row < self.row:
            return "NORTH"
        if target_row > self.row:
            return "SOUTH"
        if target_col < self.col:
            return "WEST"
        if target_col > self.col:
            return "EAST"

        return self.direction

    def choose_action(self, target):
        if self.has_glitter:
            return "Grab"

        right_turn = {
            "NORTH": "EAST",
            "EAST": "SOUTH",
            "SOUTH": "WEST",
            "WEST": "NORTH"
        }

        # Wumpus 확정 시 조준 및 발사 우선
        if self.arrows > 0 and not self.wumpus_destroyed and self.confirmed_wumpus:
            if self.is_wumpus_in_front():
                return "Shoot"
            shoot_dir = self.get_direction_to_wumpus()
            if shoot_dir is not None:
                if right_turn[self.direction] == shoot_dir:
                    return "TurnRight"
                return "TurnLeft"

        if target is None:
            return None

        target_direction = self.get_direction_to_target(target)

        if self.direction == target_direction:
            return "GoForward"

        if right_turn[self.direction] == target_direction:
            return "TurnRight"

        return "TurnLeft"