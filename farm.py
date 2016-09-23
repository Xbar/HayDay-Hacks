#!/usr/bin/env python

import pandas as pd


class HayDayFarm:
    item_list = pd.DataFrame()
    equip_list = pd.DataFrame()

    def __init__(self, item_file, equip_file, player_level):
        """Initialize farm.
        
        Keyword arguments:
        item_file    -- csv file describing items produced on the farm
        equip_file   -- csv file describing production facilities on the farm
        player_level -- level of the player
        """
        item_list = pd.read_csv(item_file, index_col='Name')
        self.item_list = item_list[item_list['Level'] <= player_level]

        need_list = []
        for _ in range(self.item_list.shape[0]):
            need_list.append(eval(self.item_list['Needs'][_]))
        self.item_list = self.item_list.assign(Needs=need_list)
        
        equip_list = pd.read_csv(equip_file, index_col='Name')
        self.equip_list = equip_list[equip_list['Level'] <= player_level]
        self._clean_items()
        
#    def get_terminal(self):
#        items = set(self.item_list.index)
#        for need_dict in self.item_list['Needs']:
#            for item in need_dict.keys():
#                items.discard(item)
#        return items

    def get_item_list(self):
        return list(self.item_list.index)

    def get_downstream(self, item):
        assert item in self.item_list.index, "Cannot make item %s" % item
        downstream_list = []
        for idx in self.item_list.index:
            if item in self.item_list.loc[idx, 'Needs']:
                downstream_list.append(idx)
        return downstream_list

    def get_upstream(self, item):
        assert item in self.item_list.index, "Cannot make item %s" % item
        return self.item_list.loc[item, 'Needs']

    def get_xp(self, item):
        assert item in self.item_list.index, "Cannot make item %s" % item
        return self.item_list.loc[item, 'XP']

    def get_price(self, item):
        assert item in self.item_list.index, "Cannot make item %s" % item
        return self.item_list.loc[item, 'Price']

    def get_source(self, item):
        assert item in self.item_list.index, "Cannot make item %s" % item
        return self.item_list.loc[item, 'Source']

    def _clean_items(self):
        """Internal function for cleaning up the item list
        
        Recursively remove any items that
         -- Require unlisted items
         -- Or require unlisted production facilities
        """
        ban_items = set()
        select_list = [True] * (self.item_list.shape[0])

        equips = set(self.equip_list.index)
        for _ in xrange(self.item_list.shape[0]):
            if not (self.item_list['Source'][_] in equips):
                select_list[_] = False
                ban_items.add(self.item_list.index[_])

        items = set(self.item_list.index)
        for _ in xrange(self.item_list.shape[0]):
            need_dict = self.item_list['Needs'][_] 
            for item in need_dict.keys():
                if not (item in items):
                    select_list[_] = False
                    ban_items.add(self.item_list.index[_])
        ban_num = 0
        while len(ban_items) > ban_num:
            ban_num = len(ban_items)
            for _ in xrange(self.item_list.shape[0]):
                need_dict = self.item_list['Needs'][_]
                for item in need_dict.keys():
                    if item in ban_items:
                        select_list[_] = False
                        ban_items.add(self.item_list.index[_])
        self.item_list = self.item_list[select_list]

    def init_inventory(self):
        items = set(self.item_list.index)
        items = list(items)
        inventory = {}
        for _ in items:
            inventory[_] = {'Quantity': 0, 'Since': 0}
            source = self.item_list.loc[_, 'Source']
            inventory[_]['Quantity'] = self.equip_list.loc[source, 'Startup']
        return inventory

    @staticmethod
    def _get_waiting(item_dict, job_queue):
        if len(job_queue) == 0:
            return 0
        start_time = item_dict['Start']
        duration = item_dict['Duration']
        current_start = start_time
        wait_time = 0
        for item in job_queue:
            item_start = item['Start']
            item_end = item['Duration'] + item_start
            if ((((item_start >= current_start) and
               (item_start < current_start + duration)) or
              ((item_end >= current_start) and (item_end < current_start + duration))) and
              (item_end - start_time > wait_time)):
                wait_time = item_end - start_time
                current_start = item_end
        return wait_time

    def _add_to_queue(self, item, num, equip_queue, inventory,
                      send_to=None, priority=None, replenish=None,):
        """
        Return the time when the items are finished.
        
        Keyword arguments:
        item        -- Name of the item to produce
        num         -- quantity needed
        equip_queue -- Dictionary describing status of all facilities
        send_to     -- Next step equipment and status
        
        Items are added to production queue as dictionaries, 
        with the following fields,
            Start:     start of production
            Duration:  duration of production
            NextEquip: the downstream equipment
            NextDict:  dictionary for production in the next step
        Queue insertion works as follows,
        Insert to the queue with least waiting time
        """
        time = self.item_list.loc[item, 'Time']
        equip = self.item_list.loc[item, 'Source']
        
        if inventory[item]['Quantity'] > 0:  # Taken from inventory
            if (inventory[item]['Since'] > 0) or (  # Newly made products
                self.equip_list.loc[equip, 'Replenish'] == 0) or (  # No need to replenish
                 replenish is not None):   # will mark to replenish
                delta_num = min(num, inventory[item]['Quantity'])
                num -= delta_num
                inventory[item]['Quantity'] -= delta_num
                if (self.equip_list.loc[equip, 'Replenish'] == 1) and (  # Need to replenish
                     replenish is not None):
                    replenish[item] += delta_num
                if num <= 0:
                    return inventory[item]['Since']
        
