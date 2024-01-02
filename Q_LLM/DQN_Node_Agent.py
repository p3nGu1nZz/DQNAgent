from Agent_Trainer import load_training_data, train_dqn_agent
import json
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import namedtuple, deque
import random
import gym

class DQNAgent:
    def __init__(self, q_network, optimizer, input_size, output_size, learning_rate=0.1, discount_factor=0.9):
        self.q_network = q_network(input_size, output_size)  # Create an instance of QNetwork
        self.optimizer = optimizer(self.q_network.parameters(), lr=learning_rate)  # Create an instance of the optimizer
        self.discount_factor = discount_factor
        self.loss_fn = nn.MSELoss()

def DQN_Node_Agent():
    QNetwork
    DQNAgent
    pass

class QNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_size)

    def forward(self, state):
        x = torch.relu(self.fc1(state))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

# Define the replay buffer
class ReplayBuffer:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.memory = deque(maxlen=buffer_size)
        self.Transition = namedtuple('Transition', ('state', 'action', 'reward', 'next_state', 'done'))

    def add(self, state, action, reward, next_state, done):
        transition = self.Transition(state, action, reward, next_state, done)
        self.memory.append(transition)

    def sample(self, batch_size):
        batch = random.sample(self.memory, batch_size)
        return self.Transition(*zip(*batch))

# Define the DQN Agent
class DQNAgent:
    def __init__(self, state_size, action_size, buffer_size=10000, batch_size=64, gamma=0.99, learning_rate=0.001):
        self.state_size = state_size
        self.action_size = action_size
        self.buffer = ReplayBuffer(buffer_size)
        self.batch_size = batch_size
        self.gamma = gamma

        # Q-networks
        self.q_network = QNetwork(state_size, action_size)
        self.target_network = QNetwork(state_size, action_size)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()

        # Optimizer
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)

    def select_action(self, state, epsilon):
        if np.random.rand() < epsilon:
            return np.random.choice(self.action_size)
        else:
            with torch.no_grad():
                q_values = self.q_network(state)
                return torch.argmax(q_values).item()

    def train(self):
        if len(self.buffer.memory) < self.batch_size:
            return

        transitions = self.buffer.sample(self.batch_size)
        batch = self.Transition(*zip(*transitions))

        # Compute Q-values
        q_values = self.q_network(batch.state)
        next_q_values = self.target_network(batch.next_state).detach()

        # Compute target Q-values
        target_q_values = q_values.clone()
        for i in range(self.batch_size):
            if batch.done[i]:
                target_q_values[i][batch.action[i]] = batch.reward[i]
            else:
                target_q_values[i][batch.action[i]] = batch.reward[i] + self.gamma * torch.max(next_q_values[i])

        # Compute loss and update Q-network
        loss = nn.MSELoss()(q_values, target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update target network
        self.update_target_network()

    def update_target_network(self):
        self.target_network.load_state_dict(self.q_network.state_dict())

# Main training loop
def train_dqn():
    # Environment parameters
    state_size = 4  # Replace with your environment's state size
    action_size = 2  # Replace with your environment's action size
    env = gym.make("CartPole-v1")  # Replace with your environment

    # DQN agent
    agent = DQNAgent(state_size, action_size, input_size=10, output_size=20)

    episodes = 1000
    epsilon = 1.0
    epsilon_decay = 0.995
    min_epsilon = 0.01

    for episode in range(episodes):
        state = env.reset()
        total_reward = 0

        while True:
            # Ensure the state has the correct length
            state = torch.tensor(state, dtype=torch.float32).view(1, -1)

            # Choose action
            action = agent.select_action(state, epsilon)

            # Take action
            next_state, reward, done, _ = env.step(action)
            next_state = torch.tensor(next_state, dtype=torch.float32).view(1, -1)

            # Store experience in replay buffer
            agent.buffer.add(state, action, reward, next_state, done)

            # Train the agent
            agent.train()

            # Update state and total reward
            state = next_state
            total_reward += reward

            if done:
                break

        # Decay exploration rate
        epsilon = max(min_epsilon, epsilon * epsilon_decay)

        print(f"Episode {episode + 1}, Total Reward: {total_reward}")

class QNetwork(nn.Module):
    def __init__(self, input_size, output_size):
        super(QNetwork, self).__init__()
        self.dense1 = nn.Linear(input_size, 128)
        self.dense2 = nn.Linear(128, 64)
        self.output_layer = nn.Linear(64, output_size)

    def forward(self, state):
        x = torch.relu(self.dense1(state))
        x = torch.relu(self.dense2(x))
        return self.output_layer(x)

class DQNAgent:
    def __init__(self, q_network, optimizer, input_size, output_size, learning_rate=0.1, discount_factor=0.9):
        self.q_network = q_network(input_size, output_size)
        self.optimizer = optimizer(self.q_network.parameters(), lr=learning_rate)
        self.discount_factor = discount_factor
        self.loss_fn = nn.MSELoss()

    def select_action(self, state, exploration_prob):
        if np.random.rand() < exploration_prob:
            return np.random.choice(self.q_network.output_layer.out_features)
        else:
            q_values = self.q_network(state)
            return torch.argmax(q_values).item()

    def update_q_network(self, state, action, reward, next_state):
        self.optimizer.zero_grad()

        q_values_current = self.q_network(state)
        q_value_next = torch.max(self.q_network(next_state).detach()).item()

        td_target = reward + self.discount_factor * q_value_next
        td_error = td_target - q_values_current[0, action].item()

        loss = self.loss_fn(q_values_current.squeeze(), torch.tensor([td_target], dtype=torch.float32))
        loss.backward()
        self.optimizer.step()

    def load_training_data(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            training_data = json.load(file)
        return training_data

    @classmethod
    def train_dqn_agent(self, agent, training_data, episodes=1000):
        for episode in range(episodes):
            for data_point in training_data:
                role = data_point.get("role")
                content = data_point.get("content")

                processed_content = [ord(char) for char in content]

                # Assuming content is now in a format suitable for your Q-network
                state = torch.tensor(processed_content, dtype=torch.float32)
                action = agent.select_action(state, exploration_prob=0.1)
                next_state = torch.tensor(next_content, dtype=torch.float32)
                reward = 1.0  # Placeholder, define the reward based on your problem

                agent.update_q_network(state, action, reward, next_state)

if __name__ == "__main__":
    q_network = QNetwork
    optimizer = optim.Adam
    input_size = 10
    output_size = 20
    dqn_agent = DQNAgent(q_network, optimizer, input_size, output_size)  # Pass instances of QNetwork and optimizer
    training_data_path = "C:/Users/Mayra/Documents/AGI/Q_LLM/training_data/training_data.json"
    training_data = load_training_data(training_data_path)

    # Call the class method using the class name and parentheses
    DQNAgent.train_dqn_agent(dqn_agent, training_data, episodes=1000)

    train_dqn()