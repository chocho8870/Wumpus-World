import tkinter as tk
from PIL import Image, ImageTk
from world import WumpusWorld
from agent import Agent

window = tk.Tk()
window.title("Wumpus World")

GRID_SIZE = 6
CELL_SIZE = 100
IMAGE_SIZE = 70

game = WumpusWorld()
agent = Agent()

canvas = tk.Canvas(
    window,
    width=GRID_SIZE * CELL_SIZE,
    height=GRID_SIZE * CELL_SIZE,
    bg="white",
    highlightthickness=0
)
canvas.pack()

info_label = tk.Label(
    window,
    text="자동 실행 버튼을 누르면 DFS 기반으로 Action을 선택합니다.",
    font=("Arial", 12)
)
info_label.pack()


def load_image(path):
    image = Image.open(path)
    image = image.resize((IMAGE_SIZE, IMAGE_SIZE))
    return ImageTk.PhotoImage(image)


agent_img = load_image("images/agent.png")
gold_img = load_image("images/gold.png")
wumpus_img = load_image("images/wumpus.png")
pit_img = load_image("images/pit.png")

image_map = {
    "gold": gold_img,
    "wumpus": wumpus_img,
    "pit": pit_img
}

direction_symbol = {
    "NORTH": "↑",
    "SOUTH": "↓",
    "WEST": "←",
    "EAST": "→"
}


def make_percept_text(percepts):
    if len(percepts) == 0:
        return "Percept: 없음"
    return "Percept: " + ", ".join(percepts)


def draw_world():
    canvas.delete("all")

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x1 = col * CELL_SIZE
            y1 = row * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            cell = game.world[row][col]

            if cell == "wall":
                fill_color = "gray"
            elif (row, col) in agent.confirmed_pit or (row, col) in agent.confirmed_wumpus:
                fill_color = "#ff9999"
            elif (row, col) in agent.possible_pit or (row, col) in agent.possible_wumpus:
                fill_color = "#ffe6e6"
            elif (row, col) in agent.visited:
                fill_color = "#e6f7ff"
            elif (row, col) in agent.safe_cells:
                fill_color = "#eaffea"
            else:
                fill_color = "white"

            canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill=fill_color,
                outline="black",
                width=2
            )

            if cell in image_map:
                canvas.create_image(
                    x1 + CELL_SIZE // 2,
                    y1 + CELL_SIZE // 2,
                    image=image_map[cell]
                )

    agent_row, agent_col = agent.get_position()
    agent_x = agent_col * CELL_SIZE + CELL_SIZE // 2
    agent_y = agent_row * CELL_SIZE + CELL_SIZE // 2

    canvas.create_image(
        agent_x,
        agent_y,
        image=agent_img
    )

    canvas.create_text(
        agent_x,
        agent_y - 40,
        text=direction_symbol[agent.get_direction()],
        font=("Arial", 34, "bold"),
        fill="red"
    )


def auto_step():
    # 1. 현재 위치에서 Percept 확인 후 지식 갱신
    row, col = agent.get_position()
    percepts = game.get_percepts(row, col)
    agent.reasoning(percepts, game.world)

    # 2. DFS로 다음 목표 칸 선택
    target = agent.choose_target_cell(game.world)

    if target is None:
        info_label.config(
            text="DFS 탐색 결과: 현재까지 안전하다고 판단한 이동 가능 칸이 없습니다."
        )
        draw_world()
        return

    # 3. 목표 칸으로 가기 위한 Action 선택
    action = agent.choose_action(target)

    # 4. Action 수행
    if action == "TurnLeft":
        agent.turn_left()
        info_label.config(
            text="Action: TurnLeft / " + make_percept_text(percepts)
        )

    elif action == "TurnRight":
        agent.turn_right()
        info_label.config(
            text="Action: TurnRight / " + make_percept_text(percepts)
        )

    elif action == "GoForward":
        next_row, next_col = agent.get_forward_position()

        if game.world[next_row][next_col] == "wall":
            info_label.config(
                text="Action: GoForward / Percept: Bump"
            )
            draw_world()
            return

        agent.go_forward()

        row, col = agent.get_position()
        current_cell = game.world[row][col]

        if current_cell == "wumpus":
            agent.mark_death_cell(row, col, "wumpus")
            info_label.config(
                text="Action: GoForward / Wumpus에게 잡힘 → 기억 유지 후 (1,1)로 복귀"
            )
            agent.reset_position()

        elif current_cell == "pit":
            agent.mark_death_cell(row, col, "pit")
            info_label.config(
                text="Action: GoForward / Pit에 빠짐 → 기억 유지 후 (1,1)로 복귀"
            )
            agent.reset_position()

        elif current_cell == "gold":
            new_percepts = game.get_percepts(row, col)
            agent.reasoning(new_percepts, game.world)

            info_label.config(
                text="Action: GoForward / " + make_percept_text(new_percepts)
            )

        else:
            new_percepts = game.get_percepts(row, col)
            agent.reasoning(new_percepts, game.world)

            info_label.config(
                text="Action: GoForward / " + make_percept_text(new_percepts)
            )

    draw_world()


auto_button = tk.Button(
    window,
    text="자동 실행",
    font=("Arial", 14),
    command=auto_step
)
auto_button.pack(pady=10)

draw_world()
window.mainloop()