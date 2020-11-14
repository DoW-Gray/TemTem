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
from copy import deepcopy
import re

from typing import Dict, List, Union

MoveDict = Dict[str, Union[str, int]]

VERBOSE = False

TARGET_LOOKUP = {
    'Self': 'self',
    'Single Target': 'single',
    'Single Other Target': 'other',
    'Other Team or Ally': 'team or ally',
    'Single Team': 'team',
    'All': 'all',
    # TODO
}
PRIORITY_LOOKUP = {
    'verylow': 0,
    'low': 1,
    'normal': 2,
    'high': 3,
    'veryhigh': 4,
    'ultra': 5,
}


def parse_move(move):
    name = move['name']
    res = {
        'class': move['class'],
        'type': move['type'].lower(),
        'damage': move['damage'],
        'stamina': move['staminaCost'],
        'hold': move['hold'],
        'priority': PRIORITY_LOOKUP[move['priority']],
        'target': TARGET_LOOKUP[move['targets']],
    }
    if move['effects'] or move['class'] == 'Status':
        # It's too difficult to try and parse the effects data in
        # techniques.json, it's just too unreliable. So just put the
        # effectText here and have a human do it :(
        res['effect text'] = move['effectText']

    if move['synergy'] not in {"None", "?", ""}:
        res['synergy type'] = move['synergy'].lower()
        yield name, res

        name = f'{name} +{move["synergy"].lower()}'
        res = deepcopy(res)
        res['synergy effects'] = move['synergyEffects']
        res['synergy move'] = True
        yield name, res
    else:
        yield name, res


def main(f_names: List[str]):
    with open(f_names[0], 'r') as fp:
        inpt = json.loads(fp.read())

    output = {}
    for move in inpt:
        try:
            for name, data in parse_move(move):
                output[name] = data
        except Exception as err:
            if not re.search(
                r'un(available|obtainable).*unknown.? what', move['description']
            ):  # we can silently skip unreleased moves
                print(f'Unable to parse {move["name"]}, ignoring', file=sys.stderr)
                if VERBOSE:
                    print(move, file=sys.stderr)
                    print(err, file=sys.stderr)

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
        print(f'Usage: {__file__} path/to/techniques.json')
        exit(0)

    for verbose_arg in ('-v', '--verbose'):
        if verbose_arg in argv:
            VERBOSE = True
            argv.remove(verbose_arg)
            break

    main(argv)
