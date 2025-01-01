
import random
import math
import time
from display import *
from config import agent_speed, FPS



def shortest_path(graph, start, end):
    import heapq
    queue = [(0, start, [])]  # (distance, current_node, path)
    visited = set()
    
    while queue:
        (cost, node, path) = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)
        path = path + [node]
        
        if node == end:
            return path
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                heapq.heappush(queue, (cost + 1, neighbor, path))
    
    return []  # Aucun chemin trouvé

def agent_process_runtime(agent_id,agent_speed, nodes_position, edges, num_agents, position_queue, last_visited_shared, shared_list_next_node, lock,agent_positions,shared_list_chemins,node_locked,stop_simulation):
    
    # Informations récupérées depuis graphstructure
    adjacency_list = {i: [] for i in range(len(nodes_position))}
    for a, b in edges:
        adjacency_list[a].append(b)
        adjacency_list[b].append(a)

    agent_position = nodes_position[0]  # Position initiale
    agent_target_position = nodes_position[1]  # Première cible
    agent_node_index = 0
    next_node_index = 0

    while not stop_simulation.value:
        x1, y1 = agent_position
        x2, y2 = agent_target_position
        dx, dy = x2 - x1, y2 - y1
        distance = math.hypot(dx, dy)

        # Si l'agent atteint un nœud
        if distance < agent_speed:
            # Déverrouillage du nœud une fois que l'agent l'a traversé
            if node_locked[agent_node_index]:
                node_locked[agent_node_index] = False

            agent_node_index = next_node_index
            with lock:
                last_visited_shared[agent_node_index] = time.time()  # Mise à jour du temps de visite

            # Décision cognitive : vérifier si on doit aller vers un nœud éloigné avec grande oisiveté
            if not shared_list_chemins[agent_id] and num_agents != 1:  # Si l'agent n'a pas encore de chemin à suivre
                if random.random() < 0.04: 
                    with lock:
                        # Calculer le nœud avec la plus grande oisiveté
                        max_idleness_node = max(
                            range(len(nodes_position)),
                            key=lambda x: (time.time() - last_visited_shared[x])
                            if last_visited_shared[x] is not None else float('inf')
                        )
                        max_idleness_value = (time.time() - last_visited_shared[max_idleness_node]
                                            if last_visited_shared[max_idleness_node] is not None else float('inf'))


                    # Si le nœud est verrouillé, chercher le suivant avec la plus grande oisiveté
                    if node_locked[max_idleness_node]:
                        with lock:
                            sorted_nodes_by_idleness = sorted(
                                range(len(nodes_position)),
                                key=lambda x: (time.time() - last_visited_shared[x])
                                if last_visited_shared[x] is not None else float('inf'),
                                reverse=True
                            )
                        for node in sorted_nodes_by_idleness:
                                if not node_locked[node]:
                                    max_idleness_node = node
                                    break
                        max_idleness_value = (time.time() - last_visited_shared[max_idleness_node]
                                                if last_visited_shared[max_idleness_node] is not None else float('inf'))


                    # 
                    if max_idleness_value > 10:
                        print("Je prends une décision cognitive, Signé agent", agent_id)
                        print("Nœud avec la plus grande oisiveté :", max_idleness_node, "Oisiveté :", max_idleness_value)

                        # Verrouiller le nœud
                        node_locked[max_idleness_node] = True

                        # Trouver l'agent le plus proche de max_idleness_node
                        closest_agent_id = agent_id
                        my_x, my_y = agent_position
                        closest_distance = math.hypot(nodes_position[max_idleness_node][0] - my_x,
                                                    nodes_position[max_idleness_node][1] - my_y)
                        #print("distance,", closest_distance)
                        for other_agent_id in range(agent_id):
                            if other_agent_id != agent_id:
                                other_agent_position = agent_positions[other_agent_id]
                                other_x, other_y = other_agent_position
                                distance_to_max_node = math.hypot(nodes_position[max_idleness_node][0] - other_x,
                                                                nodes_position[max_idleness_node][1] - other_y)
                                if distance_to_max_node < closest_distance:
                                    closest_distance = distance_to_max_node
                                    closest_agent_id = other_agent_id
                        #print("agent plus proche", closest_agent_id)
                        #print("distance,", closest_distance)

                        # Si un agent est plus proche
                        if closest_agent_id != agent_id:
                            if not shared_list_chemins[closest_agent_id]:
                                with lock:
                                    print(f"Agent {agent_id} transfère le chemin à l'agent {closest_agent_id}")
                                    transferttt = shortest_path(adjacency_list, shared_list_next_node[closest_agent_id], max_idleness_node)
                                    print("chemin que je transfere",transferttt)
                                    shared_list_chemins[closest_agent_id] = transferttt
                            else:
                                print("jsuis deja occupé akhy")
                        else:
                            # Calculer le chemin le plus court vers ce nœud
                            monchemin = shortest_path(adjacency_list, agent_node_index, max_idleness_node)
                            print(" Je garde. Voici mon chemin ", monchemin)
                            with lock:
                                shared_list_chemins[agent_id] = monchemin

            if shared_list_chemins[agent_id]:
                # Suivre le chemin calculé
                with lock:
                    shared_list_chemins_local = list(shared_list_chemins[agent_id]) # Crée une copie locale
                next_node_index = shared_list_chemins_local[0]
                shared_list_chemins_local.pop(0)
                if not shared_list_chemins_local:
                    shared_list_chemins_local = None
                with lock:
                    shared_list_chemins[agent_id] = shared_list_chemins_local  # Réécrit dans le ListProxy
            else:
                # Logique normale : choisir parmi les voisins
                voisins = adjacency_list[agent_node_index]
                random.shuffle(voisins)
                next_node_index = min(
                    voisins,
                    key=lambda x: last_visited_shared[x] if last_visited_shared[x] is not None else -float('inf')
                )
                with lock:
                    if next_node_index in shared_list_next_node and len(voisins) > 1:
                        # Choisir un autre voisin parmi les voisins restants
                        voisins_restants = [v for v in voisins if v != next_node_index]  # Liste de voisins sans le nœud actuel
                        # Si nous avons encore des voisins à choisir
                        if voisins_restants:
                            next_node_index = min(
                                voisins_restants,
                                key=lambda x: last_visited_shared[x] if last_visited_shared[x] is not None else -float('inf')
                            )
                        else:
                            # Si aucun autre voisin, on peut reprendre le même ou choisir aléatoirement parmi tous les voisins
                            next_node_index = min(
                                voisins,
                                key=lambda x: last_visited_shared[x] if last_visited_shared[x] is not None else -float('inf')
                            )

            # Mise à jour de la nouvelle cible
            with lock:
                    shared_list_next_node[agent_id] = next_node_index

            agent_target_position = nodes_position[next_node_index]
            print(f"AGENT {agent_id}, Je suis actuellement au noeud {agent_node_index}, Mon chemin pour y aller : {shared_list_next_node[agent_id]}")

        else:
            # Mouvement vers la cible
            angle = math.atan2(dy, dx)
            agent_position = (x1 + agent_speed * math.cos(angle), y1 + agent_speed * math.sin(angle))

        # Envoyer la position actuelle au processus principal
        position_queue.put(agent_position)
        time.sleep(1 / FPS)