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



def bfs_shortest_path(start, goal):
    queue = deque([[start]])  # File de chemins, initialisée avec le nœud de départ

    while queue:
        path = queue.popleft()  # Récupérer le premier chemin
        node = path[-1]  # Dernier nœud du chemin actuel

        if node == goal:  # Si le nœud cible est atteint
            return path

        for neighbor in adjacency_list[node]:
            new_path = list(path)
            new_path.append(neighbor)
            queue.append(new_path)

    return []  # Aucun chemin trouvé

# Fonction de déplacement de l'agent avec chemin donné
def agent_process_BFS(agent_id, position_queue, last_visited_shared, shared_list_next_node, lock):
    agent_position = nodes_position[0]
    agent_node_index = 0
    path = []  # Chemin que l'agent doit suivre
    path_index = 0

    while True:
        # Si l'agent a atteint sa cible ou n'a pas de chemin à suivre
        if not path or path_index >= len(path):
            # Choisir un nouveau nœud cible aléatoire
            target_node = random.randint(0, len(nodes_position) - 1)
            path = bfs_shortest_path(agent_node_index, target_node)
            if not path:
                continue
            path_index = 0

        # Déterminer le nœud cible actuel à suivre dans le chemin
        next_node_index = path[path_index]
        agent_target_position = nodes_position[next_node_index]

        x1, y1 = agent_position
        x2, y2 = agent_target_position
        dx, dy = x2 - x1, y2 - y1
        distance = math.hypot(dx, dy)

        # Si l'agent arrive au nœud cible actuel
        if distance < agent_speed:
            agent_node_index = next_node_index
            path_index += 1  # Passer au prochain nœud dans le chemin
            last_visited_shared[agent_node_index] = time.time()

        # Déplacer l'agent vers le nœud cible actuel
        else:
            angle = math.atan2(dy, dx)
            agent_position = (x1 + agent_speed * math.cos(angle), y1 + agent_speed * math.sin(angle))

        position_queue.put(agent_position)
        time.sleep(1 / FPS)