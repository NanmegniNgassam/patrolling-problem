import random
import math
import time
from display import *
from config import agent_speed, FPS



# Fonction de déplacement de l'agent avec chemin donné
def agent_process_chemins(agent_id, agent_speed, nodes_position, position_queue, chemin, last_visited_shared,stop_simulation):
    agent_position = nodes_position[chemin[0]]
    agent_target_position = nodes_position[chemin[1]]
    agent_node_index = chemin[0]

    
    i = 0
    while not stop_simulation.value:
        x1, y1 = agent_position
        x2, y2 = agent_target_position
        dx, dy = x2 - x1, y2 - y1
        distance = math.hypot(dx, dy)

        # Si on est arrivé à un nœud
        if distance < agent_speed:
            agent_node_index = chemin[i]
            # Met à jour le temps de la dernière visite du nœud actuel dans le dictionnaire partagé
            last_visited_shared[agent_node_index] = time.time()

            # Passer au prochain nœud
            i += 1
            if i >= len(chemin):  # Si la fin du chemin est atteinte
                i = 0  # Recommence depuis le début
                #print(f"Agent {agent_id}: Redémarre le chemin.")
            next_node_index = chemin[i]
            agent_target_position = nodes_position[next_node_index]
            
        else:
            angle = math.atan2(dy, dx)
            agent_position = (x1 + agent_speed * math.cos(angle), y1 + agent_speed * math.sin(angle))

        position_queue.put(agent_position)
        time.sleep(1 / FPS)

