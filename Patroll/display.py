import pygame
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import pygame
import numpy as np
import random
from config import maps
from algos.algoaco import generate_path, generate_path_with_genetic
from algos.algoacoclustering import generate_path_cluster_monobase, generate_path_cluster_multibase

# Constantes utilisées pour l'affichage
WIDTH, HEIGHT = 750, 520
NODE_RADIUS = 10
EDGE_COLOR = (200, 200, 200)
IDLE_COLOR = (255, 0, 0)  # Rouge pour les nœuds inactifs
AGENT_COLOR = (255, 0, 0)  # Couleur de l'agent
AGENT_RADIUS = 5
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (100, 149, 237)

RANDOM_BUTTON = pygame.Rect(
    (WIDTH - BUTTON_WIDTH) // 2,
    (HEIGHT - BUTTON_HEIGHT) // 2 - 20,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)
RUNTIME_BUTTON = pygame.Rect(
    (WIDTH - BUTTON_WIDTH) // 2,
    (HEIGHT - BUTTON_HEIGHT) // 2 + 60,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)
CHEMIN_BUTTON = pygame.Rect(
    (WIDTH - BUTTON_WIDTH) // 2,
    (HEIGHT - BUTTON_HEIGHT) // 2 + 140,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)
MULTIBASE_BUTTON = pygame.Rect(
    (WIDTH - BUTTON_WIDTH) // 2,
    (HEIGHT - BUTTON_HEIGHT) // 2 - 100,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)

# Boutons pour le choix du nombre d'agents (au milieu à droite)
button_width, button_height = 40, 40
center_right_x = WIDTH - 150  # Décalage du bord droit
center_y_button = HEIGHT // 2

MINUS_BUTTON = pygame.Rect(center_right_x - button_width - 20, center_y_button - 25, button_width, button_height)
PLUS_BUTTON = pygame.Rect(center_right_x + 20, center_y_button - 25, button_width, button_height)

MINUS_BUTTON_LOOP = pygame.Rect(center_right_x - button_width - 20, center_y_button - 10, button_width, button_height)
PLUS_BUTTON_LOOP = pygame.Rect(center_right_x + 20, center_y_button - 10, button_width, button_height)


def scaling_nodes_position(nodes_position):
# Calculer les dimensions de la carte d'origine
    min_x = min(node[0] for node in nodes_position)
    max_x = max(node[0] for node in nodes_position)
    min_y = min(node[1] for node in nodes_position)
    max_y = max(node[1] for node in nodes_position)

    map_width = max_x - min_x
    map_height = max_y - min_y

    # Calculer le facteur d'échelle pour ajuster la carte à la fenêtre
    scale_factor = min(WIDTH / map_width, HEIGHT / map_height) * 0.9  # Ajustement à 90% pour éviter le dépassement

    # Calculer les offsets pour centrer la carte après mise à l'échelle
    offset_x = (WIDTH - map_width * scale_factor) / 2
    offset_y = (HEIGHT - map_height * scale_factor) / 2

    # Appliquer les offsets et la mise à l'échelle aux positions des nœuds
    nodes_position = [
        ((x - min_x) * scale_factor + offset_x,
        (y - min_y) * scale_factor + offset_y)
        for x, y in nodes_position
    ]
    return nodes_position

def display_menu(screen):
    # Charger l'image de fond
    try:
        background = pygame.image.load("patrolling-problem\\Patroll\\image1.jpg")
        #background = pygame.image.load("image1.jpg")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
    except pygame.error as e:
        print(f"Erreur lors du chargement de l'image : {e}")

    # Définir les polices
    font_title = pygame.font.Font(None, 50)
    font_button = pygame.font.Font(None, 40)

    # Créer des boutons pour Multi-base et Mono-base
    MULTI_BASE_BUTTON = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 50)
    MONO_BASE_BUTTON = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 35, 300, 50)

    running = True
    selected_mode = None

    while running:
        # Effacer l'écran et afficher l'arrière-plan
        screen.fill(WHITE)
        screen.blit(background, (0, 0))

        # Titre principal
        title = font_title.render("Choisissez un mode :", True, BLACK)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200))
        screen.blit(title, title_rect)

        # Boutons Multi-base et Mono-base
        pygame.draw.rect(screen, LIGHT_BLUE, MULTI_BASE_BUTTON)
        pygame.draw.rect(screen, LIGHT_BLUE, MONO_BASE_BUTTON)

        multi_base_text = font_button.render("Multi-base", True, BLACK)
        mono_base_text = font_button.render("Mono-base", True, BLACK)

        screen.blit(multi_base_text, multi_base_text.get_rect(center=MULTI_BASE_BUTTON.center))
        screen.blit(mono_base_text, mono_base_text.get_rect(center=MONO_BASE_BUTTON.center))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if MULTI_BASE_BUTTON.collidepoint(mouse_pos):
                    selected_mode = "Multi-base"
                    running = False
                elif MONO_BASE_BUTTON.collidepoint(mouse_pos):
                    selected_mode = "Mono-base"
                    running = False

    if selected_mode == "Mono-base":
        return display_menu_monobase(screen)
    elif selected_mode == "Multi-base":
        return display_menu_multibase(screen)


    


