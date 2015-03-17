#!/usr/bin/env python
"""
    Arbalet - ARduino-BAsed LEd Table
    Arbamodel - Arbalet State

    Store a snapshot of the table state

    Copyright (C) 2015 Yoan Mollard <yoan@konqifr.fr>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from Arbapixel import *
from copy import deepcopy
from itertools import product

class Arbamodel(object):
    # line, column
    def __init__(self, width, height, *color):
        self.height = height
        self.width = width
        self.state = [[Arbapixel(*color) if len(color)>0 else Arbapixel('black') for j in range(width)] for i in range(height)]
        self.groups = {}
        self.reverse_groups = [[None for j in range(width)] for i in range(height)]

    def copy(self):
        return deepcopy(self)

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_pixel(self, h, w):
        return self.state[h][w]

    def set_pixel(self, h, w, *color):
        self.state[h][w] = Arbapixel(*color)
        self.delete_from_group([(h, w)])

    def group_pixels(self, pixels, group_name, *color):
        if not (isinstance(pixels, list) or isinstance(pixels, tuple)) and len(pixels)>0 and \
            (isinstance(pixels[0], list) or isinstance(pixels[0], tuple) and len(pixels[0])==2):
            raise Exception("[Arbamodel.create_groupe] Unexpected parameter type {}, must be a list of coordinates".format(type(pixels)))
        pixel = Arbapixel(*color)
        for h,w in pixels:
            self.state[h][w] = pixel

        # Remove pixels from a former group
        self.delete_from_group(pixels)

        if not self.groups.has_key(group_name):
            self.groups[group_name] = set()
        self.groups[group_name] = self.groups[group_name].union(map(tuple, pixels))
        for h, w in pixels:
            self.reverse_groups[h][w] = group_name

    def set_group(self, group_name, *color):
        h, w = next(iter(self.groups[group_name])) # raises a StopIteration if group is empty
        self.state[h][w].set_color(*color)

    def delete_from_group(self, pixels):
        if not (isinstance(pixels, list) or isinstance(pixels, tuple)) and len(pixels)>0 and \
        (isinstance(pixels[0], list) or isinstance(pixels[0], tuple) and len(pixels[0])==2):
            raise Exception("[Arbamodel.delete_from_group] Unexpected parameter type {}, must be a list of coordinates".format(type(pixels)))

        for h, w in pixels:
            if self.reverse_groups[h][w]:
                group_name = self.reverse_groups[h][w]
                self.groups[group_name].remove((h, w))
                self.reverse_groups[h][w] = None
                # If group has no more pixel, delete it
                if len(self.groups[group_name])==0:
                    self.groups.pop(group_name)
                # Copy a new instance of this pixel, apart from the group
                self.state[h][w] = deepcopy(self.state[h][w])

    def get_groups(self):
        return self.groups

    def set_all(self, *color):
        if not self.groups.has_key('all'):
            self.group_pixels(list(product(range(self.height), range(self.width))), "all", *color)
        else:
            self.state[0][0].set_color(*color)

    def __add__(self, other):
        model = Arbamodel(self.width, self.height)
        for w in range(self.width):
            for h in range(self.height):
                model.state[h][w] = self.state[h][w] + other.state[h][w]
        return model

    def __eq__(self, other):
        for w in range(self.width):
            for h in range(self.height):
                if self.state[h][w] != other.state[h][w]:
                    return False
        return True

    def __sub__(self, other):
        model = Arbamodel(self.width, self.height)
        for w in range(self.width):
            for h in range(self.height):
                model.state[h][w] = self.state[h][w] - other.state[h][w]
        return model

    def __repr__(self):
        return self.state

    def __str__(self):
        return str(self.state)

    def __mul__(self, m):
        model = Arbamodel()
        for w in range(self.width):
            for h in range(self.height):
                model.state[h][w] = self.state[h][w]*m
        return model

if __name__ == '__main__':
    m = Arbamodel(10, 10, 'black')
    m.group_pixels(zip(range(10), range(10)), "my_red_pixels", 'red')
    print m
    m.delete_from_group([[0,0]])
    m.set_group("my_red_pixels", "white")
    print m