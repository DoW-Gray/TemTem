#!/usr/bin/env python3.8
# vim: set fileencoding=utf-8 :
"""
temtem_parser.py: Reformat temtem api data into yaml for this library
Copyright (C) 2020 DoW

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import os
import sys

import json
import yaml

from typing import Dict, List


def moves(techs: List[Dict[str, str]]) -> Dict[str, List[str]]:
    res = {'Egg': [], 'Level Up': [], 'TC': []}
    for tech in techs:
        res[{
            'Breeding': 'Egg',
            'Levelling': 'Level Up',
            'TechniqueCourses': 'TC',
        }[tech['source']]].append(tech['name'])
    return res


def types(types: List[str]) -> List[str]:
    if len(types) == 2:
        return [type.lower() for type in types]
    return [types[0].lower(), None]


def stats(stats: Dict[str, int]) -> Dict[str, int]:
    return {
        {
            'hp': 'HP',
            'sta': 'Sta',
            'spd': 'Spe',
            'atk': 'Atk',
            'def': 'Def',
            'spatk': 'SpA',
            'spdef': 'SpD',
            'total': 'BST',
        }[stat]: val
        for stat, val in stats.items()
    }


def main(f_names: List[str]):
    with open(f_names[0], 'r') as fp:
        inpt = json.loads(fp.read())

    output = {
        tem['name']: {
            'Name': tem['name'],
            'No.': tem['number'],
            'Types': types(tem['types']),
            'Stats': stats(tem['stats']),
            'Traits': tem['traits'],
            'Moves': moves(tem['techniques']),
            'Catch Rate': tem['catchRate'],
        } for tem in inpt
    }

    output = yaml.dump(output, indent=4).replace('- ', '  - ')

    if len(f_names) > 1:
        out_file = f_names[1]
        if os.path.exists(out_file):
            if not input(f'Overwrite {out_file}? (y/N) ').lower().startswith('y'):
                print(f'Not overwriting {out_file}')
                exit(0)
        with open(out_file, 'w') as fp:
            print(output, file=fp)
    else:
        print(output, file=sys.stdout)


if __name__ == '__main__':
    argv = sys.argv[1:]
    if not argv or any('-h' in arg for arg in argv):
        print(f'Usage: {__file__} path/to/knownTemtemSpecies.json')
        exit(0)

    main(argv)
