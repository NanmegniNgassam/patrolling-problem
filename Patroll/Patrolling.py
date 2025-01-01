
import pygame
import multiprocessing
import time
from display import *
from algos.algorandom import *
from algos.algoruntime import *
from algos.algochemin import *
from algos.algoaco import generate_path
from algos.algoacoclustering import *

if __name__ == '__main__':
    # Initialisation de pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Agent - Graph Simulation")
    clock = pygame.time.Clock()
    FONT = pygame.font.Font(None, 12)  

    selected_map, algorithm, num_agents, chemins, weather = display_menu(screen)
    if selected_map in maps:
         nodes_position = scaling_nodes_position(maps[selected_map]["nodes"])
         edges = maps[selected_map]["edges"]
    if weather == "Pluie":
        nodes_position = scaling_nodes_position(modify_nodes_with_costs(nodes_position))
        agent_speed = 4

    # Utiliser un dictionnaire partagé pour `last_visited`
    manager = multiprocessing.Manager()
    last_visited_shared = manager.dict({i: time.time() for i in range(len(nodes_position))})
    # Create a shared list with three elements
    shared_list_next_node = manager.list([0] * num_agents)  # Shared list initialized to [0, 0, 0]
    shared_list_chemins = manager.list([None] * num_agents)
    lock = multiprocessing.Lock()  # Lock to avoid concurrent writes
    # Création des files de communication et des processus pour chaque agent
    position_queues = []
    agents = []
    initial_node = nodes_position[0]
    initial_target_node = nodes_position[1]
    agent_positions = manager.list([initial_node] * num_agents)
    node_locked = manager.dict({i: False for i in range(len(nodes_position))})
    stop_simulation = manager.Value('b', False)  # 'b' pour booléen
    

    for i in range(num_agents):
        position_queue = multiprocessing.Queue()
        position_queues.append(position_queue)
        if algorithm == "Random":
            agent = multiprocessing.Process(target=agent_process_random, args=(i,agent_speed, nodes_position, edges, position_queue, last_visited_shared, lock,stop_simulation))
        elif algorithm == "Runtime":
            agent = multiprocessing.Process(target=agent_process_runtime, args=(i,agent_speed,nodes_position,edges, num_agents,position_queue, last_visited_shared, shared_list_next_node, lock,agent_positions,shared_list_chemins,node_locked,stop_simulation))
        elif algorithm == "ACO":
            agent = multiprocessing.Process(target=agent_process_chemins, args=(i,agent_speed, nodes_position, position_queue, chemins[i], last_visited_shared,stop_simulation))
        elif algorithm == "M-ACOCluster":
            agent = multiprocessing.Process(target=agent_process_chemins, args=(i,agent_speed, nodes_position, position_queue, chemins[i], last_visited_shared,stop_simulation))
        agents.append(agent)    
        agent.start()

    running = True
    start_time = time.time()
    total_idleness = 0
    total_took = 0
    idleness_data = []
    while running:
        elapsed_time = time.time() - start_time
        if elapsed_time >= 60:
            running = False
            stop_simulation.value = True
        display_graph(screen, FONT,nodes_position, edges, last_visited_shared,num_agents,position_queues,agent_positions)
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                stop_simulation.value = True

        pygame.display.flip()
        clock.tick(FPS)

        # Calculer l'oisiveté moyenne pendant la simulation
        current_idleness = calculate_average_idleness(last_visited_shared)
        idleness_data.append(current_idleness)
        total_idleness += current_idleness  # Ajouter l'oisiveté du moment
        total_took += 1  # Incrémenter le nombre de prise d'info
    
    final_average_idleness = total_idleness / total_took if total_took > 0 else 0
    end_simulation(screen, FONT, final_average_idleness,agents,idleness_data)
