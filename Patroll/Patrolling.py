
import pygame
import multiprocessing
import time
from graphstructure import *  # Assurez-vous que nodes et edges sont définis dans graphstructure
from collections import deque  # Pour BFS
from display import *
from Patroll.algos.algoruntime import *
from Patroll.algos.algorandom import *
import pygame


if __name__ == '__main__':
    # Utiliser un dictionnaire partagé pour `last_visited`
    manager = multiprocessing.Manager()
    last_visited_shared = manager.dict({i: None for i in range(len(nodes_position))})
    # Create a shared list with three elements
    shared_list_next_node = manager.list([0] * num_agents)  # Shared list initialized to [0, 0, 0]
    shared_list_chemins = manager.list([None] * num_agents)
    lock = multiprocessing.Lock()  # Lock to avoid concurrent writes
    # Création des files de communication et des processus pour chaque agent
    position_queues = []
    agents = []
    initial_node = nodes_position[1]
    initial_target_node = nodes_position[2]
    agent_positions = manager.list([initial_node] * num_agents)
    node_locked = manager.dict({i: False for i in range(len(nodes_position))})
    stop_simulation = manager.Value('b', False)  # 'b' pour booléen
    
    # Initialisation de pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Agent - Graph Simulation")
    clock = pygame.time.Clock()
    font_size = 12  # Taille de la police
    FONT = pygame.font.Font(None, font_size)  # Charger la police par défaut

    algorithm = display_menu(screen,FONT)

    for i in range(num_agents):
        if algorithm == "Random":
            position_queue = multiprocessing.Queue()
            position_queues.append(position_queue)
            agent = multiprocessing.Process(target=agent_process_BFS, args=(i, position_queue, last_visited_shared, shared_list_next_node, lock))
            agents.append(agent)
            agent.start()
        elif algorithm == "Runtime":
            position_queue = multiprocessing.Queue()
            position_queues.append(position_queue)
            agent = multiprocessing.Process(target=agent_process, args=(i, position_queue, last_visited_shared, shared_list_next_node, lock,agent_positions,shared_list_chemins,node_locked,stop_simulation))
            agents.append(agent)
            agent.start()

    running = True
    start_time = time.time()
    total_idleness = 0
    total_seconds = 0

    idleness_data = []

    while running:
        elapsed_time = time.time() - start_time
        if elapsed_time >= 2:
            running = False
            stop_simulation.value = True
        display_graph(screen, FONT,nodes_position, edges, last_visited_shared,num_agents,position_queues,agent_positions)
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
        clock.tick(FPS)

        # Calculer l'oisiveté moyenne pendant la simulation
        current_idleness = calculate_average_idleness(last_visited_shared)
        idleness_data.append(current_idleness)
        total_idleness += current_idleness  # Ajouter l'oisiveté du moment
        total_seconds += 1  # Incrémenter le nombre de secondes
    
    final_average_idleness = total_idleness / total_seconds if total_seconds > 0 else 0
    end_simulation(screen, FONT, final_average_idleness,agents,idleness_data)
