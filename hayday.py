#!/usr/bin/env python

import pandas as pd
import numpy as np
import re

def get_terminal(item_list):
    items = set(item_list['Name'])
    for need_str in item_list['Needs']:
        need_dict = eval(need_str)
        for item in need_dict.keys():
            items.discard(item)
    return items

if __name__ == '__main__':
    item_list = pd.read_csv('items.csv')
    my_items = item_list[item_list['Level'] < 40]
    terminals = get_terminal(my_items)
    
    