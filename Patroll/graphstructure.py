# Graph data
import time 








# # Corridor
# nodes = [(22, 494), (21, 494), (21, 427), (21, 360), (21, 293), (21, 226), (21, 159), (21, 92), (21, 25),
#          (73, 25), (73, 92), (73, 159), (73, 226), (73, 293), (73, 360), (73, 427), (73, 494),
#          (124, 494), (124, 427), (124, 360), (124, 293), (124, 226), (124, 159), (124, 92), (124, 25),
#          (175, 25), (175, 92), (175, 159), (175, 226), (175, 293), (175, 360), (175, 427), (175, 494),
#          (226, 494), (226, 427), (226, 360), (226, 293), (226, 226), (226, 159), (226, 92), (226, 25),
#          (277, 25), (277, 92), (277, 159), (277, 226), (277, 293), (277, 360), (277, 427), (277, 494),
#          (328, 494), (328, 427), (328, 360), (328, 293), (328, 226), (328, 159), (328, 92), (328, 25),
#          (379, 25), (379, 92), (379, 159), (379, 226), (379, 293), (379, 360), (379, 427), (379, 494),
#          (406, 494), (469, 494), (533, 494), (597, 494), (660, 494), (723, 494)]

# edges = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8),
#          (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16),
#          (17, 18), (18, 19), (19, 20), (20, 21), (21, 22), (22, 23), (23, 24),
#          (25, 26), (26, 27), (27, 28), (28, 29), (29, 30), (30, 31), (31, 32),
#          (33, 34), (34, 35), (35, 36), (36, 37), (37, 38), (38, 39), (39, 40),
#          (41, 42), (42, 43), (43, 44), (44, 45), (45, 46), (46, 47), (47, 48),
#          (49, 50), (50, 51), (51, 52), (52, 53), (53, 54), (54, 55), (55, 56),
#          (57, 58), (58, 59), (59, 60), (60, 61), (61, 62), (62, 63), (63, 64),
#          (65, 66), (66, 67), (67, 68), (68, 69), (69, 70), (70, 71), (71, 72),
#          (73, 74), (74, 75), (75, 76), (76, 77), (77, 78), (78, 79), (79, 80)]


# # Grid
# nodes = [(16, 500), (15, 500), (15, 432), (15, 364), (15, 296), (15, 228), (15, 160), (15, 92), (15, 24),
#          (94, 500), (94, 432), (94, 364), (94, 296), (94, 228), (94, 160), (94, 92), (94, 24),
#          (173, 500), (173, 432), (173, 364), (173, 296), (173, 228), (173, 160), (173, 92), (173, 24),
#          (252, 500), (252, 432), (252, 364), (252, 296), (252, 228), (252, 160), (252, 92), (252, 24),
#          (331, 500), (331, 432), (331, 364), (331, 296), (331, 228), (331, 160), (331, 92), (331, 24),
#          (410, 500), (410, 432), (410, 364), (410, 296), (410, 228), (410, 160), (410, 92), (410, 24),
#          (489, 500), (489, 432), (489, 364), (489, 296), (489, 228), (489, 160), (489, 92), (489, 24),
#          (568, 500), (568, 432), (568, 364), (568, 296), (568, 228), (568, 160), (568, 92), (568, 24),
#          (647, 500), (647, 432), (647, 364), (647, 296), (647, 228), (647, 160), (647, 92), (647, 24),
#          (726, 500), (726, 432), (726, 364), (726, 296), (726, 228), (726, 160), (726, 92), (726, 24)]

# edges = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8),
#          (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16),
#          (17, 18), (18, 19), (19, 20), (20, 21), (21, 22), (22, 23), (23, 24),
#          (25, 26), (26, 27), (27, 28), (28, 29), (29, 30), (30, 31), (31, 32),
#          (33, 34), (34, 35), (35, 36), (36, 37), (37, 38), (38, 39), (39, 40),
#          (41, 42), (42, 43), (43, 44), (44, 45), (45, 46), (46, 47), (47, 48),
#          (49, 50), (50, 51), (51, 52), (52, 53), (53, 54), (54, 55), (55, 56),
#          (57, 58), (58, 59), (59, 60), (60, 61), (61, 62), (62, 63), (63, 64),
#          (65, 66), (66, 67), (67, 68), (68, 69), (69, 70), (70, 71), (71, 72),
#          (73, 74), (74, 75), (75, 76), (76, 77), (77, 78), (78, 79), (79, 80),
#          (8, 16), (7, 15), (6, 14), (5, 13), (4, 12), (3, 11), (2, 10), (1, 9),
#          (16, 24), (15, 23), (14, 22), (13, 21), (12, 20), (11, 19), (10, 18), (9, 17),
#          (24, 32), (23, 31), (22, 30), (21, 29), (20, 28), (19, 27), (18, 26), (17, 25),
#          (32, 40), (31, 39), (30, 38), (29, 37), (28, 36), (27, 35), (26, 34), (25, 33),
#          (40, 48), (39, 47), (38, 46), (37, 45), (36, 44), (35, 43), (34, 42), (33, 41),
#          (48, 56), (47, 55), (46, 54), (45, 53), (44, 52), (43, 51), (42, 50), (41, 49),
#          (56, 64), (55, 63), (54, 62), (53, 61), (52, 60), (51, 59), (50, 58), (49, 57),
#          (64, 72), (63, 71), (62, 70), (61, 69), (60, 68), (59, 67), (58, 66), (57, 65),
#          (72, 80), (71, 79), (70, 78), (69, 77), (68, 76), (67, 75), (66, 74), (65, 73)]