def display_menu_monobase(screen):
    # Nombre d'agents (initialement 3)
    num_agents = 3
    num_loop = 5

    # Charger l'image de fond
    try:
        background = pygame.image.load("patrolling-problem\\Patroll\\image1.jpg")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
    except pygame.error as e:
        print(f"Erreur lors du chargement de l'image : {e}")

    # Définir les polices
    font_title = pygame.font.Font(None, 50)
    font_button = pygame.font.Font(None, 40)
    font_label = pygame.font.Font(None, 35)
    font_dropdown = pygame.font.Font(None, 30)
    font_waiting = pygame.font.Font(None, 50)

    # Options des cartes
    listmap = list(maps.keys())
    dropdown_open = False
    selected_map_index = 0
    # Options pour la météo
    weather_options = ["Soleil", "Neige"]
    selected_weather_index = 0

    running = True
    chemins = None  # Variable pour stocker les chemins générés
    while running:
        # Effacer l'écran et afficher l'arrière-plan
        screen.fill(WHITE)
        screen.blit(background, (0, 0))

        # Titre
        title = font_title.render("Choisissez une carte et un algorithme", True, BLACK)
        title_rect = title.get_rect(center=(WIDTH // 2, 50))
        screen.blit(title, title_rect)

        # Boutons pour les algorithmes
        pygame.draw.rect(screen, LIGHT_BLUE, RANDOM_BUTTON)
        pygame.draw.rect(screen, LIGHT_BLUE, RUNTIME_BUTTON)
        pygame.draw.rect(screen, LIGHT_BLUE, CHEMIN_BUTTON)

        # Texte des boutons pour les algorithmes
        random_text = font_button.render("Random", True, BLACK)
        runtime_text = font_button.render("Runtime", True, BLACK)
        chemin_text = font_button.render("Multi-ACO", True, BLACK)

        # Positionnement du texte pour les algorithmes
        screen.blit(random_text, random_text.get_rect(center=RANDOM_BUTTON.center))
        screen.blit(runtime_text, runtime_text.get_rect(center=RUNTIME_BUTTON.center))
        screen.blit(chemin_text, chemin_text.get_rect(center=CHEMIN_BUTTON.center))

        # Ajout du bouton Multi-ACO Cluster
        cluster_button_rect = pygame.Rect((WIDTH - BUTTON_WIDTH) // 2, CHEMIN_BUTTON.bottom + 20, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(screen, LIGHT_BLUE, cluster_button_rect)
        cluster_text = font_button.render("M-ACO Cluster", True, BLACK)
        screen.blit(cluster_text, cluster_text.get_rect(center=cluster_button_rect.center))

        # Section choix du nombre d'agents (ajustée vers le haut)
        label_text = font_label.render("Nombre d'agents", True, BLACK)
        label_rect = label_text.get_rect(center=(150, HEIGHT // 2 - 30))
        screen.blit(label_text, label_rect)

        agents_text = font_label.render(f"{num_agents}", True, BLACK)
        agents_rect = agents_text.get_rect(center=(150, HEIGHT // 2 + 5))
        screen.blit(agents_text, agents_rect)

        # Section choix du nombre de patrouilles
        label_text_loops = font_label.render("Nombre de patrouille ACO", True, BLACK)
        label_rect_loops = label_text_loops.get_rect(center=(150, HEIGHT // 2 - 140))
        screen.blit(label_text_loops, label_rect_loops)

        loops_text = font_label.render(f"{num_loop}", True, BLACK)
        loops_rect = loops_text.get_rect(center=(150, HEIGHT // 2 - 100))
        screen.blit(loops_text, loops_rect)

        # Boutons + et -
        minus_button_loop = pygame.Rect(90, HEIGHT // 2 - 120, 40, 40)
        plus_button_loop = pygame.Rect(170, HEIGHT // 2 - 120, 40, 40)

        minus_button_rect = pygame.Rect(90, HEIGHT // 2 + 25, 40, 40)
        plus_button_rect = pygame.Rect(170, HEIGHT // 2 + 25, 40, 40)

        pygame.draw.rect(screen, DARK_BLUE, minus_button_rect)
        pygame.draw.rect(screen, DARK_BLUE, plus_button_rect)

        pygame.draw.rect(screen, DARK_BLUE, minus_button_loop)
        pygame.draw.rect(screen, DARK_BLUE, plus_button_loop)

        # Texte des boutons
        minus_text = font_button.render("-", True, WHITE)
        plus_text = font_button.render("+", True, WHITE)

        screen.blit(minus_text, minus_text.get_rect(center=minus_button_rect.center))
        screen.blit(plus_text, plus_text.get_rect(center=plus_button_rect.center))

        screen.blit(minus_text, minus_text.get_rect(center=minus_button_loop.center))
        screen.blit(plus_text, plus_text.get_rect(center=plus_button_loop.center))
        
        # Menu déroulant map
        dropdown_rect = pygame.Rect(WIDTH - 250, HEIGHT // 2 - 45, 200, 40)
        pygame.draw.rect(screen, LIGHT_BLUE, dropdown_rect)
        selected_map_text = font_dropdown.render(listmap[selected_map_index], True, BLACK)
        screen.blit(selected_map_text, selected_map_text.get_rect(center=dropdown_rect.center))

        # Texte "Météo" au-dessus du bouton météo
        weather_rect = pygame.Rect(WIDTH - 700, HEIGHT // 2 + 115, 200, 40)
        weather_label = font_label.render("Météo", True, BLACK)
        weather_label_rect = weather_label.get_rect(center=(weather_rect.centerx, weather_rect.top - 20))
        screen.blit(weather_label, weather_label_rect)

        # Menu déroulant pour la météo
        pygame.draw.rect(screen, LIGHT_BLUE, weather_rect)
        selected_weather_text = font_dropdown.render(weather_options[selected_weather_index], True, BLACK)
        screen.blit(selected_weather_text, selected_weather_text.get_rect(center=weather_rect.center))

        if dropdown_open:
            for i, map_name in enumerate(listmap):
                option_rect = pygame.Rect(WIDTH - 250, HEIGHT // 2 - 45 + i * 40, 200, 40)
                pygame.draw.rect(screen, DARK_BLUE if i == selected_map_index else LIGHT_BLUE, option_rect)
                option_text = font_dropdown.render(map_name, True, BLACK)
                screen.blit(option_text, option_text.get_rect(center=option_rect.center))

        # Bouton "Retour"
        return_button_rect = pygame.Rect(WIDTH - 150, HEIGHT - 50, 120, 40)
        pygame.draw.rect(screen, DARK_BLUE, return_button_rect)
        return_text = font_button.render("Retour", True, WHITE)
        screen.blit(return_text, return_text.get_rect(center=return_button_rect.center))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, None, None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if weather_rect.collidepoint(mouse_pos):
                    selected_weather_index = (selected_weather_index + 1) % len(weather_options)

                if dropdown_rect.collidepoint(mouse_pos):
                    dropdown_open = not dropdown_open
                elif dropdown_open:
                    for i, map_name in enumerate(listmap):
                        option_rect = pygame.Rect(WIDTH - 250, HEIGHT // 2 - 45 + i * 40, 200, 40)
                        if option_rect.collidepoint(mouse_pos):
                            selected_map_index = i
                            dropdown_open = False
                            break

                elif RANDOM_BUTTON.collidepoint(mouse_pos):
                    return listmap[selected_map_index], "Random", num_agents, None, weather_options[selected_weather_index]
                elif RUNTIME_BUTTON.collidepoint(mouse_pos):
                    return listmap[selected_map_index], "Runtime", num_agents, None, weather_options[selected_weather_index]
                elif CHEMIN_BUTTON.collidepoint(mouse_pos):
                    screen.fill(WHITE)
                    waiting_text = font_waiting.render("Génération des chemins, veuillez patienter...", True, BLACK)
                    waiting_rect = waiting_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                    screen.blit(waiting_text, waiting_rect)
                    pygame.display.flip()
                    nodes_position = scaling_nodes_position(maps[listmap[selected_map_index]]["nodes"])
                    edges = maps[listmap[selected_map_index]]["edges"]
                    chemins = generate_path(num_agents, nodes_position, edges)
                    return listmap[selected_map_index], "ACO", num_agents, chemins, weather_options[selected_weather_index]
                elif cluster_button_rect.collidepoint(mouse_pos):
                    screen.fill(WHITE)
                    waiting_text = font_waiting.render("Génération des chemins, veuillez patienter...", True, BLACK)
                    waiting_rect = waiting_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                    screen.blit(waiting_text, waiting_rect)
                    pygame.display.flip()
                    nodes_position = scaling_nodes_position(maps[listmap[selected_map_index]]["nodes"])
                    edges = maps[listmap[selected_map_index]]["edges"]
                    chemins = generate_path_cluster_monobase(num_agents, nodes_position, edges, num_loop)
                    return listmap[selected_map_index], "ACO", num_agents, chemins, weather_options[selected_weather_index]
                elif return_button_rect.collidepoint(mouse_pos):
                    return display_menu(screen)
                elif minus_button_rect.collidepoint(mouse_pos) and num_agents > 1:
                    num_agents -= 1
                elif plus_button_rect.collidepoint(mouse_pos) and num_agents < 10:
                    num_agents += 1
                elif minus_button_loop.collidepoint(mouse_pos) and num_loop > 0:
                    num_loop -= 1
                elif plus_button_loop.collidepoint(mouse_pos) and num_loop < 30:
                    num_loop += 1




def display_menu_multibase(screen):
    # Nombre d'agents (initialement 3)
    num_agents = 3

    # Charger l'image de fond
    try:
        background = pygame.image.load("patrolling-problem\\Patroll\\image1.jpg")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
    except pygame.error as e:
        print(f"Erreur lors du chargement de l'image : {e}")

    # Définir les polices
    font_title = pygame.font.Font(None, 50)
    font_button = pygame.font.Font(None, 40)
    font_label = pygame.font.Font(None, 35)
    font_dropdown = pygame.font.Font(None, 30)
    font_waiting = pygame.font.Font(None, 50)

    # Options des cartes
    listmap = list(maps.keys())
    dropdown_open = False
    selected_map_index = 0
    # Options pour la météo
    weather_options = ["Soleil", "Neige"]
    selected_weather_index = 0

    running = True
    chemins = None  # Variable pour stocker les chemins générés
    while running:
        # Effacer l'écran et afficher l'arrière-plan
        screen.fill(WHITE)
        screen.blit(background, (0, 0))

        # Titre
        title = font_title.render("Choisissez une carte et un algorithme :", True, BLACK)
        title_rect = title.get_rect(center=(WIDTH // 2, 50))
        screen.blit(title, title_rect)

        # Boutons pour Multibase repositionnés légèrement plus haut
        multibase_button_rect = pygame.Rect((WIDTH - BUTTON_WIDTH) // 2, HEIGHT // 2 - 40, BUTTON_WIDTH, BUTTON_HEIGHT)
        multiaco_button_rect = pygame.Rect((WIDTH - BUTTON_WIDTH) // 2, multibase_button_rect.bottom + 15, BUTTON_WIDTH, BUTTON_HEIGHT)

        pygame.draw.rect(screen, LIGHT_BLUE, multibase_button_rect)
        pygame.draw.rect(screen, LIGHT_BLUE, multiaco_button_rect)

        # Texte des boutons Multibase
        multiacocluster_text = font_button.render("M-ACO Cluster", True, BLACK)
        genetique_text = font_button.render("Multi ACO", True, BLACK)

        # Positionnement du texte pour les boutons Multibase
        screen.blit(multiacocluster_text, multiacocluster_text.get_rect(center=multibase_button_rect.center))
        screen.blit(genetique_text, genetique_text.get_rect(center=multiaco_button_rect.center))

        # Section choix du nombre d'agents
        label_text = font_label.render("Nombre d'agents", True, BLACK)
        label_rect = label_text.get_rect(center=(150, HEIGHT // 2 - 30))
        screen.blit(label_text, label_rect)

        agents_text = font_label.render(f"{num_agents}", True, BLACK)
        agents_rect = agents_text.get_rect(center=(150, HEIGHT // 2 + 5))
        screen.blit(agents_text, agents_rect)

        # Boutons + et -
        minus_button_rect = pygame.Rect(90, HEIGHT // 2 - 15, 40, 40)
        plus_button_rect = pygame.Rect(170, HEIGHT // 2 - 15, 40, 40)

        pygame.draw.rect(screen, DARK_BLUE, minus_button_rect)
        pygame.draw.rect(screen, DARK_BLUE, plus_button_rect)

        # Texte des boutons
        minus_text = font_button.render("-", True, WHITE)
        plus_text = font_button.render("+", True, WHITE)

        screen.blit(minus_text, minus_text.get_rect(center=minus_button_rect.center))
        screen.blit(plus_text, plus_text.get_rect(center=plus_button_rect.center))

        # Menu déroulant map
        dropdown_rect = pygame.Rect(WIDTH - 250, HEIGHT // 2 - 45, 200, 40)
        pygame.draw.rect(screen, LIGHT_BLUE, dropdown_rect)
        selected_map_text = font_dropdown.render(listmap[selected_map_index], True, BLACK)
        screen.blit(selected_map_text, selected_map_text.get_rect(center=dropdown_rect.center))

        # Texte "Météo" au-dessus du bouton météo
        weather_rect = pygame.Rect(WIDTH - 700, HEIGHT // 2 + 115, 200, 40)
        weather_label = font_label.render("Météo", True, BLACK)
        weather_label_rect = weather_label.get_rect(center=(weather_rect.centerx, weather_rect.top - 20))
        screen.blit(weather_label, weather_label_rect)

        # Menu déroulant pour la météo
        pygame.draw.rect(screen, LIGHT_BLUE, weather_rect)
        selected_weather_text = font_dropdown.render(weather_options[selected_weather_index], True, BLACK)
        screen.blit(selected_weather_text, selected_weather_text.get_rect(center=weather_rect.center))

        if dropdown_open:
            for i, map_name in enumerate(listmap):
                option_rect = pygame.Rect(WIDTH - 250, HEIGHT // 2 - 45 + i * 40, 200, 40)
                pygame.draw.rect(screen, DARK_BLUE if i == selected_map_index else LIGHT_BLUE, option_rect)
                option_text = font_dropdown.render(map_name, True, BLACK)
                screen.blit(option_text, option_text.get_rect(center=option_rect.center))

        # Bouton "Retour"
        return_button_rect = pygame.Rect(WIDTH - 150, HEIGHT - 50, 120, 40)
        pygame.draw.rect(screen, DARK_BLUE, return_button_rect)
        return_text = font_button.render("Retour", True, WHITE)
        screen.blit(return_text, return_text.get_rect(center=return_button_rect.center))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, None, None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if weather_rect.collidepoint(mouse_pos):
                    selected_weather_index = (selected_weather_index + 1) % len(weather_options)

                if dropdown_rect.collidepoint(mouse_pos):
                    dropdown_open = not dropdown_open
                elif dropdown_open:
                    for i, map_name in enumerate(listmap):
                        option_rect = pygame.Rect(WIDTH - 250, HEIGHT // 2 - 45 + i * 40, 200, 40)
                        if option_rect.collidepoint(mouse_pos):
                            selected_map_index = i
                            dropdown_open = False
                            break
                elif multibase_button_rect.collidepoint(mouse_pos):
                    screen.fill(WHITE)
                    waiting_text = font_waiting.render("Génération des chemins, veuillez patienter...", True, BLACK)
                    waiting_rect = waiting_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                    screen.blit(waiting_text, waiting_rect)
                    pygame.display.flip()

                    nodes_position = scaling_nodes_position(maps[listmap[selected_map_index]]["nodes"])
                    edges = maps[listmap[selected_map_index]]["edges"]
                    chemins = generate_path_cluster_multibase(num_agents, nodes_position, edges)

                    return listmap[selected_map_index], "ACO", num_agents, chemins, weather_options[selected_weather_index]
                elif multiaco_button_rect.collidepoint(mouse_pos):
                    screen.fill(WHITE)
                    waiting_text = font_waiting.render("Génération des chemins, veuillez patienter...", True, BLACK)
                    waiting_rect = waiting_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                    screen.blit(waiting_text, waiting_rect)
                    pygame.display.flip()

                    nodes_position = scaling_nodes_position(maps[listmap[selected_map_index]]["nodes"])
                    edges = maps[listmap[selected_map_index]]["edges"]
                    chemins = generate_path_with_genetic(nodes_position, edges, num_agents)

                    return listmap[selected_map_index], "ACO", num_agents, chemins, weather_options[selected_weather_index]
                elif return_button_rect.collidepoint(mouse_pos):
                    return display_menu(screen)
                elif minus_button_rect.collidepoint(mouse_pos) and num_agents > 1:
                    num_agents -= 1
                elif plus_button_rect.collidepoint(mouse_pos) and num_agents < 10:
                    num_agents += 1





def display_graph(screen, FONT, nodes_position, edges, last_visited_shared,num_agents,position_queues,agent_positions):
    
    screen.fill((255, 255, 255))

    # Dessiner les arêtes
    for edge in edges:
        pygame.draw.line(screen, EDGE_COLOR, nodes_position[edge[0]], nodes_position[edge[1]], 2)

    # Dessiner les nœuds et leurs indices
    for i, node in enumerate(nodes_position):
        node_color = calculate_node_color(last_visited_shared[i])
        pygame.draw.circle(screen, node_color, node, NODE_RADIUS)

        # Dessiner l'indice du nœud
        text_surface = FONT.render(str(i), True, (0, 0, 0))  # Texte en noir
        text_x = node[0] - text_surface.get_width() / 2
        text_y = node[1] - text_surface.get_height() / 2
        screen.blit(text_surface, (text_x, text_y))
    
    average_idleness = calculate_average_idleness(last_visited_shared)
    # Afficher l'oisiveté moyenne
    idle_text = f"Oisiveté moyenne : {average_idleness:.2f}"
    idle_surface = FONT.render(idle_text, True, (0, 0, 0))  # Texte en noir
    screen.blit(idle_surface, (10, 10))  # Affiche le texte en haut à gauche
    #Récupérer et dessiner chaque agent
    for i in range(num_agents):
        if not position_queues[i].empty():
            agent_positions[i] = position_queues[i].get()

        pygame.draw.circle(screen, AGENT_COLOR, (int(agent_positions[i][0]), int(agent_positions[i][1])), AGENT_RADIUS)



def display_graph_on_pygame(screen, idleness_data):

    # Dimensions du graphique
    graph_width = int(WIDTH * 0.75) 
    graph_height = int(HEIGHT * 0.75)  

    # Créer le graphique Matplotlib
    fig, ax = plt.subplots(figsize=(graph_width / 100, graph_height / 100))  # Taille en pouces (DPI = 100)
    time_axis = [i / 30 for i in range(len(idleness_data))]  # Axe des temps en secondes
    ax.plot(time_axis, idleness_data, label="Idleness over time", color="blue")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Average Idleness")
    ax.set_title("Average Idleness vs. Time")
    ax.set_xlim(0, 60)
    ax.legend()
    ax.grid()

    # Convertir le graphique en surface pour Pygame
    canvas = FigureCanvas(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = np.frombuffer(renderer.buffer_rgba(), dtype=np.uint8)
    width, height = fig.get_size_inches() * fig.get_dpi()
    surface = pygame.image.frombuffer(raw_data, (int(width), int(height)), "RGBA")

    # Calculer les positions pour centrer le graphique, avec un décalage vers le haut
    x_pos = (WIDTH - graph_width) // 2
    y_pos = (HEIGHT - graph_height) // 2 + 20 # Décalage ajusté pour monter le graphique

    # Afficher le graphique dans Pygame
    screen.blit(surface, (x_pos, y_pos))  # Position centrée
    plt.close(fig)  # Fermer la figure pour libérer des ressources


def end_simulation(screen, FONT, final_average_idleness, max_idleness, agents, idleness_data):
    """
    Affiche la fin de la simulation avec le graphique, l'oisiveté moyenne et maximale.
    :param screen: Surface Pygame
    :param FONT: Police pour le texte
    :param final_average_idleness: Oisiveté moyenne finale
    :param max_idleness: Oisiveté maximale pendant la simulation
    :param agents: Liste des processus des agents
    :param idleness_data: Données d'oisiveté
    """
    screen.fill((255, 255, 255))  # Fond blanc

    # Police agrandie pour "Oisiveté moyenne" et "Oisiveté maximale"
    large_font = pygame.font.Font(None, 40)  # Taille ajustée

    # Afficher "Oisiveté moyenne" en haut, au milieu
    idle_text = f"Oisiveté moyenne : {final_average_idleness:.2f}"
    idle_surface = large_font.render(idle_text, True, (0, 0, 0))  # Texte en noir
    screen.blit(idle_surface, (WIDTH // 2 - idle_surface.get_width() // 2, 10))  # Position en haut au milieu

    # Afficher "Oisiveté maximale" juste en dessous de "Oisiveté moyenne"
    max_idle_text = f"Oisiveté maximale : {max_idleness:.2f}"
    max_idle_surface = large_font.render(max_idle_text, True, (0, 0, 0))  # Texte en noir
    screen.blit(max_idle_surface, (WIDTH // 2 - max_idle_surface.get_width() // 2, 60))  # Position ajustée

    # Dessiner un bouton "Quitter" en bas de l'écran
    quit_button_rect = pygame.Rect(WIDTH - 100, HEIGHT - 40, 80, 30)
    pygame.draw.rect(screen, (0, 0, 255), quit_button_rect)  # Bouton bleu
    quit_text = FONT.render("Quitter", True, (255, 255, 255))
    screen.blit(quit_text, (WIDTH - 95, HEIGHT - 30))

    # Afficher le graphique d'oisiveté
    display_graph_on_pygame(screen, idleness_data)

    pygame.display.flip()

    # Attendre que l'utilisateur clique sur "Quitter"
    waiting_for_quit = True
    while waiting_for_quit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting_for_quit = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if quit_button_rect.collidepoint(event.pos):
                    waiting_for_quit = False

    # Terminer et rejoindre chaque processus
    for agent in agents:
        agent.terminate()
        agent.join()

    pygame.quit()


def calculate_node_color(last_visit_time):
    if last_visit_time is None or last_visit_time == 0:
        # Nœud jamais visité ou initialisé à 0, il est vert
        return (0, 255, 0)  # Vert par défaut

    elapsed_time = time.time() - last_visit_time
    # Interpole entre vert et rouge en fonction du temps depuis la dernière visite
    red_intensity = min(255, int(255 * elapsed_time / 20))  # 20 secondes pour atteindre le rouge complet
    green_intensity = max(0, 255 - red_intensity)
    return (red_intensity, green_intensity, 0)

def calculate_average_idleness(last_visited):
    total_idleness = 0
    node_count = 0

    current_time = time.time()

    for node, last_visit_time in last_visited.items():
        if last_visit_time is not None:
            total_idleness += current_time - last_visit_time
        else:
            # Si un nœud n'a jamais été visité, on peut définir une valeur par défaut (par exemple, 0 ou un grand nombre)
            total_idleness += 20  # Exemple : Oisiveté maximale par défaut
        node_count += 1

    return total_idleness / node_count if node_count > 0 else 0

def calculate_max_idleness(last_visited_shared):
    current_time = time.time()
    return max(
        current_time - last_visit if last_visit is not None else float('inf')
        for last_visit in last_visited_shared.values()
    )

def modify_nodes_with_costs(nodes, increase_factor_range=(1.05, 1.2), percentage=0.2):
    """
    Modifie les positions des nœuds pour simuler un coût accru en neige.

    :param nodes: Liste des positions des nœuds [(x1, y1), (x2, y2), ...].
    :param increase_factor_range: Plage pour augmenter les distances des nœuds.
    :param percentage: Pourcentage de nœuds à modifier.
    :return: Liste des positions des nœuds modifiées.
    """
    num_nodes = len(nodes)
    num_nodes_to_modify = int(num_nodes * percentage)

    # Sélection aléatoire des nœuds à modifier
    nodes_to_modify = random.sample(range(num_nodes), num_nodes_to_modify)

    modified_nodes = []
    for i, (x, y) in enumerate(nodes):
        if i in nodes_to_modify:
            # Augmenter les coordonnées proportionnellement pour simuler un coût accru
            factor = random.uniform(*increase_factor_range)
            modified_nodes.append((x * factor, y * factor))
        else:
            modified_nodes.append((x, y))  # Garder les positions inchangées

    return modified_nodes
