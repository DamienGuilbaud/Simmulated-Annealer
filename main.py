import networkx as nx
# import igraph
import matplotlib.pyplot as plt
import numpy as np
import math
import random
import copy
from IPython.core.debugger import set_trace
from tqdm import tqdm_notebook, tnrange

def one_list(old_list):
    new_list = []
    for sublist in old_list:
        for item in sublist:
            new_list.append(item)
    return new_list

#generate sample network

num_nodes = 50
g=nx.generators.watts_strogatz_graph(num_nodes,2,1)
g_start = g.copy()

# use simulated annealing to obtain optimal graph layout--only switches nodes

# start with random layout
# define the grid with grid_step, and draw coordinates from it
# linspace(start,stop,num items)
# (num+1)^2 is number of points on grid

grid_coord = []
xy_pair = []
x_max = num_nodes * 100
y_max = num_nodes * 100
grid_step = 5
num = x_max // grid_step
x_values = list(np.linspace(0, x_max, num + 1))
y_values = list(np.linspace(0, y_max, num + 1))
num_points = (num + 1) ** 2
# problem: what if grid step is so large that num becomes very small, and so nodes will have overlapping locations
# solution: x_max will grow with more nodes, so num will also grow with more nodes. keep grid step constant
# currently, num = (100/5)*num_nodes = 20*num_nodes. As long as 100/grid_step => 1, num=>num_nodes
# currently have (20*num_nodes+1)^2 points on grid

# have x and y-values, now need to assign random coordinates to each node in optimized fashion
# x_values = random.shuffle(x_values)
# y_values = random.shuffle(y_values)
random.shuffle(x_values)
random.shuffle(y_values)

# rand_x = x_values[0:num_nodes]
# rand_y = y_values[0:num_nodes]
# rand_pos = list(zip(rand_x,rand_y))
rand_pos = []
for i in range(num_nodes):
    rand_coord = [x_values[i], y_values[i]]
    rand_pos.append(rand_coord)
rand_pos_copy = copy.deepcopy(rand_pos)
rand_pos_opt = copy.deepcopy(rand_pos)

# show random network

plt.figure(figsize=(8, 6))
nx.draw_networkx(g, rand_pos)  # node1 gets first rand_coord, node2 gets second rand_coord, and so on
plt.title('Random Position Network')
#plt.show()

#calculate wire length of random network

def calculateDistance(x1,y1,x2,y2):
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
     return dist

def calc_wire_length(g):
    wires = g.edges
    wires = list(wires)
    wire_len = []
    for i in wires:
        node1 = i[0]
        node2 = i[1]
        x1 = rand_pos[node1][0]
        y1 = rand_pos[node1][1]
        x2 = rand_pos[node2][0]
        y2 = rand_pos[node2][1]
        dist = calculateDistance(x1,y1,x2,y2)
        wire_len.append(dist)
    tot_wire_len = sum(wire_len)
    return tot_wire_len

def calc_wire_length_opt(g):
    wires = g.edges
    wires = list(wires)
    wire_len = []
    for i in wires:
        node1 = i[0]
        node2 = i[1]
        x1 = rand_pos_opt[node1][0]
        y1 = rand_pos_opt[node1][1]
        x2 = rand_pos_opt[node2][0]
        y2 = rand_pos_opt[node2][1]
        dist = calculateDistance(x1,y1,x2,y2)
        wire_len.append(dist)
    tot_wire_len = sum(wire_len)
    return tot_wire_len


tot_wire_len_random = calc_wire_length(g)
tot_wire_len_before = calc_wire_length(g)

% % time
T = 500  # hot
frozen = 0
m = 100  # swaps per temp
count = 0
while frozen == 0:
    wire_len_previous_temp = tot_wire_len_before
    for s in range(m * num_nodes):
        node1 = random.randint(0, num_nodes - 1)
        node2 = random.randint(0, num_nodes - 1)
        x1 = rand_pos[node1][0]
        y1 = rand_pos[node1][1]
        x2 = rand_pos[node2][0]
        y2 = rand_pos[node2][1]
        rand_pos[node1][0] = x2
        rand_pos[node2][0] = x1
        rand_pos[node1][1] = y2
        rand_pos[node2][1] = y1
        tot_wire_len_now = calc_wire_length(
            g)  # don't have to calculate all wire lengths, can just calculate wire length based off change
        delta_L = tot_wire_len_now - tot_wire_len_before
        if delta_L < 0:
            tot_wire_len_before = tot_wire_len_now
        if delta_L > 0:
            if np.random.uniform(0, 1) > math.exp(-1 * delta_L / T):
                rand_pos[node1][0] = x1
                rand_pos[node1][1] = y1
                rand_pos[node2][0] = x2
                rand_pos[node2][1] = y2
            else:
                tot_wire_len_before = tot_wire_len_now

    if tot_wire_len_before >= wire_len_previous_temp:
        count = count + 1
        if count == 3:  # change to: if less than 1% difference, stop...but maybe still require 3 times in a row for random cases
            frozen = 1
        T = 0.9 * T
    else:
        count = 0
        rand_pos_opt = copy.deepcopy(rand_pos)
        T = 0.9 * T

plt.figure(figsize=(12, 4))

plt.subplot(121)
nx.draw_networkx(g,rand_pos_copy)
plt.title('Orignal Random Network')

plt.subplot(122)
nx.draw_networkx(g,rand_pos_opt)
plt.title('Optimized Visual Layout')

plt.show()
tot_wire_len_optimized = calc_wire_length_opt(g)

print("Random network total wire length:",tot_wire_len_random)
print("Optimized network total wire length:",tot_wire_len_optimized)
