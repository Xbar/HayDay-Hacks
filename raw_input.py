#!/usr/bin/env python

import pandas as pd
import numpy as np
import re

def parse_time(time_str):
    time_val = 0
    
    m = re.search('[0-9]+ d', time_str)
    if m is not None:
        time_val += int(((m.group(0)).split())[0]) * 24 * 60
    m = re.search('[0-9]+ h', time_str)
    if m is not None:
        time_val += int(((m.group(0)).split())[0]) * 60
    m = re.search('[0-9]+ min', time_str)
    if m is not None:
        time_val += int(((m.group(0)).split())[0])
    return time_val
    
    
def input_time(time_str):
    reduce_pos = time_str.find('|')
    l1_str = time_str
    l2_str = ''
    if reduce_pos >= 0:
        l1_str = time_str[:reduce_pos]
        l2_str = time_str[(reduce_pos + 1):]
    return (parse_time(l1_str), parse_time(l2_str))
    
def safe_int(str):
    try:
        return int(str)
    except ValueError:
        m = re.search('[0-9]+', str)
        if m is None:
            print str
            return str
        else:
            return int(m.group(0))
    
def parse_name(str):
    m = re.search('\[\[.+\]\]', str)
    str = m.group()
    pos = str.find('|')
    if pos >= 0:
        return str[:pos] + ']]'
    return str

def parse_needs(str):
    p = re.compile('\[\[[A-Za-z0-9 \|]+\]\]s{0,1}\([0-9]+\)')
    needs = p.findall(str)
    result = {}
    for item in needs:
        try:
            m = re.search('\[\[.+\]\]', item)
            n = re.search('\([0-9]+\)', item)
            result[parse_name(m.group())] = int((n.group())[1:-1])
        except:
            print item
    return result

def read_items(file):
    items = {'Name':[], 'Level':[], 'Price':[], 'Time':[], 'Reduction':[], 'XP':[], 'Needs':[], 'Source':[]}
    with open(file, 'r') as meta:
        counter = 0
        for line in meta:
            if line[0] == '#':
                continue
            if counter == 0:
                items['Name'].append(parse_name(line[:-1]))
            elif counter == 1:
                items['Level'].append(safe_int(line[:-1]))
            elif counter == 2:
                items['Price'].append(safe_int(line[:-1]))
            elif counter == 3:
                times = input_time(line[:-1])
                items['Time'].append(times[0])
                items['Reduction'].append(times[1])
            elif counter == 4:
                items['XP'].append(safe_int(line[:-1]))
            elif counter == 5:
                items['Needs'].append(parse_needs(line[:-1]))
            elif counter == 6:
                items['Source'].append(parse_name(line[:-1]))
            counter += 1
            counter = counter % 9
    return pd.DataFrame.from_dict(items)

if __name__ == '__main__':
    item_list = read_items('item.txt')
    item_list.to_csv('items.csv', index=False)
    
    