import gym
from stable_baselines3 import PPO, A2C
from stable_baselines3.common.vec_env import DummyVecEnv
from tetris_env import TetrisEnv
import time
import pygame

learn = 1
if learn:
    env = TetrisEnv(r=False)
    env = DummyVecEnv([lambda: env])
    model_ppo = PPO("MlpPolicy", env, verbose=1, learning_rate=0.9)
    model_ppo.learn(total_timesteps=1 * 10**5)

    model_ppo.save("tetris_ppo_model")


def play_game(model):
    pygame.init()
    clock = pygame.time.Clock()
    env = TetrisEnv(r=True, render_mode="human")

    screen_width, screen_height = 400, 500
    done = False
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Tetris")

    obs = env.reset()

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, _ = env.step(action)
        screen.fill((255, 255, 255))
        env.render()
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


model = PPO.load("tetris_ppo_model")
while 1:
    play_game(model)
