import random
import time
import math
from cube_model import *

class SeasonLights:

    def __init__(self, light_lists, tick_speed, flip_rate, solid_season_length, 
                 edge_length=4):
        self.starting_time = time.time()
        self.tick_speed = tick_speed
        self.flip_rate = flip_rate
        self.solid_season_length = solid_season_length
        self.light_lists = light_lists
        self.edge_length = edge_length
        max_time = 0
        for light in light_lists[0]:
            max_time = max(max_time, light.loop_duration)
        max_time = max_time / 4

        self.holder_cube = [[[0 for k in xrange(0, edge_length)]
                                for j in xrange(0, edge_length)]
                                for i in xrange(0, edge_length)]
        self.holder_list = []
        dark = Color(0, 0, 0)
        for i in xrange(0, edge_length):
            for j in xrange(0, edge_length):
                for k in xrange(0, edge_length):
                    dark_light_loop = random.uniform(0, max_time)
                    light = Light([[dark, dark_light_loop]])
                    light_holder = LightHolder(light)
                    self.holder_cube[i][j][k] = light_holder
                    self.holder_list.append(light_holder)

    @staticmethod
    def get_default_lights():
        winter_color_timings = []
        for i in xrange(1, 15):
            winter_color_timings.append([Color(0, 0, i), 0.3])
        for i in xrange(1, 15):
            winter_color_timings.append([Color(0, i, 15), 0.3])
        for i in xrange(1, 14):
            winter_color_timings.append([Color(i, 15, 15), 0.3])
        winter_color_timings.append([Color(15, 15, 15), 1])
        for i in xrange(1, 15):
            winter_color_timings.append([Color(15-i, 15-i, 15), 0.3])
        for i in xrange(1, 15):
            winter_color_timings.append([Color(0, 0, 15-i), 0.3])
        winter_light = Light(winter_color_timings)
        
        spring_green_timings = []
        for i in xrange(4, 15):
            spring_green_timings.append([Color(0, i, 0), 0.3])
        for i in xrange(1, 12):
            spring_green_timings.append([Color(i, 15, 0), 0.3])
        for i in xrange(4, 15):
            spring_green_timings.append([Color(15-i, 15, 0), 0.3])
        for i in xrange(1, 11):
            spring_green_timings.append([Color(0, 15-i, 0), 0.3])
        spring_flower_timings = []
        for i in xrange(7, 15):
            spring_flower_timings.append([Color(i, 0, 15), 0.3])
        for i in xrange(1, 15):
            spring_flower_timings.append([Color(15, i, 15-i), 0.3])
        for i in xrange(1, 15):
            spring_flower_timings.append([Color(15, 15-i, i), 0.3])
        for i in xrange(1, 8):
            spring_flower_timings.append([Color(15-i, 0, 15), 0.3])
        spring_green_light = Light(spring_green_timings)
        spring_flower_light = Light(spring_flower_timings)

        summer_timings = []
        for i in xrange(1, 15):
            summer_timings.append([Color(0, i, 0), 0.3])
        for i in xrange(0, 14):
            summer_timings.append([Color(0, 15-i, 0), 0.3])
        summer_light = Light(summer_timings)

        autumn_timings = []
        for i in xrange(0, 15):
            autumn_timings.append([Color(i, 15, 0), 0.3])
        for i in xrange(0, 15):
            autumn_timings.append([Color(15, 15-i, 0), 0.3])
        for i in xrange(0, 15):
            autumn_timings.append([Color(15, i, 0), 0.3])
        for i in xrange(0, 15):
            autumn_timings.append([Color(15-i, 15, 0), 0.3])
        autumn_light = Light(autumn_timings)

        return SeasonLights([[winter_light], 
                             [spring_green_light, spring_green_light, 
                              spring_flower_light, spring_flower_light],
                             [summer_light],
                             [autumn_light]
                            ], 0.05, 0.25, 10)


    def next_cube(self):
        cube = CubeModel(self.edge_length, self.tick_speed)
        current_list_num = 0
        current_list = self.light_lists[current_list_num]
        while 1==1:
            new_holders = []
            flip_session_start_time = time.time() - self.starting_time
            flips = 0
            # do all of the transitions
            while len(self.holder_list) > 0:
                current_time = time.time() - self.starting_time
                if self.flip_rate * flips < current_time - flip_session_start_time:
                    flips = flips + 1
                    holder = random.choice(self.holder_list)
                    self.holder_list.remove(holder)
                    new_holders.append(holder)
                    holder.add_light(random.choice(current_list), current_time)
                
                self.fill_cube_in_from_holders(cube, self.holder_cube, current_time)
                yield cube
            
            self.holder_list.extend(new_holders)
            current_list_num = (current_list_num + 1) % len(self.light_lists)
            current_list = self.light_lists[current_list_num]

            # It takes a while for the new lights to actually push out
            # the old ones.  Wait for that to happen, so we get some solid 
            # time betwen seasons.  
            old_lights_still_exist = True
            while old_lights_still_exist:
                light_counts = []
                old_lights_still_exist = False
                for holder in self.holder_list:
                    light_counts.append(len(holder.lights))
                    old_lights_still_exist = old_lights_still_exist or (len(holder.lights) > 1)
                
                current_time = time.time() - self.starting_time
                self.fill_cube_in_from_holders(cube, self.holder_cube, current_time)
                yield cube

            solid_season_start = time.time()
            while time.time() < solid_season_start + self.solid_season_length:
                self.fill_cube_in_from_holders(cube, self.holder_cube, time.time() - self.starting_time)
                yield cube
            



    def fill_cube_in_from_holders(self, cube, holders, time):
        for i in xrange(0, self.edge_length):
            for j in xrange(0, self.edge_length):
                for k in xrange(0, self.edge_length):
                    cube.set_pixel(i, j, k, 
                                   holders[i][j][k].get_color_from_time(time))





class LightHolder:

    def __init__(self, light):
        self.time_offset = 0
        self.lights = [light]

    def add_light(self, light, current_time):
        self.lights.append(light)
        self.burnout_loop = self.lights[0].get_loop(current_time-self.time_offset)

    def get_color_from_time(self, time):
        adjusted_time = time - self.time_offset
        if len(self.lights) > 1:
            light = self.lights[0]
            if light.get_loop(adjusted_time) > self.burnout_loop:
                self.time_offset = self.time_offset + \
                                   (self.burnout_loop+1) * light.loop_duration
                adjusted_time = time - self.time_offset
                self.lights.pop(0)

        return self.lights[0].get_color_from_time(adjusted_time)


class Light:

    def __init__(self, color_timings):
        self.color_timings = color_timings
        self.loop_duration = 0
        for color_timing in color_timings:
            self.loop_duration = self.loop_duration + color_timing[1]

    def get_color_from_time(self, time):
        time = time % self.loop_duration
        i = 0
        while time >= 0:
            time = time - self.color_timings[i][1]
            i = i + 1

        return self.color_timings[i-1][0]

    def get_loop(self, time):
       return math.floor(time/self.loop_duration)

 