#Island
nodes_position = [(40, 490), (128, 490), (40, 430), (128, 430), (83, 460), (83, 401), (171, 460),
         (628, 490), (717, 490), (628, 430), (717, 430), (673, 460), (673, 401), (584, 460),
         (40, 96), (128, 96), (39, 37), (128, 37), (84, 67), (84, 128), (171, 68),
         (628, 96), (717, 96), (628, 37), (717, 37), (672, 67), (672, 127), (584, 68),
         (334, 489), (422, 489), (334, 430), (422, 430),
         (40, 293), (127, 293), (40, 234), (127, 234),
         (334, 96), (422, 96), (334, 37), (422, 37),
         (627, 292), (717, 292), (627, 234), (717, 234),
         (334, 293), (421, 293), (334, 234), (421, 234), (379, 264), (466, 264)]


edges = [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 4), (1, 4), (0, 4), (2, 5), (5, 3), (3, 6), (6, 1),
         (14, 15), (15, 17), (17, 16), (16, 14), (16, 18), (18, 17), (18, 15), (18, 14), (14, 19), (19, 15), (15, 20), (20, 17),
         (23, 21), (21, 22), (22, 24), (23, 24), (23, 25), (24, 25), (22, 25), (21, 25), (23, 27), (27, 21), (21, 26), (26, 22),
         (7, 9), (9, 10), (10, 8), (7, 8), (9, 11), (10, 11), (8, 11), (7, 11), (7, 13), (13, 9), (9, 12), (10, 12),
         (13, 29), (29, 31), (30, 31), (28, 30), (28, 29), (6, 28),
         (5, 32), (32, 33), (33, 35), (35, 34), (32, 34), (19, 35),
         (20, 38), (38, 36), (36, 37), (37, 39), (38, 39), (39, 27),
         (26, 42), (42, 43), (43, 41), (40, 41), (40, 42), (41, 12),
         (3, 44), (44, 46), (46, 47), (47, 45), (44, 45), (46, 48), (47, 48), (44, 48), (45, 48), (47, 48), (45, 49), (47, 49), (49, 21)]


#Map A
nodes_position = [
        (0, 0), (50, 0), (100, 0), (130, 0), (230, 0), (260, 0), (340, 20), (0, 60),
        (50, 50), (100, 60), (140, 40), (230, 40), (260, 30), (320, 30), (200, 60),
        (260, 50), (320, 50), (140, 80), (270, 80), (0, 100), (80, 100), (140, 100),
        (170, 100), (270, 100), (320, 110), (360, 115), (0, 120), (110, 120), (170, 120),
        (280, 120), (170, 130), (280, 130), (360, 130), (0, 150), (80, 150), (130, 150),
        (250, 165), (300, 160), (110, 180), (80, 190), (170, 180), (290, 200), (360, 180),
        (80, 210), (0, 220), (110, 230), (160, 230), (20, 240), (190, 240), (340, 240)
    ]
