import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox

# Global variables for dynamic settings
GRID_SIZE = 20
NUM_ANTS_PER_COLONY = 5
NUM_RESOURCES = 15
STEPS = 100
PHEROMONE_DECAY = 0.05
PHEROMONE_STRENGTH = 3
RESOURCE_TYPES = {1: "Leaves", 2: "Wood"}
RESPAWN_DELAY = 10  # Steps before resources respawn

SCORES = {"Colony A": 0, "Colony B": 0}
current_step = 0


# Environment class
class Environment:
    def __init__(self, grid_size, num_resources):
        self.grid_size = grid_size
        self.grid = np.zeros((grid_size, grid_size))  # 0: empty, 1/2: resource types
        self.pheromones_a = np.zeros((grid_size, grid_size))  # Colony A pheromones
        self.pheromones_b = np.zeros((grid_size, grid_size))  # Colony B pheromones
        self.nests = {"Colony A": (2, 2), "Colony B": (grid_size - 3, grid_size - 3)}
        self.resource_respawn_tracker = {}
        self.spawn_resources(num_resources)

    def spawn_resources(self, num_resources):
        for _ in range(num_resources):
            x, y = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
            if (x, y) not in self.nests.values():
                self.grid[x, y] = random.choice(list(RESOURCE_TYPES.keys()))

    def decay_pheromones(self):
        self.pheromones_a = np.maximum(0, self.pheromones_a - PHEROMONE_DECAY)
        self.pheromones_b = np.maximum(0, self.pheromones_b - PHEROMONE_DECAY)

    def respawn_resources(self, step):
        to_respawn = [loc for loc, respawn_step in self.resource_respawn_tracker.items() if step >= respawn_step]
        for x, y in to_respawn:
            self.grid[x, y] = random.choice(list(RESOURCE_TYPES.keys()))
            del self.resource_respawn_tracker[(x, y)]


# Ant class
class Ant:
    def __init__(self, colony, env):
        self.x, self.y = env.nests[colony]
        self.has_food = False
        self.colony = colony
        self.env = env

    def move(self):
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.x = (self.x + dx) % self.env.grid_size
        self.y = (self.y + dy) % self.env.grid_size

    def act(self, step):
        pheromones = self.env.pheromones_a if self.colony == "Colony A" else self.env.pheromones_b
        if self.has_food:
            if (self.x, self.y) == self.env.nests[self.colony]:
                SCORES[self.colony] += 1
                self.has_food = False
            else:
                pheromones[self.x, self.y] += PHEROMONE_STRENGTH
                self.move()
        else:
            if self.env.grid[self.x, self.y] in RESOURCE_TYPES:
                self.has_food = True
                self.env.resource_respawn_tracker[(self.x, self.y)] = step + RESPAWN_DELAY
                self.env.grid[self.x, self.y] = 0
            else:
                self.follow_pheromones(pheromones)
                self.move()

    def follow_pheromones(self, pheromones):
        max_pheromone = 0
        target = (self.x, self.y)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = (self.x + dx) % self.env.grid_size, (self.y + dy) % self.env.grid_size
            if pheromones[nx, ny] > max_pheromone:
                max_pheromone = pheromones[nx, ny]
                target = (nx, ny)
        self.x, self.y = target


# Initialize environment and ants
def init_simulation(grid_size, num_ants, num_resources):
    global env, ants_a, ants_b, SCORES, current_step
    env = Environment(grid_size, num_resources)
    ants_a = [Ant("Colony A", env) for _ in range(num_ants)]
    ants_b = [Ant("Colony B", env) for _ in range(num_ants)]
    SCORES = {"Colony A": 0, "Colony B": 0}
    current_step = 0


# Visualization Function
def run_simulation(steps):
    global current_step
    plt.ion()
    fig, ax = plt.subplots(figsize=(9, 9))  # Increased figure size
    for step in range(current_step, current_step + steps):
        # Ant actions
        for ant in ants_a + ants_b:
            ant.act(step)

        env.decay_pheromones()
        env.respawn_resources(step)

        ax.clear()
        for x in range(env.grid_size):
            for y in range(env.grid_size):
                if env.grid[x, y] == 1:
                    ax.scatter(y, x, color="green", s=200, marker="s", label="Leaves")  # Larger resource markers
                elif env.grid[x, y] == 2:
                    ax.scatter(y, x, color="brown", s=200, marker="o", label="Wood")  # Larger resource markers

        # Display pheromone trails
        ax.imshow(env.pheromones_a, cmap="Reds", alpha=0.5, interpolation="nearest")
        ax.imshow(env.pheromones_b, cmap="Blues", alpha=0.5, interpolation="nearest")

        # Display ants
        for ant in ants_a:
            ax.scatter(ant.y, ant.x, color="red", s=150, label="Colony A Ants")
        for ant in ants_b:
            ax.scatter(ant.y, ant.x, color="blue", s=150, label="Colony B Ants")

        # Display nests and scores
        for name, (x, y) in env.nests.items():
            ax.text(y, x, name, color="black", fontsize=12, ha="center", va="center")
            ax.text(y, x + 0.5, f"Score: {SCORES[name]}", color="black", fontsize=10, ha="center")

        # Title and layout adjustments
        ax.set_title(f"Step {step + 1} | Colony A: {SCORES['Colony A']} | Colony B: {SCORES['Colony B']}", fontsize=16)
        ax.set_xlim(-1, env.grid_size)
        ax.set_ylim(-1, env.grid_size)
        ax.set_xticks(range(env.grid_size))
        ax.set_yticks(range(env.grid_size))
        ax.grid(color="black", linestyle="--", linewidth=0.5)
        plt.pause(0.2)

    current_step += steps
    plt.ioff()
    plt.show()


# Interactive controls
def on_restart(event):
    grid_size = int(grid_size_box.text)
    num_ants = int(num_ants_box.text)
    num_resources = int(num_resources_box.text)
    steps = int(steps_box.text)
    init_simulation(grid_size, num_ants, num_resources)
    run_simulation(steps)


# Initialize controls
fig, ax = plt.subplots(figsize=(6, 2))
plt.subplots_adjust(bottom=0.5)

restart_button = Button(plt.axes([0.1, 0.05, 0.2, 0.075]), "Restart")
restart_button.on_clicked(on_restart)

grid_size_box = TextBox(plt.axes([0.4, 0.25, 0.2, 0.075]), "Grid Size", initial=str(GRID_SIZE))
num_ants_box = TextBox(plt.axes([0.4, 0.15, 0.2, 0.075]), "Ants per Colony", initial=str(NUM_ANTS_PER_COLONY))
num_resources_box = TextBox(plt.axes([0.4, 0.05, 0.2, 0.075]), "Resources", initial=str(NUM_RESOURCES))
steps_box = TextBox(plt.axes([0.7, 0.15, 0.2, 0.075]), "Steps", initial=str(STEPS))

init_simulation(GRID_SIZE, NUM_ANTS_PER_COLONY, NUM_RESOURCES)
run_simulation(STEPS)
