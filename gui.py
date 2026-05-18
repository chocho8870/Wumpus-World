import tkinter as tk
from PIL import Image, ImageTk
from world import WumpusWorld
from agent import Agent

window = tk.Tk()
window.title("Wumpus World")

GRID_SIZE = 6
CELL_SIZE = 100
IMAGE_SIZE = 80

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
    text="자동 실행 버튼을 누르면 에이전트가 한 칸씩 판단하여 이동합니다.",
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
            elif (row, col) in agent.visited:
                fill_color = "#e6f7ff"
            else:
                fill_color = "white"

            canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill=fill_color,
                outline=""
            )

    for i in range(GRID_SIZE + 1):
        canvas.create_line(
            i * CELL_SIZE,
            0,
            i * CELL_SIZE,
            GRID_SIZE * CELL_SIZE,
            fill="black",
            width=2
        )

        canvas.create_line(
            0,
            i * CELL_SIZE,
            GRID_SIZE * CELL_SIZE,
            i * CELL_SIZE,
            fill="black",
            width=2
        )

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            cell = game.world[row][col]

            if cell in image_map:
                x = col * CELL_SIZE + CELL_SIZE // 2
                y = row * CELL_SIZE + CELL_SIZE // 2
                canvas.create_image(x, y, image=image_map[cell])

    agent_row, agent_col = agent.get_position()
    agent_x = agent_col * CELL_SIZE + CELL_SIZE // 2
    agent_y = agent_row * CELL_SIZE + CELL_SIZE // 2
    canvas.create_image(agent_x, agent_y, image=agent_img)


def auto_step():
    # 현재 위치에서 percept 확인 후 추론
    row, col = agent.get_position()
    percepts = game.get_percepts(row, col)
    agent.reasoning(percepts, game.world)

    # 다음 이동 위치 선택
    next_row, next_col = agent.choose_next_move(game.world)
    agent.move_to(next_row, next_col)

    current_cell = game.world[next_row][next_col]

    # 위험 요소 처리
    if current_cell == "wumpus":
        info_label.config(
            text="Wumpus에게 잡힘 → 기억 유지 후 시작 위치로 복귀"
        )
        agent.reset_position()
        draw_world()
        return

    elif current_cell == "pit":
        info_label.config(
            text="Pit에 빠짐 → 기억 유지 후 시작 위치로 복귀"
        )
        agent.reset_position()
        draw_world()
        return

    elif current_cell == "gold":
        info_label.config(
            text="Gold 발견! / Percept: Glitter"
        )
        draw_world()
        return

    # 이동한 새 위치에서 percept 다시 확인
    new_percepts = game.get_percepts(next_row, next_col)
    agent.reasoning(new_percepts, game.world)

    if len(new_percepts) == 0:
        percept_text = "Percept: 없음"
    else:
        percept_text = "Percept: " + ", ".join(new_percepts)

    info_label.config(text=percept_text + " / 이동 완료")
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