#!/usr/bin/env python

from farm import *
from evolver import *
import numpy as np
import random
import os

# def find_available_name(path):
#     from os import listdir
#     from os.path import join
#     files = [f for f in listdir(path)]
#     num = 1
#     while True:
#         filename = "result%03d" % num
#         if not (filename in files):
#             return join(path, filename)
#         num += 1


class GoldEvolver(Evolution):
    def score(self, queue, inventory):
        gold = 0
        for item in inventory:
            gold += self.farm.get_price(item) * inventory[item]['Quantity']
        return gold

if __name__ == '__main__':
    seed = np.fromstring(os.urandom(4), dtype=np.uint32)
    random.seed(seed[0])
    my_farm = HayDayFarm('items.csv', 'equip.csv', 40)
    my_nature = GoldEvolver(my_farm, read_from='results', player_num=200, write_to='goldres')
    score = my_nature.evolve(selection_round=20)
    print score
    # item_list = my_farm.get_item_list()
    # p1 = Player(item_list)
    # p1.target = {'[[Bacon and Eggs]]': 1,
    #              '[[Bacon]]': 0,
    #              '[[Blackberry Jam]]': 3,
    #              '[[Blue Sweater]]': 1,
    #              '[[Butter]]': 0,
    #              '[[Casserole]]': 1,
    #              '[[Cheesecake]]': 5,
    #              '[[Hamburger]]': 1,
    #              '[[Honey Popcorn]]': 4,
    #              '[[Potato Bread]]': 3,
    #              '[[Red Berry Cake]]': 1,
    #              '[[Strawberry Cake]]': 3,
    #              '[[Strawberry]]': 3,
    #              '[[Tomato]]': 1,
    #              '[[Violet Dress]]': 3}
    # p1.target = {'[[Blackberry Jam]]': 3}
    # (t, q) = p1.play(my_farm)
    # while t > 1000:
    #     new_player = Player.from_deduction(p1)
    #     print new_player.target
    #     (t2, q) = new_player.play(my_farm)
    #     if t2 < t:
    #         t = t2
    #         p1 = new_player
    # print t, p1.target
    # print t
    # for item in p1.target:
    #     num = p1.target[item]
    #     p1.target[item] = 0
    #     (t, q) = p1.play(my_farm)
    #     print t, item
    #     p1.target[item] = num
    # p1.save(find_available_name('.'))
