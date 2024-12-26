import random
import math
import time
from graphstructure import *  # Assurez-vous que nodes et edges sont définis dans graphstructure
from display import *
from collections import deque  # Pour BFS
FPS = 30

agent_speed = 5
num_agents = 3

# Informations récupérées depuis graphstructure
adjacency_list = {i: [] for i in range(len(nodes_position))}
for a, b in edges:
    adjacency_list[a].append(b)
    adjacency_list[b].append(a)

# Fonction de déplacement de l'agent avec chemin donné
def agent_process_chemins(agent_id, position_queue, chemin, last_visited_shared):
    agent_position = nodes_position[chemin[0]]
    agent_target_position = nodes_position[chemin[1]]
    agent_node_index = chemin[0]

    i = 1
    while True:
        x1, y1 = agent_position
        x2, y2 = agent_target_position
        dx, dy = x2 - x1, y2 - y1
        distance = math.hypot(dx, dy)

        # Si on est arrivé à un nœud
        if distance < agent_speed:
            agent_node_index = chemin[i]
            # Met à jour le temps de la dernière visite du nœud actuel dans le dictionnaire partagé
            last_visited_shared[agent_node_index] = time.time()

            next_node_index = chemin[i+1]
            agent_target_position = nodes_position[next_node_index]
            i += 1
        else:
            angle = math.atan2(dy, dx)
            agent_position = (x1 + agent_speed * math.cos(angle), y1 + agent_speed * math.sin(angle))

        position_queue.put(agent_position)
        time.sleep(1 / FPS)

