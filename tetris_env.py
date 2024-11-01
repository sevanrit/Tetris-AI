import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
import pygame
from tetris import Tetris, colors
import time


class TetrisEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self, height=20, width=10, r=True, render_mode="human"):
        self.done = False
        self.height = height
        self.width = width
        self.action_space = spaces.Discrete(
            4
        )  # 0: rotate, 1: move left, 2: move right, 3: place
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(self.height, self.width + 4), dtype=np.uint8
        )

        self.game = Tetris(height, width)
        self.seed()
        self.clock = pygame.time.Clock()
        self.viewer = None
        self.state = None
        self.prev_score = (
            0  # Добавление атрибута prev_score и инициализация его значением 0
        )
        self.drop_interval = 0.001  # Интервал опускания фигуры (в секундах)
        self.r = r  # Флаг для определения рендеринга эпизодов
        self.render_mode = render_mode

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def compute_reward(self, action):
        reward = 0

        # Награда за удаление линий
        if self.game.state == "breaklines":
            reward += 100 * self.game.score

        # Штраф за высоту
        height_penalty = sum([max(row) for row in zip(*self.game.field[::1])])
        reward += 20 - height_penalty

        # Награда за использование различных действий
        # Например, поворот дается награда 1, движение влево/вправо награда 0.5
        if action == 0:
            reward += 0
        elif action == 1 or action == 2:
            reward += 2

        # Штраф за пустоты
        holes_penalty = sum([row.count(0) for row in self.game.field[:4]])
        reward -= holes_penalty

        # Награда за создание полных линий на последнем или предпоследнем ряду
        if self.game.state == "breaklines" and self.game.figure.y >= self.height - 2:
            reward += 500

        # Штраф за столкновения с предыдущими блоками
        if self.game.state == "gameover":
            reward -= 1000
        return reward

    def step(self, action):
        assert self.action_space.contains(action)
        reward = 0
        # ДЕЙСТВИЯ АГЕНТА
        if action == 0:
            self.game.rotate()
        elif action == 1:
            self.game.go_side(-1)  # влево
        elif action == 2:
            self.game.go_side(1)
        elif action == 3:
            pass

        self.game.start()  # игра делает один "ход" - фигура чутка опустилась НЕ ПИШИ
        state = self._get_obs()  # обновляем текуцщее состояние среды

        # k_height = self.game.k()
        # reward += (1 - k_height)*0.02
        # reward += self.game.r()*0.01

        # Проверка событий и добавление соответствующей награды
        # if self.game.state == "gameover":
        #    reward += -100  # Негативная награда за поражение
        # if self.game.state == "breaklines":
        #    reward += 10
        #    self.game.state = "game"

        reward = self.compute_reward(action)
        if self.r:
            self.render()

        self.done = (
            self.game.state == "gameover"
        )  # Установить параметр done в True, если игра завершена

        return (
            state,
            reward,
            self.done,
            {},
        )  # Возвращаем текущее состояние, итоговую награду, конец эпизода или нет

    def reset(self):
        self.game.reset()  # Сброс игры в самое начало
        self.state = self._get_obs()
        self.done = False  # Установить параметр done в False после сброса среды
        return self.state

    """def _get_obs(self):
        field = np.array(self.game.field)
        field[field > 0] = 1
        return field
        """

    def _get_obs(self):
        field = np.array(self.game.field)
        field[field > 0] = 1

        # Создаем массив для текущей фигуры
        current_figure = np.zeros((self.height, 4))
        if self.game.figure is not None:
            figure_image = self.game.figure.image()
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in figure_image:
                        current_figure[i + self.game.figure.y, j] = 1

        # Объединяем поле и текущую фигуру в один массив
        state = np.concatenate((field, current_figure), axis=1)

        return state

    def render(self, render_mode="human"):
        self.game.render()  # Отрисовка
