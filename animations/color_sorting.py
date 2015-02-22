import random
import pprint
from cube_model import *

class ColorSorting:

    def __init__(self, n):
        self.n = n
        self.sorting_cube = SortingCube(n, 0.1, [0, 1, 2], [True, True, True])
        

    def next_cube(self):
        return self.sorting_cube.next_cube()


class SortingCube:

    intensities = [0, 1, 4, 15]

    # rgb_directions is some ording of the numbers 0, 1, 2 in a list.  
    # comparison_ups is three booleans in a list.  
    def __init__(self, n, duration, rgb_directions, comparison_ups):
        self.rgb_directions = rgb_directions
        self.flips = [self.keep_direction if keep else self.flip_direction 
                              for keep in comparison_ups]
        self.n = n
        self.duration = duration
        
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
                print "we kinda think we're sorted"
                print "here's the result:\n%s" % pprint.pformat(self.color_slots)
                break
            c = random.choice(slot_list_copy)
            slot_list_copy.remove(c)
            print "there are %s slots in the cube copy" % len(slot_list_copy)
            neighbors_sorted = False
            # We want a copy here, not the original, because we'll change it.
            neighbors_list = self.get_neighbor_list_copy(c)
            if c[0] == 0 and c[1] == 0 and c[2] == 0:
                print "%s    %s" % (pprint.pformat(c), pprint.pformat(neighbors_list))
            counter = counter + 1
            print "neighbors were sorted, starting a random slot %s" % counter
            while not neighbors_sorted:
                neighbor = random.choice(neighbors_list)
                neighbors_list.remove(neighbor)
                new_c = self.check_and_swap(c, neighbor)
                # This means new_c is an actual value, so the swap was made.
                # That means we should start over.  
                if new_c:
                    yield self.get_cube_model()
                    c = new_c
                    neighbors_list = self.get_neighbor_list_copy(c)
                    slot_list_copy = []
                    slot_list_copy.extend(self.slot_list)
                    slot_list_copy.remove(c)
                neighbors_sorted = (len(neighbors_list) == 0)


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
        if c[1] == 0 and c[2] == 0:
            print "checking %s against %s" % (pprint.pformat(c), pprint.pformat(neighbor))
            print "colors:  %s and %s" % (pprint.pformat(c_color), pprint.pformat(n_color))
        # This means the sign of the difference is opposite what we want. 
        # That means we should swap these two colors.
        if ((n_color[index] - c_color[index]) * sign) < 0:
            self.color_slots[n_location[0]][n_location[1]][n_location[2]] = c_color
            self.color_slots[c[0]][c[1]][c[2]] = n_color
            if c[1] == 0 and c[2] == 0:
                print "swapped"
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
        return SortingCube.intensities[i]

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




