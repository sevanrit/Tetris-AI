import pygame
import random
import time

colors = [
    (0, 0, 0),
    (111, 111, 111),  # rr
    (128, 0, 0),
    (0, 0, 205),  # r
    (250, 191, 10),  # rr
    (114, 0, 245),
    (72, 61, 139),
]
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FPS = 600
SIZE = (400, 500)
LEVEL = 200


class Figure:
    x = 0
    y = 0

    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    # Инициализция
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # ТИП ФИГУРЫ
        # self.type = random.randint(0, len(self.figures) - 1)
        self.type = random.randint(0, 1) * 6

        self.color = random.randint(1, len(colors) - 1)
        # self.color = 1
        self.rotation = 0

    # Отображение фигуры
    def image(self):
        return self.figures[self.type][self.rotation]

    # Поворот фигуры
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])


class Tetris:
    # Инициализация
    def __init__(self, height, width):
        pygame.init()
        self.screen = pygame.display.set_mode(SIZE)
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.level = LEVEL
        self.score = 0
        # Состояние
        self.state = "game"
        self.field = []
        self.x = 100
        self.y = 60
        self.zoom = 20
        self.figure = None
        self.pixel_counts = 0
        self.last_drop_time = time.time()  # Инициализация времени последнего опускания

        self.height = height
        self.width = width
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(0)
            self.field.append(new_line)
        self.new_figure()

    # Создаем новую фигуру
    def new_figure(self):
        self.figure = Figure(3, 0)
        self.pixel_counts += 4

    # Если True - поражение (проверка проигрыш или нет)
    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if (
                        i + self.figure.y > self.height - 1
                        or j + self.figure.x > self.width - 1
                        or j + self.figure.x < 0
                        or self.field[i + self.figure.y][j + self.figure.x] > 0
                    ):
                        intersection = True
        return intersection

    # Если есть линия, стираем его и возвращаем True
    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                self.pixel_counts -= 10
                for i1 in range(i, -1, -1):
                    for j in range(self.width):
                        if i1 == 0:
                            self.field[i1][j] = 0
                        else:
                            self.field[i1][j] = self.field[i1 - 1][j]

        self.score += lines**2
        if lines > 0:
            return True
        return False

    def k(self):
        h = 0
        for i in range(len(self.field)):
            if sum(self.field[i]) != 0:
                h = i - 1
                break
        return 18 - h

    def r(self):
        return sum(self.field[-1]) + sum(self.field[-2]) + sum(self.field[-3])

    """def go_space(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()"""

    # Движение фигуры вниз
    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    # Проверка на остановку фигуры
    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.new_figure()
        # Проверка на проигрыш
        if self.intersects():
            self.state = "gameover"
        # Проверка что убралась линия
        elif self.break_lines():
            self.state = "breaklines"
        # Состояние находимся в игре
        else:
            self.state = "game"

    # В сторону
    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    # Вращение
    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation

    # Отображение
    def render(self):
        self.screen.fill(WHITE)

        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(
                    self.screen,
                    BLACK,
                    [
                        self.x + self.zoom * j,
                        self.y + self.zoom * i,
                        self.zoom,
                        self.zoom,
                    ],
                    1,
                )
                if self.field[i][j] > 0:
                    pygame.draw.rect(
                        self.screen,
                        colors[self.field[i][j]],
                        [
                            self.x + self.zoom * j + 1,
                            self.y + self.zoom * i + 1,
                            self.zoom - 2,
                            self.zoom - 1,
                        ],
                    )

        if self.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in self.figure.image():
                        pygame.draw.rect(
                            self.screen,
                            colors[self.figure.color],
                            [
                                self.x + self.zoom * (j + self.figure.x) + 1,
                                self.y + self.zoom * (i + self.figure.y) + 1,
                                self.zoom - 2,
                                self.zoom - 2,
                            ],
                        )

        font = pygame.font.SysFont("Calibri", 25, True, False)
        font1 = pygame.font.SysFont("Calibri", 65, True, False)
        text = font.render("Score: " + str(self.score), True, BLACK)

        self.screen.blit(text, [0, 0])

        pygame.display.flip()

    # Сброс всех параметров на начальный этап
    def reset(self):
        self.level = LEVEL
        self.score = 0
        self.state = "game"
        self.field = []
        self.x = 100
        self.y = 60
        self.zoom = 20
        self.figure = None
        for i in range(self.height):
            new_line = []
            for j in range(self.width):
                new_line.append(0)
            self.field.append(new_line)
        self.new_figure()

    # Запуск игры от человека
    def start_human(self):
        done = False
        pressing_down = False
        if self.figure is None:
            self.new_figure()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.go_side(-1)  # Движение фигуры влево
                elif event.key == pygame.K_RIGHT:
                    self.go_side(1)  # Движение фигуры вправо
                elif event.key == pygame.K_UP:
                    self.rotate()  # Вращение фигуры
                elif event.key == pygame.K_DOWN:
                    pressing_down = True
                    self.go_down()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    pressing_down = False

        current_time = time.time()  # Текущее время
        drop_interval = 1 / self.level  # Интервал опускания, зависящий от уровня
        if pressing_down or current_time - self.last_drop_time > drop_interval:
            if self.state != "gameover":
                self.go_down()
                self.last_drop_time = (
                    current_time  # Обновление времени последнего опускания
                )

        if game.state == "gameover":
            game.reset()
        game.render()

    # Запуск самой игры для компа
    def start(self):
        pressing_down = False
        if self.figure is None:
            self.new_figure()

        current_time = time.time()  # Текущее время
        drop_interval = 1 / self.level  # Интервал опускания, зависящий от уровня
        if pressing_down or current_time - self.last_drop_time > drop_interval:
            if self.state != "gameover":
                self.go_down()
                self.last_drop_time = (
                    current_time  # Обновление времени последнего опускания
                )


if __name__ == "__main__":
    game = Tetris(20, 10)
    while 1:
        game.clock.tick(FPS)
        game.start_human()
