#!/usr/bin/env python3.8
"""
tests.py: unit tests for the library
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

from sys import stderr

import consts
from consts import Stats, Types

GYALIS_DATA = (
    {
        Stats.HP: 86,
        Stats.Sta: 44,
        Stats.Spe: 100,
        Stats.Atk: 85,
        Stats.Def: 61,
        Stats.SpA: 23,
        Stats.SpD: 61,
    },
    (Types.crystal, Types.melee),
)
PIGEPIC_DATA = (
    {
        Stats.HP: 54,
        Stats.Sta: 72,
        Stats.Spe: 58,
        Stats.Atk: 60,
        Stats.Def: 72,
        Stats.SpA: 45,
        Stats.SpD: 72,
    },
    (Types.wind, None),
)
BETA_BURST_DATA = {
    'Name': 'Beta Burst',
    'Type': Types.mental,
    'Synergy Type': None,
    'Class': 'Special',
    'DMG': 100,
    'STA': 23,
    'Hold': 0,
    'Priority': 2,
}
HIGHPRESSURE_WATER_DATA = {
    'Name': 'High-pressure Water',
    'Type': Types.water,
    'Synergy Type': Types.fire,
    'Class': 'Special',
    'DMG': 50,
    'STA': 15,
    'Hold': 1,
    'Priority': 2,
}
STONE_WALL_DATA = {
    'Name': 'Stone Wall',
    'Type': Types.earth,
    'Synergy Type': None,
    'Class': 'Status',
    'DMG': 0,
    'STA': 18,
    'Hold': 1,
    'Priority': 1,
}

def test_load_temtem_data():
    consts.load_temtem_data()

    assert consts.TEMTEM_DATA['Gyalis'] == GYALIS_DATA
    assert consts.TEMTEM_DATA['Pigepic'] == PIGEPIC_DATA

def test_load_attack_data():
    consts.load_attack_data()

    assert consts.ATTACK_DATA['Beta Burst'] == BETA_BURST_DATA
    assert consts.ATTACK_DATA['High-pressure Water'] == HIGHPRESSURE_WATER_DATA
    assert consts.ATTACK_DATA['Stone Wall'] == STONE_WALL_DATA

def test_lookup_temtem():
    assert consts.lookup_temtem_data('Gyalis') == GYALIS_DATA
    assert consts.lookup_temtem_data('Pigepic') == PIGEPIC_DATA

def test_lookup_attack():
    assert consts.lookup_attack('Beta Burst') == BETA_BURST_DATA
    assert consts.lookup_attack('High-pressure Water') == HIGHPRESSURE_WATER_DATA
    assert consts.lookup_attack('Stone Wall') == STONE_WALL_DATA

import temtem

GYALIS_IMPORT = '''Gyalis @ Ice Cube
Trait: Resistant
TVs: 350 HP / 4 Sta / 146 Spe / 498 Atk / 1 Def / 1 SpD
SVs: 0 SpA
- Heat Up
- Crystal Bite
- Haito Uchi
- Sharp Stabs
'''

def test_temtem_class():
    gyalis = temtem.TemTem(
        'Gyalis',
        ['Heat Up', 'Crystal Bite', 'Haito Uchi', 'Sharp Stabs'],
        'Resistant',
        {'SpA': 0},
        {'HP': 350, 'Sta': 4, 'Spe': 146, 'Atk': 498, 'Def': 1, 'SpD': 1},
        'Ice Cube',
    )
    assert gyalis.stats == {
        Stats.HP: 222,
        Stats.Sta: 52,
        Stats.Spe: 129,
        Stats.Atk: 151,
        Stats.Def: 83,
        Stats.SpA: 26,
        Stats.SpD: 83,
    }
    assert gyalis.export() == GYALIS_IMPORT

    imported = temtem.TemTem.from_importable(GYALIS_IMPORT)
    assert imported.stats == gyalis.stats
    assert imported.moves == gyalis.moves

def run_tests():
    import traceback

    test_funcs = (
        test_load_temtem_data,
        test_load_attack_data,
        test_lookup_temtem,
        test_lookup_attack,
        test_temtem_class,
    )
    successes = []
    failures = {}
    for test_fn in test_funcs:
        try:
            test_fn()
            successes.append(test_fn.__name__)
            print('.', end='')
        except Exception as err:
            failures[test_fn.__name__] = err
            print('f', end='')

    print('\n')

    if failures:
        for func, err in failures.items():
            print('\n=== Test %s failed ===' % func, file=stderr)
            print('%r' % err, file=stderr)
            print(''.join(traceback.format_tb(err.__traceback__)), file=stderr)
            print('', file=stderr)
    else:
        print('All tests finished successfully.')

    return len(failures)

if __name__ == '__main__':
    exit(run_tests())
