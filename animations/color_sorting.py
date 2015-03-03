import random
from cube_model import *

class ColorSorting:

    def __init__(self, n):
        self.n = n

    def next_cube(self):
        while 1==1:
            sorting_cube = self.make_new_sorting_cube()
            for color_cube in sorting_cube.next_cube():
                yield color_cube


    def make_new_sorting_cube(self):
        directions = [0, 1, 2]
        random.shuffle(directions)
        tf = [True, False]
        orientations = [random.choice(tf), random.choice(tf), random.choice(tf)]
        possible_intensities = range(0, 15)
        color_intensities = []
        for i in xrange(0, self.n):
            color = random.choice(possible_intensities)
            possible_intensities.remove(color)
            color_intensities.append(color)
        return SortingCube(self.n, 0.1, directions, orientations, 
                           color_intensities=color_intensities)


class SortingCube:

    # rgb_directions is some ording of the numbers 0, 1, 2 in a list.  
    # comparison_ups is three booleans in a list.  
    def __init__(self, n, duration, rgb_directions, comparison_ups, 
                 color_intensities=[0, 1, 4, 15]):
        self.rgb_directions = rgb_directions
        self.flips = [self.keep_direction if keep else self.flip_direction 
                              for keep in comparison_ups]
        self.n = n
        self.duration = duration
        self.intensities = color_intensities
        self.intensities.sort()
        
        # Initialize the nXnXn cube.  
        self.color_slots = [[[[i, j, k] for k in xrange(self.n)]
                                        for j in xrange(self.n)]
                                        for i in xrange(self.n)]

        # Table of slot names.  Seems sort of silly and redundant.  
        # But it will come in handy when randomly looking at all slots.  
        self.slot_list = []
        for i in xrange(self.n):
            for j in xrange(self.n):
                self.slot_list.extend(self.color_slots[i][j])

        # Need to scramble it, in order to sort it.  
        self.scramble_cube()

        # Table of neighbors.  
        # Two nice things about this.  
        # 1.  We don't have to recalculate valid neighbors all the time.
        # 2.  Handy list form for random neighbor selection.
        # Each neighbor also comes with an index of which slot matters,
        # and also which direction it should go in.  
        self.neighbor_lists = [[[ [([i+1, j, k], 0, 1), ([i-1, j, k], 0, -1), 
                                   ([i, j+1, k], 1, 1), ([i, j-1, k], 1, -1), 
                                   ([i, j, k+1], 2, 1), ([i, j, k-1], 2, -1)
                                  ] for k in xrange(self.n)]
                                    for j in xrange(self.n)]
                                    for i in xrange(self.n)]
        for i in xrange(self.n):
            for j in xrange(self.n):
                for k in xrange(self.n):
                    x = 0
                    while x < len(self.neighbor_lists[i][j][k]):
                        neighbor = self.neighbor_lists[i][j][k][x]
                        # All of these are out-of-bounds neighbors.  
                        if neighbor[0][0] < 0 or \
                                neighbor[0][0] == self.n or \
                                neighbor[0][1] < 0 or \
                                neighbor[0][1] == self.n or \
                                neighbor[0][2] < 0 or \
                                neighbor[0][2] == self.n:
                            self.neighbor_lists[i][j][k].remove(neighbor)
                        else:
                            x = x + 1


    def next_cube(self):
        yield self.get_cube_model()
        counter = 0
        slot_list_copy = []
        slot_list_copy.extend(self.slot_list)
        while 1==1:
            if len(slot_list_copy) == 0:
                break
            c = random.choice(slot_list_copy)
            slot_list_copy.remove(c)
            neighbors_sorted = False
            # We want a copy here, not the original, because we'll change it.
            neighbors_list = self.get_neighbor_list_copy(c)
            while not neighbors_sorted:
                neighbor = random.choice(neighbors_list)
                neighbors_list.remove(neighbor)
                new_c = self.check_and_swap(c, neighbor)
                # This means new_c is an actual value, so the swap was made.
                # That means we should start over.  
                if new_c:
                    counter = counter + 1
                    yield self.get_cube_model()
                    neighbors_list = self.get_neighbor_list_copy(new_c)
                    # The new neighbors list should not include the neighbor 
                    # that we just swapped with.  
                    # This is important because we're swapping equals, 
                    # and that can result in swaps that could just swap right 
                    # back, which makes useless infinite loops.  
                    for neighbor in neighbors_list:
                        if neighbor[0] == c:
                            neighbors_list.remove(neighbor)
                            # We found the one neighbor, no need look further.
                            break
                    c = new_c
                    slot_list_copy = []
                    slot_list_copy.extend(self.slot_list)
                    slot_list_copy.remove(c)
                neighbors_sorted = (len(neighbors_list) == 0)
        print "sorted in %s swaps" % counter
        yield CubeModel(self.n, self.duration)
        for i in xrange(100):
            yield self.get_cube_model()


    # We'll be messing up the list, so make a copy.  
    def get_neighbor_list_copy(self, slot_coords):
        copy = []
        copy.extend(self.neighbor_lists[slot_coords[0]]
                                       [slot_coords[1]]
                                       [slot_coords[2]])
        return copy

    # If we need to swap, return the new location.  
    # Else, return nothing and the caller will try another neighbor.
    def check_and_swap(self, c, neighbor):
        c_color = self.color_slots[c[0]][c[1]][c[2]]
        n_location = neighbor[0]
        n_color = self.color_slots[n_location[0]][n_location[1]][n_location[2]]
        index = neighbor[1]
        sign = neighbor[2]
        # This means the sign of the difference is opposite what we want. 
        # That means we should swap these two colors.
        if ((n_color[index] - c_color[index]) * sign) <= 0:
            self.color_slots[n_location[0]][n_location[1]][n_location[2]] = c_color
            self.color_slots[c[0]][c[1]][c[2]] = n_color
            return n_location


    def scramble_cube(self):
        swap_count = self.n * self.n * self.n * 7
        for s in xrange(swap_count):
            a = [random.randint(0, 3),
                 random.randint(0, 3),
                 random.randint(0, 3)]
            b = [random.randint(0, 3),
                 random.randint(0, 3),
                 random.randint(0, 3)]
            temp = self.color_slots[a[0]][a[1]][a[2]]
            self.color_slots[a[0]][a[1]][a[2]] = \
                    self.color_slots[b[0]][b[1]][b[2]]
            self.color_slots[b[0]][b[1]][b[2]] = temp


    def led_color(self, i):
        return self.intensities[i]

    def flip_direction(self, i):
        return self.n-i-1

    def keep_direction(self, i):
        return i

    def color_from_slot(self, coords):
        changed_coords = [self.flips[0](coords[self.rgb_directions[0]]), 
                          self.flips[1](coords[self.rgb_directions[1]]), 
                          self.flips[2](coords[self.rgb_directions[2]])]
        simple_colors = self.color_slots[changed_coords[0]] \
                                        [changed_coords[1]] \
                                        [changed_coords[2]]
        return Color(self.led_color(simple_colors[0]),
                     self.led_color(simple_colors[1]),
                     self.led_color(simple_colors[2]))


    def get_cube_model(self):
        cube = CubeModel(self.n, self.duration)
        for i in xrange(self.n):
            for j in xrange(self.n):
                for k in xrange(self.n):
                    cube.set_pixel(i, j, k, self.color_from_slot([i, j, k]))
        return cube




