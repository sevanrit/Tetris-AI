import pygame
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.evaluation import evaluate_policy
from tetris_env import TetrisEnv

learn = 0  # 0 - просмотр, 1 - обучение
steps = 1 * 10**5  # кол-во действий агента
render = False
if learn:
    env = TetrisEnv(r=render, render_mode="human")
    # обертка среды в VecEnv
    env = make_vec_env(lambda: env, n_envs=1)
    # обучение модели DQN
    model = DQN("MlpPolicy", env, verbose=1)
    print("START LEARNING...")
    model.learn(total_timesteps=steps)
    print("STOP LEARNING, TEST...")
    # сохранение обученной модели
    model.save("tetris_dqn_model_1k_F")
    # оценка производительности модели
    mean_reward, _ = evaluate_policy(model, env, n_eval_episodes=10, render=True)
    print(f"Средняя награда на 10 оценочных эпизодах: {mean_reward}")


# функция для отображения игры
def play_game(model):
    pygame.init()
    clock = pygame.time.Clock()
    env = TetrisEnv(r=True)

    screen_width, screen_height = 400, 500
    done = False
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Tetris")

    obs = env.reset()

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        # предсказания действий
        action, _ = model.predict(obs)

        # применение действия к среде
        obs, _, done, _ = env.step(action)

        # отображение игры
        screen.fill((255, 255, 255))
        env.render()
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


model = DQN.load("models//tetris_dqn_model_1M_FIG")
while 1:
    play_game(model)
