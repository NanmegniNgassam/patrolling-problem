import random
import math
import time
import heapq
from display import *
from config import agent_speed, FPS



# Heuristique (distance euclidienne)
def heuristic(nodes_position, node_a, node_b):
    x1, y1 = nodes_position[node_a]
    x2, y2 = nodes_position[node_b]
    return math.hypot(x2 - x1, y2 - y1)

# Algorithme A* pour trouver le chemin le plus court
def a_star_shortest_path(nodes_position, edges, start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start, [start]))  # (coût estimé, nœud actuel, chemin)
    g_score = {i: float('inf') for i in range(len(nodes_position))}
    g_score[start] = 0
    adjacency_list = {i: [] for i in range(len(nodes_position))}
    for a, b in edges:
        adjacency_list[a].append(b)
        adjacency_list[b].append(a)
    while open_set:
        _, current, path = heapq.heappop(open_set)

        if current == goal:
            return path

        for neighbor in adjacency_list[current]:
            tentative_g_score = g_score[current] + heuristic(nodes_position, current, neighbor)
            if tentative_g_score < g_score[neighbor]:
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(nodes_position, neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor, path + [neighbor]))

    return []  # Aucun chemin trouvé


# Fonction de déplacement de l'agent avec chemin donné
def agent_process_random(agent_id, agent_speed, nodes_position, edges, position_queue, last_visited_shared, lock,stop_simulation):
    agent_position = nodes_position[0]
    agent_node_index = 0
    path = []  # Chemin que l'agent doit suivre
    path_index = 0


    while not stop_simulation.value:
        # Si l'agent a atteint sa cible ou n'a pas de chemin à suivre
        if not path or path_index >= len(path):
            # Choisir un nouveau nœud cible aléatoire
            target_node = random.randint(0, len(nodes_position) - 1)
            path = a_star_shortest_path(nodes_position, edges, agent_node_index, target_node)
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
            with lock:
                last_visited_shared[agent_node_index] = time.time()

        # Déplacer l'agent vers le nœud cible actuel
        else:
            angle = math.atan2(dy, dx)
            agent_position = (x1 + agent_speed * math.cos(angle), y1 + agent_speed * math.sin(angle))
        with lock:
            position_queue.put(agent_position)
        time.sleep(1 / FPS)