edges = [
    (0, 1), (0, 7), (1, 2), (1, 8), (2, 3), (2, 9), (2, 10), (3, 4), (3, 9), (3, 10),
    (4, 5), (4, 11), (5, 6), (5, 12), (6, 12), (6, 13), (7, 8), (7, 9), (7, 19),
    (8, 9), (9, 10), (9, 17), (9, 20), (10, 14), (10, 17), (11, 12), (11, 14), (11, 15),
    (12, 13), (12, 15), (13, 16), (14, 15), (14, 17), (14, 18), (15, 16), (15, 18),
    (16, 18), (16, 24), (17, 20), (17, 21), (18, 23), (18, 24), (19, 20), (19, 26),
    (20, 27), (20, 30), (21, 22), (21, 27), (22, 23), (22, 28), (22, 35), (22, 36),
    (23, 24), (23, 28), (23, 29), (23, 36), (24, 25), (24, 29), (25, 32), (26, 33),
    (27, 28), (27, 34), (27, 35), (28, 29), (28, 30), (29, 30), (29, 31), (30, 35),
    (30, 36), (31, 32), (31, 36), (31, 37), (32, 42), (33, 34), (33, 44), (34, 35),
    (34, 38), (34, 39), (34, 44), (35, 38), (36, 37), (36, 40), (36, 41), (37, 41),
    (37, 42), (38, 39), (38, 40), (39, 40), (39, 43), (39, 44), (39, 45), (39, 47),
    (40, 41), (40, 46), (41, 42), (41, 49), (42, 49), (43, 45), (43, 47), (44, 47),
    (45, 46), (46, 48), (47, 48), (48, 49)
]

#Circle
nodes_position = [
    (59, 72), (68, 60), (80, 49), (92, 39), (104, 32),
    (118, 26), (132, 25), (145, 25), (159, 25), (172, 26),
    (186, 22), (198, 23), (212, 24), (223, 26), (234, 29),
    (246, 35), (254, 39), (268, 45), (280, 48), (292, 48),
    (305, 48), (320, 49), (335, 55), (347, 64), (357, 76),
    (362, 86), (364, 98), (359, 116), (352, 127), (347, 137),
    (338, 149), (325, 164), (314, 168), (305, 174), (292, 177),
    (280, 176), (267, 177), (258, 174), (247, 171), (234, 167),
    (222, 169), (209, 167), (196, 166), (182, 168), (169, 171),
    (157, 174), (145, 174), (134, 174), (114, 172), (97, 165),
    (82, 155), (66, 144), (52, 132), (44, 115), (46, 98),
    (51, 82)
]

edges = [
    (0, 1), (0, 55), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8),
    (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16),
    (16, 17), (17, 18), (18, 19), (19, 20), (20, 21), (21, 22), (22, 23),
    (23, 24), (24, 25), (25, 26), (26, 27), (27, 28), (28, 29), (29, 30),
    (30, 31), (31, 32), (32, 33), (33, 34), (34, 35), (35, 36), (36, 37),
    (37, 38), (38, 39), (39, 40), (40, 41), (41, 42), (42, 43), (43, 44),
    (44, 45), (45, 46), (46, 47), (47, 48), (48, 49), (49, 50), (50, 51),
    (51, 52), (52, 53), (53, 54), (54, 55)
]

# Map B
nodes_position = [
    (0, 0), (50, 0), (100, 0), (130, 0), (230,  0), 
    (260,  0), (340, 20), (0, 60), (50,  50), (100,  60), 
    (140,  40), (230,  40), (260,  30), (320,  30), (200,  60), 
    (260,  50), (320, 50), (140,  80), (270,  80), (0,  100), 
    (80,  100), (140,  100), (170, 100), (270,  100), (320,  110), 
    (360,  115), (0,  120), (110,  120), (170,  120), (280,  120), 
    (170,  130), (280,  130), (360,  130), (0,  150), (80,  150), 
    (130,  150), (250,  165), (300,  160), (110,  180), (80,  190), 
    (170,  180), (290,  200), (360,  180), (80,  210), (0,  220), 
    (110,  230), (160, 230), (20,  240), (190,  240), (340,  240)
]

edges = [
    (0, 1), (0, 7), (1, 2), (1, 8), (2, 9), (3, 4), (3, 10), (4, 5), (4, 11),
    (6, 13), (7, 8), (7, 9), (7, 19), (8, 9), (9, 20), (10, 14), (10, 17), (11, 14),
    (12, 13), (12, 15), (13, 16), (14, 17), (14, 18), (15, 16), (16, 24), (17, 21),
    (18, 23), (19, 20), (19, 26), (20, 27), (21, 22), (22, 23), (22, 28), (24, 25),
    (24, 29), (25, 32), (26, 33), (27, 28), (27, 34), (28, 29), (28, 30), (29, 31),
    (30, 35), (30, 36), (31, 32), (31, 37), (32, 42), (33, 34), (33, 44), (34, 44),
    (35, 38), (36, 40), (36, 41), (37, 42), (38, 39), (38, 40), (39, 40), (39, 43),
    (39, 45), (39, 47), (40, 41), (40, 46), (41, 49), (43, 45), (43, 47), (45, 46),
    (46, 48), (47, 48), (48, 49)
]




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