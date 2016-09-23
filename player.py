#!/usr/bin/env python

import pickle
import random


class Player:
    priority = {}
    target = {}
    
    def __init__(self, item_list=None, num_target=10,
                 num_production=5):
        if item_list is not None:
            items = [_ for _ in item_list]
            ranks = list(range(len(items)))
            random.shuffle(ranks)
            self.priority = dict(zip(items, ranks))

            target_items = random.sample(self.priority, num_target)
            target_produce = [random.randint(0, num_production) for _ in range(num_target)]
            self.target = dict(zip(target_items, target_produce))
        
    def save(self, filename):
        with open(filename, 'w') as f:
            pickle.dump(self.priority, f)
            pickle.dump(self.target, f)
        
    def load(self, filename):
        with open(filename, 'r') as f:
            self.priority = pickle.load(f)
            self.target = pickle.load(f)
    
    def play(self, farm):
        return farm.produce(self.target, self.priority)

    @staticmethod
    def clean_dict(input_dict):
        assert isinstance(input_dict, dict), "Input must be a dictionary"
        drop_list = []
        for x in input_dict:
            if input_dict[x] <= 0:
                drop_list.append(x)
        for x in drop_list:
            input_dict.pop(x)
        return input_dict

    @classmethod
    def from_deduction(cls, origin):
        """Initialize by removing one item from the original"""
        assert isinstance(origin, cls), "input is not a player, type: " + str(type(origin))
        new_player = cls()
        new_player.priority = dict(origin.priority)
        new_player.target = dict(origin.target)
        drop_item = random.sample(new_player.target.keys(), 1)
        new_player.target.pop(drop_item[0])
        # new_player.target[drop_item[0]] -= 1
        # cls.clean_dict(new_player.target)
        return new_player

    @classmethod
    def from_file(cls, filename):
        new_player = cls()
        new_player.load(filename)
        return new_player

    @classmethod
    def from_hybrid(cls, first, second):
        """Initialize by hybridizing two players"""
        assert isinstance(first, cls), "first is not a player, type: " + str(type(first))
        assert isinstance(second, cls), "second is not a player, type: " + str(type(second))
        assert len(first.priority) == len(second.priority)
        new_player = cls(first.priority)
        
        items = first.priority.keys()
        item_score = [0] * len(items)
        for idx, item in enumerate(items):
            item_score[idx] = first.priority[item] + second.priority[item]
        new_priority = sorted(list(range(len(items))), key=lambda x: item_score[x])
        new_player.priority = dict(zip(items, new_priority))
        new_target = set(first.target.keys() + second.target.keys())
        new_player.target = {}
        for item in new_target:
            # new_player.target[item] = 0
            if (item in first.target) and (item in second.target):
                if random.random() > 0.5:
                    new_player.target[item] = first.target[item]
                else:
                    new_player.target[item] = second.target[item]
            elif item in first.target:
                if random.random() > 0.5:
                    new_player.target[item] = first.target[item]
            else:
                if random.random() > 0.5:
                    new_player.target[item] = second.target[item]
        # cls.clean_dict(new_player.target)
        return new_player
    
    @classmethod
    def from_mutation(cls, origin, target_num=1, delta_quant=2):
        """Initialize by mutate the original one"""
        assert isinstance(origin, cls), "input is not a player, type: " + str(type(origin))
        new_player = cls(origin.priority)
        items = [_ for _ in origin.priority]
        target = random.sample(items, target_num)
        for item in target:
            if item in new_player.target:
                delta_value = random.randint(1, delta_quant)
                if random.random() < 0.5:
                    delta_value = - delta_value
                new_player.target[item] += delta_value
                if new_player.target[item] <= 0:
                    new_player.target.pop(item)
            else:
                new_player.target[item] = random.randint(1, delta_quant)
        # prior_item = random.sample(items, target_num * 2)
        # for _ in range(0, len(prior_item), 2):
        #     item1 = prior_item[_]
        #     item2 = prior_item[_ + 1]
        #     (new_player.priority[item1],
        #      new_player.priority[item2]) = (new_player.priority[item2],
        #                                     new_player.priority[item1])
        # cls.clean_dict(new_player.target)
        return new_player