#        if inventory[item]['Quantity'] >= num:  # Taken from inventory
#            if (inventory[item]['Since'] > 0) or (replenish is not None):
#                inventory[item]['Quantity'] -= num
#                if (self.equip_list.loc[equip, 'Replenish'] == 1) and\
#                     (replenish is not None):
#                    replenish[item] += num
#                return inventory[item]['Since']
#        elif inventory[item]['Quantity'] > 0:  # Taken from and then produce some
#            if (inventory[item]['Since'] > 0) or (replenish is not None):
#                if replenish is not None:
#                    replenish[item] += inventory[item]['Quantity']
#                num -= inventory[item]['Quantity']
#                inventory[item]['Quantity'] = 0
        slots = (num - 1) / self.equip_list.loc[equip, 'Produce'] + 1
    #    slots = (num - 1) / (equip_list.loc[equip, 'Slot'] * equip_list.loc[equip, 'Produce']) + 1
        occupy_time = {'Name': item, 'Start': 0, 'Duration': time,
                       'NextEquip': None, 'NextDict': None}
        if send_to is not None:
            occupy_time['NextEquip'] = send_to['NextEquip']
            occupy_time['NextDict'] = send_to['NextDict']
        
        need_dict = self.item_list.loc[item, 'Needs']
        need_list = need_dict.keys()
        if priority is not None:
            need_list = sorted(need_list, key=lambda x: priority[x])
        
        finish_time = time
        for item_index in xrange(slots):
            head_time = 0
            item_dict = dict(occupy_time)
            if len(need_list) > 1 or need_list != [item]:
                for need_item in need_list:
                    item_time = self._add_to_queue(need_item, need_dict[need_item], 
                                                   equip_queue, inventory,
                                                   send_to={'NextEquip': equip,
                                                   'NextDict': item_dict},
                                                   priority=priority,
                                                   replenish=replenish)
                    if item_time > head_time:
                        head_time = item_time

            item_dict['Start'] = head_time
            add_to_queue = []
            found_queue = False
            min_waiting = 1e9
            for (_index, queue) in enumerate(equip_queue[equip]):
                waiting = self._get_waiting(item_dict, queue)
                if waiting < min_waiting:
                    min_waiting = waiting
                    add_to_queue = queue
                    found_queue = True
            assert found_queue, "Unable to insert item into a valid queue"
            item_dict['Start'] = item_dict['Start'] + min_waiting
            add_to_queue.append(item_dict)
            if finish_time < item_dict['Start'] + item_dict['Duration']:
                finish_time = item_dict['Start'] + item_dict['Duration']
        if slots * self.equip_list.loc[equip, 'Produce'] > num:
            assert inventory[item]['Quantity'] == 0
            inventory[item]['Quantity'] = slots * self.equip_list.loc[equip, 'Produce'] - num
            inventory[item]['Since'] = finish_time
        return finish_time

    def produce(self, target, priority=None):
        """Return the time and production queue to produce the target items
        
        Keyword arguments:
        target -- Dictionary of items to be produced, with the key as the name,
                    and value as quantity
        """
        equip_queue = {key: []
                       for key in self.equip_list.index}
        for key in self.equip_list.index:
            for _ in xrange(self.equip_list.loc[key, 'Slot']):
                equip_queue[key].append([])
        inventory = self.init_inventory()
        replenish = {key: 0 for key in self.item_list.index}
        
        total_time = 0
        item_time = 0
        items = target.keys()
        if priority is not None:
            items = sorted(items, key=lambda x: priority[x])
        for item in items:
            if target[item] > 0:
                item_time = self._add_to_queue(item, target[item], equip_queue, 
                                               inventory, priority=priority,
                                               replenish=replenish)
            if total_time < item_time:
                total_time = item_time
        items = replenish.keys()
        if priority is not None:
            items.sort(key=lambda x: priority[x])
        for item in replenish:
            if replenish[item] > 0:
                item_time = self._add_to_queue(item, replenish[item], equip_queue,
                                               inventory, priority=priority)
            if total_time < item_time:
                total_time = item_time
        return total_time, equip_queue, inventory

# if __name__ == '__main__':
#     my_farm = HayDayFarm('items.csv', 'equip.csv', 40)
#     my_todo = dict(zip(my_farm.item_list.index[:5], [2, 4, 3, 3, 4]))
#     (tot_time, queue) = my_farm.produce(my_todo)
#    item_list = pd.read_csv('items.csv', index_col='Name')
#    item_list = item_list.set_index('Name')
#    my_items = item_list[item_list['Level'] < 40]
#    need_list = []
#    for _ in range(my_items.shape[0]):
#        need_list.append(eval(my_items['Needs'][_]))
#    for _ in my_items.index:
#        my_items.loc[_, 'Needs'] = \
#            eval(my_items.loc[_, 'Needs'])
#    my_items['Needs'] = need_list
#    my_items = my_items.assign(Needs = need_list)
    
#    equip_list = pd.read_csv('equip.csv', index_col='Name')
#    my_equip = equip_list[equip_list['Level'] < 40]
#    my_items = clean_items(my_items, my_equip)
#    my_inventory = init_inventory(my_items)
    
#    my_todo = dict(zip(my_items.index[:5], [2, 4, 3, 3, 4]))
#    my_todo = {'[[Chicken Feed]]':2}
#    (tot_time, queue) = produce(my_todo, my_items, my_equip)
