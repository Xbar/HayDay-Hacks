#!/usr/bin/env python

from player import *
import random
import sys


class Evolution:
    player_list = []
    score_list = []
    time_limit = 24 * 60
    farm = None

    def __init__(self, farm, time_limit=24*60, player_num=1000, read_from=None):
        self.time_limit = time_limit
        self.farm = farm
        item_list = farm.get_item_list()
        if read_from is None:
            for _ in xrange(player_num):
                self.player_list.append(Player(item_list))
        else:
            from os import listdir
            from os.path import isfile, join
            files = [join(read_from, f) for f in listdir(read_from)
                     if f[:6] == 'player' and isfile(join(read_from, f))]
            assert len(files) > 0, "Unable to find record files in the given directory"
            player_num = len(files)
            for _ in xrange(player_num):
                self.player_list.append(Player.from_file(files[_]))
        self.score_list = [0] * player_num

    def score(self, queue):
        queue_score = 0
        for equip in queue:
            for sub_queue in queue[equip]:
                for job in sub_queue:
                    item = job['Name']
                    xp = self.farm.get_xp(item)
                    queue_score += xp
        return queue_score

    def evolve(self, selection_round=1, survival_rate=0.2):
        assert (survival_rate > 0) and (survival_rate < 0.5), "Survival rate cannot be too high or too low"
        num_survivor = int(len(self.player_list) * survival_rate)
        assert num_survivor >= 2, "At least 2 individuals must survive to spawn off next generation"
        max_score = 0
        for _ in range(selection_round):
            print "Start selection round", _ + 1
            for idx in xrange(len(self.player_list)):
                # print "Player: ", idx
                if idx % 100 == 0 and idx > 0:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                sys.stdout.write(".")
                (time_elapse, queue) = self.player_list[idx].play(self.farm)
                retry_counter = 5
                while retry_counter > 0 and time_elapse > self.time_limit:
                    self.player_list[idx] = Player.from_deduction(self.player_list[idx])
                    (time_elapse, queue) = self.player_list[idx].play(self.farm)
                    retry_counter -= 1
                if time_elapse > self.time_limit:
                    self.score_list[idx] = 0
                else:
                    self.score_list[idx] = self.score(queue)

            # select survivors
            next_players = [y for (x, y) in sorted(zip(self.score_list, self.player_list),
                                                   reverse=True)]
            self.score_list.sort(reverse=True)
            if max_score < self.score_list[0]:
                max_score = self.score_list[0]
            for idx in xrange(num_survivor, num_survivor * 2):
                parents = random.sample(next_players[:num_survivor], 2)
                next_players[idx] = Player.from_hybrid(parents[0], parents[1])

            for idx in xrange(num_survivor * 2, len(next_players)):
                next_players[idx] = Player.from_mutation(next_players[idx - 2 * num_survivor])
            self.player_list = next_players
            print "Finished round", _ + 1
            print "Max score is", max_score
        self.dump_result(num_items=num_survivor)
        return max_score

    def dump_result(self, path='results', num_items=None):
        from os.path import join
        counter = 1
        for player in self.player_list:
            filename = join(path, 'player%04d' % counter)
            player.save(filename)
            counter += 1
            if num_items is not None and counter > num_items:
                break
