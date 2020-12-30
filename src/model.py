import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from collections import deque

class NeuralNet:

    def __init__(self):
        self.state_size = 6 #pos (x,y), vel (x,y), score, game_over
        self.action_size = 6 #left/right flipers, left/right tilt, bottom tilt, plunger
        self.gamma = 0.98
        self.epsilon_max = 1.0
        self.epsilon_min = 0.1
        self.lr = 0.001
        self.batch_size = 64
        self.epsiode_steps = 10000
        self.model = self.generate_model()
        self.target = self.generate_model()
        self.optimizer = keras.optimizers.Adam(learning_rate=self.lr)
        self.action_hist = deque(maxlen=100000)
        self.state_hist = deque(maxlen=100000)
        self.next_state_hist = deque(max_len=100000)
        self.episode_reward_hist = deque(maxlen=100000)
        self.num_random_frames = 50000
        self.num_greedy_frames = 100000
        self.update_actions = 4 #num actions to take before updating model
        self.target_update_actions = 1000 #num actions to take before updating target
        self.loss = keras.losses.mean_squared_error()

    #Network needs to learn the Q-Table with dim (state_size * action_size)
    def generate_model(self):
        states = layers.Input(shape=(self.state_size,))
        actions = layers.Dense(self.action_size, activation='sigmoid')(states)

        return keras.Model(inputs=states, outputs=actions)

