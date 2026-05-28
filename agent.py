class Agent:
    def __init__(self):
        self.row = 4
        self.col = 1
        self.direction = "EAST"

        self.visited = set()
        self.safe_cells = {(1, 1)}

        self.no_pit_cells = {(1, 1)}
        self.no_wumpus_cells = {(1, 1)}

        self.possible_pit = set()
        self.possible_wumpus = set()

        self.confirmed_pit = set()
        self.confirmed_wumpus = set()
        self.danger_cells = set()

        self.breeze_cells = set()
        self.stench_cells = set()

        self.arrows = 3
        self.wumpus_destroyed = False

        self.has_glitter = False
        self.grab = False
        self.returning_home = False

        self.path_stack = []
        self.current_target = None

        self.move_history = []
        self.return_path = []

    def get_position(self):
        return self.row, self.col

    def get_direction(self):
        return self.direction

    def reset_position(self):
        self.row = 1
        self.col = 1
        self.direction = "SOUTH"

        self.path_stack = []
        self.current_target = None
        self.move_history = []
        self.return_path = []
        self.returning_home = False

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
        previous_position = (self.row, self.col)

        self.row, self.col = self.get_forward_position()
        current_position = (self.row, self.col)

        if self.returning_home:
            if self.return_path and current_position == self.return_path[0]:
                self.return_path.pop(0)
        else:
            self.move_history.append(previous_position)

        self.current_target = None

    def get_neighbors(self, row=None, col=None):
        if row is None:
            row = self.row
        if col is None:
            col = self.col

        return [
            (row - 1, col),
            (row, col + 1),
            (row + 1, col),
            (row, col - 1)
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

        if "Breeze" not in percepts:
            for cell in neighbors:
                self.no_pit_cells.add(cell)
        else:
            self.breeze_cells.add(current)

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

        if not self.wumpus_destroyed:
            wumpus_candidate_sets = []

            for stench_cell in self.stench_cells:
                candidates = set()

                for cell in self.get_valid_neighbors(stench_cell[0], stench_cell[1], world):
                    if (
                        cell not in self.safe_cells
                        and cell not in self.no_wumpus_cells
                        and cell not in self.confirmed_pit
                    ):
                        candidates.add(cell)

                if candidates:
                    wumpus_candidate_sets.append(candidates)
                    self.possible_wumpus.update(candidates)

            # 여러 Stench 정보의 교집합으로 Wumpus 위치 확정
            if wumpus_candidate_sets:
                common_wumpus = set.intersection(*wumpus_candidate_sets)

                if len(common_wumpus) == 1:
                    wumpus_cell = next(iter(common_wumpus))
                    self.confirmed_wumpus.add(wumpus_cell)
                    self.safe_cells.discard(wumpus_cell)
                    self.possible_wumpus.discard(wumpus_cell)

        pit_candidate_sets = []

        for breeze_cell in self.breeze_cells:
            candidates = set()

            for cell in self.get_valid_neighbors(breeze_cell[0], breeze_cell[1], world):
                if (
                    cell not in self.safe_cells
                    and cell not in self.no_pit_cells
                    and cell not in self.confirmed_wumpus
                ):
                    candidates.add(cell)

            if candidates:
                pit_candidate_sets.append(candidates)
                self.possible_pit.update(candidates)

        # 여러 Breeze 정보의 교집합으로 Pit 위치 확정
        if pit_candidate_sets:
            common_pit = set.intersection(*pit_candidate_sets)

            if len(common_pit) == 1:
                pit_cell = next(iter(common_pit))
                self.confirmed_pit.add(pit_cell)
                self.safe_cells.discard(pit_cell)
                self.possible_pit.discard(pit_cell)

        self.possible_wumpus -= self.confirmed_pit
        self.possible_pit -= self.confirmed_wumpus

        if self.wumpus_destroyed:
            self.possible_wumpus.clear()
            self.confirmed_wumpus.clear()

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
        self.wumpus_destroyed = True

        # Wumpus 제거 후 해당 칸은 더 이상 위험하지 않음
        for cell in self.confirmed_wumpus:
            self.safe_cells.add(cell)
            self.no_wumpus_cells.add(cell)
            self.danger_cells.discard(cell)

        self.confirmed_wumpus.clear()
        self.possible_wumpus.clear()
        self.stench_cells.clear()

        self.danger_cells = self.confirmed_pit | self.possible_pit

    def is_wumpus_in_front(self):
        if (
            not self.confirmed_wumpus
            or self.wumpus_destroyed
            or self.arrows == 0
        ):
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

            if r <= 0 or r >= 5 or c <= 0 or c >= 5:
                return False

            if (r, c) in self.confirmed_wumpus:
                return True

    def get_direction_to_wumpus(self):
        if not self.confirmed_wumpus or self.wumpus_destroyed:
            return None

        wr, wc = next(iter(self.confirmed_wumpus))

        if self.row == wr:
            if wc < self.col:
                return "WEST"
            return "EAST"

        if self.col == wc:
            if wr < self.row:
                return "NORTH"
            return "SOUTH"

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

    def find_shortest_safe_path(self, start, goal, world):
        queue = [(start, [])]
        visited = {start}

        while queue:
            current, path = queue.pop(0)

            if current == goal:
                return path

            row, col = current

            for neighbor in self.get_valid_neighbors(row, col, world):
                if neighbor in visited:
                    continue

                # 복귀는 실제 방문했던 칸만 사용
                if neighbor not in self.visited and neighbor != goal:
                    continue

                if neighbor in self.danger_cells:
                    continue

                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

        return []

    def prepare_return_home(self, world):
        self.grab = True
        self.returning_home = True

        start = (self.row, self.col)
        goal = (4, 1)

        # Gold 획득 후에는 안전 칸 기준 최단 경로로 복귀
        shortest_path = self.find_shortest_safe_path(start, goal, world)

        if shortest_path:
            self.return_path = shortest_path
        else:
            self.return_path = list(reversed(self.move_history))

        self.current_target = None
        self.path_stack = []

    def choose_target_cell(self, world):
        current = (self.row, self.col)

        if self.returning_home:
            if self.return_path:
                self.current_target = self.return_path[0]
                return self.current_target

            return None

        if (
            self.current_target is not None
            and self.is_adjacent(self.current_target)
            and self.current_target in self.safe_cells
            and self.current_target not in self.danger_cells
        ):
            return self.current_target

        # DFS: 안전한 미방문 칸 우선 탐색
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

        # DFS Backtracking
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

    def choose_action(self, target, percepts, world):
        if self.grab and (self.row, self.col) == (4, 1):
            return "Climb"

        if self.has_glitter and not self.grab:
            return "Grab"

        right_turn = {
            "NORTH": "EAST",
            "EAST": "SOUTH",
            "SOUTH": "WEST",
            "WEST": "NORTH"
        }

        # 현재 위치에서 Stench를 느끼고 Wumpus 위치가 확정되면
        # DFS 이동보다 Shoot 조준을 우선 수행
        if (
            "Stench" in percepts
            and self.arrows > 0
            and not self.wumpus_destroyed
            and self.confirmed_wumpus
        ):
            if self.is_wumpus_in_front():
                return "Shoot"

            shoot_dir = self.get_direction_to_wumpus()

            if shoot_dir is not None:
                if right_turn[self.direction] == shoot_dir:
                    return "TurnRight"

                return "TurnLeft"

        # Shoot 조건이 아니면 DFS 목표 칸으로 이동
        if target is not None:
            target_direction = self.get_direction_to_target(target)

            if self.direction == target_direction:
                return "GoForward"

            if right_turn[self.direction] == target_direction:
                return "TurnRight"

            return "TurnLeft"

        return None